#!/usr/bin/env python3
from typing import Any, Dict

import os

import numpy as np
import requests


SERVER_URL = os.getenv("SERVER_URL")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
PLAYER_NAME = os.getenv("PLAYER_NAME")


def strategy(state: Dict[str, Any]) -> Dict[str, Dict[str, int]]:
    my_id = state.get("myPlayerId")
    opponents = state.get("opponentsIds") or []

    if not my_id or not opponents:
        return {"shoot": {}, "keep": {}}

    shoot = np.random.randint(0, 3, len(opponents)).tolist()
    keep = np.random.randint(0, 3, len(opponents)).tolist()

    return {
        "shoot": {pid: int(direction) for pid, direction in zip(opponents, shoot)},
        "keep": {pid: int(direction) for pid, direction in zip(opponents, keep)},
    }


def main():
    if not SERVER_URL:
        raise SystemExit("SERVER_URL env var required")
    if not PLAYER_NAME:
        raise SystemExit("PLAYER_NAME env var required")

    status = requests.get(
        f"{SERVER_URL}/status",
        headers={"Authorization": f"Bearer {GITHUB_TOKEN}"},
        params={"player_name": PLAYER_NAME},
        timeout=10,
    )
    status.raise_for_status()
    payload = status.json()

    action = strategy(payload)
    response = requests.post(
        f"{SERVER_URL}/action",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GITHUB_TOKEN}",
        },
        json={"action": action, "player_name": PLAYER_NAME},
        timeout=10,
    )

    if not response.ok:
        detail = response.text or response.reason
        raise SystemExit(f"Submission failed: {response.status_code} {detail}")


if __name__ == "__main__":
    main()
