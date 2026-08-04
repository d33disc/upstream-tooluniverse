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
from pathlib import Path
from typing import Any, Iterable

PR161_MERGE = "16af425c053c306a658c96e254b4c4114338dd11"
PRESERVATION_CLASSES = (
    "custom_code", "tool_definition", "plugin_asset", "skill", "test",
    "workflow", "documentation", "generated_asset", "planning",
    "other_review_required",
)
FINAL_FLAGS = ("ci_evidence", "publish_root", "result_json")


class BaselineValidationError(ValueError):
    """A probe result or evidence bundle violates the baseline contract."""


class RetryExhaustedError(RuntimeError):
    """A retryable probe failed on every bounded attempt."""


class EvidencePublicationError(ValueError):
    """Evidence cannot be published safely or completely."""


class GitCaptureError(RuntimeError):
    """A Git command or invariant failed while capturing evidence."""


def run_git(argv: Iterable[str], cwd: Path | str, timeout: float = 60.0) -> str:
    """Run Git with an argv-only boundary and return stdout."""
    args = ["git", *map(str, argv)]
    try:
        proc = subprocess.run(
            args, cwd=os.fspath(cwd), capture_output=True, text=False,
            timeout=timeout, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise GitCaptureError(f"git command failed: {' '.join(args)}: {exc}") from exc
    if proc.returncode:
        stderr = proc.stderr.decode("utf-8", "replace").strip()
        raise GitCaptureError(f"git command failed ({proc.returncode}): {' '.join(args)}: {stderr}")
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
    branch = run_git(["symbolic-ref", "--quiet", "--short", "HEAD"], root).strip() if _symbolic(root) else None
    status_raw = run_git(["status", "--porcelain=v2", "-z", "--branch", "--untracked-files=all"], root)
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
        raise GitCaptureError("blocking upstream ref mismatch: local upstream/main differs from ls-remote")
    merge_base = None
    divergence = None
    if upstream_local:
        merge_base = _oid(root, f"merge-base HEAD {upstream_local}") if False else run_git(["merge-base", "HEAD", upstream_local], root).strip()
        counts = run_git(["rev-list", "--left-right", "--count", f"HEAD...{upstream_local}"], root).split()
        divergence = {"fork_only": int(counts[0]), "upstream_only": int(counts[1])}
    pr161_ancestor = False
    if upstream_local:
        proc = subprocess.run(["git", "merge-base", "--is-ancestor", PR161_MERGE, upstream_local], cwd=root, capture_output=True, timeout=60, check=False)
        pr161_ancestor = proc.returncode == 0
    return {
        "repo": str(root), "head": head, "branch": branch, "detached": branch is None,
        "status_records": _nul_records(status_raw), "staged_records": _nul_records(staged_raw),
        "unstaged_records": _nul_records(unstaged_raw), "untracked_paths": untracked,
        "upstream_local_oid": upstream_local, "upstream_remote_oid": upstream_remote,
        "merge_base": merge_base, "divergence": divergence,
        "pr161_merge_oid": PR161_MERGE, "pr161_ancestor": pr161_ancestor,
    }


def _symbolic(repo: Path) -> bool:
    proc = subprocess.run(["git", "symbolic-ref", "--quiet", "HEAD"], cwd=repo, capture_output=True, timeout=60, check=False)
    return proc.returncode == 0


def create_isolated_worktree(repo: Path | str, fork_oid: str, worktree_dir: Path | str) -> Path:
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
    """Enforce the disposable-only parser contract for Plan 01-01."""
    if not args.repo or not args.worktree_dir:
        raise ValueError("--repo and --worktree-dir are required")
    supplied = [name for name in FINAL_FLAGS if getattr(args, name, None)]
    if supplied:
        raise ValueError("final-publication flags are reserved for Plan 01-04")
    if not args.output_dir:
        raise ValueError("--output-dir is required in disposable mode")
    repo = Path(args.repo).resolve()
    worktree = Path(args.worktree_dir).resolve()
    output = Path(args.output_dir).resolve()
    if output == worktree or worktree in output.parents:
        raise ValueError("output directory must be outside isolated worktree")
    if output == repo or repo in output.parents:
        raise ValueError("output directory must not be inside original checkout")


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
    if p == "TOOL_MANIFEST.json" or p == "uv.lock" or "_lazy_registry_static" in p or "embedding" in p.lower() or p.startswith("src/tooluniverse/") and p.endswith("_generated.py"):
        return "generated_asset"
    if p.startswith("tools/") or p.startswith("tooluniverse/") or p.startswith("src/tooluniverse/tool_"):
        return "tool_definition"
    if p.startswith("src/") or p.startswith("scripts/"):
        return "custom_code"
    return "other_review_required"


def inspect_symlink(repo: Path | str, index_record: dict[str, Any]) -> dict[str, Any]:
    root = Path(repo).resolve()
    path = root / index_record["path"]
    target = os.readlink(path) if path.is_symlink() else None
    lexical = (path.parent / target).resolve(strict=False) if target is not None else None
    in_repo = bool(lexical and (lexical == root or root in lexical.parents))
    return {
        "mode": index_record.get("mode", "120000"), "blob_oid": index_record.get("blob_oid"),
        "link_text": target, "lexical_target": str(lexical) if lexical else None,
        "in_repo": in_repo, "exists": bool(lexical and lexical.exists()),
        "tracked": bool(lexical and run_git(["ls-files", "--error-unmatch", str(lexical.relative_to(root))], root).strip()) if in_repo and lexical.exists() else False,
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


def collect_preservation_inventory(repo: Path | str, upstream_oid: str, fork_oid: str) -> dict[str, Any]:
    root = Path(repo).resolve()
    raw = run_git(["diff", "--raw", "-z", "--find-renames", upstream_oid, fork_oid], root)
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
        item = {"path": path, "old_mode": old_mode, "new_mode": new_mode, "old_oid": old_oid, "new_oid": new_oid, "status": status, "class": classify_preservation_path(path), "must_survive": "fork delta retained pending staged synchronization"}
        if new_mode == "120000" and (root / path).is_symlink():
            item["symlink"] = inspect_symlink(root, {"path": path, "mode": new_mode, "blob_oid": new_oid})
        paths.append(item)
    untracked = []
    for path in run_git(["ls-files", "--others", "--exclude-standard", "-z"], root).split("\0"):
        if path:
            untracked.append({"path": path, "metadata_only": True, "class": "other_review_required" if path.startswith("ralph-specs/") else classify_preservation_path(path), "must_survive": "user-owned untracked path; contents intentionally not read"})
    blockers = [p for p in paths if p["class"] == "other_review_required"] + [p for p in paths if p.get("symlink", {}).get("blocking")]
    return {"upstream_oid": upstream_oid, "fork_oid": fork_oid, "paths": paths, "untracked": untracked, "blocking": bool(blockers), "blockers": blockers}


def prove_plugin_link_mapping(repo: Path | str, authoritative_oid: str, mappings: dict[str, str]) -> dict[str, Any]:
    root = Path(repo).resolve()
    run_git(["merge-base", "--is-ancestor", PR161_MERGE, authoritative_oid], root)
    for target in mappings.values():
        tree = run_git(["ls-tree", "-r", "--name-only", authoritative_oid, target], root)
        if not tree.strip():
            raise GitCaptureError(f"authoritative target is absent: {target}")
    siblings = [p for p in root.joinpath("plugin/skills").iterdir() if p.is_symlink()]
    if not any(os.readlink(p).startswith("../../skills/") for p in siblings):
        raise GitCaptureError("no conforming sibling plugin link")
    return {"authoritative_oid": authoritative_oid, "pr161_merge_oid": PR161_MERGE, "mappings": mappings, "proven": True}


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
    return len(path) == len(pattern) and all(a == b or b == "*" for a, b in zip(path, pattern))


def normalize_probe_result(value: Any, volatile_paths: Iterable[str | Iterable[Any]] = (), unordered_arrays: dict[str, str] | Iterable[str | Iterable[Any]] = ()) -> Any:
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
            key = next((identity for pattern, identity in unordered.items() if _path_matches(path, pattern)), None)
            if key:
                try:
                    result.sort(key=lambda child: (str(child.get(key)), json.dumps(child, sort_keys=True, default=str)))
                except (AttributeError, TypeError):
                    raise BaselineValidationError(f"unordered array at {path} must contain mapping items")
            return result
        if item is None or isinstance(item, (str, int, float, bool)):
            return item
        raise BaselineValidationError(f"result is not JSON serializable at {path}")

    return walk(value, ())


def _type_matches(value: Any, expected: str | type) -> bool:
    if isinstance(expected, type):
        return isinstance(value, expected) and not (expected is int and isinstance(value, bool))
    return {"object": dict, "array": list, "string": str, "number": (int, float), "integer": int, "boolean": bool, "null": type(None)}.get(expected, object) is type(value) or (expected == "number" and isinstance(value, (int, float)) and not isinstance(value, bool))


def validate_probe_invariants(spec: dict[str, Any], raw: Any, normalized: Any, expected: dict[str, Any] | None = None) -> dict[str, Any]:
    """Validate schema/status/domain invariants and return a typed outcome."""
    if not isinstance(normalized, dict) or not isinstance(raw, dict):
        raise BaselineValidationError("probe result must be a JSON object")
    if json.dumps(normalized, sort_keys=True, ensure_ascii=False) is None:
        raise BaselineValidationError("probe result is not JSON serializable")
    status = normalized.get("status", "success" if "data" in normalized else "error" if "error" in normalized else None)
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
                raise BaselineValidationError(f"missing invariant path: {path}") from exc
        if actual != wanted:
            raise BaselineValidationError(f"invariant drift at {path}: {actual!r} != {wanted!r}")
    for check in expected.get("checks", ()):
        if not check(normalized):
            raise BaselineValidationError("domain invariant failed")
    return {"status": status, "valid": True, "normalized": normalized}


def classify_retryable(outcome: Any) -> bool:
    """Classify transient failures without retrying auth/schema/domain errors."""
    status = outcome if isinstance(outcome, int) else outcome.get("status_code") if isinstance(outcome, dict) else getattr(outcome, "status_code", None)
    if status in {408, 429, 500, 502, 503, 504}:
        return True
    if isinstance(outcome, (TimeoutError, ConnectionError, TimeoutError)):
        return True
    if isinstance(outcome, BaseException):
        return outcome.__class__.__name__.lower() in {"timeouterror", "connectionerror", "connecterror"}
    return False


def run_with_retry(run_once, sleep=time.sleep, attempts: int = 3, delay: float = 2.0) -> Any:
    """Run a probe at most three times, with exactly fixed-delay retries."""
    if attempts != 3:
        raise ValueError("baseline retry policy requires exactly three attempts")
    diagnostics = []
    for attempt in range(1, attempts + 1):
        try:
            result = run_once()
        except Exception as exc:  # provider exceptions are evidence, not leaks
            result = exc
        diagnostics.append({"attempt": attempt, "retryable": classify_retryable(result), "outcome": _safe_diagnostic(result)})
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
        return {"status_code": value.get("status_code"), "status": value.get("status"), "error_type": value.get("error_type")}
    return str(value)[:240]


def build_provider_manifest(tool_definitions: Iterable[dict[str, Any]], credential_specs: dict[str, Any] | None = None, environment: dict[str, str] | None = None) -> dict[str, Any]:
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
        matches = [str(tool.get("name")) for tool in tools if category and category.lower() in json.dumps(tool, sort_keys=True).lower() or service.lower() in json.dumps(tool, sort_keys=True).lower()]
        configured = bool(environment.get(env_name))
        manifest.append({"credential_name": env_name, "service": service, "category": category, "configured": configured, "selected_tools": sorted(set(matches))[:3], "blocking": configured and not matches})
    return {"providers": manifest, "configured_families": [item["credential_name"] for item in manifest if item["configured"]], "value_free": True}


def select_catalog_sample(tool_definitions: Iterable[dict[str, Any]], fork_oid: str, categories: Iterable[str] | None = None) -> dict[str, Any]:
    """Choose one stable representative per category using SHA-256 scoring."""
    tools = [tool for tool in tool_definitions if tool.get("name")]
    grouped: dict[str, list[dict[str, Any]]] = {}
    for tool in tools:
        category = str(tool.get("category") or tool.get("type") or "uncategorized")
        grouped.setdefault(category, []).append(tool)
    if categories is not None:
        grouped = {category: grouped[category] for category in sorted(set(categories)) if category in grouped}
    choices = {}
    for category, candidates in sorted(grouped.items()):
        eligible = sorted(candidates, key=lambda item: str(item["name"]))
        scored = [(hashlib.sha256(f"{fork_oid}{category}{item['name']}".encode()).hexdigest(), str(item["name"])) for item in eligible]
        choices[category] = min(scored)[1]
    return {"seed": fork_oid, "candidate_counts": {key: len(value) for key, value in sorted(grouped.items())}, "choices": choices, "tier": "catalog_category"}


def _canonical_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _contains_secret(path: Path, secrets: Iterable[str]) -> bool:
    data = path.read_bytes()
    return any(secret and secret.encode() in data for secret in secrets)


def publish_evidence(evidence: dict[str, Any], output_root: Path | str, secrets: Iterable[str] = (), required_stages: Iterable[str] = ()) -> Path:
    """Validate and atomically publish a canonical evidence tree."""
    output = Path(output_root).expanduser().resolve()
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
            raise EvidencePublicationError(f"required stages incomplete: {missing or required_stages}")
        for path in stage.rglob("*"):
            if path.is_file() and _contains_secret(path, secrets):
                raise EvidencePublicationError(f"credential canary found in {path.name}")
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
            evidence = {"initial_checkout": before, "isolated_checkout": capture_git_snapshot(worktree)}
            if before.get("upstream_local_oid"):
                evidence["preservation"] = collect_preservation_inventory(repo, before["upstream_local_oid"], before["head"])
            output = Path(args.output_dir).resolve()
            output.mkdir(parents=True, exist_ok=True)
            (output / "git.json").write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
        finally:
            run_git(["worktree", "remove", "--force", str(worktree)], repo)
        after = capture_git_snapshot(repo)
        if before["head"] != after["head"] or before["status_records"] != after["status_records"]:
            raise GitCaptureError("original checkout changed during capture")
        return 0
    except (GitCaptureError, ValueError, FileExistsError) as exc:
        parser.error(str(exc))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
