#!/usr/bin/env python3
"""
PPT Master - CONTEXT.md Intake

Validates and normalizes a single CONTEXT.md (YAML frontmatter + Markdown body) into a
FACOM/UFMS talk deck project, then hands the body off to the existing Generate PPTX pipeline
as its Step 1 source. Never modifies project_manager.py / project_specs.py; only calls them.

Usage:
    python3 scripts/context_intake.py <CONTEXT.md> --project-dir <path> [--validate-only]

Exit codes:
    0  success (with or without warnings)
    1  schema validation error (missing required field or wrong type)
    2  brand.profile references a brand not present in brands_index.json

Dependencies:
    None required. PyYAML is used when available; otherwise a minimal frontmatter fallback
    parser handles the flat key: value pairs this schema actually needs (same posture as
    register_template.py / svg_quality_checker.py's YAML fallback).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover - exercised only without PyYAML installed
    yaml = None

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
SCHEMA_PATH = SKILL_DIR / "templates" / "schemas" / "context.schema.json"
BRANDS_INDEX_PATH = SKILL_DIR / "templates" / "brands" / "brands_index.json"

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from console_encoding import configure_utf8_stdio  # noqa: E402

configure_utf8_stdio()


class ContextIntakeError(RuntimeError):
    """Raised for a schema validation failure (exit code 1)."""


class BrandProfileError(RuntimeError):
    """Raised when brand.profile does not resolve to a registered brand (exit code 2)."""


# ---------------------------------------------------------------------------
# Frontmatter parsing
# ---------------------------------------------------------------------------

def split_frontmatter(text: str) -> tuple[dict, str]:
    """Split CONTEXT.md into (frontmatter dict, body). Preserves body verbatim."""
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    fm_block = text[4:end]
    body = text[end + 5:]
    if yaml is not None:
        try:
            data = yaml.safe_load(fm_block) or {}
        except yaml.YAMLError as exc:
            raise ContextIntakeError(f"invalid YAML frontmatter: {exc}") from exc
        if not isinstance(data, dict):
            raise ContextIntakeError("YAML frontmatter must be a mapping")
        return data, body
    return _fallback_parse_frontmatter(fm_block), body


def _fallback_parse_frontmatter(fm_block: str) -> dict:
    """Minimal nested key: value parser for a two-level frontmatter (no PyYAML)."""
    root: dict = {}
    stack: list[tuple[int, dict]] = [(-1, root)]
    for raw_line in fm_block.splitlines():
        if not raw_line.strip() or raw_line.strip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if value == "":
            child: dict = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            parent[key] = _coerce_scalar(value)
    return root


def _coerce_scalar(value: str):
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    if value in ("true", "True"):
        return True
    if value in ("false", "False"):
        return False
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


# ---------------------------------------------------------------------------
# Schema validation (hand-rolled, matching project_specs.py's stdlib-only style)
# ---------------------------------------------------------------------------

def load_schema() -> dict:
    with SCHEMA_PATH.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def validate_and_resolve(frontmatter: dict, schema: dict) -> tuple[dict, list[dict], list[str]]:
    """Validate `frontmatter` against `schema`'s top-level object; apply defaults.

    Returns (resolved, defaults_applied, warnings). Raises ContextIntakeError on the
    first schema violation that would materially change generation scope (FR-002).
    """
    resolved: dict = {}
    defaults_applied: list[dict] = []
    warnings: list[str] = []

    for prop_name, prop_schema in schema.get("properties", {}).items():
        present = prop_name in frontmatter
        value = frontmatter.get(prop_name)
        if prop_schema.get("type") == "object":
            sub_resolved, sub_defaults, sub_warnings = _validate_object(
                prop_name, value if present else {}, prop_schema, required_group=prop_name in schema.get("required", [])
            )
            resolved[prop_name] = sub_resolved
            defaults_applied.extend(sub_defaults)
            warnings.extend(sub_warnings)
        elif present:
            resolved[prop_name] = value

    known_top = set(schema.get("properties", {}))
    for unknown in set(frontmatter) - known_top:
        warnings.append(f"unknown top-level field '{unknown}' (ignored, not an error)")

    return resolved, defaults_applied, warnings


def _validate_object(
    path: str, value, prop_schema: dict, required_group: bool
) -> tuple[dict, list[dict], list[str]]:
    resolved: dict = {}
    defaults_applied: list[dict] = []
    warnings: list[str] = []

    if not isinstance(value, dict):
        if required_group:
            raise ContextIntakeError(f"'{path}' must be an object/mapping")
        value = {}

    sub_props = prop_schema.get("properties", {})
    for field_name, field_schema in sub_props.items():
        field_path = f"{path}.{field_name}"
        has_value = field_name in value and value[field_name] not in (None, "")
        if has_value:
            field_value = value[field_name]
            _check_type(field_path, field_value, field_schema)
            resolved[field_name] = field_value
        elif field_name in prop_schema.get("required", []):
            raise ContextIntakeError(
                f"required field '{field_path}' is missing "
                f"(expected type: {field_schema.get('type', field_schema.get('oneOf', 'value'))})"
            )
        elif "default" in field_schema:
            resolved[field_name] = field_schema["default"]
            defaults_applied.append({
                "field": field_path,
                "default_value": field_schema["default"],
                "reason": "omitted in CONTEXT.md frontmatter",
            })

    known_fields = set(sub_props)
    for unknown in set(value) - known_fields:
        warnings.append(f"unknown field '{path}.{unknown}' (ignored, not an error)")

    return resolved, defaults_applied, warnings


def _check_type(field_path: str, value, field_schema: dict) -> None:
    expected = field_schema.get("type")
    enum = field_schema.get("enum")
    one_of = field_schema.get("oneOf")

    if one_of is not None:
        for option in one_of:
            if option.get("const") is not None and value == option["const"]:
                return
            if option.get("type") == "integer" and isinstance(value, int) and not isinstance(value, bool):
                return
        raise ContextIntakeError(
            f"field '{field_path}' = {value!r} does not match any allowed form in {one_of!r}"
        )

    if enum is not None and value not in enum:
        raise ContextIntakeError(
            f"field '{field_path}' = {value!r} must be one of {enum!r}"
        )

    if expected == "string" and not isinstance(value, str):
        raise ContextIntakeError(f"field '{field_path}' must be a string, got {type(value).__name__}")
    if expected == "boolean" and not isinstance(value, bool):
        raise ContextIntakeError(f"field '{field_path}' must be a boolean, got {type(value).__name__}")
    if expected == "number":
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ContextIntakeError(f"field '{field_path}' must be a number, got {type(value).__name__}")
        minimum = field_schema.get("exclusiveMinimum")
        if minimum is not None and not value > minimum:
            raise ContextIntakeError(f"field '{field_path}' must be greater than {minimum}, got {value}")
    if expected == "string" and field_schema.get("minLength") and len(value) < field_schema["minLength"]:
        raise ContextIntakeError(f"field '{field_path}' must not be empty")


# ---------------------------------------------------------------------------
# Brand profile resolution (FR-006 companion — fails fast, never substitutes)
# ---------------------------------------------------------------------------

def check_brand_profile(resolved: dict) -> None:
    profile = resolved.get("brand", {}).get("profile")
    if not profile:
        return
    if not BRANDS_INDEX_PATH.exists():
        raise BrandProfileError(f"brands_index.json not found at {BRANDS_INDEX_PATH}")
    with BRANDS_INDEX_PATH.open("r", encoding="utf-8") as stream:
        brands_index = json.load(stream)
    if profile not in brands_index:
        available = ", ".join(sorted(brands_index)) or "(none registered)"
        raise BrandProfileError(
            f"brand.profile '{profile}' is not registered in brands_index.json "
            f"(available: {available})"
        )


# ---------------------------------------------------------------------------
# Normalized brief
# ---------------------------------------------------------------------------

def build_brief(
    context_path: Path,
    resolved: dict,
    defaults_applied: list[dict],
    warnings: list[str],
    schema_version: str,
) -> dict:
    context_bytes = context_path.read_bytes()
    return {
        "source_context_path": str(context_path),
        "resolved": resolved,
        "defaults_applied": defaults_applied,
        "warnings": warnings,
        "schema_version": schema_version,
        "created_at_context_hash": hashlib.sha256(context_bytes).hexdigest(),
    }


def write_brief(project_path: Path, brief: dict) -> Path:
    analysis_dir = project_path / "analysis"
    analysis_dir.mkdir(parents=True, exist_ok=True)
    brief_path = analysis_dir / "context_brief.json"
    with brief_path.open("w", encoding="utf-8") as stream:
        json.dump(brief, stream, indent=2, ensure_ascii=False)
        stream.write("\n")
    return brief_path


# ---------------------------------------------------------------------------
# Project initialization (delegates to project_manager.py — never reimplemented)
# ---------------------------------------------------------------------------

def init_and_import(project_dir: Path, body: str, canvas_format: str) -> Path:
    import tempfile

    from project_manager import ProjectManager

    project_dir = project_dir.resolve()
    manager = ProjectManager(base_dir=str(project_dir.parent))
    actual_path = Path(
        manager.init_project(
            project_name=project_dir.name,
            canvas_format=canvas_format,
            base_dir=str(project_dir.parent),
        )
    )

    # Write the body outside the project dir first — import_sources() moves (rather than
    # copies) any source path it finds already nested under the target project, which would
    # otherwise print a confusing "already under projects/" note for a file we just created.
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", prefix="context_body_", delete=False, encoding="utf-8"
    ) as handle:
        handle.write(body)
        body_path = Path(handle.name)
    try:
        manager.import_sources(str(actual_path), [str(body_path)])
    finally:
        body_path.unlink(missing_ok=True)

    return actual_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("context_md", help="Path to CONTEXT.md")
    parser.add_argument("--project-dir", required=True, help="Target project directory")
    parser.add_argument(
        "--validate-only", action="store_true",
        help="Validate and normalize only; do not init/import (used by conformance_report.py)",
    )
    args = parser.parse_args(argv)

    context_path = Path(args.context_md)
    if not context_path.is_file():
        print(f"Error: CONTEXT.md not found: {context_path}", file=sys.stderr)
        return 1

    text = context_path.read_text(encoding="utf-8-sig")

    try:
        frontmatter, body = split_frontmatter(text)
        schema = load_schema()
        resolved, defaults_applied, warnings = validate_and_resolve(frontmatter, schema)
        check_brand_profile(resolved)
    except ContextIntakeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except BrandProfileError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    schema_version = schema.get("$id", "context/v1")
    brief = build_brief(context_path, resolved, defaults_applied, warnings, schema_version)

    project_dir = Path(args.project_dir)
    if args.validate_only:
        if not project_dir.is_dir():
            print(f"Error: --validate-only requires an existing project dir: {project_dir}", file=sys.stderr)
            return 1
        brief_path = write_brief(project_dir, brief)
    elif project_dir.is_dir():
        brief_path = write_brief(project_dir, brief)
    else:
        canvas_format = resolved.get("presentation", {}).get("format", "ppt169")
        actual_path = init_and_import(project_dir, body, canvas_format)
        brief_path = write_brief(actual_path, brief)
        project_dir = actual_path

    for warning in warnings:
        print(f"Warning: {warning}", file=sys.stderr)
    for default in defaults_applied:
        print(
            f"Default applied: {default['field']} = {default['default_value']!r} "
            f"({default['reason']})",
            file=sys.stderr,
        )
    print(f"[OK] {brief_path} written for project: {project_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
