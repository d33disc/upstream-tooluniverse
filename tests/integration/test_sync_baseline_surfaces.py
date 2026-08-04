"""Real five-surface baseline certification for the deterministic reference tool."""

from __future__ import annotations

import json
import importlib.util
import sys
from pathlib import Path

import pytest

_MODULE_SPEC = importlib.util.spec_from_file_location(
    "capture_sync_baseline",
    Path(__file__).parents[2] / "scripts" / "capture_sync_baseline.py",
)
assert _MODULE_SPEC and _MODULE_SPEC.loader
_MODULE = importlib.util.module_from_spec(_MODULE_SPEC)
sys.modules["capture_sync_baseline"] = _MODULE
_MODULE_SPEC.loader.exec_module(_MODULE)

from capture_sync_baseline import (
    REFERENCE_TOOL,
    REFERENCE_ARGUMENTS,
    run_cli_probe,
    run_mcp_http_probe,
    run_mcp_stdio_probe,
    run_python_probe,
    run_rest_probe,
    run_surface_matrix,
)


def _assert_probe(probe: dict) -> None:
    assert probe["tool"] == REFERENCE_TOOL
    assert probe["schema_inspected"] is True
    assert probe["arguments"] == sorted(REFERENCE_ARGUMENTS)
    for stage_name in ("discover", "inspect", "execute", "assert"):
        assert probe[stage_name]["status"] == "success", json.dumps(
            probe[stage_name], default=str
        )
    assert (
        probe["assert"]["outcome"]["normalized"]["data"]["degrees_of_unsaturation"]
        == 4.0
    )
    assert probe["assert"]["outcome"]["normalized"]["data"]["is_integer"] is True


@pytest.mark.integration
@pytest.mark.parametrize(
    "runner",
    [
        run_python_probe,
        run_cli_probe,
        run_mcp_stdio_probe,
        run_mcp_http_probe,
        run_rest_probe,
    ],
    ids=["python", "cli", "mcp-stdio", "mcp-http", "rest"],
)
def test_deterministic_discover_inspect_execute_assert(runner):
    """Every supported surface uses the inspected reference schema."""
    _assert_probe(runner())


@pytest.mark.integration
def test_deterministic_surface_matrix():
    matrix = run_surface_matrix()
    assert matrix["status"] == "green"
    assert {probe["surface"] for probe in matrix["surfaces"]} == {
        "python",
        "cli",
        "mcp-stdio",
        "mcp-http",
        "rest",
    }
    for probe in matrix["surfaces"]:
        _assert_probe(probe)
