"""Return-schema validation must have teeth — and must never silently lose them.

Root cause (audit CROWN finding): `tu test` validated a tool's `return_schema`
inside `try: import jsonschema ... except ImportError: pass`. `jsonschema` is a
DECLARED dependency (pyproject.toml), yet in any environment missing it every
schema check silently no-opped while the suite still reported green — the one
semantic gate invisibly disabled.

These tests pin the corrected contract of the extracted validator:
  - a valid payload passes (no failures)
  - a wrong-but-well-formed payload is REJECTED (the teeth)
  - a missing jsonschema is itself a FAILURE, never a silent skip
"""

from __future__ import annotations

import sys

from tooluniverse.cli import _validate_return_schema

_SCHEMA = {
    "type": "object",
    "required": ["count"],
    "properties": {"count": {"type": "integer"}},
}


def test_valid_payload_has_no_failures():
    assert _validate_return_schema({"count": 3}, _SCHEMA) == []


def test_wrong_payload_is_rejected():
    # well-formed dict, but `count` is a string, not an integer
    failures = _validate_return_schema({"count": "three"}, _SCHEMA)
    assert failures, "a schema-violating payload must be rejected (teeth)"
    assert "return_schema mismatch" in failures[0]


def test_missing_required_key_is_rejected():
    failures = _validate_return_schema({}, _SCHEMA)
    assert failures, "missing required key must be rejected"


def test_missing_jsonschema_is_a_failure_not_silent_skip(monkeypatch):
    # Simulate an environment where the declared dependency is absent:
    # mapping the module name to None makes `import jsonschema` raise ImportError.
    monkeypatch.setitem(sys.modules, "jsonschema", None)
    failures = _validate_return_schema({"count": 3}, _SCHEMA)
    assert failures, "missing jsonschema must be a loud failure, not a silent pass"
    assert "jsonschema" in failures[0].lower()
