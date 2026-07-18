#!/usr/bin/env python3
"""Render public GitHub contribution data as an animated monochrome SVG."""

from __future__ import annotations

import html
import json
import os
from datetime import date, timedelta
from pathlib import Path


# --- HEATMAP CONFIG: edit only this marked block -----------------------------
INPUT = Path("contributions.json")
OUTPUT = Path("contrib-heatmap.svg")
W = 900
H = 205
CELL = 10
GAP = 3
LEVEL_COLORS = ["#161b22", "#30363d", "#57606a", "#8c959f", "#f0f6fc"]
BACKGROUND = "#0d1117"
# --- END HEATMAP CONFIG ------------------------------------------------------


def truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def render(data: dict, static: bool) -> str:
    days = sorted(data["days"], key=lambda item: item["date"])
    first = date.fromisoformat(days[0]["date"])
    # GitHub calendars place Sunday at row zero.
    grid_start = first - timedelta(days=(first.weekday() + 1) % 7)
    x0 = 30
    y0 = 55

    cells: list[str] = []
    month_labels: list[str] = []
    seen_months: set[tuple[int, int]] = set()
    for sequence, item in enumerate(days):
        day = date.fromisoformat(item["date"])
        offset = (day - grid_start).days
        week = offset // 7
        weekday = offset % 7
        x = x0 + week * (CELL + GAP)
        y = y0 + weekday * (CELL + GAP)
        level = max(0, min(4, int(item.get("level", 0))))
        fill = LEVEL_COLORS[level]
        label = html.escape(f"{item['count']} contributions on {day:%B %d, %Y}")
        animation = "" if static else f' class="cell" style="--delay:{sequence * 0.012:.3f}s"'
        cells.append(
            f'<rect{animation} x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" '
            f'fill="{fill}"><title>{label}</title></rect>'
        )

        month_key = (day.year, day.month)
        if day.day <= 7 and month_key not in seen_months:
            seen_months.add(month_key)
            month_labels.append(f'<text class="month" x="{x}" y="45">{day:%b}</text>')

    legend_x = W - 174
    legend = [f'<text class="small" x="{legend_x}" y="177">Less</text>']
    for index, color in enumerate(LEVEL_COLORS):
        x = legend_x + 35 + index * (CELL + 4)
        legend.append(
            f'<rect x="{x}" y="168" width="{CELL}" height="{CELL}" rx="2" fill="{color}"/>'
        )
    legend.append(f'<text class="small" x="{legend_x + 111}" y="177">More</text>')

    animation_css = ""
    if not static:
        animation_css = """
    .cell { opacity: 0; animation: reveal .08s steps(1, end) forwards; animation-delay: var(--delay); }
    @keyframes reveal { to { opacity: 1; } }
    @media (prefers-reduced-motion: reduce) { .cell { opacity: 1; animation: none; } }
"""

    username = html.escape(str(data["username"]))
    total = int(data["total"])
    current = int(data["current_streak"])
    longest = int(data["longest_streak"])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">
  <title id="title">GitHub contribution activity for {username}</title>
  <desc id="desc">{total} contributions in the last year. Current streak {current} days; longest streak {longest} days.</desc>
  <style>
    text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}
    .heading {{ fill: #f0f6fc; font-size: 12px; font-weight: 600; }}
    .month, .small {{ fill: #8b949e; font-size: 9px; }}
    .stats {{ fill: #c9d1d9; font-size: 10px; }}
{animation_css}  </style>
  <rect width="{W}" height="{H}" rx="12" fill="{BACKGROUND}"/>
  <rect x="0.75" y="0.75" width="{W - 1.5}" height="{H - 1.5}" rx="11.25" fill="none" stroke="#30363d" stroke-width="1.5"/>
  <text class="heading" x="25" y="25">{username} // CONTRIBUTION SIGNAL</text>
  <text class="small" x="875" y="25" text-anchor="end">LAST 365 DAYS</text>
  {''.join(month_labels)}
  {''.join(cells)}
  <text class="stats" x="25" y="177">TOTAL {total:,}   ·   CURRENT STREAK {current}D   ·   LONGEST {longest}D</text>
  {''.join(legend)}
</svg>
'''


def main() -> None:
    if not INPUT.is_file():
        raise SystemExit(f"Contribution data not found: {INPUT}")
    data = json.loads(INPUT.read_text(encoding="utf-8"))
    static = truthy(os.getenv("STATIC"))
    OUTPUT.write_text(render(data, static), encoding="utf-8")
    mode = "static" if static else "animated"
    print(f"Wrote {OUTPUT} ({W}x{H}, {mode})")


if __name__ == "__main__":
    main()
