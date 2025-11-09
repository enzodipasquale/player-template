# Neutral Player Template

Quick-start kit for a penalty-shootout bot.

## 1. Repository Setup

- Fork if you want GitHub Actions to run on schedule. A clone works for local testing but you must push to a repo you control before the workflow can post moves.
- In **Settings → Secrets and variables → Actions** add:
  - `GAME_TOKEN` – fine-grained PAT with `Actions` and `Workflows` read/write permissions.
  - `SERVER_URL` – base UBX server URL (no extra path segments).
- Optional variable: `ENABLE_SCHEDULE=true` to let the cron workflow fire.

## 2. Registration

1. Pick a player handle.
2. Register locally or via Actions:
   ```bash
   export SERVER_URL="https://ubx-dev-...run.app"
   export GITHUB_TOKEN="ghp_...."
   python register.py        # or python register.py your-handle
   ```
3. The script reports whether the player was created or already existed and shows the server-issued ID.
4. Troubleshooting: missing env vars, URLs without `https://`, or stray path components are the usual suspects.

## 3. Strategy Flow

- `strategy.py` calls `/status`, grabs `myPlayerId`, builds random `"shoot"`/`"keep"` maps for the remaining IDs, and posts to `/action`.
- Swap out the internals of `strategy()` with your own logic. Keep the payload structure and stick to `"0"`, `"1"`, `"2"` for directions.
- `/status` highlights:
  - `playerIds` – all registered players.
  - `myPlayerId` – your ID for this token.
  - `opponents` – everyone else.
  - `state` – history of past rounds.
- Example action payload:
  ```json
  {
    "action": {
      "shoot": { "opponent-id": "2" },
      "keep":  { "opponent-id": "1" }
    }
  }
  ```
  Use `"*": "direction"` to broadcast a default choice.

## 4. GitHub Actions

- `.github/workflows/schedule_strategy.yml` runs every 5 minutes and can also be triggered manually from the Actions tab.
- To enable the schedule:
  1. Populate `GAME_TOKEN` and `SERVER_URL` secrets.
  2. (Optional) set `ENABLE_SCHEDULE=true`.
  3. Watch the workflow logs to confirm submissions.

## 5. Local Iteration

- Install `requests` and `numpy`, export `SERVER_URL` and `GITHUB_TOKEN`, then run `python strategy.py`.
- `python show_state.py` is handy for dumping the `/status` payload while debugging.

Adjust `strategy()` as you like and let the workflow handle recurring submissions.
