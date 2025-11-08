#!/usr/bin/env python3
"""Fetch and print the current game state from the penalty shootout server."""

import json
import os

import requests


DEFAULT_SERVER_URL = "https://game-platform-v2-914970891924.us-central1.run.app"


def main() -> None:
    server_url = os.getenv("SERVER_URL", "").strip() or DEFAULT_SERVER_URL
    server_url = server_url.rstrip("/")

    try:
        response = requests.get(f"{server_url.rstrip('/')}/status", timeout=10)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise SystemExit(f"Failed to fetch status: {exc}") from exc

    try:
        payload = response.json()
    except ValueError:
        print(response.text)
        return

    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

