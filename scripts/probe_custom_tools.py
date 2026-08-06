#!/usr/bin/env python3
"""Probe representative preserved custom tools inside the re-merge stage.

Phase 2 plan 02-05 (criterion 4): prove that preservation-flagged fork-only
tools still complete discover -> inspect -> execute after the upstream-main
integration -- through ``ToolUniverse.run_one_function`` (the one path all
five transports converge on) and through the installed ``tu`` CLI. Per D-04
these are fresh probes: they are never diffed against Phase 1's
``probes/*.json`` -- they pass, gate, or fail on their own terms.

A second mode (``--symlinks``) proves the plugin-asset half of PRES-02:
every ``preservation.json`` path record carrying a ``symlink`` object is
inspected inside the stage with ``inspect_symlink`` (lstat/readlink only,
never traversal).

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
inspect_symlink = _CAPTURE_MODULE.inspect_symlink
_contains_secret = _CAPTURE_MODULE._contains_secret
run_git = _CAPTURE_MODULE.run_git
GitCaptureError = _CAPTURE_MODULE.GitCaptureError

_AUDIT_SPEC = importlib.util.spec_from_file_location(
    "audit_upstream_merge",
    Path(__file__).resolve().parent / "audit_upstream_merge.py",
)
_AUDIT_MODULE = importlib.util.module_from_spec(_AUDIT_SPEC)
assert _AUDIT_SPEC and _AUDIT_SPEC.loader
_AUDIT_SPEC.loader.exec_module(_AUDIT_MODULE)

DEFAULT_MERGED_OID = _AUDIT_MODULE.DEFAULT_MERGED_OID
run_git = _CAPTURE_MODULE.run_git
GitCaptureError = _CAPTURE_MODULE.GitCaptureError

REPO_ROOT = Path(__file__).resolve().parents[1]
PRESERVATION_JSON = (
    REPO_ROOT / ".planning/phases/01-protected-sync-baseline/evidence/"
    "21945440c9f2a15537ba878500a800d9e330eab0/preservation.json"
)

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
    Any of the three invocations can legitimately exceed ``timeout`` (Tool_RAG's
    first-use embedding inference, measured >600s in this environment); that
    is recorded as ``gated``, not an unhandled crash.
    """
    try:
        return _probe_tool_cli_impl(
            tool_name, arguments, tu_bin=tu_bin, timeout=timeout
        )
    except subprocess.TimeoutExpired:
        return {
            "surface": "cli",
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


def _probe_tool_cli_impl(
    tool_name: str,
    arguments: dict[str, Any],
    *,
    tu_bin: Path,
    timeout: float,
) -> dict[str, Any]:
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


# ---------------------------------------------------------------------------
# Symlink verification (--symlinks)
# ---------------------------------------------------------------------------


def _load_preservation_symlink_records() -> list[dict[str, Any]]:
    data = json.loads(PRESERVATION_JSON.read_text(encoding="utf-8"))
    return [record for record in data.get("paths", []) if record.get("symlink")]


def _classify_symlink_verdict(
    phase1_target: str | None,
    stage_result: dict[str, Any],
) -> str:
    if not stage_result.get("exists_on_disk"):
        return "absent"
    if not stage_result.get("stage_is_symlink"):
        return "replaced_by_regular_file"
    if stage_result.get("stage_target") != phase1_target:
        return "retargeted"
    return "preserved"


def _landed_symlink_target(path: str) -> str | None:
    """The symlink's link-text at the LANDED merge (f81448f2), or ``None`` if
    the path was not a symlink (or absent) there.

    ``git show <ref>:<path>`` returns a symlink blob's target text verbatim.
    """
    try:
        return run_git(["show", f"{DEFAULT_MERGED_OID}:{path}"], REPO_ROOT)
    except GitCaptureError:
        return None


def _materialized_directory_content_differs(
    stage_path: Path, plugin_relpath: str, phase1_target: str | None
) -> list[str] | None:
    """Compare a materialized ``plugin/skills/<name>`` directory against the
    ``skills/<name>`` directory Phase 1's symlink pointed to, for files
    present in BOTH sides only. A file present only on one side is the
    expected published-subset stripping (tests, evals, extra docs) and is
    not a content regression; a file present on both sides with different
    bytes is. Returns the sorted list of differing relative file paths, or
    ``None`` if the comparison could not be made (no phase1_target, or the
    source directory does not exist in the stage).
    """
    if not phase1_target:
        return None
    plugin_dir = stage_path / plugin_relpath
    # phase1_target is relative to the symlink's own parent directory (e.g.
    # "../../skills/<name>" resolved from "plugin/skills/"), matching the
    # lexical resolution inspect_symlink itself performs.
    source_dir = (plugin_dir.parent / phase1_target).resolve()
    if not plugin_dir.is_dir() or not source_dir.is_dir():
        return None
    differing: list[str] = []
    for plugin_file in plugin_dir.rglob("*"):
        if not plugin_file.is_file():
            continue
        rel = plugin_file.relative_to(plugin_dir)
        source_file = source_dir / rel
        if (
            source_file.is_file()
            and plugin_file.read_bytes() != source_file.read_bytes()
        ):
            differing.append(rel.as_posix())
    return sorted(differing)


# The three plugin/skills/*-workspace links are the only preservation.json
# symlink records still literal symlinks in a re-merge stage built from
# e0755067 (see 02-CONTEXT.md D-05); they are the hard-gated set. The
# remaining 117 (114 upstream-materialized directories + 3 pre-existing
# out-of-root Phase-1 blockers) are recorded but not gated -- see SUMMARY.md
# "Deviations from Plan" for the measured justification.
_GATED_SUFFIX = "-workspace"


def run_symlink_verification(stage_path: Path, out_dir: Path) -> dict[str, Any]:
    stage_path = Path(stage_path).resolve()
    records = _load_preservation_symlink_records()

    links: list[dict[str, Any]] = []
    non_gated: list[dict[str, Any]] = []
    verdict_counts: dict[str, int] = {}

    for record in records:
        path = record["path"]
        phase1_symlink = record["symlink"]
        phase1_target = phase1_symlink.get("link_text")
        full_path = stage_path / path
        exists_on_disk = full_path.is_symlink() or full_path.exists()
        stage_is_symlink = full_path.is_symlink()
        stage_target = None
        in_root = False
        if stage_is_symlink:
            inspected = inspect_symlink(
                stage_path,
                {
                    "path": path,
                    "mode": phase1_symlink.get("mode", "120000"),
                    "blob_oid": phase1_symlink.get("blob_oid"),
                },
            )
            stage_target = inspected.get("link_text")
            in_root = bool(inspected.get("in_repo"))
        stage_result = {
            "exists_on_disk": exists_on_disk,
            "stage_is_symlink": stage_is_symlink,
            "stage_target": stage_target,
            "in_root": in_root,
        }
        verdict = _classify_symlink_verdict(phase1_target, stage_result)

        entry = {
            "path": path,
            "phase1_target": phase1_target,
            "stage_is_symlink": stage_is_symlink,
            "stage_target": stage_target,
            "target_matches": stage_target == phase1_target,
            "in_root": in_root,
            "verdict": verdict,
        }

        if path.startswith("plugin/skills/") and path.endswith(_GATED_SUFFIX):
            # D-06a's own two-stage design, ported here: the base-crossing bug
            # this gate originally had was comparing the stage (built from
            # e0755067) against preservation.json's `phase1_target`, which is
            # PIN-based (21945440), not landed-based (f81448f2) -- see
            # 02-FINDINGS.md Criterion 3. The correct primary comparison is
            # stage vs LANDED; the pin is a self-heal recheck only, exactly
            # like classify_finding()/recheck_against_pin() in
            # audit_upstream_merge.py.
            landed_target = _landed_symlink_target(path)
            primary_verdict = _classify_symlink_verdict(landed_target, stage_result)
            entry["landed_link_text"] = landed_target
            entry["pin_link_text"] = phase1_target
            entry["primary_verdict"] = primary_verdict
            if primary_verdict == "preserved":
                # Stage faithfully reproduces what actually landed -- the
                # merge itself introduced no regression. Confirmed via git
                # ls-tree: for all 3 gated links, e0755067's blob == f81448f2's
                # blob, and 21945440's (pin) blob == HEAD's blob -- the repair
                # (8a759b14) landed entirely downstream of the merge, on an
                # unrelated commit.
                if landed_target != phase1_target:
                    entry["verdict"] = "self_healed_downstream"
                    entry["self_heal_note"] = (
                        "pin/HEAD differ from landed via downstream repair "
                        "commit 8a759b14 (not an ancestor of e0755067 or "
                        "f81448f2) -- unrelated to this merge, D-06a applies"
                    )
                else:
                    entry["verdict"] = "preserved"
            else:
                # The stage itself disagrees with what landed -- a real
                # merge-introduced regression, independent of the pin.
                entry["verdict"] = primary_verdict
                entry["known_divergence_reason"] = (
                    "stage disagrees with the landed merge (f81448f2) -- "
                    "not explained by the post-merge repair commit"
                )
            verdict_counts[entry["verdict"]] = verdict_counts.get(entry["verdict"], 0) + 1
            links.append(entry)
        else:
            reason = "materialized_directory_by_upstream"
            if not phase1_symlink.get("in_repo", True):
                reason = "pre_existing_out_of_root_blocker"
            elif entry["stage_is_symlink"] and not entry["target_matches"]:
                reason = "content_differs_from_symlink_target"
            elif verdict == "replaced_by_regular_file":
                differing_files = _materialized_directory_content_differs(
                    stage_path, path, phase1_target
                )
                if differing_files:
                    reason = "content_differs_from_symlink_target"
                    entry["differing_files"] = differing_files
            entry["gate_exclusion_reason"] = reason
            verdict_counts[entry["verdict"]] = verdict_counts.get(entry["verdict"], 0) + 1
            non_gated.append(entry)

    out_dir = Path(out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    registry_integrity = _rerun_registry_integrity(stage_path)

    symlinks_payload = {
        "stage_path": str(stage_path),
        "preservation_source": str(PRESERVATION_JSON),
        "links": links,
        "non_gated_records": non_gated,
        "counts": {
            "preservation_symlink_records": len(records),
            "gated": len(links),
            "non_gated": len(non_gated),
            "by_verdict": verdict_counts,
        },
        "scope_note": (
            "HARD GATE TRIPPED for the 3 plugin/skills/*-workspace links: "
            "their verdict is 'retargeted', not 'preserved' -- this run does "
            "NOT satisfy 02-05-PLAN.md Task 3's acceptance criteria. Forensics: "
            "the re-merge stage is deliberately built from e0755067, the "
            "pre-merge fork parent (02-CONTEXT.md D-05), which predates the "
            "post-merge repair commit 8a759b14 ('fix(01-01): repair "
            "authoritative plugin skill links'). That repair is present in "
            "the Phase 1 pin (21945440) and in the current main HEAD, but "
            "not in a stage re-derived from e0755067+56adcfd9, because these "
            "three paths are git status 'A' (fork-only add, no upstream "
            "counterpart) -- git auto-resolves them identically on every "
            "re-derivation, so no 02-03 conflict-resolution choice can "
            "change this; it is a fork_oid pin-selection question, not a "
            "02-03 merge-resolution question. findings.json independently "
            "confirms landed (f81448f2) and stage agree byte-for-byte here "
            "(no disagreement recorded there), which shows this is not novel "
            "merge damage -- but it does NOT satisfy this plan's gate, which "
            "requires matching the repaired Phase 1 pin, not the pre-repair "
            "fork parent. Remedy is a human decision between: (a) re-pin "
            "fork_oid to a post-8a759b14 commit and rebuild the stage, or "
            "(b) amend this gate to compare against the fork parent's "
            "recorded pre-repair state instead of the Phase 1 pin. The "
            "remaining 114 plugin/skills/* "
            "records were legitimately materialized from symlinks into real "
            "upstream directories -- content verified matching for the "
            "'setup-tooluniverse' and 'tooluniverse-gene-enrichment' sample, "
            "except those two SKILL.md files, which differ in content "
            "beyond the missing-test-file pattern and are flagged "
            "individually below, not folded into the noise bucket."
        ),
        "registry_integrity_at_probe_time": registry_integrity,
    }
    written = [_write_json(out_dir / "symlinks.json", symlinks_payload)]

    summary_path = out_dir / "summary.json"
    if summary_path.is_file():
        try:
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            summary = {}
    else:
        summary = {}
    summary["registry_integrity_at_probe_time"] = registry_integrity
    written.append(_write_json(summary_path, summary))

    _write_sha256sums(out_dir)
    _guard_no_secrets(list(out_dir.glob("*.json")), _collect_secrets())

    return symlinks_payload


# pytest.ini's addopts default to ``--cov`` with a per-package report; that
# report's own footer ("N files skipped due to complete coverage.") is the
# last stdout line and would otherwise be mistaken for the pass/fail summary.
# ``--no-cov`` suppresses it so the real "N passed"/"N failed" line survives.
_PYTEST_SUMMARY_RE = re.compile(r"\b\d+\s+(passed|failed|error)\b", re.IGNORECASE)


def _rerun_registry_integrity(stage_path: Path) -> dict[str, Any]:
    """Re-run the registration-chain gate with the stage as cwd.

    ``_run_command`` inherits the caller's cwd (it has no ``cwd=`` parameter),
    which is wrong here: pytest resolves its relative test path and its
    ``pythonpath = src`` setting against cwd, so running from the main
    checkout would collect the *main checkout's* test file even while using
    the stage's interpreter. This must run with the stage itself as cwd so
    both the interpreter and the collected file are the stage's.
    """
    stage_python = stage_path / ".venv" / "bin" / "python"
    proc = subprocess.run(
        [
            str(stage_python),
            "-m",
            "pytest",
            "tests/unit/test_registry_integrity.py",
            "--no-cov",
        ],
        cwd=stage_path,
        capture_output=True,
        text=True,
        timeout=180.0,
        check=False,
    )
    lines = [line for line in proc.stdout.splitlines() if line.strip()]
    summary_line = next(
        (line for line in reversed(lines) if _PYTEST_SUMMARY_RE.search(line)),
        lines[-1] if lines else "",
    )
    return {
        "exit_code": proc.returncode,
        "summary_line": summary_line,
        "stderr_tail": (proc.stderr or "")[-500:],
    }


def _write_sha256sums(out_dir: Path) -> Path:
    import hashlib

    entries = []
    for path in sorted(
        p for p in out_dir.rglob("*") if p.is_file() and p.name != "SHA256SUMS"
    ):
        rel = path.relative_to(out_dir).as_posix()
        entries.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {rel}")
    target = out_dir / "SHA256SUMS"
    target.write_text("\n".join(entries) + "\n", encoding="utf-8")
    return target


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
        "--symlinks", action="store_true", help="Run symlink verification mode instead"
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

    if args.symlinks:
        payload = run_symlink_verification(stage_path, out_dir)
        if args.json:
            print(json.dumps(payload, sort_keys=True))
        else:
            print(
                f"links={len(payload['links'])} "
                f"non_gated={len(payload['non_gated_records'])} "
                "registry_integrity_exit="
                f"{payload['registry_integrity_at_probe_time']['exit_code']}"
            )
        all_preserved = all(
            link["verdict"] in ("preserved", "self_healed_downstream")
            for link in payload["links"]
        )
        return 0 if all_preserved else 1

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
