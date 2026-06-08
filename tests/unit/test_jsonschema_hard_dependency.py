"""jsonschema is a declared, non-optional dependency — it must never be silently skipped.

Root cause (audit CROWN, 2nd site): `base_tool.py` validated tool *input* parameters inside
`try: import jsonschema ... except ImportError: return None  # skip validation`. In any env
missing the declared dependency, every tool ran with UNVALIDATED inputs and the skip was silent —
the production-path twin of the `tu test` bug fixed in PR #51.

Contract pinned here:
  - base_tool imports jsonschema at module load (no lazy silent-skip branch can exist)
  - a malformed *schema* (developer error) is reported as a distinct, diagnosable config error,
    not conflated with a user input-validation error
"""

from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tooluniverse import base_tool as bt  # noqa: E402
from tooluniverse.base_tool import BaseTool  # noqa: E402
from tooluniverse.exceptions import ToolConfigError  # noqa: E402


@pytest.mark.unit
def test_jsonschema_imported_at_module_level_no_silent_skip():
    """jsonschema is imported at module load, so no silent `except ImportError` skip exists."""
    assert isinstance(getattr(bt, "jsonschema", None), types.ModuleType)


@pytest.mark.unit
def test_malformed_schema_is_a_diagnosable_config_error():
    """A malformed parameter schema is a developer bug → distinct ToolConfigError."""
    # `required` must be an array; a string makes the SCHEMA itself invalid.
    tool = BaseTool({"name": "t", "parameter": {"type": "object", "required": "oops"}})
    err = tool.validate_parameters({"x": 1})
    assert isinstance(err, ToolConfigError), (
        f"expected ToolConfigError, got {type(err)}"
    )
    assert "schema" in str(err).lower()
