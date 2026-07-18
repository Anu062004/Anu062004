#!/usr/bin/env python3
"""Remove a portrait background and enhance foreground detail with CLAHE."""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import new_session, remove


# --- PORTRAIT PREP CONFIG: tune only this marked block -----------------------
CLIP_LIMIT = 7.5
CLAHE_GRID = (8, 8)
SHADOW_GAMMA = 0.72
MODEL = "u2net_human_seg"
# --- END PORTRAIT PREP CONFIG ------------------------------------------------


def enhance_foreground(image: Image.Image, clip_limit: float) -> Image.Image:
    rgba = np.asarray(image.convert("RGBA"), dtype=np.uint8)
    rgb = rgba[:, :, :3]
    alpha = rgba[:, :, 3]

    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
    lightness, channel_a, channel_b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=CLAHE_GRID)
    lightness = clahe.apply(lightness)

    # Lift shadow detail before returning to RGB. The alpha channel remains
    # untouched, so the removed background stays transparent.
    normalized = lightness.astype(np.float32) / 255.0
    lightness = np.clip(np.power(normalized, SHADOW_GAMMA) * 255.0, 0, 255).astype(
        np.uint8
    )
    enhanced = cv2.cvtColor(cv2.merge((lightness, channel_a, channel_b)), cv2.COLOR_LAB2RGB)
    enhanced[alpha == 0] = 0
    return Image.fromarray(np.dstack((enhanced, alpha)), mode="RGBA")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Remove a photo background and boost local foreground contrast."
    )
    parser.add_argument("input", type=Path, help="Input portrait (JPG/PNG)")
    parser.add_argument("output", type=Path, help="Transparent output PNG")
    parser.add_argument(
        "--clip-limit",
        type=float,
        default=CLIP_LIMIT,
        help=f"CLAHE clip limit (default: {CLIP_LIMIT})",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.input.is_file():
        raise SystemExit(f"Input photo not found: {args.input}")
    if args.clip_limit <= 0:
        raise SystemExit("--clip-limit must be greater than zero")

    source = Image.open(args.input).convert("RGBA")
    session = new_session(MODEL)
    cutout = remove(source, session=session, post_process_mask=True)
    result = enhance_foreground(cutout, args.clip_limit)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.save(args.output, format="PNG", optimize=True)
    print(f"Wrote {args.output} ({result.width}x{result.height}, clipLimit={args.clip_limit:g})")


if __name__ == "__main__":
    main()
