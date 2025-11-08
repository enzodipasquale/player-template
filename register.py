#!/usr/bin/env python3
import os
import sys

import requests


DEFAULT_SERVER_URL = "https://game-platform-v2-914970891924.us-central1.run.app"


def main() -> None:
    raw_server = os.getenv("SERVER_URL", "").strip()
    if raw_server:
        server_url = raw_server
    else:
        server_url = DEFAULT_SERVER_URL
        print(f"[register] SERVER_URL not set; defaulting to {server_url}", flush=True)

    if not server_url.startswith(("http://", "https://")):
        server_url = "https://" + server_url.lstrip("/")
        print(f"[register] Added https:// scheme → {server_url}", flush=True)

    server_url = server_url.rstrip("/")
    print(f"[register] Using endpoint {server_url}/register", flush=True)
    github_token = os.getenv("GITHUB_TOKEN", "").strip()

    if not github_token:
        raise SystemExit("GITHUB_TOKEN environment variable not set")

    try:
        response = requests.post(
            f"{server_url}/register",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {github_token}",
            },
            json={"player_name": "player-template"},
            timeout=10,
        )
    except Exception as exc:
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
