"""Unit coverage for scripts/probe_custom_tools.py's pure contract logic.

``assert_probe_contract`` and ``PROBE_SAMPLE`` are provable without importing
``tooluniverse`` -- these tests build stage-dict fixtures by hand, matching
the shape ``probe_tool_python`` / ``probe_tool_cli`` actually produce, and
never instantiate ``ToolUniverse``.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "probe_custom_tools", Path(__file__).parents[2] / "scripts/probe_custom_tools.py"
)
_MODULE = importlib.util.module_from_spec(_SPEC)
assert _SPEC and _SPEC.loader
_SPEC.loader.exec_module(_MODULE)

assert_probe_contract = _MODULE.assert_probe_contract
PROBE_SAMPLE = _MODULE.PROBE_SAMPLE


def _stages(
    *,
    discover_found: bool = True,
    spec: dict | None = None,
    execute_status: str = "success",
    error_type: str | None = None,
    missing_keys: list[str] | None = None,
    result=None,
    gate_reason: str | None = None,
) -> dict:
    """Build a hand-crafted stage dict matching probe_tool_python's shape."""
    execute: dict = {
        "status": execute_status,
        "error_type": error_type,
        "missing_keys": missing_keys or [],
        "result": result,
        "error": None,
    }
    if gate_reason is not None:
        execute["gate_reason"] = gate_reason
    return {
        "discover": {"found": discover_found},
        "inspect": {"spec": spec},
        "execute": execute,
    }


_COMPLETE_SPEC = {"parameter": {"type": "object", "properties": {}, "required": []}}
_ALT_SPEC = {"parameters": {"type": "object", "properties": {}, "required": []}}
_NON_EMPTY_RESULT = {"status": "success", "data": {"value": 4.0}}


@pytest.mark.parametrize(
    "stages, expected_verdict",
    [
        pytest.param(
            _stages(spec=_COMPLETE_SPEC, result=_NON_EMPTY_RESULT),
            "pass",
            id="complete_stage_set_yields_pass",
        ),
        pytest.param(
            _stages(spec=_ALT_SPEC, result=_NON_EMPTY_RESULT),
            "pass",
            id="parameters_key_also_satisfies_inspect",
        ),
        pytest.param(
            _stages(
                spec=_COMPLETE_SPEC,
                execute_status="error",
                missing_keys=["USPTO_API_KEY"],
                result=None,
            ),
            "gated",
            id="missing_credential_yields_gated_with_key_names",
        ),
        pytest.param(
            _stages(discover_found=False, spec=None, result=None),
            "fail",
            id="discover_found_nothing_yields_fail",
        ),
        pytest.param(
            _stages(spec={"description": "no schema here"}, result=_NON_EMPTY_RESULT),
            "fail",
            id="inspect_missing_parameter_schema_yields_fail",
        ),
        pytest.param(
            _stages(
                spec=_COMPLETE_SPEC, error_type="ImportError", execute_status="error"
            ),
            "fail",
            id="execute_raising_import_error_yields_fail",
        ),
        pytest.param(
            _stages(
                spec=_COMPLETE_SPEC, error_type="AttributeError", execute_status="error"
            ),
            "fail",
            id="execute_raising_attribute_error_yields_fail",
        ),
    ],
)
def test_assert_probe_contract_verdicts(stages, expected_verdict):
    result = assert_probe_contract(stages)
    assert result["verdict"] == expected_verdict


def test_gated_verdict_carries_missing_key_names_through():
    stages = _stages(
        spec=_COMPLETE_SPEC,
        execute_status="error",
        missing_keys=["USPTO_API_KEY"],
        result=None,
    )
    result = assert_probe_contract(stages)
    assert result["verdict"] == "gated"
    assert result["missing_keys"] == ["USPTO_API_KEY"]


def test_resource_timeout_gate_reason_also_yields_gated_with_empty_missing_keys():
    """Tool_RAG's first-use embedding inference can exceed the probe's time
    budget; that is an environment/resource limit, not a broken registration
    path, so it must gate rather than fail even with no credential name."""
    stages = _stages(
        spec=_COMPLETE_SPEC,
        execute_status="error",
        missing_keys=[],
        result=None,
        gate_reason="resource_timeout",
    )
    result = assert_probe_contract(stages)
    assert result["verdict"] == "gated"
    assert result["reason"] == "resource_timeout"


def test_empty_list_result_with_no_gating_signal_is_rejected_not_passed():
    """Named regression guard: this repository has a recorded history of an
    empty result masquerading as success past a health gate (T-02-17). An
    execute stage with a fully-populated schema but an empty ``[]`` result
    and no missing-credential signal must be ``fail``, never ``pass``."""
    stages = _stages(spec=_COMPLETE_SPEC, execute_status="success", result=[])
    result = assert_probe_contract(stages)
    assert result["verdict"] == "fail"
    assert "empty" in result["reason"].lower()


def test_empty_dict_result_with_no_gating_signal_is_also_rejected():
    stages = _stages(spec=_COMPLETE_SPEC, execute_status="success", result={})
    result = assert_probe_contract(stages)
    assert result["verdict"] == "fail"
    assert "empty" in result["reason"].lower()


def test_none_result_with_no_gating_signal_is_rejected():
    stages = _stages(spec=_COMPLETE_SPEC, execute_status="success", result=None)
    result = assert_probe_contract(stages)
    assert result["verdict"] == "fail"


REQUIRED_SAMPLE_FIELDS = (
    "name",
    "arguments",
    "selection_rule",
    "preservation_linkage",
    "credential_expectation",
)


@pytest.mark.parametrize(
    "entry", PROBE_SAMPLE, ids=[entry["name"] for entry in PROBE_SAMPLE]
)
def test_probe_sample_entry_has_non_empty_required_fields(entry):
    for field in REQUIRED_SAMPLE_FIELDS:
        assert entry.get(field), f"{entry.get('name')} missing non-empty {field!r}"


def test_probe_sample_has_no_duplicate_names():
    names = [entry["name"] for entry in PROBE_SAMPLE]
    assert len(names) == len(set(names))


def test_probe_sample_has_exactly_six_entries():
    assert len(PROBE_SAMPLE) == 6


def test_probe_sample_includes_the_offline_control():
    assert any(
        entry["name"] == "DegreesOfUnsaturation_calculate" for entry in PROBE_SAMPLE
    )
