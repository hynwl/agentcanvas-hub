#!/usr/bin/env python3
"""Validate one or more `teams/<slug>/` submissions (M5-T6).

Runs three key-less checks against each `team.acanvas.json`:

1. schema_check   — structural conformance to the CanvasDoc shape
2. publish_scan   — leaked-secret / PII preflight (only `block`-risk fails CI;
                    `warn`/`info` are printed for the human PR reviewer)
3. dry_run_compile — graph topology + required-field checks, no LLM calls,
                    no API keys needed

Usage: python3 scripts/validate_submission.py <slug> [<slug> ...]
       python3 scripts/validate_submission.py --all

Exits non-zero if any team fails any check.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dry_run_compile import dry_run_compile  # noqa: E402
from publish_scan import scan_for_publish  # noqa: E402
from schema_check import check_schema  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def validate_team(team_dir: Path) -> list[str]:
    slug = team_dir.name
    doc_path = team_dir / "team.acanvas.json"
    if not doc_path.is_file():
        return [f"teams/{slug}: missing team.acanvas.json"]

    try:
        doc = json.loads(doc_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"teams/{slug}: team.acanvas.json is not valid JSON ({exc})"]

    errors: list[str] = [f"teams/{slug}: [schema] {e}" for e in check_schema(doc)]

    # Findings on a malformed doc are unreliable (missing nodes/data), so only
    # scan and dry-run-compile once the shape is sound enough to trust.
    if not errors:
        findings = scan_for_publish(doc)
        blocking = [f for f in findings if f.risk == "block"]
        errors.extend(f"teams/{slug}: [publish-scan:BLOCK] {f.rule} at {f.path}: {f.match}" for f in blocking)
        for f in findings:
            if f.risk != "block":
                print(f"::warning::teams/{slug}: [publish-scan:{f.risk}] {f.rule} at {f.path}: {f.match}")

        errors.extend(f"teams/{slug}: [dry-run] {e}" for e in dry_run_compile(doc))

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("slugs", nargs="*", help="team directory names under teams/ to validate")
    parser.add_argument("--all", action="store_true", help="validate every team under teams/")
    parser.add_argument("--root", type=Path, default=ROOT, help="registry repo root")
    args = parser.parse_args()

    teams_dir = args.root / "teams"
    if args.all:
        slugs = sorted(p.name for p in teams_dir.iterdir() if p.is_dir() and not p.name.startswith("."))
    else:
        slugs = args.slugs

    if not slugs:
        print("no teams to validate", file=sys.stderr)
        return 1

    all_errors: list[str] = []
    for slug in slugs:
        errors = validate_team(teams_dir / slug)
        if errors:
            all_errors.extend(errors)
        else:
            print(f"teams/{slug}: OK")

    if all_errors:
        print(f"\n{len(all_errors)} problem(s) found:", file=sys.stderr)
        for e in all_errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(f"\nall {len(slugs)} team(s) passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
