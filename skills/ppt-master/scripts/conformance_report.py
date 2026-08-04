#!/usr/bin/env python3
"""
PPT Master - Conformance Report

Orchestrates the quality gates that do not yet block svg_to_pptx.py (schema, SVG grammar,
full-page render + contact sheet, brand lint), then — only if every gate passes — invokes
svg_to_pptx.py and folds its own postflight report in. Implements the hard gate decided in
the 2026-07-27 clarification (FR-019): a `fail` or `skipped` gate blocks export; no PPTX is
written until every gate reports `pass`.

Usage:
    python3 scripts/conformance_report.py <project_path> --host codex

Exit codes:
    0   all gates + export passed
    10  one or more pre-export gates failed or were skipped (no PPTX written)
    11  svg_to_pptx.py itself failed after every pre-export gate passed (inherited, unchanged)

Dependencies:
    None beyond the scripts it orchestrates (each already declares its own).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
ADAPTERS_DIR = SKILL_DIR / "adapters"

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from console_encoding import configure_utf8_stdio  # noqa: E402

configure_utf8_stdio()


def _run(script_name: str, args: list[str]) -> tuple[int, str]:
    script_path = SCRIPT_DIR / script_name
    result = subprocess.run(
        [sys.executable, str(script_path), *args],
        capture_output=True,
        text=True,
    )
    output = (result.stdout or "") + (result.stderr or "")
    return result.returncode, output.strip()


def load_capabilities(host_id: str) -> dict:
    capabilities_path = ADAPTERS_DIR / host_id / "capabilities.json"
    if not capabilities_path.is_file():
        raise FileNotFoundError(f"no capabilities.json declared for host '{host_id}': {capabilities_path}")
    with capabilities_path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def load_context_brief(project_path: Path) -> dict | None:
    brief_path = project_path / "analysis" / "context_brief.json"
    if not brief_path.is_file():
        return None
    with brief_path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def run_gates(project_path: Path, capabilities: dict, brief: dict | None) -> list[dict]:
    gates: list[dict] = []

    if brief and brief.get("source_context_path"):
        code, output = _run(
            "context_intake.py",
            [brief["source_context_path"], "--project-dir", str(project_path), "--validate-only"],
        )
        gates.append({
            "name": "schema",
            "status": "pass" if code == 0 else "fail",
            "detail": output or "context_intake.py --validate-only",
        })
    else:
        gates.append({
            "name": "schema",
            "status": "fail",
            "detail": "no analysis/context_brief.json found — run context_intake.py first",
        })

    code, output = _run("svg_quality_checker.py", [str(project_path)])
    gates.append({
        "name": "svg",
        "status": "pass" if code == 0 else "fail",
        "detail": output or "svg_quality_checker.py",
    })

    if capabilities.get("browser") != "true" and capabilities.get("browser") is not True:
        gates.append({
            "name": "render",
            "status": "skipped",
            "detail": f"browser capability unavailable on {capabilities.get('host_id', '?')}",
        })
    else:
        code, output = _run("visual_review.py", [str(project_path)])
        if code == 0:
            sheet_code, sheet_output = _run("contact_sheet.py", [str(project_path)])
            gates.append({
                "name": "render",
                "status": "pass" if sheet_code == 0 else "fail",
                "detail": sheet_output or "contact_sheet.py",
            })
        else:
            gates.append({
                "name": "render",
                "status": "fail",
                "detail": output or "visual_review.py",
            })

    brand_profile = None
    if brief:
        brand_profile = brief.get("resolved", {}).get("brand", {}).get("profile")
    if brand_profile:
        code, output = _run("brand_lint.py", [str(project_path), "--brand-profile", brand_profile])
        gates.append({
            "name": "brand_lint",
            "status": "pass" if code == 0 else "fail",
            "detail": output or "brand_lint.py",
        })

    return gates


def invoke_export(project_path: Path) -> tuple[bool, str, str | None]:
    code, output = _run("svg_to_pptx.py", [str(project_path)])
    if code != 0:
        return False, output, None

    exports_dir = project_path / "exports"
    pptx_candidates = sorted(exports_dir.glob("*.pptx"), key=lambda p: p.stat().st_mtime, reverse=True)
    pptx_path = str(pptx_candidates[0]) if pptx_candidates else None

    validation_dir = project_path / "validation"
    report_candidates = sorted(
        validation_dir.glob("*.report.json"), key=lambda p: p.stat().st_mtime, reverse=True
    )
    export_report = {}
    if report_candidates:
        with report_candidates[0].open("r", encoding="utf-8") as stream:
            export_report = json.load(stream)

    return True, json.dumps(export_report, ensure_ascii=False), pptx_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_path", help="Project directory")
    parser.add_argument("--host", required=True, help="Host id, e.g. codex")
    args = parser.parse_args(argv)

    project_path = Path(args.project_path)
    if not project_path.is_dir():
        print(f"Error: project directory not found: {project_path}", file=sys.stderr)
        return 10

    try:
        capabilities = load_capabilities(args.host)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 10

    brief = load_context_brief(project_path)
    gates = run_gates(project_path, capabilities, brief)

    for gate in gates:
        marker = {"pass": "[OK]", "fail": "[FAIL]", "skipped": "[SKIP]"}[gate["status"]]
        print(f"{marker} {gate['name']}: {gate['status']}")

    all_passed = all(gate["status"] == "pass" for gate in gates)

    report = {
        "host_id": args.host,
        "capabilities_used": capabilities,
        "gates": gates,
        "overall_status": "blocked",
        "pptx_path": None,
    }

    if not all_passed:
        _write_report(project_path, report)
        print("[BLOCKED] one or more gates did not pass — no PPTX written (FR-019)")
        return 10

    export_ok, export_detail, pptx_path = invoke_export(project_path)
    gates.append({
        "name": "export",
        "status": "pass" if export_ok else "fail",
        "detail": export_detail,
    })
    report["gates"] = gates

    if not export_ok:
        report["overall_status"] = "blocked"
        _write_report(project_path, report)
        print("[FAIL] svg_to_pptx.py failed after all pre-export gates passed")
        return 11

    report["overall_status"] = "pass"
    report["pptx_path"] = pptx_path
    _write_report(project_path, report)
    print(f"[OK] all gates passed — {pptx_path}")
    return 0


def _write_report(project_path: Path, report: dict) -> None:
    validation_dir = project_path / "validation"
    validation_dir.mkdir(parents=True, exist_ok=True)
    report_path = validation_dir / "conformance_report.json"
    with report_path.open("w", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2, ensure_ascii=False)
        stream.write("\n")


if __name__ == "__main__":
    sys.exit(main())
