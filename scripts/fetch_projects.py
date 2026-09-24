"""Fetch public GitHub repos tagged with the `portfolio` topic -> data/projects.json.

Also writes changes.json (new / edited projects) for the notification step.
"""
import json
import os
import sys
from pathlib import Path

import requests

USER = os.environ.get("GH_USER", "mohamedgameel21")
TOPIC = os.environ.get("PORTFOLIO_TOPIC", "portfolio")
TOKEN = os.environ.get("GITHUB_TOKEN")
OUT = Path("data/projects.json")
CHANGES = Path("changes.json")

# Fields whose change should trigger a notification (not "updated"/"stars").
WATCHED = ("description", "demo", "topics", "language")


def pretty(name: str) -> str:
    return name.replace("_", " ").replace("-", " ").strip()


def fetch_repos():
    headers = {"Accept": "application/vnd.github+json"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    repos, page = [], 1
    while True:
        r = requests.get(
            f"https://api.github.com/users/{USER}/repos",
            params={"per_page": 100, "page": page, "sort": "pushed"},
            headers=headers,
            timeout=30,
        )
        r.raise_for_status()
        batch = r.json()
        repos += batch
        if len(batch) < 100:
            return repos
        page += 1


def main() -> int:
    projects = []
    for p in fetch_repos():
        if p["fork"] or p["archived"] or p["name"].lower() == USER.lower():
            continue  # skip forks, archived repos and the profile-README repo
        if TOPIC not in (p.get("topics") or []):
            continue
        projects.append(
            {
                "name": p["name"],
                "title": pretty(p["name"]),
                "description": (p["description"] or "").strip(),
                "url": p["html_url"],
                "demo": (p["homepage"] or "").strip(),
                "topics": [t for t in p["topics"] if t != TOPIC],
                "language": p["language"] or "",
                "stars": p["stargazers_count"],
                "updated": p["pushed_at"],
            }
        )
    projects.sort(key=lambda x: x["updated"], reverse=True)

    first_run = not OUT.exists() or OUT.read_text().strip() in ("", "[]")
    old = {} if first_run else {p["name"]: p for p in json.loads(OUT.read_text())}

    changes = []
    if not first_run:  # first run = baseline, don't spam notifications
        for p in projects:
            prev = old.get(p["name"])
            if prev is None:
                changes.append({"kind": "new", **p})
            elif any(prev.get(k) != p.get(k) for k in WATCHED):
                changes.append({"kind": "updated", **p})

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(projects, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    CHANGES.write_text(json.dumps(changes, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"{len(projects)} projects, {len(changes)} changes (first_run={first_run})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
