#!/usr/bin/env python3
"""Fetch one year of public GitHub contribution data without authentication."""

from __future__ import annotations

import json
import os
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup


# --- CONTRIBUTION FETCH CONFIG: edit only this marked block ------------------
DEFAULT_USER = "Anu062004"
OUTPUT = Path("contributions.json")
DAYS = 365
# --- END CONTRIBUTION FETCH CONFIG ------------------------------------------


COUNT_PATTERN = re.compile(r"([\d,]+) contributions?")


def contribution_count(cell, soup: BeautifulSoup) -> int:
    direct = cell.get("data-count")
    if direct is not None:
        return int(direct)

    candidates = [cell.get("aria-label", "")]
    element_id = cell.get("id")
    if element_id:
        tooltip = soup.find(attrs={"for": element_id})
        if tooltip:
            candidates.append(tooltip.get_text(" ", strip=True))

    for text in candidates:
        if "No contributions" in text:
            return 0
        match = COUNT_PATTERN.search(text)
        if match:
            return int(match.group(1).replace(",", ""))

    # Levels remain useful if GitHub omits tooltip counts, but inventing totals
    # would make the streak statistics inaccurate, so fail loudly instead.
    raise ValueError(f"Could not find contribution count for {cell.get('data-date')}")


def calculate_streaks(days: list[dict[str, int | str]], today: date) -> tuple[int, int]:
    by_date = {date.fromisoformat(str(item["date"])): int(item["count"]) for item in days}

    cursor = today
    if by_date.get(cursor, 0) == 0:
        cursor -= timedelta(days=1)
    current = 0
    while by_date.get(cursor, 0) > 0:
        current += 1
        cursor -= timedelta(days=1)

    longest = 0
    running = 0
    for item in days:
        if int(item["count"]) > 0:
            running += 1
            longest = max(longest, running)
        else:
            running = 0
    return current, longest


def fetch(username: str) -> dict:
    today = date.today()
    start = today - timedelta(days=DAYS - 1)
    url = f"https://github.com/users/{username}/contributions"
    response = requests.get(
        url,
        params={"from": start.isoformat(), "to": today.isoformat()},
        headers={
            "Accept": "text/html",
            "Accept-Language": "en-US,en;q=0.9",
            "User-Agent": "profile-art-contribution-fetcher/1.0",
        },
        timeout=30,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    cells = soup.select("[data-date][data-level]")
    if len(cells) < 300:
        raise RuntimeError(f"GitHub returned only {len(cells)} contribution cells")

    found: dict[date, dict[str, int | str]] = {}
    for cell in cells:
        day = date.fromisoformat(cell["data-date"])
        if start <= day <= today:
            found[day] = {
                "date": day.isoformat(),
                "count": contribution_count(cell, soup),
                "level": int(cell.get("data-level", 0)),
            }

    days: list[dict[str, int | str]] = []
    cursor = start
    while cursor <= today:
        days.append(found.get(cursor, {"date": cursor.isoformat(), "count": 0, "level": 0}))
        cursor += timedelta(days=1)

    current, longest = calculate_streaks(days, today)
    total = sum(int(item["count"]) for item in days)
    return {
        "username": username,
        "range": {"from": start.isoformat(), "to": today.isoformat()},
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "total": total,
        "current_streak": current,
        "longest_streak": longest,
        "days": days,
    }


def main() -> None:
    username = os.getenv("GH_PROFILE_USER", DEFAULT_USER).strip() or DEFAULT_USER
    data = fetch(username)
    OUTPUT.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(
        f"Wrote {OUTPUT}: {data['total']} contributions, "
        f"current streak {data['current_streak']}, longest {data['longest_streak']}"
    )


if __name__ == "__main__":
    main()
