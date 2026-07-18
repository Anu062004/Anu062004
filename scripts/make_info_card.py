#!/usr/bin/env python3
"""Generate the monochrome profile information panel."""

from __future__ import annotations

import html
from pathlib import Path


# --- INFO CARD CONFIG: edit only this marked block ---------------------------
HOST = "github.com/Anu062004"
ROWS = [
    ("NAME", "Anubhav Rajput"),
    ("ROLE", "Full-Stack Web3 Developer"),
    ("FOCUS", "Smart contracts · DeFi · dApps"),
    ("STACK", "TypeScript · Solidity · Node.js · Rust"),
    ("BUILDING", "Polygon & Linera products"),
    ("SHIPPED", "polPUMP · ShiftAid · FlowPay · CasFin"),
    ("EDU", "BMSIT Bengaluru · undergraduate"),
    ("OPEN TO", "Open-source Web3 collaboration"),
]
W = 490
H = 480
# --- END INFO CARD CONFIG ----------------------------------------------------

BACKGROUND = "#0d1117"
FOREGROUND = "#f0f6fc"
MUTED = "#8b949e"
BORDER = "#30363d"


def render() -> str:
    header_y = 58
    footer_h = 42
    available = H - header_y - footer_h - 16
    row_h = available / len(ROWS)
    if row_h < 34:
        raise SystemExit("Info rows overflow the card; increase H or shorten ROWS")

    row_markup: list[str] = []
    for index, (label, value) in enumerate(ROWS):
        y_top = header_y + index * row_h
        y_text = y_top + row_h * 0.62
        label_text = html.escape(label.upper())
        value_text = html.escape(value)
        row_markup.append(
            f'<path d="M20 {y_top:.2f}H470" stroke="{BORDER}" stroke-opacity=".55"/>'
            f'<text class="key" x="25" y="{y_text:.2f}">{label_text}</text>'
            f'<text class="value" x="128" y="{y_text:.2f}">{value_text}</text>'
        )

    footer_y = H - 22
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">
  <title id="title">Profile information for Anubhav Rajput</title>
  <desc id="desc">A monochrome terminal-style panel listing role, stack, projects, and education.</desc>
  <style>
    text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}
    .host {{ fill: {FOREGROUND}; font-size: 12px; font-weight: 600; }}
    .key {{ fill: {MUTED}; font-size: 10px; letter-spacing: 1px; }}
    .value {{ fill: {FOREGROUND}; font-size: 12px; }}
    .status {{ fill: {MUTED}; font-size: 10px; letter-spacing: .5px; }}
  </style>
  <rect width="{W}" height="{H}" rx="12" fill="{BACKGROUND}"/>
  <rect x="0.75" y="0.75" width="{W - 1.5}" height="{H - 1.5}" rx="11.25" fill="none" stroke="{BORDER}" stroke-width="1.5"/>
  <circle cx="18" cy="21" r="3" fill="#f0f6fc"/>
  <circle cx="29" cy="21" r="3" fill="#8b949e"/>
  <circle cx="40" cy="21" r="3" fill="#484f58"/>
  <text class="host" x="55" y="25">{html.escape(HOST)}</text>
  <path d="M16 37.5H474" stroke="{BORDER}"/>
  {''.join(row_markup)}
  <path d="M20 {H - footer_h:.2f}H470" stroke="{BORDER}" stroke-opacity=".55"/>
  <circle cx="28" cy="{footer_y - 3}" r="3" fill="{FOREGROUND}"/>
  <text class="status" x="39" y="{footer_y}">AVAILABLE FOR MEANINGFUL BUILDS</text>
</svg>
'''


def main() -> None:
    output = Path("info-card.svg")
    output.write_text(render(), encoding="utf-8")
    print(f"Wrote {output} ({W}x{H})")


if __name__ == "__main__":
    main()
