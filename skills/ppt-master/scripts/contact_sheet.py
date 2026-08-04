#!/usr/bin/env python3
"""
PPT Master - Contact Sheet

Composes the per-page PNGs already rendered by visual_review.py
(<project_path>/.preview/*.png) into a single grid image for quick visual inspection —
the "renderização completa... e produzir contact sheet" gate (FR-010).

This script never renders pages itself; it only tiles PNGs visual_review.py already wrote.

Usage:
    python3 scripts/contact_sheet.py <project_path>

Exit codes:
    0  contact sheet written
    4  no page PNGs found under <project_path>/.preview/ (propagates visual_review.py's
       "page render failure" code — nothing to compose)

Dependencies:
    Pillow (already a project dependency — see requirements.txt)
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from console_encoding import configure_utf8_stdio  # noqa: E402

configure_utf8_stdio()

THUMB_WIDTH = 320
LABEL_HEIGHT = 24
PADDING = 12
BACKGROUND = (30, 30, 30)
LABEL_BG = (0, 0, 0)
LABEL_FG = (255, 255, 255)


def build_contact_sheet(preview_dir: Path) -> Image.Image:
    png_paths = sorted(preview_dir.glob("*.png"))
    if not png_paths:
        raise FileNotFoundError(f"no page PNGs found under {preview_dir}")

    thumbnails: list[tuple[str, Image.Image]] = []
    for png_path in png_paths:
        with Image.open(png_path) as img:
            img = img.convert("RGB")
            ratio = THUMB_WIDTH / img.width
            thumb_height = round(img.height * ratio)
            thumbnails.append((png_path.stem, img.resize((THUMB_WIDTH, thumb_height))))

    cell_h = max(h for _, img in thumbnails for h in [img.height]) + LABEL_HEIGHT
    cols = math.ceil(math.sqrt(len(thumbnails)))
    rows = math.ceil(len(thumbnails) / cols)

    cell_w = THUMB_WIDTH + PADDING
    sheet_w = cols * cell_w + PADDING
    sheet_h = rows * (cell_h + PADDING) + PADDING

    sheet = Image.new("RGB", (sheet_w, sheet_h), BACKGROUND)
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.load_default()
    except Exception:  # pragma: no cover - defensive, load_default rarely fails
        font = None

    for index, (stem, thumb) in enumerate(thumbnails):
        col = index % cols
        row = index // cols
        x = PADDING + col * cell_w
        y = PADDING + row * (cell_h + PADDING)
        sheet.paste(thumb, (x, y))
        draw.rectangle(
            [x, y + thumb.height, x + THUMB_WIDTH, y + thumb.height + LABEL_HEIGHT],
            fill=LABEL_BG,
        )
        draw.text((x + 4, y + thumb.height + 4), stem, fill=LABEL_FG, font=font)

    return sheet


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_path", help="Project directory (expects .preview/*.png)")
    args = parser.parse_args(argv)

    project_path = Path(args.project_path)
    preview_dir = project_path / ".preview"

    try:
        sheet = build_contact_sheet(preview_dir)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 4

    validation_dir = project_path / "validation"
    validation_dir.mkdir(parents=True, exist_ok=True)
    out_path = validation_dir / "contact_sheet.png"
    sheet.save(out_path)
    print(f"[OK] {out_path} ({sheet.width}x{sheet.height})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
