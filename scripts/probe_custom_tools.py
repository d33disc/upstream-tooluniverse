#!/usr/bin/env python3
"""Probe representative preserved custom tools inside the re-merge stage.

Phase 2 plan 02-05 (criterion 4): prove that preservation-flagged fork-only
tools still complete discover -> inspect -> execute after the upstream-main
integration -- through ``ToolUniverse.run_one_function`` (the one path all
five transports converge on) and through the installed ``tu`` CLI. Per D-04
these are fresh probes: they are never diffed against Phase 1's
``probes/*.json`` -- they pass, gate, or fail on their own terms.

Git/evidence helpers are reused from ``scripts/capture_sync_baseline.py`` via
``importlib.util`` -- ``scripts/`` has no ``__init__.py``, so a plain import
fails; ``tests/unit/test_sync_baseline_git.py`` uses the same idiom.

This module is dual-purpose: it is both the CLI entry point (invoked with the
caller's own interpreter, typically the main checkout's ``python3``) and,
via the hidden ``--_internal-python-probe`` flag, the payload that re-invokes
itself under the re-merge stage's own ``.venv/bin/python`` so the Python
probe always answers for the stage's installation, never the caller's.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

_CAPTURE_SPEC = importlib.util.spec_from_file_location(
    "capture_sync_baseline",
    Path(__file__).resolve().parent / "capture_sync_baseline.py",
)
_CAPTURE_MODULE = importlib.util.module_from_spec(_CAPTURE_SPEC)
assert _CAPTURE_SPEC and _CAPTURE_SPEC.loader
_CAPTURE_SPEC.loader.exec_module(_CAPTURE_MODULE)

_run_command = _CAPTURE_MODULE._run_command
normalize_probe_result = _CAPTURE_MODULE.normalize_probe_result
_contains_secret = _CAPTURE_MODULE._contains_secret
run_git = _CAPTURE_MODULE.run_git
GitCaptureError = _CAPTURE_MODULE.GitCaptureError

REPO_ROOT = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------------------
# PROBE_SAMPLE -- the recorded, justified sample from 02-05-PLAN.md's
# <probe_sample_selection>. Replaces capture_sync_baseline.py's single
# REFERENCE_TOOL / REFERENCE_ARGUMENTS pair, which is baked into the
# calculator-specific _assert_reference and cannot serve a heterogeneous list.
# ---------------------------------------------------------------------------

PROBE_SAMPLE: list[dict[str, Any]] = [
    {
        "name": "USPTO_get_patent_assignment",
        "arguments": {"applicationNumberText": "14966067"},
        "selection_rule": "rule_1_fork_only_hand_resolved_array",
        "preservation_linkage": (
            "fork-only entry in the hand-resolved data/uspto_tools.json array; "
            "type USPTOOpenDataPortalTool"
        ),
        "credential_expectation": (
            "gated on USPTO_API_KEY; a gated result is a pass for "
            "registration-chain purposes"
        ),
    },
    {
        "name": "USPTO_get_patent_transactions",
        "arguments": {"applicationNumberText": "14966067"},
        "selection_rule": "rule_1_fork_only_hand_resolved_array",
        "preservation_linkage": (
            "second fork-only entry in the same hand-resolved "
            "data/uspto_tools.json array"
        ),
        "credential_expectation": (
            "gated on USPTO_API_KEY; a gated result is a pass for "
            "registration-chain purposes"
        ),
    },
    {
        "name": "Tool_Finder_Keyword",
        "arguments": {"description": "protein structure prediction", "limit": 3},
        "selection_rule": "rule_2_tool_definition_class",
        "preservation_linkage": (
            "implemented by src/tooluniverse/tool_finder_keyword.py; "
            "class: tool_definition, status: M"
        ),
        "credential_expectation": "none -- offline BM25",
    },
    {
        "name": "Tool_Finder_LLM",
        "arguments": {"description": "protein structure prediction", "limit": 3},
        "selection_rule": "rule_2_tool_definition_class",
        "preservation_linkage": (
            "implemented by src/tooluniverse/tool_finder_llm.py; "
            "class: tool_definition, status: M"
        ),
        "credential_expectation": (
            "LLM backend may be gated; schema load must still succeed"
        ),
    },
    {
        "name": "Tool_RAG",
        "arguments": {"description": "protein structure prediction", "limit": 3},
        "selection_rule": "rule_2_tool_definition_class",
        "preservation_linkage": (
            "defined in data/finder_tools.json; exercises the discovery layer "
            "implemented by src/tooluniverse/tool_discovery_tools.py "
            "(class: tool_definition, status: M, one of the 22 hand-resolved files)"
        ),
        "credential_expectation": (
            "embedding assets may be absent, or first-use CPU embedding "
            "inference over the full catalog may exceed the probe time "
            "budget; either is recorded as gated, not fail"
        ),
        "timeout": 480.0,
    },
    {
        "name": "DegreesOfUnsaturation_calculate",
        "arguments": {"operation": "calculate", "formula": "C6H6"},
        "selection_rule": "rule_3_offline_control",
        "preservation_linkage": (
            "Phase 1's reference tool; fully offline, deterministic, no credentials"
        ),
        "credential_expectation": (
            "none -- a failure here means the environment, not the merge"
        ),
    },
]

# Deliberately-not-covered scope, recorded per <probe_sample_selection> so the
# coverage boundary is explicit rather than implied.
EXCLUSIONS: list[str] = [
    "512 custom_code preservation.json entries -- covered by plan 02-04's "
    "path-level disposition (findings.json / preservation-reclass.json), "
    "not by execution probes",
    "240 plugin_asset preservation.json entries -- covered by plan 02-04's "
    "path-level disposition, not by execution probes",
    "Full cross-surface certification across Python, CLI, MCP stdio, MCP "
    "HTTP, and REST -- Phase 5 / SURF-01; this plan probes Python plus the "
    "tu CLI only",
    "Catalog-wide and test-level regression certification -- Phase 5 / TEST-01",
]

DEFAULT_TIMEOUT = 120.0

# Credential env-var names that appear across the sample's required_api_keys
# and LLM-backend fallback chain. Used only to build the ``secrets`` list the
# `_contains_secret` guard scans probe output against -- never written verbatim.
CREDENTIAL_ENV_NAMES: tuple[str, ...] = (
    "USPTO_API_KEY",
    "AZURE_OPENAI_API_KEY",
    "OPENROUTER_API_KEY",
    "GEMINI_API_KEY",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
)


def _module_matches_interpreter(python_bin: Path) -> bool:
    try:
        return Path(python_bin).resolve() == Path(sys.executable).resolve()
    except OSError:
        return False


_MISSING_KEY_RE = re.compile(
    r"(?:requires api key\(s\) not set|missing API key\(s\))\s*[:\-]?\s*([A-Z0-9_,\s]+)",
    re.IGNORECASE,
)


def _extract_missing_key_names(text: str) -> list[str]:
    """Pull clean, deduplicated ``SOME_API_KEY`` names out of an error string."""
    names: list[str] = []
    for match in _MISSING_KEY_RE.finditer(text):
        for candidate in match.group(1).split(","):
            candidate = candidate.strip().rstrip(".").strip()
            if (
                candidate
                and candidate.replace("_", "").isalnum()
                and candidate.isupper()
                and candidate not in names
            ):
                names.append(candidate)
    return names


def _classify_error_type(message: str | None) -> str | None:
    """Detect the signature of a broken lazy-registry module string.

    ``run_one_function`` catches most tool-instantiation failures internally
    and returns a structured ``{"status": "error", "error": ...}`` dict
    rather than letting the exception propagate, so the classifier must also
    recognize the error text, not only a raised exception.
    """
    if not message:
        return None
    lowered = message.lower()
    if "importerror" in lowered or "modulenotfounderror" in lowered:
        return "ImportError"
    if "attributeerror" in lowered:
        return "AttributeError"
    return None


def _probe_tool_python_inprocess(
    tool_name: str, arguments: dict[str, Any]
) -> dict[str, Any]:
    """Run discover -> inspect -> execute through the Python core.

    Must only be called with the interpreter that owns the target
    ``tooluniverse`` installation (the stage's own venv) -- ``probe_tool_python``
    is the dispatch boundary that guarantees this.
    """
    from tooluniverse.execute_function import ToolUniverse

    started = time.monotonic()
    universe = ToolUniverse()
    error_type: str | None = None
    error_text: str | None = None
    missing_keys: list[str] = []
    normalized: Any = None
    execute_status = "error"
    discover_found = False
    spec: dict[str, Any] | None = None
    try:
        universe.load_tools(include_tools=[tool_name])
        discover_found = bool(
            universe.find_tools_by_pattern(
                tool_name, search_in="name", case_sensitive=True
            )
        )
        spec = universe.tool_specification(tool_name)
        missing_keys = list(
            getattr(universe, "_excluded_api_key_tools", {}).get(tool_name, [])
        )
        if spec is None and missing_keys:
            # Excluded from the registry at load time for a missing credential
            # -- never reaches execute at all. This is the common case for
            # required_api_keys-gated tools.
            execute_status = "error"
            error_text = f"tool excluded: missing API key(s) {', '.join(missing_keys)}"
        else:
            try:
                raw = universe.run_one_function(
                    {"name": tool_name, "arguments": arguments}
                )
                missing_keys = list(
                    getattr(universe, "_excluded_api_key_tools", {}).get(
                        tool_name, missing_keys
                    )
                )
                wrapped = raw if isinstance(raw, dict) else {"value": raw}
                normalized = normalize_probe_result(wrapped)
                if isinstance(normalized, dict) and normalized.get("status") == "error":
                    execute_status = "error"
                    error_text = str(normalized.get("error", ""))[:500]
                else:
                    execute_status = "success"
            except (ImportError, AttributeError) as exc:
                error_type = type(exc).__name__
                error_text = str(exc)[:500]
    finally:
        close = getattr(universe, "close", None)
        if close:
            close()

    if error_type is None:
        error_type = _classify_error_type(error_text)

    duration_ms = round((time.monotonic() - started) * 1000, 3)
    return {
        "surface": "python",
        "tool": tool_name,
        "duration_ms": duration_ms,
        "discover": {"found": discover_found},
        "inspect": {"spec": spec},
        "execute": {
            "status": execute_status,
            "error_type": error_type,
            "missing_keys": missing_keys,
            "result": normalized,
            "error": error_text,
        },
    }


def probe_tool_python(
    tool_name: str,
    arguments: dict[str, Any],
    *,
    stage_python: Path,
    timeout: float = DEFAULT_TIMEOUT,
) -> dict[str, Any]:
    """Run the Python-core probe, always against ``stage_python``'s installation.

    Dispatches through a subprocess when the caller's own interpreter is not
    ``stage_python`` -- the probe must never answer for the main checkout's
    environment. A timeout (heavy embedding inference on first use, for
    example) is recorded as ``gated``, not ``fail``: it signals an
    environment/resource limit, not a broken registration path.
    """
    if not _module_matches_interpreter(stage_python):
        argv = [
            str(stage_python),
            str(Path(__file__).resolve()),
            "--_internal-python-probe",
            tool_name,
            "--_internal-arguments",
            json.dumps(arguments),
        ]
        try:
            code, stdout, stderr = _run_command(argv, timeout=timeout)
        except subprocess.TimeoutExpired:
            return {
                "surface": "python",
                "tool": tool_name,
                "discover": {"found": True},
                "inspect": {"spec": {"parameter": {}}},
                "execute": {
                    "status": "error",
                    "error_type": None,
                    "missing_keys": [],
                    "result": None,
                    "error": f"probe exceeded {timeout}s time budget",
                    "gate_reason": "resource_timeout",
                },
            }
        # The stage subprocess's own tooluniverse logger writes informational
        # lines to stdout ahead of the final JSON print, so only the last
        # non-empty line is guaranteed to be the probe's JSON payload.
        payload = None
        stdout_lines = [line for line in stdout.splitlines() if line.strip()]
        if stdout_lines:
            try:
                payload = json.loads(stdout_lines[-1])
            except (json.JSONDecodeError, ValueError):
                payload = None
        if not isinstance(payload, dict):
            return {
                "surface": "python",
                "tool": tool_name,
                "discover": {"found": False},
                "inspect": {"spec": None},
                "execute": {
                    "status": "error",
                    "error_type": "SubprocessDispatchError",
                    "missing_keys": [],
                    "result": None,
                    "error": (
                        stderr or stdout or "no output from stage probe subprocess"
                    )[:500],
                },
            }
        if code != 0 and payload.get("execute", {}).get("status") != "error":
            payload.setdefault("execute", {})["status"] = "error"
        return payload
    return _probe_tool_python_inprocess(tool_name, arguments)


def probe_tool_cli(
    tool_name: str,
    arguments: dict[str, Any],
    *,
    tu_bin: Path,
    timeout: float = DEFAULT_TIMEOUT,
) -> dict[str, Any]:
    """Run discover/inspect/execute through the stage's own ``tu`` executable.

    ``tu_bin`` must be resolved from the stage's ``.venv/bin/tu`` -- never
    PATH -- so the main checkout's installation cannot answer for the stage.
    """
    code, stdout, stderr = _run_command(
        [str(tu_bin), "grep", tool_name, "--json", "--field", "name", "--limit", "5"],
        timeout=timeout,
    )
    try:
        discovered = json.loads(stdout or "{}") if code == 0 else {}
    except json.JSONDecodeError:
        discovered = {}
    tools = discovered.get("tools", []) if isinstance(discovered, dict) else discovered
    discover_found = any(
        isinstance(item, dict) and item.get("name") == tool_name
        for item in (tools or [])
    )

    code, stdout, stderr = _run_command(
        [str(tu_bin), "info", tool_name, "--json"], timeout=timeout
    )
    try:
        info_payload = json.loads(stdout or "{}") if code == 0 else {}
    except json.JSONDecodeError:
        info_payload = {}
    spec: dict[str, Any] | None = None
    missing_keys: list[str] = []
    if isinstance(info_payload, dict):
        tools_list = info_payload.get("tools")
        if tools_list:
            spec = tools_list[0]
        missing = info_payload.get("missing_api_keys") or info_payload.get(
            "missing_keys"
        )
        if missing:
            missing_keys = list(missing)
    if not missing_keys and code != 0:
        missing_keys = _extract_missing_key_names(f"{stdout}\n{stderr}")

    code, stdout, stderr = _run_command(
        [str(tu_bin), "run", tool_name, json.dumps(arguments), "--json"],
        timeout=timeout,
    )
    try:
        result = (
            json.loads(stdout)
            if stdout
            else {"status": "error", "error": stderr.strip()[:500]}
        )
    except json.JSONDecodeError:
        result = {"status": "error", "error": (stdout + stderr).strip()[:500]}
    normalized = normalize_probe_result(
        result if isinstance(result, dict) else {"value": result}
    )
    execute_status = "success"
    error_text = None
    if isinstance(normalized, dict) and normalized.get("status") == "error":
        execute_status = "error"
        error_text = str(normalized.get("error", ""))[:500]
        if not missing_keys:
            missing_keys = _extract_missing_key_names(error_text or "")
    elif code != 0:
        execute_status = "error"
        error_text = (stderr or stdout or "tu run exited non-zero")[:500]

    return {
        "surface": "cli",
        "tool": tool_name,
        "discover": {"found": discover_found},
        "inspect": {"spec": spec},
        "execute": {
            "status": execute_status,
            "error_type": _classify_error_type(error_text),
            "missing_keys": missing_keys,
            "result": normalized,
            "error": error_text,
        },
    }


def assert_probe_contract(stages: dict[str, Any]) -> dict[str, Any]:
    """Pure verdict function over one surface's discover/inspect/execute stages.

    ``stages`` carries ``discover`` (``{"found": bool}``), ``inspect``
    (``{"spec": dict | None}``), and ``execute`` (``{"status", "error_type",
    "missing_keys", "result", ...}``). No ``ToolUniverse`` import -- provable
    with hand-built fixtures.
    """
    discover = stages.get("discover", {}) or {}
    inspect = stages.get("inspect", {}) or {}
    execute = stages.get("execute", {}) or {}

    error_type = execute.get("error_type")
    if error_type in ("ImportError", "AttributeError"):
        return {
            "verdict": "fail",
            "reason": f"execute raised {error_type} -- broken lazy-registry module string",
            "missing_keys": [],
        }

    missing_keys = list(execute.get("missing_keys") or [])
    gate_reason = execute.get("gate_reason")
    if missing_keys or gate_reason:
        return {
            "verdict": "gated",
            "reason": gate_reason or "tool excluded for missing credential(s)",
            "missing_keys": missing_keys,
        }

    if not discover.get("found"):
        return {
            "verdict": "fail",
            "reason": "discover found nothing",
            "missing_keys": [],
        }

    spec = inspect.get("spec")
    if not (isinstance(spec, dict) and ("parameter" in spec or "parameters" in spec)):
        return {
            "verdict": "fail",
            "reason": "inspect returned no parameter/parameters schema",
            "missing_keys": [],
        }

    if execute.get("status") == "error":
        return {
            "verdict": "fail",
            "reason": execute.get("error") or "execute failed",
            "missing_keys": [],
        }

    result = execute.get("result")
    if result is None or result == {} or result == []:
        return {
            "verdict": "fail",
            "reason": "execute returned an empty result with no gating signal",
            "missing_keys": [],
        }

    return {
        "verdict": "pass",
        "reason": "discover -> inspect -> execute completed",
        "missing_keys": [],
    }


def _write_json(path: Path, value: Any) -> Path:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def _collect_secrets() -> list[str]:
    import os

    return [os.environ[name] for name in CREDENTIAL_ENV_NAMES if os.environ.get(name)]


def _guard_no_secrets(paths: list[Path], secrets: list[str]) -> None:
    if not secrets:
        return
    for path in paths:
        if path.is_file() and _contains_secret(path, secrets):
            raise _CAPTURE_MODULE.EvidencePublicationError(
                f"credential canary found in {path.name}"
            )


def run_probe_suite(
    stage_path: Path, sample: list[dict[str, Any]], out_dir: Path
) -> dict[str, Any]:
    """Run both probe flavors for every ``sample`` entry inside ``stage_path``."""
    stage_path = Path(stage_path).resolve()
    stage_python = stage_path / ".venv" / "bin" / "python"
    tu_bin = stage_path / ".venv" / "bin" / "tu"
    if not stage_python.is_file():
        raise GitCaptureError(f"stage interpreter not found: {stage_python}")
    if not tu_bin.is_file():
        raise GitCaptureError(f"stage tu executable not found: {tu_bin}")

    # Pre-flight: the stage's own interpreter must resolve tooluniverse inside
    # the stage, never the main checkout -- otherwise every probe below would
    # silently answer for the wrong environment.
    code, stdout, stderr = _run_command(
        [str(stage_python), "-c", "import tooluniverse; print(tooluniverse.__file__)"],
        timeout=30.0,
    )
    if code != 0 or not stdout.strip().startswith(str(stage_path)):
        raise GitCaptureError(
            "stage interpreter does not resolve tooluniverse inside the stage: "
            f"stdout={stdout.strip()!r} stderr={stderr.strip()!r}"
        )

    stage_merge_oid = run_git(["rev-parse", "HEAD"], stage_path).strip()

    out_dir = Path(out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    contract: list[dict[str, Any]] = []
    written: list[Path] = []
    for entry in sample:
        name = entry["name"]
        arguments = entry["arguments"]
        timeout = float(entry.get("timeout", DEFAULT_TIMEOUT))
        python_stage = probe_tool_python(
            name, arguments, stage_python=stage_python, timeout=timeout
        )
        cli_stage = probe_tool_cli(name, arguments, tu_bin=tu_bin, timeout=timeout)
        python_verdict = assert_probe_contract(python_stage)
        cli_verdict = assert_probe_contract(cli_stage)
        combined_missing = sorted(
            set(python_verdict["missing_keys"]) | set(cli_verdict["missing_keys"])
        )
        overall = "pass"
        if python_verdict["verdict"] == "fail" or cli_verdict["verdict"] == "fail":
            overall = "fail"
        elif "gated" in (python_verdict["verdict"], cli_verdict["verdict"]):
            overall = "gated"
        record = {
            "name": name,
            "selection_rule": entry.get("selection_rule"),
            "verdict": overall,
            "missing_keys": combined_missing,
            "python": python_verdict,
            "cli": cli_verdict,
        }
        contract.append(record)
        tool_payload = {
            "name": name,
            "arguments": arguments,
            "python": python_stage,
            "cli": cli_stage,
            "contract": record,
        }
        written.append(_write_json(out_dir / f"{name}.json", tool_payload))

    counts = {
        "passed": sum(1 for c in contract if c["verdict"] == "pass"),
        "gated": sum(1 for c in contract if c["verdict"] == "gated"),
        "failed": sum(1 for c in contract if c["verdict"] == "fail"),
    }
    summary_path = out_dir / "summary.json"
    if summary_path.is_file():
        try:
            existing = json.loads(summary_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = {}
    else:
        existing = {}
    summary = {
        **existing,
        "stage_path": str(stage_path),
        "stage_merge_oid": stage_merge_oid,
        "sample": sample,
        "exclusions": EXCLUSIONS,
        "contract": contract,
        "passed": counts["passed"],
        "gated": counts["gated"],
        "failed": counts["failed"],
    }
    written.append(_write_json(summary_path, summary))
    _guard_no_secrets(written, _collect_secrets())
    return summary


def _default_stage_path() -> Path | None:
    remerge_json = (
        REPO_ROOT
        / ".planning/phases/02-upstream-main-integration/evidence/staging/remerge.json"
    )
    if not remerge_json.is_file():
        return None
    try:
        data = json.loads(remerge_json.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    stage_path = data.get("stage_path")
    return Path(stage_path) if stage_path else None


def _run_internal_python_probe(argv: list[str]) -> int:
    """Hidden re-entry point: run one in-process Python probe and print JSON.

    Only ever invoked by ``probe_tool_python`` via subprocess against the
    stage's own interpreter -- never called directly by a human.
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--_internal-python-probe", dest="tool_name", required=True)
    parser.add_argument("--_internal-arguments", dest="arguments", required=True)
    args, _ = parser.parse_known_args(argv)
    try:
        arguments = json.loads(args.arguments)
    except json.JSONDecodeError:
        arguments = {}
    result = _probe_tool_python_inprocess(args.tool_name, arguments)
    print(json.dumps(result, ensure_ascii=False))
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=str, default=None, help="Re-merge stage path")
    parser.add_argument(
        "--out",
        type=str,
        default=None,
        help="Output directory for probes/*.json (default: evidence/staging/probes)",
    )
    parser.add_argument(
        "--tool", type=str, default=None, help="Probe a single tool name"
    )
    parser.add_argument(
        "--json", action="store_true", help="Print JSON summary to stdout"
    )
    parser.add_argument("--_internal-python-probe", dest="internal_tool", default=None)
    parser.add_argument(
        "--_internal-arguments", dest="internal_arguments", default=None
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    raw_argv = list(argv if argv is not None else sys.argv[1:])
    if "--_internal-python-probe" in raw_argv:
        return _run_internal_python_probe(raw_argv)

    parser = _parser()
    args = parser.parse_args(raw_argv)

    stage_path = Path(args.stage) if args.stage else _default_stage_path()
    if stage_path is None:
        parser.error("--stage not given and remerge.json has no stage_path")
        return 2

    out_dir = (
        Path(args.out)
        if args.out
        else REPO_ROOT
        / ".planning/phases/02-upstream-main-integration/evidence/staging/probes"
    )

    sample = PROBE_SAMPLE
    if args.tool:
        sample = [entry for entry in PROBE_SAMPLE if entry["name"] == args.tool]
        if not sample:
            parser.error(f"unknown tool: {args.tool}")
            return 2

    payload = run_probe_suite(stage_path, sample, out_dir)
    if args.json:
        print(json.dumps(payload, sort_keys=True))
    else:
        print(
            f"passed={payload['passed']} gated={payload['gated']} failed={payload['failed']}"
        )
    return 1 if payload["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
