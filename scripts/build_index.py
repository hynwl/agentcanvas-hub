#!/usr/bin/env python3
"""Deterministically build index.json from teams/*/team.acanvas.json.

Usage: python3 scripts/build_index.py [--root PATH] [--check]

No third-party dependencies (stdlib only) — this script runs in CI before
any language toolchain is guaranteed to be set up, and contributors should
never need to install anything just to inspect the registry.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0"
REQUIRED_TEAM_FILES = ("team.acanvas.json", "README.md", "preview.png")


class TeamError(Exception):
    def __init__(self, slug: str, message: str) -> None:
        super().__init__(f"teams/{slug}: {message}")
        self.slug = slug


def _load_team(team_dir: Path) -> dict[str, Any]:
    slug = team_dir.name
    for filename in REQUIRED_TEAM_FILES:
        if not (team_dir / filename).is_file():
            raise TeamError(slug, f"missing required file {filename!r}")

    doc_path = team_dir / "team.acanvas.json"
    try:
        doc = json.loads(doc_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise TeamError(slug, f"team.acanvas.json is not valid JSON ({exc})") from exc

    for field in ("id", "name", "created_at", "updated_at"):
        if field not in doc:
            raise TeamError(slug, f"team.acanvas.json missing required field {field!r}")

    meta = doc.get("meta") or {}

    # `meta.thumbnail` in a locally-saved .acanvas.json is a data: URI (embedded
    # PNG bytes) — fine for one document on disk, but it would bloat index.json
    # by orders of magnitude once hundreds of teams are listed. The registry
    # layout puts the real image at teams/<slug>/preview.png instead, so we
    # point there and drop whatever the document itself carried.
    entry = {
        "slug": slug,
        "id": doc["id"],
        "name": doc["name"],
        "description": doc.get("description"),
        "tags": sorted(doc.get("tags") or []),
        "author": doc.get("author"),
        "license": doc.get("license"),
        "revision": doc.get("revision", 0),
        "forked_from": doc.get("forked_from"),
        "created_at": doc["created_at"],
        "updated_at": doc["updated_at"],
        "meta": {
            "requires_keys": sorted(meta.get("requires_keys") or []),
            "difficulty": meta.get("difficulty"),
        },
        "path": f"teams/{slug}/team.acanvas.json",
        "thumbnail": f"teams/{slug}/preview.png",
    }
    return entry


def build_index(root: Path) -> dict[str, Any]:
    teams_dir = root / "teams"
    slugs = sorted(
        p.name for p in teams_dir.iterdir() if p.is_dir() and not p.name.startswith(".")
    )

    entries = [_load_team(teams_dir / slug) for slug in slugs]

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_by": "scripts/build_index.py",
        "team_count": len(entries),
        "teams": entries,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="registry repo root (default: repo root this script lives in)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit non-zero if index.json on disk is stale instead of writing it",
    )
    args = parser.parse_args()

    try:
        index = build_index(args.root)
    except TeamError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    rendered = json.dumps(index, indent=2, ensure_ascii=False, sort_keys=False) + "\n"
    index_path = args.root / "index.json"

    if args.check:
        current = index_path.read_text(encoding="utf-8") if index_path.is_file() else ""
        if current != rendered:
            print("index.json is stale — run scripts/build_index.py to regenerate", file=sys.stderr)
            return 1
        print(f"index.json is up to date ({index['team_count']} teams)")
        return 0

    index_path.write_text(rendered, encoding="utf-8")
    print(f"wrote {index_path} ({index['team_count']} teams)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
