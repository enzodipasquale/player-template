# Player Template

Quick-start kit for a penalty-shootout bot. All shoot/keep directions are integers (`0`, `1`, `2`) everywhere in the protocol.

## 1. Quick Start Checklist

1. **Copy the template** – Fork this repository into your own GitHub account if you want the automated player to run. You can clone first to experiment locally, but GitHub Actions only executes in your fork.
2. **Set your player name** – Edit `register.py` and change `PLAYER_NAME` to the display name you want the server to show.
3. **Add secrets for automation** – In your fork visit **Settings → Secrets and variables → Actions** and create:
   - `GAME_TOKEN` – a fine-grained GitHub token with `Actions` and `Workflows` read/write scopes.
   - `SERVER_URL` – the base UBX server URL.

## 2. Registration

Run `.github/workflows/register.yml` from the Actions tab whenever you change `PLAYER_NAME`; the response includes the assigned `player_id`.

## 3. What the scripts do

- `register.py` validates secrets, posts `{ "player_name": PLAYER_NAME }` to `/register`, and logs the result. The GitHub Action runs the same script on pushes.
- `strategy.py` fetches `/status`, builds an action, and posts it back via `/action`. The default logic is random; customise it by editing `strategy(state)` (or adding helper functions) to pick `shoot`/`keep` directions based on the state history, opponent behaviour, etc. The function must still return the same dictionary shape so the payload remains valid.

Test changes locally by exporting `SERVER_URL` and `GITHUB_TOKEN` and running `python strategy.py`. When you are happy with the behaviour, let the scheduled workflow keep submitting moves.

## 4. Understanding the `/status` payload

`/status` responds with a JSON dictionary—`{}` at the very beginning of a fresh game—that contains:

- `playerIds`: every registered player ID (these are what you target in your action maps).
- `myPlayerId`: the ID associated with your GitHub token.
- `opponentsIds`: convenience list of all other IDs.
- `state`: a list where each entry records one completed turn. Penalty shootout rounds look like:
  ```json
  [
    {
      "_turnId": 1,
      "player-id-A": {
        "shoot": { "player-id-B": 2 },
        "keep":  { "player-id-B": 0 },
        "outcome": { "player-id-B": { "goal": 1 } }
      },
      "player-id-B": {
        "shoot": { "player-id-A": 1 },
        "keep":  { "player-id-A": 2 },
        "outcome": { "player-id-A": { "goal": 0 } }
      }
    },
    {
      "_turnId": 2,
      "...": { "...": "..." }
    }
  ]
  ```
- `turnId`, `registrationPhase`, `gamePhase`: metadata describing where the match is.

Store or inspect this data to drive smarter strategies.

## 5. Building the action payload

Your `strategy(state)` function must return a dictionary with two maps, one for shooting and one for keeping. For example:

```json
{
  "shoot": { "player-id-A": 2, "player-id-B": 1 },
  "keep":  { "player-id-A": 0, "player-id-B": 2 }
}
```

- `shoot` lists the direction (`0`, `1`, or `2`) you will shoot against each opponent.
- `keep` lists the direction you will guard against each opponent.
- Opponent IDs come straight from `playerIds`/`opponentsIds` in the `/status` payload.

Example: if the server identifies you as `"player-A"` and you face opponents `"player-B"` and `"player-C"`, one admissible return value is

```json
{
  "shoot": { "player-B": 2, "player-C": 0 },
  "keep":  { "player-B": 1, "player-C": 1 }
}
```

`main()` already turns this dictionary into the HTTP payload, so you do not need to worry about the outer structure—just return the maps above.

`main()` already turns this dictionary into the HTTP payload, so you do not need to worry about the outer structure—just return the maps above.

## 6. GitHub Actions

- `.github/workflows/register.yml` registers (or re-registers) the player on push/dispatch.
- `.github/workflows/schedule_strategy.yml` runs every 5 minutes and can also be triggered manually from the Actions tab.
- Make sure `GAME_TOKEN` and `SERVER_URL` secrets are populated, then watch the workflow logs to confirm submissions.

