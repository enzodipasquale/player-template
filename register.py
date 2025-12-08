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
    
    # Required fields for automated workflow triggering
    # GITHUB_REPOSITORY is automatically set by GitHub Actions (format: "owner/repo")
    # GITHUB_REPOSITORY is automatically set by GitHub Actions; GITHUB_REPO can be used as fallback
    github_repo = os.getenv("GITHUB_REPOSITORY", os.getenv("GITHUB_REPO", "")).strip()
    github_workflow_name = os.getenv("GITHUB_WORKFLOW_NAME", "").strip()  # Default: "play-game.yml"

    # Print what we know without leaking actual secrets.
    print(
        f"[register] Config state: SERVER_URL={'set' if server_url else 'missing'}, "
        f"GAME_TOKEN={'set' if game_token else 'missing'}, "
        f"PLAYER_NAME={'set' if player_name else 'missing'}, "
        f"GITHUB_REPO={'set' if github_repo else 'missing'}",
        flush=True,
    )
    
    if not github_repo:
        raise SystemExit(
            "GITHUB_REPO not found. "
            "If running in GitHub Actions, GITHUB_REPOSITORY is automatically set. "
            "Otherwise, set GITHUB_REPO environment variable (format: 'username/repo-name')"
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

    # Build registration payload
    # Note: GAME_TOKEN from Authorization header will be used for both auth and triggering
    registration_data = {
        "player_name": player_name,
        "github_repo": github_repo,
    }
    
    if github_workflow_name:
        registration_data["github_workflow_name"] = github_workflow_name
    
    print(f"[register] Configuring auto-trigger for repo: {github_repo}", flush=True)
    print(f"[register] Using GAME_TOKEN for both authentication and workflow triggering", flush=True)

    try:
        response = requests.post(
            f"{server_url}/register",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {game_token}",
            },
            json=registration_data,
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
        if payload.get("github_repo"):
            print(f"✅ Auto-trigger configured for repo: {payload.get('github_repo')}")
    elif status == "already_registered":
        print(f"Player '{payload.get('player_name')}' already registered. Using id {payload.get('player_id')}.")
    else:
        print(f"Registration response: {payload}")


if __name__ == "__main__":
    main()

