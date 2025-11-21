#!/usr/bin/env python3
"""CLI helper for registering this template player with the penalty shootout server."""
import os
import sys

import requests


def main() -> None:
    # Workflows and local runs both rely on these secrets.
    server_url = os.getenv("SERVER_URL", "").strip()
    game_token = os.getenv("GAME_TOKEN", "").strip()
    player_name = os.getenv("PLAYER_NAME", "").strip()

    # Print what we know without leaking actual secrets.
    print(
        f"[register] Config state: SERVER_URL={'set' if server_url else 'missing'}, "
        f"GAME_TOKEN={'set' if game_token else 'missing'}, "
        f"PLAYER_NAME={'set' if player_name else 'missing'}",
        flush=True,
    )

    if not server_url:
        raise SystemExit("SERVER_URL environment variable not set")
    if not game_token:
        raise SystemExit("GAME_TOKEN environment variable not set")
    if not player_name:
        raise SystemExit("PLAYER_NAME environment variable not set")

    if not server_url.startswith(("http://", "https://")):
        raise SystemExit(f"SERVER_URL must include scheme (http/https); got '{server_url}'")

    # Normalise the base URL before appending the path.
    server_url = server_url.rstrip("/")
    print(f"[register] Using endpoint {server_url}/register", flush=True)

    try:
        response = requests.post(
            f"{server_url}/register",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {game_token}",
            },
            json={"player_name": player_name},
            timeout=10,
        )
    except Exception as exc:  # pragma: no cover - network failure path
        raise SystemExit(f"Registration error: {exc}") from exc

    if not response.ok:
        raise SystemExit(f"Registration failed: {response.status_code} {response.text}")

    try:
        payload = response.json()
    except ValueError:
        print("Registration succeeded but response was not JSON.")
        return

    status = (payload.get("status") or "").lower()
    if status == "registered":
        print(f"Player '{payload.get('player_name')}' registered with id {payload.get('player_id')}.")
    elif status == "already_registered":
        print(f"Player '{payload.get('player_name')}' already registered. Using id {payload.get('player_id')}.")
    else:
        print(f"Registration response: {payload}")


if __name__ == "__main__":
    main()

