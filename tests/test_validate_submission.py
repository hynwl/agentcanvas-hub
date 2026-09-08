#!/usr/bin/env python3
"""Proves the three fixture failure modes required by M5-T6's DoD actually
fail, and that a well-formed submission passes. stdlib unittest, zero deps —
run directly: `python3 tests/test_validate_submission.py`.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from validate_submission import validate_team  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"


class ValidateSubmissionTests(unittest.TestCase):
    def test_valid_team_passes(self) -> None:
        errors = validate_team(FIXTURES / "valid_team")
        self.assertEqual(errors, [])

    def test_broken_schema_fails(self) -> None:
        errors = validate_team(FIXTURES / "broken_schema")
        self.assertTrue(errors)
        self.assertTrue(any("[schema]" in e for e in errors), errors)

    def test_broken_secret_fails(self) -> None:
        errors = validate_team(FIXTURES / "broken_secret")
        self.assertTrue(errors)
        self.assertTrue(any("publish-scan:BLOCK" in e and "secret" in e for e in errors), errors)

    def test_broken_compile_fails(self) -> None:
        errors = validate_team(FIXTURES / "broken_compile")
        self.assertTrue(errors)
        self.assertTrue(any("[dry-run]" in e and "AC-E101" in e for e in errors), errors)

    def test_missing_team_dir_fails(self) -> None:
        errors = validate_team(FIXTURES / "does_not_exist")
        self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
