"""Send a WhatsApp message (via the free CallMeBot API) for each new/updated project,
formatted so it can be pasted straight into LinkedIn > Projects."""
import json
import os
import sys
from pathlib import Path

import requests

API = "https://api.callmebot.com/whatsapp.php"
PHONE = os.environ.get("WHATSAPP_PHONE", "").strip()      # e.g. +2010XXXXXXXX
APIKEY = os.environ.get("CALLMEBOT_APIKEY", "").strip()
CHANGES = Path("changes.json")


def build_message(p: dict) -> str:
    head = "New project" if p["kind"] == "new" else "Project updated"
    lines = [
        f"{head} on GitHub: {p['title']}",
        "",
        "Paste into LinkedIn > Add profile section > Projects:",
        f"Name: {p['title']}",
        f"Description: {p['description'] or '(add a repo description on GitHub)'}",
    ]
    if p["topics"]:
        lines.append("Skills: " + ", ".join(p["topics"][:5]))
    lines.append(f"URL: {p['demo'] or p['url']}")
    if p["demo"]:
        lines.append(f"Code: {p['url']}")
    return "\n".join(lines)


def main() -> int:
    if not CHANGES.exists():
        print("no changes.json - nothing to send")
        return 0
    changes = json.loads(CHANGES.read_text(encoding="utf-8"))
    if not changes:
        print("no new or updated projects")
        return 0
    if not (PHONE and APIKEY):
        print("WARNING: WHATSAPP_PHONE / CALLMEBOT_APIKEY secrets missing - skipping WhatsApp")
        return 0
    for p in changes:
        r = requests.get(
            API,
            params={"phone": PHONE, "text": build_message(p), "apikey": APIKEY},
            timeout=30,
        )
        print(p["name"], "->", r.status_code)
        if r.status_code != 200:
            print(r.text[:300])
            return 1  # fail the run so nothing is committed and the next run retries
    return 0


if __name__ == "__main__":
    sys.exit(main())
