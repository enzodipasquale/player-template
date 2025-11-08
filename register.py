#!/usr/bin/env python3
import os
import sys

import requests


def main() -> None:
    server_url = os.getenv("SERVER_URL", "https://game-platform-v2-914970891924.us-central1.run.app").rstrip("/")
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
            json={},
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
        print(f"Player registered with id {payload.get('player_id')}.")
    elif status == "already_registered":
        print(f"Player already registered. Using id {payload.get('player_id')}.")
    else:
        print(f"Registration response: {payload}")


if __name__ == "__main__":
    main()
