# Template Player

Minimal starter repo for the penalty-shootout pilots. Fork / copy it for each new bot.

## Game Snapshot

- Each round every player acts *against every other player* twice: once as shooter, once as keeper.
- Actions are digits `'0'`, `'1'`, `'2'` (`left`, `centre`, `right`).
- The turn state returned by `/status` looks like:
  ```json
  {
    "gameState": {
      "turn_id": 3,
      "state": [
        {
          "cassano": { "shoot": {"ibrahimovic": "2"}, "keep": {"ibrahimovic": "1"} },
          "ibrahimovic": { "shoot": {"cassano": "0"}, "keep": {"cassano": "2"} }
        },
        ...
      ]
    }
  }
  ```
- For this template we answer with `"shoot"`/`"keep"` maps keyed by **player name**.

## Repo Contents

- `strategy.py` – fetches `/status`, builds random `"shoot"`/`"keep"` maps, and posts the action.
- `register.py` – helper you can run locally or from CI to register the player.
- `.github/workflows/`
  - `register.yml` – manual workflow to run `register.py`.
  - `manual_strategy.yml` – triggers a single strategy run on demand.
  - `scheduled_strategy.yml` – cron job that only runs when you set a toggle (see below).

## Setup Checklist

1. Set secrets via **Settings → Secrets and variables → Actions**:
   - `GAME_TOKEN` – fine-grained personal access token with permissions
     - Repository: this repo only
     - Permissions: `actions:read/write`, `metadata:read`
   - `SERVER_URL` – e.g. `https://game-platform-v2-914970891924.us-central1.run.app`
2. (Optional) set repository **Variable** `ENABLE_SCHEDULE=true` to turn on the cron job.
   - Leave it unset/false and the scheduled workflow will exit immediately with a notice.
   - You can still run the workflow manually via “Run workflow”.

## Running Workflows

- **Register Player** – open Actions → *Register Player* → *Run workflow*. Re-run if you rotate tokens.
- **Manual Strategy** – trigger on demand to see a single action submission.
- **Scheduled Strategy** – runs every 10 minutes once `ENABLE_SCHEDULE=true`. Disable by clearing that variable.

## Customising `strategy.py`

`strategy.py` currently builds random `"shoot"`/`"keep"` maps (broadcasting `"*"` if alone). Swap in your own logic—just fill those maps with `'0'`, `'1'`, `'2'` per opponent name. The helper already fetches `/status` for you.

That’s it—copy the repo, set the secrets, and you’re ready to launch your own . Good luck!
