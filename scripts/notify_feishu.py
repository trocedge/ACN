#!/usr/bin/env python3
"""Report a GitHub Actions run to a Feishu (Lark) group bot.

The webhook is read from the FEISHU_WEBHOOK secret; when the secret is not
configured the script is a no-op so forks and pull requests keep working.
"""

import json
import os
import sys
import time
import urllib.request

MESSAGES = {
    "success": "deployment succeeded",
    "failure": "deployment failed",
    "cancelled": "deployment was cancelled",
    "skipped": "deployment was skipped",
}


def compose_text() -> str:
    deploy = os.environ.get("DEPLOY_RESULT", "unknown")
    build = os.environ.get("BUILD_RESULT", "unknown")
    summary = MESSAGES.get(deploy, f"deployment finished with {deploy}")
    lines = [
        f"[ACN] {summary}",
        f"build: {build} / deploy: {deploy}",
        f"commit: {os.environ.get('COMMIT_SHA', '')[:7]} on {os.environ.get('BRANCH', 'main')}",
        f"site: {os.environ.get('SITE_URL', '')}",
        f"run: {os.environ.get('RUN_URL', '')}",
    ]
    return "\n".join(line for line in lines if line.split(": ", 1)[-1])


def main() -> int:
    webhook = os.environ.get("FEISHU_WEBHOOK", "").strip()
    if not webhook:
        print("FEISHU_WEBHOOK is not configured; skipping the Feishu notification.")
        return 0

    body = json.dumps({"msg_type": "text", "content": {"text": compose_text()}}).encode()
    for attempt in range(1, 4):
        request = urllib.request.Request(
            webhook, data=body, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                payload = response.read().decode("utf-8", "replace")
            print(f"Feishu response: {payload}")
            if '"code":0' in payload.replace(" ", ""):
                return 0
        except Exception as error:  # noqa: BLE001 - notification must never mask the deploy
            print(f"Feishu notification attempt {attempt} failed: {error}")
        time.sleep(3)
    print("Giving up on the Feishu notification.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
