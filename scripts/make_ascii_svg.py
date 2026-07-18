#!/usr/bin/env python3
"""Render a transparent portrait as animated, monochrome ASCII SVG art."""

from __future__ import annotations

import argparse
import html
import os
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


# --- ASCII PORTRAIT CONFIG: tune only this marked block ----------------------
CONTRAST = 1.08
GAMMA = 0.96
WHITE_FLOOR = 0.025
EDGE_WEIGHT = 0.90
DETAIL_WEIGHT = 0.36
W = 370
H = 480
COLS = 78
ROWS = 70
CHARACTERS = " .,:;irsXA253hMHGS#9B&@"
BACKGROUND = "#0d1117"
FOREGROUND = "#f0f6fc"
MUTED = "#8b949e"
# --- END ASCII PORTRAIT CONFIG ----------------------------------------------


def truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def fit_to_grid(image: Image.Image) -> tuple[np.ndarray, np.ndarray]:
    rgba = image.convert("RGBA")
    alpha = rgba.getchannel("A")
    bbox = alpha.getbbox()
    if bbox is None:
        raise SystemExit("The prepared image has no visible foreground pixels")

    subject = rgba.crop(bbox)
    art_w, art_h = W - 34, H - 67
    scale = min(art_w / subject.width, art_h / subject.height)
    size = (
        max(1, round(subject.width * scale)),
        max(1, round(subject.height * scale)),
    )
    subject = subject.resize(size, Image.Resampling.LANCZOS)

    canvas = Image.new("RGBA", (art_w, art_h), (0, 0, 0, 0))
    x = (art_w - size[0]) // 2
    y = art_h - size[1]
    canvas.alpha_composite(subject, (x, y))
    sampled = canvas.resize((COLS, ROWS), Image.Resampling.LANCZOS)

    array = np.asarray(sampled, dtype=np.uint8)
    gray = cv2.cvtColor(array[:, :, :3], cv2.COLOR_RGB2GRAY).astype(np.float32) / 255.0
    alpha_values = array[:, :, 3].astype(np.float32) / 255.0
    return gray, alpha_values


def make_density(gray: np.ndarray, alpha: np.ndarray) -> np.ndarray:
    foreground = gray[alpha > 0.15]
    if foreground.size == 0:
        raise SystemExit("The prepared image has no usable foreground detail")

    # Normalize against the subject itself. This expands the narrow tonal
    # range found in backlit photos instead of letting the dark shirt collapse
    # into one repeated high-density character.
    low, high = np.percentile(foreground, (3.0, 97.0))
    if high - low < 0.01:
        high = low + 0.01
    normalized = np.clip((gray - low) / (high - low), 0.0, 1.0)
    global_darkness = 1.0 - normalized

    # Retain small local changes in the face, hair, collar, and shirt while
    # keeping the overall silhouette stable.
    work = gray.copy()
    work[alpha <= 0.15] = float(np.median(foreground))
    local_mean = cv2.GaussianBlur(work, (0, 0), 1.15)
    local_detail = np.clip(0.5 + (local_mean - work) * 3.8, 0.0, 1.0)
    darkness = (1.0 - DETAIL_WEIGHT) * global_darkness + DETAIL_WEIGHT * local_detail
    tone = np.clip((darkness - 0.5) * CONTRAST + 0.5, 0.0, 1.0)
    tone = np.power(tone, GAMMA)
    density = alpha * (WHITE_FLOOR + (1.0 - WHITE_FLOOR) * tone)

    # Edge energy makes a backlit silhouette read as an intentional contour.
    alpha_edge_x = cv2.Sobel(alpha, cv2.CV_32F, 1, 0, ksize=3)
    alpha_edge_y = cv2.Sobel(alpha, cv2.CV_32F, 0, 1, ksize=3)
    tone_edge_x = cv2.Sobel(work * alpha, cv2.CV_32F, 1, 0, ksize=3)
    tone_edge_y = cv2.Sobel(work * alpha, cv2.CV_32F, 0, 1, ksize=3)
    edge = np.maximum(
        cv2.magnitude(alpha_edge_x, alpha_edge_y),
        cv2.magnitude(tone_edge_x, tone_edge_y),
    )
    maximum = float(edge.max())
    if maximum > 0:
        edge /= maximum
    density = np.maximum(density, edge * EDGE_WEIGHT)
    density[alpha < 0.035] = 0.0
    return np.clip(density, 0.0, 1.0)


def render_svg(density: np.ndarray, static: bool, square_preview: bool = False) -> str:
    pad_x = 17
    top = 49
    bottom = 18
    art_h = H - top - bottom
    cell_w = (W - 2 * pad_x) / COLS
    cell_h = art_h / ROWS
    font_size = cell_h * 1.04
    total_cells = COLS * ROWS
    delay_step = 4.8 / total_cells

    spans: list[str] = []
    for row in range(ROWS):
        for column in range(COLS):
            value = float(density[row, column])
            index = min(len(CHARACTERS) - 1, int(round(value * (len(CHARACTERS) - 1))))
            character = CHARACTERS[index]
            if character == " ":
                continue
            x = pad_x + column * cell_w
            y = top + (row + 0.82) * cell_h
            escaped = html.escape(character)
            fill_opacity = 0.48 + value * 0.52
            if static:
                spans.append(
                    f'<text fill-opacity="{fill_opacity:.2f}" '
                    f'x="{x:.2f}" y="{y:.2f}">{escaped}</text>'
                )
            else:
                delay = (row * COLS + column) * delay_step
                spans.append(
                    f'<text class="char" fill-opacity="{fill_opacity:.2f}" '
                    f'style="--delay:{delay:.3f}s" '
                    f'x="{x:.2f}" y="{y:.2f}">{escaped}</text>'
                )

    animation = ""
    if not static:
        animation = """
      .char { opacity: 0; animation: reveal .01s steps(1, end) forwards; animation-delay: var(--delay); }
      @keyframes reveal { to { opacity: 1; } }
      @media (prefers-reduced-motion: reduce) { .char { opacity: 1; animation: none; } }
"""

    canvas_w = H if square_preview else W
    offset_x = (canvas_w - W) / 2

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{H}" viewBox="0 0 {canvas_w} {H}" role="img" aria-labelledby="title desc">
  <title id="title">Animated ASCII portrait of Anubhav Rajput</title>
  <desc id="desc">A monochrome terminal-style portrait that reveals character by character.</desc>
  <style>
    text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}
    .art {{ fill: {FOREGROUND}; font-size: {font_size:.2f}px; }}
    .label {{ fill: {MUTED}; font-size: 10px; letter-spacing: 1.2px; }}
{animation}  </style>
  <g transform="translate({offset_x:g} 0)">
  <rect width="{W}" height="{H}" rx="12" fill="{BACKGROUND}"/>
  <rect x="0.75" y="0.75" width="{W - 1.5}" height="{H - 1.5}" rx="11.25" fill="none" stroke="#30363d" stroke-width="1.5"/>
  <circle cx="18" cy="21" r="3" fill="#f0f6fc"/>
  <circle cx="29" cy="21" r="3" fill="#8b949e"/>
  <circle cx="40" cy="21" r="3" fill="#484f58"/>
  <text class="label" x="55" y="25">ANU062004 // PORTRAIT</text>
  <path d="M16 37.5H354" stroke="#30363d"/>
  <g class="art">{''.join(spans)}</g>
  </g>
</svg>
'''


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert a prepared PNG to animated ASCII SVG.")
    parser.add_argument("input", nargs="?", type=Path, default=Path("source-prepped.png"))
    parser.add_argument("output", nargs="?", type=Path, default=Path("avi-ascii.svg"))
    parser.add_argument("--static", action="store_true", help="Render the fully revealed frame")
    parser.add_argument(
        "--square-preview",
        action="store_true",
        help="Pad the static preview to a square so macOS Quick Look does not crop it",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.input.is_file():
        raise SystemExit(f"Prepared portrait not found: {args.input}")
    static = args.static or truthy(os.getenv("STATIC"))
    gray, alpha = fit_to_grid(Image.open(args.input))
    density = make_density(gray, alpha)
    args.output.write_text(render_svg(density, static, args.square_preview), encoding="utf-8")
    mode = "static" if static else "animated"
    output_w = H if args.square_preview else W
    print(f"Wrote {args.output} ({output_w}x{H}, {mode})")


if __name__ == "__main__":
    main()
