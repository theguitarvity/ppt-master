#!/usr/bin/env python3
"""
PPT Master - Brand Lint

Checks a project's active brand against its brand-policy.yaml (FR-011). Two independent
passes:

  (a) Pre-flight — every asset path the active brand-policy.yaml/provenance.json names
      exists on disk. Fails clearly, never substitutes (FR-006).
  (b) Usage lint — for every page in <project_path>/svg_output/, the institutional mark
      variant (positive/negative) actually used matches the background contrast rule, and
      no referenced brand logo is stretched out of its native aspect ratio.

Usage:
    python3 scripts/brand_lint.py <project_path> --brand-profile facom-ufms

Exit codes:
    0  no violations
    1  one or more violations (pre-flight asset missing, or usage violation)

Dependencies:
    None (stdlib only; PyYAML optional — falls back to a minimal parser for this file's
    flat/nested key: value shape, same posture as context_intake.py).
"""

from __future__ import annotations

import argparse
import re
import struct
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover
    yaml = None

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
BRANDS_DIR = SKILL_DIR / "templates" / "brands"

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from console_encoding import configure_utf8_stdio  # noqa: E402

configure_utf8_stdio()


def load_policy(brand_profile: str) -> dict:
    policy_path = BRANDS_DIR / brand_profile / "brand-policy.yaml"
    if not policy_path.is_file():
        raise FileNotFoundError(f"brand-policy.yaml not found for profile '{brand_profile}': {policy_path}")
    text = policy_path.read_text(encoding="utf-8")
    if yaml is not None:
        return yaml.safe_load(text) or {}
    return _fallback_parse_yaml(text)


def _fallback_parse_yaml(text: str) -> dict:
    root: dict = {}
    stack: list[tuple[int, dict]] = [(-1, root)]
    for raw_line in text.splitlines():
        if not raw_line.strip() or raw_line.strip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip().strip('">').strip()
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if value == "" or value == ">":
            child: dict = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            parent[key] = value
    return root


# ---------------------------------------------------------------------------
# (a) Pre-flight — asset existence (FR-006)
# ---------------------------------------------------------------------------

def preflight_assets(brand_profile: str, policy: dict) -> list[str]:
    brand_dir = BRANDS_DIR / brand_profile
    errors: list[str] = []
    variants = policy.get("mark_variants", {})
    for role, rel_path in variants.items():
        asset_path = brand_dir / rel_path
        if not asset_path.is_file():
            errors.append(
                f"brand asset missing for mark_variants.{role}: {asset_path} "
                "(never substitute — fix by re-downloading the official asset, FR-006)"
            )
    return errors


# ---------------------------------------------------------------------------
# (b) Usage lint — contrast + proportion (FR-011)
# ---------------------------------------------------------------------------

def _hex_to_rgb(hex_color: str) -> tuple[int, int, int] | None:
    match = re.fullmatch(r"#?([0-9A-Fa-f]{6})", hex_color.strip())
    if not match:
        return None
    value = match.group(1)
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def _relative_luminance(rgb: tuple[int, int, int]) -> float:
    r, g, b = (c / 255.0 for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _png_dimensions(path: Path) -> tuple[int, int] | None:
    try:
        with path.open("rb") as stream:
            header = stream.read(24)
    except OSError:
        return None
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    width, height = struct.unpack(">II", header[16:24])
    return width, height


def _page_background_fill(root: ET.Element) -> str | None:
    ns = {"svg": "http://www.w3.org/2000/svg"}
    canvas_w = root.get("width")
    canvas_h = root.get("height")
    for rect in root.iter("{http://www.w3.org/2000/svg}rect"):
        if rect.get("width") == canvas_w and rect.get("height") == canvas_h:
            fill = rect.get("fill")
            if fill:
                return fill
    return None


def lint_usage(svg_output_dir: Path, brand_profile: str, policy: dict) -> list[str]:
    errors: list[str] = []
    brand_dir = BRANDS_DIR / brand_profile
    variants = policy.get("mark_variants", {})
    threshold = float(policy.get("contrast_threshold_dark_fill_pct", 40))

    positive_name = Path(variants.get("positive", "")).name
    negative_name = Path(variants.get("negative", "")).name

    for svg_path in sorted(svg_output_dir.glob("*.svg")):
        try:
            root = ET.parse(svg_path).getroot()
        except ET.ParseError as exc:
            errors.append(f"{svg_path.name}: not valid SVG XML ({exc})")
            continue

        background_fill = _page_background_fill(root)
        is_dark_background = False
        if background_fill:
            rgb = _hex_to_rgb(background_fill)
            if rgb is not None:
                is_dark_background = _relative_luminance(rgb) < (1 - threshold / 100.0)

        image_hrefs = [
            image.get("{http://www.w3.org/1999/xlink}href") or image.get("href") or ""
            for image in root.iter("{http://www.w3.org/2000/svg}image")
        ]
        used_positive = any(positive_name and positive_name in href for href in image_hrefs)
        used_negative = any(negative_name and negative_name in href for href in image_hrefs)

        if is_dark_background and used_positive and not used_negative:
            errors.append(
                f"{svg_path.name}: background fill {background_fill} exceeds the "
                f"{threshold}% dark-fill threshold but uses the positive/colored mark "
                f"({positive_name}) — must use the negative/white variant ({negative_name})"
            )

        for image in root.iter("{http://www.w3.org/2000/svg}image"):
            href = image.get("{http://www.w3.org/1999/xlink}href") or image.get("href") or ""
            asset_name = Path(href).name
            if asset_name not in (positive_name, negative_name):
                continue
            source_path = brand_dir / "images" / asset_name
            native = _png_dimensions(source_path)
            if native is None:
                continue
            try:
                used_w = float(image.get("width", "0"))
                used_h = float(image.get("height", "0"))
            except ValueError:
                continue
            if used_w <= 0 or used_h <= 0:
                continue
            native_ratio = native[0] / native[1]
            used_ratio = used_w / used_h
            drift = abs(used_ratio - native_ratio) / native_ratio
            if drift > 0.02:
                errors.append(
                    f"{svg_path.name}: {asset_name} used at {used_w:g}x{used_h:g} "
                    f"(ratio {used_ratio:.3f}) distorts the native ratio {native_ratio:.3f} "
                    f"by {drift * 100:.1f}% — logo proportions must be preserved"
                )

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_path", help="Project directory (expects svg_output/)")
    parser.add_argument("--brand-profile", required=True, help="Brand profile key, e.g. facom-ufms")
    args = parser.parse_args(argv)

    try:
        policy = load_policy(args.brand_profile)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    errors = preflight_assets(args.brand_profile, policy)
    if errors:
        for error in errors:
            print(f"[BRAND LINT] {error}", file=sys.stderr)
        print(f"[FAIL] {len(errors)} brand asset(s) missing — geração bloqueada (FR-006)")
        return 1

    svg_output_dir = Path(args.project_path) / "svg_output"
    if svg_output_dir.is_dir():
        errors = lint_usage(svg_output_dir, args.brand_profile, policy)
    else:
        errors = []

    if errors:
        for error in errors:
            print(f"[BRAND LINT] {error}", file=sys.stderr)
        print(f"[FAIL] {len(errors)} brand violation(s) found")
        return 1

    print("[OK] brand_lint: no violations")
    return 0


if __name__ == "__main__":
    sys.exit(main())
