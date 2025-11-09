# Player Template

Quick-start kit for a penalty-shootout bot.

## 1. Quick Start Checklist

1. **Copy the template** – Fork this repository into your own GitHub account if you want the automated player to run. You can clone first to experiment locally, but GitHub Actions only executes in your fork.
2. **Choose your handle** – Open `register.py` and change the line  
   ```python
   json={"player_name": "player-template"},
   ```  
   Replace `"player-template"` with the public name you want the server to show (letters, numbers, or hyphens keep things simple).
3. **Add secrets for automation** – In your fork visit **Settings → Secrets and variables → Actions** and create:
   - `GAME_TOKEN` – a fine-grained GitHub token with `Actions` and `Workflows` read/write scopes.
   - `SERVER_URL` – the base UBX server URL, e.g. `https://ubx-dev-123.a.run.app` (no extra path segments).

## 2. Registration

1. Confirm the player name you set in `register.py`—that nickname is what the server will display on leaderboards.
2. Register via GitHub Actions (Actions tab → “Scheduled Strategy” → “Run workflow”). The workflow will execute `register.py` before the first scheduled submission, report whether the handle was created, and log the server-issued ID.
3. If registration fails, double-check the `SERVER_URL` and `GAME_TOKEN` secrets—typos or missing URL schemes (`https://`) are the usual culprits.

## 3. What the scripts do

- `register.py` validates that `SERVER_URL` and `GITHUB_TOKEN` are present, prints a quick config summary, then calls `/register` with your chosen player name. Run it once per fork (or any time you change the name) so the server links your token to that handle.
- `strategy.py` fetches `/status`, builds an action, and posts it back via `/action`. The default logic is random; customise it by editing `strategy(state)` (or adding helper functions) to pick `shoot`/`keep` directions based on the state history, opponent behaviour, etc. The function must still return the same dictionary shape so the payload remains valid.

Test changes locally by exporting `SERVER_URL` and `GITHUB_TOKEN` and running `python strategy.py`. When you are happy with the behaviour, let the scheduled workflow keep submitting moves.

## 4. Understanding the `/status` payload

`/status` responds with a JSON dictionary—`{}` at the very beginning of a fresh game—that contains:

- `playerIds`: every registered player ID (these are what you target in your action maps).
- `myPlayerId`: the ID associated with your GitHub token.
- `opponents`: convenience list of all other IDs.
- `state`: nested structure that captures past rounds, scores, and other bookkeeping. For penalty shootout you will see something like:
  ```json
  {
    "round": 12,
    "scoreboard": {
      "player-id-A": {"goals": 7, "saves": 4},
      "player-id-B": {"goals": 5, "saves": 6}
    },
    "history": {
      "1": {
        "player-id-A": {"shoot": 2, "keep": 1, "scored": true},
        "player-id-B": {"shoot": 0, "keep": 2, "scored": false}
      },
      "...": "..."
    }
  }
  ```
- `turn`, `registrationPhase`, `gamePhase`: metadata describing where the match is.

Store or inspect this data to drive smarter strategies.

## 5. Building the action payload

Submissions to `/action` must look like:

```json
{
  "action": {
    "shoot": { "opponent-id": 2 },
    "keep":  { "*": 1 }
  }
}
```

- `shoot` describes the direction (`0`, `1`, or `2`) you will shoot at each opponent. Keys must be opponent IDs from the status payload or the wildcard `"*"`.
- `keep` sets your goalkeeper direction against each opponent (same key/value rules as above).
- Empty maps are acceptable until you have opponents.

The server merges the two maps per opponent when resolving the turn.

## 6. GitHub Actions

- `.github/workflows/schedule_strategy.yml` runs every 5 minutes and can also be triggered manually from the Actions tab.
- Make sure `GAME_TOKEN` and `SERVER_URL` secrets are populated, then watch the workflow logs to confirm submissions.

## 7. Local Iteration

- Install `requests` and `numpy`, export `SERVER_URL` and `GITHUB_TOKEN`, then run `python strategy.py`.
- `python show_state.py` is handy for dumping the `/status` payload while debugging.

Adjust `strategy()` as you like and let the workflow handle recurring submissions.
