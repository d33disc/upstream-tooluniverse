#!/usr/bin/env python3
"""Capture a protected, reproducible Git baseline for ToolUniverse.

The capture command is intentionally disposable in this first phase.  It never
changes the caller's checkout; all mutable work is performed in a detached
secondary worktree and caller-provided output directory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import socket
import threading
import urllib.error
import urllib.request
import select
from pathlib import Path
from typing import Any, Iterable

PR161_MERGE = "16af425c053c306a658c96e254b4c4114338dd11"
PRESERVATION_CLASSES = (
    "custom_code",
    "tool_definition",
    "plugin_asset",
    "skill",
    "test",
    "workflow",
    "documentation",
    "generated_asset",
    "planning",
    "other_review_required",
)
FINAL_FLAGS = ("ci_evidence", "publish_root", "result_json")
EXPECTED_CI_JOB_NAMES = tuple(
    f"Python {version} compatibility"
    for version in ("3.10", "3.11", "3.12", "3.13", "3.14")
)


class BaselineValidationError(ValueError):
    """A probe result or evidence bundle violates the baseline contract."""


class RetryExhaustedError(RuntimeError):
    """A retryable probe failed on every bounded attempt."""


class EvidencePublicationError(ValueError):
    """Evidence cannot be published safely or completely."""


class GitCaptureError(RuntimeError):
    """A Git command or invariant failed while capturing evidence."""


REFERENCE_TOOL = "DegreesOfUnsaturation_calculate"
REFERENCE_ARGUMENTS = {"operation": "calculate", "formula": "C6H6"}


def _stage(
    name: str, started: float, outcome: Any, *, command: str | None = None
) -> dict[str, Any]:
    """Build a bounded, transport-neutral stage record."""
    result = outcome if isinstance(outcome, dict) else {"value": outcome}
    return {
        "name": name,
        "status": "success"
        if result.get("status") in {"success", "ok"} or result.get("valid") is True
        else "error",
        "duration_ms": round((time.monotonic() - started) * 1000, 3),
        "outcome": normalize_probe_result(result),
        **({"command": command} if command else {}),
    }


def _probe_contract(
    surface: str,
    discover: dict[str, Any],
    inspect: dict[str, Any],
    execute: dict[str, Any],
    assertion: dict[str, Any],
) -> dict[str, Any]:
    """Return the common discover/inspect/execute/assert evidence shape."""
    return {
        "surface": surface,
        "tier": "local",
        "tool": REFERENCE_TOOL,
        "discover": discover,
        "inspect": inspect,
        "execute": execute,
        "assert": assertion,
        "arguments": sorted(REFERENCE_ARGUMENTS),
        "schema_inspected": True,
    }


def _error_stage(value: Any) -> dict[str, Any]:
    normalized = normalize_probe_result(value)
    if (
        not isinstance(normalized, dict)
        or normalized.get("status") != "error"
        and "error" not in normalized
    ):
        raise BaselineValidationError("invalid probe must return a structured error")
    return {"name": "structured_error", "status": "success", "outcome": normalized}


def _assert_reference(result: Any) -> dict[str, Any]:
    normalized = normalize_probe_result(result)
    validate_probe_invariants(
        {"required_keys": ("status", "data"), "types": {"status": "string"}},
        result,
        normalized,
        {
            "equals": {
                "status": "success",
                "data.degrees_of_unsaturation": 4.0,
                "data.is_integer": True,
            }
        },
    )
    return {"status": "success", "valid": True, "normalized": normalized}


def run_python_probe() -> dict[str, Any]:
    """Run the reference workflow directly through the Python API."""
    from tooluniverse.execute_function import ToolUniverse

    started = time.monotonic()
    universe = ToolUniverse()
    try:
        universe.load_tools(include_tools=[REFERENCE_TOOL])
        found = universe.find_tools_by_pattern(
            REFERENCE_TOOL, search_in="name", case_sensitive=True
        )
        discover = _stage(
            "discover",
            started,
            {"status": "success", "tools": [REFERENCE_TOOL] if found else []},
        )
        spec = universe.tool_specification(REFERENCE_TOOL)
        inspect = _stage("inspect", started, {"status": "success", "spec": spec})
        required = spec.get("parameter", {}).get("required", [])
        if "operation" not in required:
            raise BaselineValidationError(
                "reference schema no longer requires operation"
            )
        result = universe.run_one_function(
            {"name": REFERENCE_TOOL, "arguments": REFERENCE_ARGUMENTS}
        )
        execute = _stage("execute", started, result)
        assertion = _stage("assert", started, _assert_reference(result))
        probe = _probe_contract("python", discover, inspect, execute, assertion)
        probe["structured_error"] = _error_stage(
            universe.run_one_function(
                {"name": REFERENCE_TOOL, "arguments": {"operation": "invalid"}}
            )
        )
        return probe
    finally:
        close = getattr(universe, "close", None)
        if close:
            close()


def _run_command(argv: list[str], timeout: float = 60.0) -> tuple[int, str, str]:
    proc = subprocess.run(
        argv,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
        env={**os.environ, "PYTHONUNBUFFERED": "1"},
    )
    return proc.returncode, proc.stdout, proc.stderr


def run_cli_probe() -> dict[str, Any]:
    """Run grep/info/run through the installed ``tu`` executable."""
    code, stdout, stderr = _run_command(
        ["tu", "grep", REFERENCE_TOOL, "--json", "--field", "name", "--limit", "5"]
    )
    discovered = json.loads(stdout or "{}") if code == 0 else {}
    tools = discovered.get("tools", []) if isinstance(discovered, dict) else discovered
    discover = {
        "name": "discover",
        "status": "success"
        if any(item.get("name") == REFERENCE_TOOL for item in tools)
        else "error",
        "outcome": normalize_probe_result(discovered),
        "stderr": stderr[:240],
    }
    code, stdout, stderr = _run_command(["tu", "info", REFERENCE_TOOL, "--json"])
    info_payload = json.loads(stdout or "{}") if code == 0 else {}
    spec = (
        (info_payload.get("tools") or [{}])[0] if isinstance(info_payload, dict) else {}
    )
    required = spec.get("parameters", spec.get("parameter", {})).get("required", [])
    inspect = {
        "name": "inspect",
        "status": "success" if "operation" in required else "error",
        "outcome": normalize_probe_result(spec),
        "stderr": stderr[:240],
    }
    if inspect["status"] != "success":
        raise BaselineValidationError("CLI schema does not require operation")
    code, stdout, stderr = _run_command(
        ["tu", "run", REFERENCE_TOOL, json.dumps(REFERENCE_ARGUMENTS), "--json"]
    )
    result = (
        json.loads(stdout or "{}")
        if stdout
        else {"status": "error", "error": stderr.strip()[:240]}
    )
    execute = {
        "name": "execute",
        "status": "success" if code == 0 else "error",
        "outcome": normalize_probe_result(result),
        "stderr": stderr[:240],
    }
    assertion = _stage("assert", time.monotonic(), _assert_reference(result))
    code, bad_stdout, bad_stderr = _run_command(
        ["tu", "run", REFERENCE_TOOL, json.dumps({"operation": "invalid"}), "--json"]
    )
    bad = (
        json.loads(bad_stdout or "{}")
        if bad_stdout
        else {"status": "error", "error": bad_stderr[:240]}
    )
    probe = _probe_contract("cli", discover, inspect, execute, assertion)
    probe["structured_error"] = _error_stage(bad)
    return probe


def _stdio_request(
    proc: subprocess.Popen[str], request: dict[str, Any], timeout: float = 60.0
) -> dict[str, Any]:
    assert proc.stdin and proc.stdout
    proc.stdin.write(json.dumps(request) + "\n")
    proc.stdin.flush()
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        ready, _, _ = select.select(
            [proc.stdout], [], [], min(0.5, max(0.0, deadline - time.monotonic()))
        )
        if not ready:
            continue
        line = proc.stdout.readline()
        if not line:
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if value.get("id") == request.get("id"):
            return value
    raise TimeoutError(f"stdio request timed out: {request.get('method')}")


def run_mcp_stdio_probe() -> dict[str, Any]:
    """Exercise MCP stdio using its JSON-RPC lifecycle (not a direct API call)."""
    cmd = [
        sys.executable,
        "-m",
        "tooluniverse.smcp_server",
        "--transport",
        "stdio",
        "--include-tools",
        REFERENCE_TOOL,
        "--compact-mode",
    ]
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env={**os.environ, "PYTHONUNBUFFERED": "1"},
    )
    try:
        init = _stdio_request(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "baseline", "version": "1"},
                },
            },
        )
        if "result" not in init:
            raise BaselineValidationError(f"MCP stdio initialize failed: {init}")
        proc.stdin.write(
            json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n"
        )
        proc.stdin.flush()
        listed = _stdio_request(
            proc, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
        )
        names = [item.get("name") for item in listed.get("result", {}).get("tools", [])]
        discover = {
            "name": "discover",
            "status": "success"
            if "get_tool_info" in names and "execute_tool" in names
            else "error",
            "outcome": {"tools": names},
        }
        info = _stdio_request(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "get_tool_info",
                    "arguments": {"tool_name": REFERENCE_TOOL},
                },
            },
        )
        info_result = info.get("result", {})
        inspect = {
            "name": "inspect",
            "status": "success" if info_result else "error",
            "outcome": info_result,
        }
        call = _stdio_request(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "execute_tool",
                    "arguments": {
                        "tool_name": REFERENCE_TOOL,
                        "arguments": REFERENCE_ARGUMENTS,
                    },
                },
            },
        )
        result = call.get("result", {}).get("structuredContent") or call.get(
            "result", {}
        ).get("content", [{}])[0].get("text", "{}")
        if isinstance(result, str):
            result = json.loads(result)
        execute = {
            "name": "execute",
            "status": "success" if "isError" not in call else "error",
            "outcome": result,
        }
        assertion = _stage("assert", time.monotonic(), _assert_reference(result))
        bad_call = _stdio_request(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {
                    "name": "execute_tool",
                    "arguments": {
                        "tool_name": REFERENCE_TOOL,
                        "arguments": {"operation": "invalid"},
                    },
                },
            },
        )
        bad = bad_call.get("result", {}).get("structuredContent") or {
            "status": "error",
            "error": str(bad_call.get("result", {}))[:240],
        }
        probe = _probe_contract("mcp-stdio", discover, inspect, execute, assertion)
        probe["structured_error"] = _error_stage(bad)
        return probe
    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


async def _mcp_http_async(url: str) -> dict[str, Any]:
    from mcp.client.session import ClientSession
    from mcp.client.streamable_http import streamablehttp_client

    async with streamablehttp_client(url, timeout=30, sse_read_timeout=60) as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            listed = await session.list_tools()
            names = [item.name for item in listed.tools]
            info = await session.call_tool(
                "get_tool_info", {"tool_name": REFERENCE_TOOL}
            )
            call = await session.call_tool(
                "execute_tool",
                {"tool_name": REFERENCE_TOOL, "arguments": REFERENCE_ARGUMENTS},
            )
            value = getattr(call, "structuredContent", None)
            if value is None and getattr(call, "content", None):
                value = json.loads(call.content[0].text)
            return {
                "names": names,
                "info": info.model_dump()
                if hasattr(info, "model_dump")
                else info.dict(),
                "result": value,
            }


def run_mcp_http_probe() -> dict[str, Any]:
    """Exercise streamable HTTP through the MCP client session."""
    import asyncio

    port = _free_port()
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "tooluniverse.smcp_server",
            "--transport",
            "http",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--include-tools",
            REFERENCE_TOOL,
            "--compact-mode",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env={**os.environ, "PYTHONUNBUFFERED": "1"},
    )
    try:
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            try:
                with socket.create_connection(("127.0.0.1", port), timeout=1):
                    break
            except Exception:
                if proc.poll() is not None:
                    raise RuntimeError("MCP HTTP child exited before readiness")
        payload = asyncio.run(_mcp_http_async(f"http://127.0.0.1:{port}/mcp"))
        discover = {
            "name": "discover",
            "status": "success" if "execute_tool" in payload["names"] else "error",
            "outcome": {"tools": payload["names"]},
        }
        inspect = {
            "name": "inspect",
            "status": "success" if payload["info"] else "error",
            "outcome": payload["info"],
        }
        execute = {"name": "execute", "status": "success", "outcome": payload["result"]}
        assertion = _stage(
            "assert", time.monotonic(), _assert_reference(payload["result"])
        )
        probe = _probe_contract("mcp-http", discover, inspect, execute, assertion)

        async def invalid():
            from mcp.client.session import ClientSession
            from mcp.client.streamable_http import streamablehttp_client

            async with streamablehttp_client(
                f"http://127.0.0.1:{port}/mcp", timeout=30
            ) as (r, w, _):
                async with ClientSession(r, w) as session:
                    await session.initialize()
                    bad = await session.call_tool(
                        "execute_tool",
                        {
                            "tool_name": REFERENCE_TOOL,
                            "arguments": {"operation": "invalid"},
                        },
                    )
                    return getattr(bad, "structuredContent", None) or {
                        "status": "error",
                        "error": str(bad)[:240],
                    }

        probe["structured_error"] = _error_stage(asyncio.run(invalid()))
        return probe
    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)


def run_rest_probe() -> dict[str, Any]:
    """Exercise the REST API's method discovery, inspection, and call routes."""
    import uvicorn
    from tooluniverse.http_api_server import app, _tu_manager

    port = _free_port()
    ready = threading.Event()
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=lambda: (ready.set(), server.run()), daemon=True)
    thread.start()
    try:
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            try:
                with socket.create_connection(("127.0.0.1", port), timeout=1):
                    break
            except Exception:
                time.sleep(0.1)

        def post(payload: dict[str, Any]) -> dict[str, Any]:
            request = urllib.request.Request(
                f"http://127.0.0.1:{port}/api/call",
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(request, timeout=60) as response:
                return json.loads(response.read())

        discover = {
            "name": "discover",
            "status": "success",
            "outcome": post(
                {"method": "get_available_tools", "kwargs": {"name_only": True}}
            ),
        }
        spec = post(
            {"method": "tool_specification", "kwargs": {"tool_name": REFERENCE_TOOL}}
        )
        inspect = {
            "name": "inspect",
            "status": "success" if spec.get("success") else "error",
            "outcome": spec,
        }
        result = post(
            {
                "method": "run_one_function",
                "kwargs": {
                    "function_call_json": {
                        "name": REFERENCE_TOOL,
                        "arguments": REFERENCE_ARGUMENTS,
                    }
                },
            }
        )
        result = result.get("result", result)
        execute = {
            "name": "execute",
            "status": "success" if result.get("status") == "success" else "error",
            "outcome": result,
        }
        assertion = _stage("assert", time.monotonic(), _assert_reference(result))
        bad = post(
            {
                "method": "run_one_function",
                "kwargs": {
                    "function_call_json": {
                        "name": REFERENCE_TOOL,
                        "arguments": {"operation": "invalid"},
                    }
                },
            }
        )
        bad = bad.get("result", bad)
        probe = _probe_contract("rest", discover, inspect, execute, assertion)
        probe["structured_error"] = _error_stage(bad)
        return probe
    finally:
        server.should_exit = True
        thread.join(timeout=10)
        _tu_manager.reset()


def run_surface_matrix() -> dict[str, Any]:
    """Run all five transport probes and return one auditable matrix."""
    probes = [
        run_python_probe,
        run_cli_probe,
        run_mcp_stdio_probe,
        run_mcp_http_probe,
        run_rest_probe,
    ]
    results = [probe() for probe in probes]
    return {
        "status": "green",
        "tool": REFERENCE_TOOL,
        "tier": "local",
        "surfaces": results,
    }


def run_git(argv: Iterable[str], cwd: Path | str, timeout: float = 60.0) -> str:
    """Run Git with an argv-only boundary and return stdout."""
    args = ["git", *map(str, argv)]
    try:
        proc = subprocess.run(
            args,
            cwd=os.fspath(cwd),
            capture_output=True,
            text=False,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise GitCaptureError(f"git command failed: {' '.join(args)}: {exc}") from exc
    if proc.returncode:
        stderr = proc.stderr.decode("utf-8", "replace").strip()
        raise GitCaptureError(
            f"git command failed ({proc.returncode}): {' '.join(args)}: {stderr}"
        )
    return proc.stdout.decode("utf-8", "surrogateescape")


def _oid(repo: Path, ref: str) -> str:
    value = run_git(["rev-parse", "--verify", f"{ref}^{{commit}}"], repo).strip()
    if len(value) != 40:
        raise GitCaptureError(f"not a full commit OID: {ref}")
    return value


def _nul_records(value: str) -> list[str]:
    return [record for record in value.split("\0") if record]


def capture_git_snapshot(repo: Path | str) -> dict[str, Any]:
    """Capture branch, refs, divergence, and byte-safe worktree state."""
    root = Path(repo).resolve()
    head = _oid(root, "HEAD")
    branch = (
        run_git(["symbolic-ref", "--quiet", "--short", "HEAD"], root).strip()
        if _symbolic(root)
        else None
    )
    status_raw = run_git(
        ["status", "--porcelain=v2", "-z", "--branch", "--untracked-files=all"], root
    )
    staged_raw = run_git(["diff", "--cached", "--raw", "-z", "--no-renames"], root)
    unstaged_raw = run_git(["diff", "--raw", "-z", "--no-renames"], root)
    untracked = [r[2:] for r in _nul_records(status_raw) if r.startswith("? ")]
    upstream_local = None
    try:
        upstream_local = _oid(root, "upstream/main")
    except GitCaptureError:
        pass
    upstream_remote = None
    try:
        remote_lines = run_git(["ls-remote", "upstream", "refs/heads/main"], root)
    except GitCaptureError:
        remote_lines = ""
    if remote_lines.strip():
        upstream_remote = remote_lines.split()[0]
    if upstream_remote and upstream_local and upstream_remote != upstream_local:
        raise GitCaptureError(
            "blocking upstream ref mismatch: local upstream/main differs from ls-remote"
        )
    merge_base = None
    divergence = None
    if upstream_local:
        merge_base = (
            _oid(root, f"merge-base HEAD {upstream_local}")
            if False
            else run_git(["merge-base", "HEAD", upstream_local], root).strip()
        )
        counts = run_git(
            ["rev-list", "--left-right", "--count", f"HEAD...{upstream_local}"], root
        ).split()
        divergence = {"fork_only": int(counts[0]), "upstream_only": int(counts[1])}
    pr161_ancestor = False
    if upstream_local:
        proc = subprocess.run(
            ["git", "merge-base", "--is-ancestor", PR161_MERGE, upstream_local],
            cwd=root,
            capture_output=True,
            timeout=60,
            check=False,
        )
        pr161_ancestor = proc.returncode == 0
    return {
        "repo": str(root),
        "head": head,
        "branch": branch,
        "detached": branch is None,
        "status_records": _nul_records(status_raw),
        "staged_records": _nul_records(staged_raw),
        "unstaged_records": _nul_records(unstaged_raw),
        "untracked_paths": untracked,
        "upstream_local_oid": upstream_local,
        "upstream_remote_oid": upstream_remote,
        "merge_base": merge_base,
        "divergence": divergence,
        "pr161_merge_oid": PR161_MERGE,
        "pr161_ancestor": pr161_ancestor,
    }


def _symbolic(repo: Path) -> bool:
    proc = subprocess.run(
        ["git", "symbolic-ref", "--quiet", "HEAD"],
        cwd=repo,
        capture_output=True,
        timeout=60,
        check=False,
    )
    return proc.returncode == 0


def create_isolated_worktree(
    repo: Path | str, fork_oid: str, worktree_dir: Path | str
) -> Path:
    """Create a detached worktree at *fork_oid* without touching the checkout."""
    root = Path(repo).resolve()
    target = Path(worktree_dir).resolve()
    if target == root or root in target.parents:
        raise ValueError("isolated worktree must not be inside the original checkout")
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and any(target.iterdir()):
        raise FileExistsError(target)
    run_git(["worktree", "add", "--detach", str(target), _oid(root, fork_oid)], root)
    return target


def validate_capture_mode(args: argparse.Namespace) -> None:
    """Enforce the mutually exclusive disposable and final contracts."""
    if not args.repo or not args.worktree_dir:
        raise ValueError("--repo and --worktree-dir are required")
    supplied = [name for name in FINAL_FLAGS if getattr(args, name, None)]
    if args.output_dir and supplied:
        raise ValueError("--output-dir cannot be combined with final flags")
    if not args.output_dir and not supplied:
        raise ValueError("exactly one capture mode is required")
    if args.output_dir and supplied:
        raise ValueError("mixed capture modes are not allowed")
    if args.output_dir:
        mode_output = args.output_dir
    else:
        if len(supplied) != len(FINAL_FLAGS):
            raise ValueError("--ci-evidence, --publish-root, and --result-json are required together")
        mode_output = None
    repo = Path(args.repo).resolve()
    worktree = Path(args.worktree_dir).resolve()
    if mode_output:
        output = Path(mode_output).resolve()
        if output == worktree or worktree in output.parents:
            raise ValueError("output directory must be outside isolated worktree")
        if output == repo or repo in output.parents:
            raise ValueError("output directory must not be inside original checkout")


def _gh_json(argv: list[str], run_command=_run_command) -> Any:
    code, stdout, stderr = run_command(argv, timeout=60.0)
    if code:
        raise GitCaptureError(f"GitHub command failed ({argv[1]}): {stderr[:240]}")
    try:
        return json.loads(stdout or "null")
    except json.JSONDecodeError as exc:
        raise GitCaptureError("GitHub command returned invalid JSON") from exc


def validate_ci_jobs(
    run: dict[str, Any], expected_job_names: Iterable[str] = EXPECTED_CI_JOB_NAMES
) -> dict[str, Any]:
    """Reject incomplete, duplicate, failed, or unexpected Actions jobs."""
    expected = tuple(expected_job_names)
    if run.get("conclusion") not in (None, "success"):
        raise GitCaptureError(f"Actions run conclusion is not successful: {run.get('conclusion')}")
    jobs = run.get("jobs")
    if not isinstance(jobs, list):
        raise GitCaptureError("Actions run has no jobs")
    names = [job.get("name") for job in jobs if isinstance(job, dict)]
    if any(names.count(name) != 1 for name in expected) or set(names) != set(expected):
        raise GitCaptureError("Actions run does not contain exactly the approved jobs")
    for job in jobs:
        if job.get("name") in expected and (
            job.get("status") != "completed" or job.get("conclusion") != "success"
        ):
            raise GitCaptureError(f"Actions job is not successful: {job.get('name')}")
    return {
        "headSha": run.get("headSha"),
        "conclusion": run.get("conclusion"),
        "url": run.get("url"),
        "event": run.get("event"),
        "jobs": [{key: job.get(key) for key in ("name", "status", "conclusion")} for job in jobs],
        "comprehensive_job": "Python 3.12 compatibility",
    }


def collect_ci_evidence(repo: Path | str, head_sha: str, run_command=_run_command) -> dict[str, Any]:
    """Collect read-only Actions evidence tied to one exact full commit SHA."""
    root = Path(repo).resolve()
    listing = _gh_json(
        ["gh", "run", "list", "--repo", str(root), "--workflow", "tests.yml", "--commit", head_sha,
         "--json", "databaseId,headSha,status,conclusion,event,url,name,createdAt"], run_command
    )
    if not isinstance(listing, list):
        raise GitCaptureError("Actions run list is not an array")
    matches = [item for item in listing if item.get("headSha") == head_sha]
    if len(matches) != 1:
        raise GitCaptureError("exactly one matching full-SHA Actions run is required")
    run_id = matches[0].get("databaseId")
    if not run_id:
        raise GitCaptureError("Actions run has no databaseId")
    code, _, stderr = run_command(["gh", "run", "watch", str(run_id), "--repo", str(root), "--exit-status"], timeout=60.0)
    if code:
        raise GitCaptureError(f"Actions run did not complete successfully: {stderr[:240]}")
    run = _gh_json(["gh", "run", "view", str(run_id), "--repo", str(root), "--json", "headSha,conclusion,jobs,url,event"], run_command)
    if run.get("headSha") != head_sha:
        raise GitCaptureError("Actions run headSha changed or does not match requested commit")
    return validate_ci_jobs(run)


def classify_preservation_path(path: str) -> str:
    p = path.replace("\\", "/")
    if p.startswith(".planning/"):
        return "planning"
    if p.startswith("tests/"):
        return "test"
    if p.startswith(".github/workflows/"):
        return "workflow"
    if p.startswith("docs/") or p.endswith(".md"):
        return "documentation"
    if p.startswith("plugin/"):
        return "plugin_asset"
    if p.startswith("skills/"):
        return "skill"
    if (
        p == "TOOL_MANIFEST.json"
        or p == "uv.lock"
        or "_lazy_registry_static" in p
        or "embedding" in p.lower()
        or p.startswith("src/tooluniverse/")
        and p.endswith("_generated.py")
    ):
        return "generated_asset"
    if (
        p.startswith("tools/")
        or p.startswith("tooluniverse/")
        or p.startswith("src/tooluniverse/tool_")
    ):
        return "tool_definition"
    if p.startswith("src/") or p.startswith("scripts/"):
        return "custom_code"
    return "other_review_required"


def inspect_symlink(repo: Path | str, index_record: dict[str, Any]) -> dict[str, Any]:
    root = Path(repo).resolve()
    path = root / index_record["path"]
    target = os.readlink(path) if path.is_symlink() else None
    lexical = (
        (path.parent / target).resolve(strict=False) if target is not None else None
    )
    in_repo = bool(lexical and (lexical == root or root in lexical.parents))
    return {
        "mode": index_record.get("mode", "120000"),
        "blob_oid": index_record.get("blob_oid"),
        "link_text": target,
        "lexical_target": str(lexical) if lexical else None,
        "in_repo": in_repo,
        "exists": bool(lexical and lexical.exists()),
        "tracked": bool(
            lexical
            and run_git(
                ["ls-files", "--error-unmatch", str(lexical.relative_to(root))], root
            ).strip()
        )
        if in_repo and lexical.exists()
        else False,
        "blocking": not (in_repo and lexical and lexical.exists()),
    }


def _index_records(repo: Path) -> list[dict[str, Any]]:
    records = []
    for line in run_git(["ls-files", "-s", "-z"], repo).split("\0"):
        if not line:
            continue
        meta, path = line.split("\t", 1)
        mode, blob, stage = meta.split()
        records.append({"mode": mode, "blob_oid": blob, "stage": stage, "path": path})
    return records


def collect_preservation_inventory(
    repo: Path | str, upstream_oid: str, fork_oid: str
) -> dict[str, Any]:
    root = Path(repo).resolve()
    raw = run_git(
        ["diff", "--raw", "-z", "--find-renames", upstream_oid, fork_oid], root
    )
    paths: list[dict[str, Any]] = []
    tokens = _nul_records(raw)
    index = 0
    while index < len(tokens):
        rec = tokens[index]
        index += 1
        if "\t" in rec:
            meta, path = rec.split("\t", 1)
        elif rec.startswith(":") and index < len(tokens):
            meta, path = rec, tokens[index]
            index += 1
        else:
            continue
        fields = meta.split()
        if len(fields) < 5:
            continue
        old_mode, new_mode, old_oid, new_oid, status = fields[-5:]
        item = {
            "path": path,
            "old_mode": old_mode,
            "new_mode": new_mode,
            "old_oid": old_oid,
            "new_oid": new_oid,
            "status": status,
            "class": classify_preservation_path(path),
            "must_survive": "fork delta retained pending staged synchronization",
        }
        if new_mode == "120000" and (root / path).is_symlink():
            item["symlink"] = inspect_symlink(
                root, {"path": path, "mode": new_mode, "blob_oid": new_oid}
            )
        paths.append(item)
    untracked = []
    for path in run_git(
        ["ls-files", "--others", "--exclude-standard", "-z"], root
    ).split("\0"):
        if path:
            untracked.append(
                {
                    "path": path,
                    "metadata_only": True,
                    "class": "other_review_required"
                    if path.startswith("ralph-specs/")
                    else classify_preservation_path(path),
                    "must_survive": "user-owned untracked path; contents intentionally not read",
                }
            )
    blockers = [p for p in paths if p["class"] == "other_review_required"] + [
        p for p in paths if p.get("symlink", {}).get("blocking")
    ]
    return {
        "upstream_oid": upstream_oid,
        "fork_oid": fork_oid,
        "paths": paths,
        "untracked": untracked,
        "blocking": bool(blockers),
        "blockers": blockers,
    }


def prove_plugin_link_mapping(
    repo: Path | str, authoritative_oid: str, mappings: dict[str, str]
) -> dict[str, Any]:
    root = Path(repo).resolve()
    run_git(["merge-base", "--is-ancestor", PR161_MERGE, authoritative_oid], root)
    for target in mappings.values():
        tree = run_git(
            ["ls-tree", "-r", "--name-only", authoritative_oid, target], root
        )
        if not tree.strip():
            raise GitCaptureError(f"authoritative target is absent: {target}")
    siblings = [p for p in root.joinpath("plugin/skills").iterdir() if p.is_symlink()]
    if not any(os.readlink(p).startswith("../../skills/") for p in siblings):
        raise GitCaptureError("no conforming sibling plugin link")
    return {
        "authoritative_oid": authoritative_oid,
        "pr161_merge_oid": PR161_MERGE,
        "mappings": mappings,
        "proven": True,
    }


# The following helpers are deliberately stdlib-only.  Baseline evidence is a
# contract consumed by later sync phases, so normalization must be explicit,
# conservative, and independent of the live provider implementation.
_VOLATILE_PARTS = re.compile(r"(?:^|\.)([^.\[\]]+)|\[([^\]]+)\]")


def _path_parts(path: str | Iterable[Any]) -> tuple[Any, ...]:
    if not isinstance(path, str):
        return tuple(path)
    value = path[2:] if path.startswith("$.") else path.lstrip(".")
    parts: list[Any] = []
    for match in _VOLATILE_PARTS.finditer(value):
        token = match.group(1) if match.group(1) is not None else match.group(2)
        parts.append(int(token) if token.isdigit() else token.strip("'\""))
    return tuple(parts)


def _path_matches(path: tuple[Any, ...], pattern: tuple[Any, ...]) -> bool:
    return len(path) == len(pattern) and all(
        a == b or b == "*" for a, b in zip(path, pattern)
    )


def normalize_probe_result(
    value: Any,
    volatile_paths: Iterable[str | Iterable[Any]] = (),
    unordered_arrays: dict[str, str] | Iterable[str | Iterable[Any]] = (),
) -> Any:
    """Return a conservative, deterministic copy of a JSON-compatible result.

    Volatile values are replaced only at exact allowlisted paths.  Mappings are
    rebuilt in key order; arrays retain order unless explicitly listed as
    unordered, in which case the configured identity key is used.
    """
    volatile = [_path_parts(path) for path in volatile_paths]
    if isinstance(unordered_arrays, dict):
        unordered = {_path_parts(path): key for path, key in unordered_arrays.items()}
    else:
        unordered = {_path_parts(path): "id" for path in unordered_arrays}

    def walk(item: Any, path: tuple[Any, ...]) -> Any:
        if any(_path_matches(path, pattern) for pattern in volatile):
            return "<volatile>"
        if isinstance(item, dict):
            return {key: walk(item[key], path + (key,)) for key in sorted(item)}
        if isinstance(item, list):
            result = [walk(child, path + (index,)) for index, child in enumerate(item)]
            key = next(
                (
                    identity
                    for pattern, identity in unordered.items()
                    if _path_matches(path, pattern)
                ),
                None,
            )
            if key:
                try:
                    result.sort(
                        key=lambda child: (
                            str(child.get(key)),
                            json.dumps(child, sort_keys=True, default=str),
                        )
                    )
                except (AttributeError, TypeError):
                    raise BaselineValidationError(
                        f"unordered array at {path} must contain mapping items"
                    )
            return result
        if item is None or isinstance(item, (str, int, float, bool)):
            return item
        raise BaselineValidationError(f"result is not JSON serializable at {path}")

    return walk(value, ())


def _type_matches(value: Any, expected: str | type) -> bool:
    if isinstance(expected, type):
        return isinstance(value, expected) and not (
            expected is int and isinstance(value, bool)
        )
    return {
        "object": dict,
        "array": list,
        "string": str,
        "number": (int, float),
        "integer": int,
        "boolean": bool,
        "null": type(None),
    }.get(expected, object) is type(value) or (
        expected == "number"
        and isinstance(value, (int, float))
        and not isinstance(value, bool)
    )


def validate_probe_invariants(
    spec: dict[str, Any],
    raw: Any,
    normalized: Any,
    expected: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate schema/status/domain invariants and return a typed outcome."""
    if not isinstance(normalized, dict) or not isinstance(raw, dict):
        raise BaselineValidationError("probe result must be a JSON object")
    if json.dumps(normalized, sort_keys=True, ensure_ascii=False) is None:
        raise BaselineValidationError("probe result is not JSON serializable")
    status = normalized.get(
        "status",
        "success"
        if "data" in normalized
        else "error"
        if "error" in normalized
        else None,
    )
    allowed = spec.get("statuses", ("success", "error"))
    if status not in allowed:
        raise BaselineValidationError(f"unexpected structured status: {status!r}")
    if status == "error" and not spec.get("expects_error", False):
        raise BaselineValidationError("unexpected structured error")
    required = spec.get("required_keys", ())
    missing = [key for key in required if key not in normalized]
    if missing:
        raise BaselineValidationError(f"missing required keys: {missing}")
    for key, kind in spec.get("types", {}).items():
        if key in normalized and not _type_matches(normalized[key], kind):
            raise BaselineValidationError(f"key {key!r} has wrong type")
    expected = expected or {}
    for path, wanted in expected.get("equals", {}).items():
        actual: Any = normalized
        for part in _path_parts(path):
            try:
                actual = actual[part]
            except (KeyError, IndexError, TypeError) as exc:
                raise BaselineValidationError(
                    f"missing invariant path: {path}"
                ) from exc
        if actual != wanted:
            raise BaselineValidationError(
                f"invariant drift at {path}: {actual!r} != {wanted!r}"
            )
    for check in expected.get("checks", ()):
        if not check(normalized):
            raise BaselineValidationError("domain invariant failed")
    return {"status": status, "valid": True, "normalized": normalized}


def classify_retryable(outcome: Any) -> bool:
    """Classify transient failures without retrying auth/schema/domain errors."""
    status = (
        outcome
        if isinstance(outcome, int)
        else outcome.get("status_code")
        if isinstance(outcome, dict)
        else getattr(outcome, "status_code", None)
    )
    if status in {408, 429, 500, 502, 503, 504}:
        return True
    if isinstance(outcome, (TimeoutError, ConnectionError, TimeoutError)):
        return True
    if isinstance(outcome, BaseException):
        return outcome.__class__.__name__.lower() in {
            "timeouterror",
            "connectionerror",
            "connecterror",
        }
    return False


def run_with_retry(
    run_once, sleep=time.sleep, attempts: int = 3, delay: float = 2.0
) -> Any:
    """Run a probe at most three times, with exactly fixed-delay retries."""
    if attempts != 3:
        raise ValueError("baseline retry policy requires exactly three attempts")
    diagnostics = []
    for attempt in range(1, attempts + 1):
        try:
            result = run_once()
        except Exception as exc:  # provider exceptions are evidence, not leaks
            result = exc
        diagnostics.append(
            {
                "attempt": attempt,
                "retryable": classify_retryable(result),
                "outcome": _safe_diagnostic(result),
            }
        )
        if not classify_retryable(result):
            if isinstance(result, BaseException):
                raise result
            return result
        if attempt < attempts:
            sleep(delay)
    raise RetryExhaustedError(json.dumps({"attempts": diagnostics}, sort_keys=True))


def _safe_diagnostic(value: Any) -> dict[str, Any] | str:
    if isinstance(value, BaseException):
        return {"type": value.__class__.__name__, "message": str(value)[:240]}
    if isinstance(value, dict):
        return {
            "status_code": value.get("status_code"),
            "status": value.get("status"),
            "error_type": value.get("error_type"),
        }
    return str(value)[:240]


def build_provider_manifest(
    tool_definitions: Iterable[dict[str, Any]],
    credential_specs: dict[str, Any] | None = None,
    environment: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Project credential specs to names/booleans and require mappings."""
    try:
        from tooluniverse.config_env import ToolUniverseConfig

        specs = credential_specs or ToolUniverseConfig.CREDENTIAL_SPECS
    except ImportError:
        specs = credential_specs or {}
    environment = environment or os.environ
    tools = list(tool_definitions)
    manifest = []
    for env_name, spec in sorted(specs.items()):
        service = spec.get("service", env_name) if isinstance(spec, dict) else env_name
        category = spec.get("category") if isinstance(spec, dict) else None
        matches = [
            str(tool.get("name"))
            for tool in tools
            if category
            and category.lower() in json.dumps(tool, sort_keys=True).lower()
            or service.lower() in json.dumps(tool, sort_keys=True).lower()
        ]
        configured = bool(environment.get(env_name))
        manifest.append(
            {
                "credential_name": env_name,
                "service": service,
                "category": category,
                "configured": configured,
                "selected_tools": sorted(set(matches))[:3],
                "blocking": configured and not matches,
            }
        )
    return {
        "providers": manifest,
        "configured_families": [
            item["credential_name"] for item in manifest if item["configured"]
        ],
        "value_free": True,
    }


def select_catalog_sample(
    tool_definitions: Iterable[dict[str, Any]],
    fork_oid: str,
    categories: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Choose one stable representative per category using SHA-256 scoring."""
    tools = [tool for tool in tool_definitions if tool.get("name")]
    grouped: dict[str, list[dict[str, Any]]] = {}
    for tool in tools:
        category = str(tool.get("category") or tool.get("type") or "uncategorized")
        grouped.setdefault(category, []).append(tool)
    if categories is not None:
        grouped = {
            category: grouped[category]
            for category in sorted(set(categories))
            if category in grouped
        }
    choices = {}
    for category, candidates in sorted(grouped.items()):
        eligible = sorted(candidates, key=lambda item: str(item["name"]))
        scored = [
            (
                hashlib.sha256(
                    f"{fork_oid}{category}{item['name']}".encode()
                ).hexdigest(),
                str(item["name"]),
            )
            for item in eligible
        ]
        choices[category] = min(scored)[1]
    return {
        "seed": fork_oid,
        "candidate_counts": {key: len(value) for key, value in sorted(grouped.items())},
        "choices": choices,
        "tier": "catalog_category",
    }


def _canonical_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _contains_secret(path: Path, secrets: Iterable[str]) -> bool:
    data = path.read_bytes()
    return any(secret and secret.encode() in data for secret in secrets)


def publish_evidence(
    evidence: dict[str, Any],
    output_root: Path | str,
    secrets: Iterable[str] = (),
    required_stages: Iterable[str] = (),
    worktree_root: Path | str | None = None,
) -> Path:
    """Validate and atomically publish a canonical evidence tree."""
    output = Path(output_root).expanduser().resolve()
    if worktree_root is not None:
        worktree = Path(worktree_root).expanduser().resolve()
        if output == worktree or worktree in output.parents:
            raise EvidencePublicationError(
                "output root must be outside the isolated worktree"
            )
    if output.exists() and output.is_symlink():
        raise EvidencePublicationError("output root must not be a symlink")
    if any(part.is_symlink() for part in [output, *output.parents]):
        raise EvidencePublicationError("output path contains symlink component")
    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="baseline-", dir=output.parent))
    try:
        for name, value in sorted(evidence.items()):
            target = stage / (name if name.endswith(".json") else f"{name}.json")
            target.parent.mkdir(parents=True, exist_ok=True)
            _canonical_json(target, value)
        stages = evidence.get("stages", {})
        missing = sorted(set(required_stages) - set(stages))
        if missing or any(stages.get(name) != "green" for name in required_stages):
            raise EvidencePublicationError(
                f"required stages incomplete: {missing or required_stages}"
            )
        for path in stage.rglob("*"):
            if path.is_file() and _contains_secret(path, secrets):
                raise EvidencePublicationError(
                    f"credential canary found in {path.name}"
                )
        entries = []
        for path in sorted(p for p in stage.rglob("*") if p.is_file()):
            rel = path.relative_to(stage).as_posix()
            entries.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {rel}")
        (stage / "SHA256SUMS").write_text("\n".join(entries) + "\n", encoding="utf-8")
        if output.exists():
            if output.is_dir() and any(output.iterdir()):
                raise EvidencePublicationError("output root must be empty")
            if output.is_file():
                raise EvidencePublicationError("output root is a file")
            output.rmdir()
        stage.rename(output)
        return output
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def verify_checksums(bundle_root: Path | str) -> bool:
    """Verify every sorted SHA256SUMS entry and reject missing/extra artifacts."""
    root = Path(bundle_root).expanduser().resolve()
    manifest = root / "SHA256SUMS"
    if not manifest.is_file():
        raise EvidencePublicationError("SHA256SUMS is missing")
    entries = []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, separator, relative = line.partition("  ")
        if (
            not separator
            or len(digest) != 64
            or any(char not in "0123456789abcdef" for char in digest.lower())
        ):
            raise EvidencePublicationError("malformed SHA256SUMS entry")
        path = (root / relative).resolve()
        if root not in path.parents or not path.is_file() or relative == "SHA256SUMS":
            raise EvidencePublicationError(
                "checksum path escapes bundle or names manifest"
            )
        entries.append((relative, digest))
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise EvidencePublicationError(f"checksum mismatch: {relative}")
    expected = sorted(
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and path.name != "SHA256SUMS"
    )
    if [relative for relative, _ in entries] != expected:
        raise EvidencePublicationError(
            "SHA256SUMS does not cover exactly the evidence files"
        )
    return True


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--worktree-dir", required=True)
    parser.add_argument("--output-dir")
    parser.add_argument("--ci-evidence")
    parser.add_argument("--publish-root")
    parser.add_argument("--result-json")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        validate_capture_mode(args)
        repo = Path(args.repo).resolve()
        before = capture_git_snapshot(repo)
        worktree = create_isolated_worktree(repo, before["head"], args.worktree_dir)
        try:
            evidence = {
                "initial_checkout": before,
                "isolated_checkout": capture_git_snapshot(worktree),
            }
            if before.get("upstream_local_oid"):
                evidence["preservation"] = collect_preservation_inventory(
                    repo, before["upstream_local_oid"], before["head"]
                )
            if args.output_dir:
                output = Path(args.output_dir).resolve()
                output.mkdir(parents=True, exist_ok=True)
                (output / "git.json").write_text(
                    json.dumps(evidence, indent=2, sort_keys=True) + "\n"
                )
            else:
                ci = collect_ci_evidence(repo, before["head"])
                ci_path = Path(args.ci_evidence).resolve()
                ci_path.parent.mkdir(parents=True, exist_ok=True)
                ci_path.write_text(json.dumps(ci, indent=2, sort_keys=True) + "\n")
                evidence["ci"] = ci
                output = Path(args.publish_root).resolve() / before["head"]
                publish_evidence(evidence, output, worktree_root=worktree)
                result_path = Path(args.result_json).resolve()
                result_path.parent.mkdir(parents=True, exist_ok=True)
                result_path.write_text(
                    json.dumps({"fork_oid": before["head"], "output_dir": str(output)}, sort_keys=True) + "\n"
                )
        finally:
            run_git(["worktree", "remove", "--force", str(worktree)], repo)
        after = capture_git_snapshot(repo)
        if (
            before["head"] != after["head"]
            or before["status_records"] != after["status_records"]
        ):
            raise GitCaptureError("original checkout changed during capture")
        return 0
    except (GitCaptureError, ValueError, FileExistsError) as exc:
        parser.error(str(exc))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
