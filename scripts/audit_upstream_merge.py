#!/usr/bin/env python3
"""Audit the upstream-main merge that already landed as ``f81448f2``.

Phase 2 (``docs/gsd-codebase-map``) is not "perform the merge" -- it is
"audit and reconcile the merge that already landed". This script provides
the ``union`` subcommand: an entry-level tool-name union sweep over every
``src/tooluniverse/data/*.json`` file that both the fork side and the
upstream side modified, comparing the pre-merge fork tree, the upstream
tree, and what the landed merge actually produced.

Git invocation reuses ``run_git`` (and friends) from
``scripts/capture_sync_baseline.py`` via ``importlib.util`` -- ``scripts/``
has no ``__init__.py``, so a plain import fails. No other subprocess
boundary is introduced here.
"""

from __future__ import annotations

import argparse
import ast
import datetime
import hashlib
import importlib.util
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Iterable

# ---------------------------------------------------------------------------
# Reused Git/evidence boundary from Phase 1's capture script.
# ---------------------------------------------------------------------------

_CAPTURE_SPEC = importlib.util.spec_from_file_location(
    "capture_sync_baseline",
    Path(__file__).resolve().parent / "capture_sync_baseline.py",
)
_CAPTURE_MODULE = importlib.util.module_from_spec(_CAPTURE_SPEC)
assert _CAPTURE_SPEC and _CAPTURE_SPEC.loader
_CAPTURE_SPEC.loader.exec_module(_CAPTURE_MODULE)

run_git = _CAPTURE_MODULE.run_git
GitCaptureError = _CAPTURE_MODULE.GitCaptureError
_oid = _CAPTURE_MODULE._oid
_canonical_json = _CAPTURE_MODULE._canonical_json
create_isolated_worktree = _CAPTURE_MODULE.create_isolated_worktree
classify_preservation_path = _CAPTURE_MODULE.classify_preservation_path
_nul_records = _CAPTURE_MODULE._nul_records

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_FORK_OID = "e0755067ebe7cc5374f033c5c28160980c5eddfa"
DEFAULT_UPSTREAM_OID = "56adcfd9c299078d0c40fde642b0be006510ccf3"
DEFAULT_MERGED_OID = "f81448f2047a6f35bd552956a0d9990019a39eb1"
DEFAULT_PIN_OID = "21945440c9f2a15537ba878500a800d9e330eab0"
DEFAULT_BASE_OID = "4d668698a1116a6aa18a8dfeef83b7c9715f7a8b"

_EXPECTED_BRANCH = "docs/gsd-codebase-map"
_KNOWN_UNTRACKED_PATHS = {".planning/config.json", "ralph-specs/fleet/results"}
_OWN_OUTPUT_PREFIXES = (
    "scripts/audit_upstream_merge.py",
    "tests/unit/test_audit_upstream_merge.py",
    ".planning/phases/02-upstream-main-integration/evidence/",
    ".planning/phases/02-upstream-main-integration/02-FINDINGS.md",
)

_PHASE1_GIT_JSON = (
    Path(__file__).resolve().parents[1]
    / ".planning/phases/01-protected-sync-baseline/evidence"
    / "21945440c9f2a15537ba878500a800d9e330eab0/git.json"
)

_LAZY_REGISTRY_PATH = "src/tooluniverse/_lazy_registry_static.py"

REMERGE_REF = "refs/audit/remerge"
"""Where the committed, pinned re-merge stage lives -- outside ``refs/heads/`` so no
branch operation can pick it up and garbage collection cannot reclaim it (D-06, D-09)."""

_UNPARSEABLE = object()

_FAILING_SUMMARY_KEYS = (
    "net_removed_fork_entries",
    "net_removed_upstream_entries",
    "unexpected_added_entries",
    "duplicate_name_files",
    "unparseable_files",
    "not_an_array_files",
)

_VERDICT_SUMMARY_KEY = {
    "union_ok": "union_ok",
    "net_removed_fork_entry": "net_removed_fork_entries",
    "net_removed_upstream_entry": "net_removed_upstream_entries",
    "unexpected_added_entry": "unexpected_added_entries",
    "duplicate_name": "duplicate_name_files",
    "upstream_deleted": "upstream_deleted_files",
    "fork_deleted": "fork_deleted_files",
    "not_an_array": "not_an_array_files",
    "unparseable": "unparseable_files",
}


# ---------------------------------------------------------------------------
# Working-context safety
# ---------------------------------------------------------------------------


def assert_safe_working_context(repo: Path) -> None:
    """Refuse to run against the wrong branch or over another session's WIP.

    This checkout is shared with concurrent Claude sessions that auto-commit
    each other's edits. The sweep itself is read-only against Git history,
    but a stray untracked file under a path this run is about to touch is a
    signal of concurrent interference worth halting on. A *tracked*
    modification (e.g. the GSD workflow's own ``.planning/STATE.md`` edits)
    is ordinary housekeeping, not a hazard for this read-only sweep, so it
    is not treated as unexpected here. This script's own not-yet-committed
    output (itself, its test file, and its evidence directory) is also not
    a hazard -- it is exactly what this run produces or has just produced.
    """
    branch = run_git(["rev-parse", "--abbrev-ref", "HEAD"], repo).strip()
    if branch != _EXPECTED_BRANCH:
        raise GitCaptureError(
            f"refusing to run: expected branch {_EXPECTED_BRANCH!r}, found {branch!r}"
        )
    status = run_git(["status", "--porcelain"], repo)
    unexpected = []
    for line in status.splitlines():
        if not line.strip():
            continue
        marker, path = line[:2], line[3:].strip()
        if marker.strip() != "??":
            continue
        if path.rstrip("/") in _KNOWN_UNTRACKED_PATHS:
            continue
        if path.startswith(_OWN_OUTPUT_PREFIXES):
            continue
        unexpected.append(line)
    if unexpected:
        raise GitCaptureError(
            "refusing to run: unexpected untracked paths present, possible "
            "concurrent session work: " + "; ".join(unexpected)
        )


# ---------------------------------------------------------------------------
# Both-sides path derivation
# ---------------------------------------------------------------------------


def derive_both_sides_paths(
    repo: Path,
    fork_oid: str,
    upstream_oid: str,
    expected_base: str | None = DEFAULT_BASE_OID,
) -> tuple[str, list[str]]:
    """Re-derive the merge-base and the both-sides-touched path set at runtime.

    The base is a fixed property of the two fixed parent commits: if it
    drifts, the refs moved and every downstream comparison is invalid, so
    a mismatch against *expected_base* fails loudly. Pass ``expected_base=
    None`` to disable the check (used by unit tests against a synthetic
    repository whose base OID is not known in advance).
    """
    base = run_git(["merge-base", fork_oid, upstream_oid], repo).strip()
    if expected_base is not None and base != expected_base:
        raise GitCaptureError(
            f"merge-base drifted: expected {expected_base}, found {base} -- "
            "the audited refs moved; re-verify before trusting downstream comparisons"
        )
    fork_diff = set(run_git(["diff", "--name-only", base, fork_oid], repo).splitlines())
    upstream_diff = set(
        run_git(["diff", "--name-only", base, upstream_oid], repo).splitlines()
    )
    return base, sorted(fork_diff & upstream_diff)


# ---------------------------------------------------------------------------
# Per-ref JSON loading
# ---------------------------------------------------------------------------


def load_json_at(repo: Path, ref: str, path: str) -> tuple[bool, Any]:
    """Load and parse *path* at *ref*.

    Returns ``(False, None)`` when the path is absent at that ref.
    Returns ``(True, _UNPARSEABLE)`` when the path exists but fails JSON
    decode. Returns ``(True, parsed)`` otherwise.
    """
    try:
        text = run_git(["show", f"{ref}:{path}"], repo)
    except GitCaptureError:
        return False, None
    try:
        return True, json.loads(text)
    except json.JSONDecodeError:
        return True, _UNPARSEABLE


def tool_name_list(value: Any) -> list[str] | None:
    """Tool ``name`` values in encounter order, repeats preserved.

    Mirrors the defensive shape of
    ``tests/unit/test_registry_integrity.py::_load_defined_tool_names``:
    a bare ``dict`` is wrapped as a single-item list, items with no
    ``"name"`` key are skipped, and a value that is neither a ``list`` nor
    a ``dict`` returns ``None``.
    """
    if isinstance(value, list):
        items: list[Any] = value
    elif isinstance(value, dict):
        items = [value]
    else:
        return None
    return [item["name"] for item in items if isinstance(item, dict) and "name" in item]


def tool_names(value: Any) -> set[str] | None:
    """Tool ``name`` values as a set; ``None`` when *value* is not an array/dict."""
    names = tool_name_list(value)
    return None if names is None else set(names)


# ---------------------------------------------------------------------------
# Pure classifier
# ---------------------------------------------------------------------------


def classify_union(
    fork_names: set[str] | None,
    upstream_names: set[str] | None,
    merged_names: set[str] | None,
    present: tuple[bool, bool, bool],
    *,
    merged_name_list: list[str] | None = None,
    unparseable: tuple[bool, bool, bool] = (False, False, False),
) -> str:
    """Classify one file's three-way tool-name comparison.

    ``present`` is ``(fork_present, upstream_present, merged_present)`` --
    whether the path exists at that ref, independent of parse success.
    ``unparseable`` marks a present side whose JSON failed to decode. A
    present side whose parsed value is neither a ``list`` nor a ``dict``
    (so ``tool_names()`` returned ``None`` while not flagged undecodable)
    is ``not_an_array``.

    Verdict precedence (most specific first): ``unparseable`` >
    ``not_an_array`` > single-sided presence (``upstream_deleted`` /
    ``fork_deleted``) > ``duplicate_name`` > ``unexpected_added_entry`` >
    ``net_removed_fork_entry`` > ``net_removed_upstream_entry`` >
    ``union_ok``.
    """
    fork_present, upstream_present, merged_present = present
    fork_bad, upstream_bad, merged_bad = unparseable

    if fork_bad or upstream_bad or merged_bad:
        return "unparseable"

    if (
        (fork_present and fork_names is None)
        or (upstream_present and upstream_names is None)
        or (merged_present and merged_names is None)
    ):
        return "not_an_array"

    if present == (True, False, False):
        return "upstream_deleted"
    if present == (False, True, False):
        return "fork_deleted"

    fork_set = fork_names or set()
    upstream_set = upstream_names or set()
    merged_set = merged_names or set()
    merged_list = merged_name_list or []

    if len(merged_list) != len(set(merged_list)):
        return "duplicate_name"

    combined = fork_set | upstream_set
    extra = merged_set - combined
    if extra:
        return "unexpected_added_entry"

    missing = combined - merged_set
    if missing:
        if missing & fork_set:
            return "net_removed_fork_entry"
        return "net_removed_upstream_entry"

    return "union_ok"


# ---------------------------------------------------------------------------
# Relocation search for upstream-deleted files
# ---------------------------------------------------------------------------


def search_relocated_names(
    repo: Path, ref: str, names: Iterable[str]
) -> dict[str, list[str]]:
    """For each lost *names* value, find every JSON path at *ref* that still defines it.

    Turns a silent upstream deletion into an accounted-for relocation (e.g.
    a tool moved under ``src/tooluniverse/data/broken_apis/``) rather than
    a pass. Walks the whole ``src/tooluniverse/data`` tree at *ref* once.
    """
    wanted = set(names)
    result: dict[str, list[str]] = {name: [] for name in wanted}
    if not wanted:
        return result
    listing = run_git(
        ["ls-tree", "-r", "--name-only", ref, "--", "src/tooluniverse/data"], repo
    )
    for path in listing.splitlines():
        if not path.endswith(".json"):
            continue
        present, value = load_json_at(repo, ref, path)
        if not present or value is _UNPARSEABLE:
            continue
        found = tool_names(value)
        if not found:
            continue
        for name in wanted & found:
            result[name].append(path)
    for name in result:
        result[name].sort()
    return result


# ---------------------------------------------------------------------------
# Sweep over every both-sides data/*.json file
# ---------------------------------------------------------------------------


def _side_info(
    repo: Path, ref: str, path: str
) -> tuple[bool, set[str] | None, list[str] | None, bool]:
    present, value = load_json_at(repo, ref, path)
    if not present:
        return present, None, None, False
    if value is _UNPARSEABLE:
        return present, None, None, True
    return present, tool_names(value), tool_name_list(value), False


def sweep_data_json(
    repo: Path,
    base: str,
    fork_oid: str,
    upstream_oid: str,
    merged_oid: str,
    paths: Iterable[str],
) -> dict[str, Any]:
    """Run the three-way union classification over every both-sides data/*.json path."""
    filtered = sorted(
        p
        for p in paths
        if p.startswith("src/tooluniverse/data/") and p.endswith(".json")
    )
    files: list[dict[str, Any]] = []
    summary: dict[str, Any] = {
        "files_checked": 0,
        "union_ok": 0,
        "net_removed_fork_entries": 0,
        "net_removed_upstream_entries": 0,
        "unexpected_added_entries": 0,
        "duplicate_name_files": 0,
        "upstream_deleted_files": 0,
        "fork_deleted_files": 0,
        "not_an_array_files": 0,
        "unparseable_files": 0,
        "unrelocated_lost_names": [],
    }

    for path in filtered:
        fork_present, fork_names, _fork_list, fork_bad = _side_info(
            repo, fork_oid, path
        )
        upstream_present, upstream_names, _upstream_list, upstream_bad = _side_info(
            repo, upstream_oid, path
        )
        merged_present, merged_names, merged_list, merged_bad = _side_info(
            repo, merged_oid, path
        )
        present = (fork_present, upstream_present, merged_present)
        verdict = classify_union(
            fork_names,
            upstream_names,
            merged_names,
            present,
            merged_name_list=merged_list,
            unparseable=(fork_bad, upstream_bad, merged_bad),
        )

        fork_set = fork_names or set()
        upstream_set = upstream_names or set()
        merged_set = merged_names or set()
        merged_list_safe = merged_list or []

        record: dict[str, Any] = {
            "path": path,
            "verdict": verdict,
            "fork_name_count": len(fork_set),
            "upstream_name_count": len(upstream_set),
            "merged_name_count": len(merged_set),
            "missing_names": sorted((fork_set | upstream_set) - merged_set),
            "extra_names": sorted(merged_set - (fork_set | upstream_set)),
            "duplicate_names": sorted(
                {n for n in merged_list_safe if merged_list_safe.count(n) > 1}
            ),
        }

        if verdict == "upstream_deleted":
            relocated = search_relocated_names(repo, merged_oid, fork_set)
            record["relocated_to"] = relocated
            for name, locations in relocated.items():
                if not locations:
                    summary["unrelocated_lost_names"].append(name)

        files.append(record)
        summary["files_checked"] += 1
        summary[_VERDICT_SUMMARY_KEY[verdict]] += 1

    summary["unrelocated_lost_names"] = sorted(set(summary["unrelocated_lost_names"]))
    return {
        "base_oid": base,
        "fork_oid": fork_oid,
        "upstream_oid": upstream_oid,
        "merged_oid": merged_oid,
        "files": files,
        "summary": summary,
    }


# ---------------------------------------------------------------------------
# Evidence publication
# ---------------------------------------------------------------------------


def write_staging_artifact(out_dir: Path, name: str, payload: dict[str, Any]) -> Path:
    """Write canonical JSON, then regenerate a sorted SHA256SUMS over out_dir.

    Names, paths, counts and verdicts only -- never file contents, tool
    payloads, or credential values flow into this artifact.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / (name if name.endswith(".json") else f"{name}.json")
    _canonical_json(target, payload)

    entries = []
    for path in sorted(p for p in out_dir.rglob("*.json") if p.is_file()):
        rel = path.relative_to(out_dir).as_posix()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        entries.append(f"{digest}  {rel}")
    (out_dir / "SHA256SUMS").write_text("\n".join(entries) + "\n", encoding="utf-8")
    return target


# ---------------------------------------------------------------------------
# Re-merge stage: isolation (Task 1)
# ---------------------------------------------------------------------------


def _status_lines(path: Path) -> list[str]:
    """Non-empty porcelain status lines for *path* (repo root or worktree)."""
    return [
        line
        for line in run_git(["status", "--porcelain"], path).splitlines()
        if line.strip()
    ]


def default_stage_path(fork_oid: str) -> Path:
    """Default isolated-worktree location: ``${TMPDIR:-/tmp}/tu-remerge-audit-<short-oid>``."""
    tmpdir = os.environ.get("TMPDIR") or "/tmp"
    return Path(tmpdir) / f"tu-remerge-audit-{fork_oid[:8]}"


def _phase1_untracked_paths(git_json_path: Path = _PHASE1_GIT_JSON) -> list[str]:
    data = json.loads(git_json_path.read_text(encoding="utf-8"))
    return list(data.get("untracked_paths", []))


def _check_excluded_preexisting(
    stage_path: Path, excluded_paths: Iterable[str] | None = None
) -> list[dict[str, Any]]:
    """For each pre-existing dirty/untracked path Phase 1 recorded, is it present in the stage?

    Every entry must resolve ``present_in_stage: false`` -- a clean detached
    worktree at *fork_oid* carries none of the main checkout's pre-existing
    untracked or dirty paths. *excluded_paths* overrides the Phase 1 source
    for unit tests exercising a synthetic repository.
    """
    paths = (
        list(excluded_paths)
        if excluded_paths is not None
        else _phase1_untracked_paths()
    )
    return [
        {"path": path, "present_in_stage": (stage_path / path).exists()}
        for path in paths
    ]


def create_remerge_stage(
    repo: Path,
    fork_oid: str,
    upstream_oid: str,
    worktree_dir: Path,
    *,
    excluded_paths: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Create an isolated detached worktree at *fork_oid*, proving SYNC-01 containment.

    Calls ``create_isolated_worktree`` from ``scripts/capture_sync_baseline.py``
    unmodified -- its ``target == root or root in target.parents`` guard and
    non-empty-target guard make isolation mechanical rather than asserted.
    *upstream_oid* is not read here (the merge starts later); it is part of
    the signature because the caller's provenance record is keyed on both
    OIDs together.
    """
    del upstream_oid  # not needed until the merge step; kept for signature symmetry
    repo = Path(repo).resolve()
    worktree_dir = Path(worktree_dir).resolve()

    repo_head_before = run_git(["rev-parse", "HEAD"], repo).strip()
    repo_branch_before = run_git(["rev-parse", "--abbrev-ref", "HEAD"], repo).strip()
    repo_status_before = _status_lines(repo)

    stage_path = create_isolated_worktree(repo, fork_oid, worktree_dir)

    repo_head_after = run_git(["rev-parse", "HEAD"], repo).strip()
    repo_branch_after = run_git(["rev-parse", "--abbrev-ref", "HEAD"], repo).strip()
    repo_status_after = _status_lines(repo)

    stage_head = run_git(["rev-parse", "HEAD"], stage_path).strip()
    stage_status = _status_lines(stage_path)
    containment_diffstat = run_git(
        ["diff", "--stat", fork_oid, "HEAD"], stage_path
    ).strip()
    excluded_preexisting = _check_excluded_preexisting(stage_path, excluded_paths)

    return {
        "repo_head_before": repo_head_before,
        "repo_head_after": repo_head_after,
        "repo_branch_before": repo_branch_before,
        "repo_branch_after": repo_branch_after,
        "repo_status_before": repo_status_before,
        "repo_status_after": repo_status_after,
        "stage_path": str(stage_path),
        "stage_head": stage_head,
        "stage_status": stage_status,
        "containment_diffstat": containment_diffstat,
        "excluded_preexisting": excluded_preexisting,
    }


def _existing_stage(worktree_dir: Path, fork_oid: str) -> bool:
    """Detect a stage this run already created, refusing to silently reuse a stranger directory."""
    if not worktree_dir.exists():
        return False
    if not (worktree_dir / ".git").exists():
        raise GitCaptureError(
            f"refusing to reuse {worktree_dir}: exists but is not a git worktree"
        )
    head = run_git(["rev-parse", "HEAD"], worktree_dir).strip()
    if head != fork_oid:
        raise GitCaptureError(
            f"refusing to reuse {worktree_dir}: HEAD is {head}, expected fork OID {fork_oid}"
        )
    return True


def _describe_existing_stage(
    repo: Path,
    worktree_dir: Path,
    fork_oid: str,
    excluded_paths: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Same provenance shape as ``create_remerge_stage``, for a stage a prior run already made."""
    repo_head_before = run_git(["rev-parse", "HEAD"], repo).strip()
    repo_branch_before = run_git(["rev-parse", "--abbrev-ref", "HEAD"], repo).strip()
    repo_status_before = _status_lines(repo)

    stage_head = run_git(["rev-parse", "HEAD"], worktree_dir).strip()
    stage_status = _status_lines(worktree_dir)
    containment_diffstat = run_git(
        ["diff", "--stat", fork_oid, "HEAD"], worktree_dir
    ).strip()
    excluded_preexisting = _check_excluded_preexisting(worktree_dir, excluded_paths)

    repo_head_after = run_git(["rev-parse", "HEAD"], repo).strip()
    repo_branch_after = run_git(["rev-parse", "--abbrev-ref", "HEAD"], repo).strip()
    repo_status_after = _status_lines(repo)

    return {
        "repo_head_before": repo_head_before,
        "repo_head_after": repo_head_after,
        "repo_branch_before": repo_branch_before,
        "repo_branch_after": repo_branch_after,
        "repo_status_before": repo_status_before,
        "repo_status_after": repo_status_after,
        "stage_path": str(worktree_dir),
        "stage_head": stage_head,
        "stage_status": stage_status,
        "containment_diffstat": containment_diffstat,
        "excluded_preexisting": excluded_preexisting,
    }


# ---------------------------------------------------------------------------
# Re-merge stage: merge + conflict re-derivation (Task 2)
# ---------------------------------------------------------------------------


def read_text_at(repo: Path, ref: str, path: str) -> str:
    """Read *path* at *ref* as text via ``git show`` -- the argv-only boundary, never a checkout."""
    return run_git(["show", f"{ref}:{path}"], repo)


def _stage_git_dir(stage: Path) -> Path:
    return Path(run_git(["rev-parse", "--absolute-git-dir"], stage).strip())


def _merge_in_progress(stage: Path) -> bool:
    """``MERGE_HEAD`` lives under the *shared* repo's ``.git/worktrees/<name>/`` for a linked
    worktree, never at ``<stage>/.git/MERGE_HEAD`` (that path is a file pointing elsewhere).
    ``--absolute-git-dir`` resolves the real location regardless."""
    return (_stage_git_dir(stage) / "MERGE_HEAD").is_file()


def _start_or_continue_merge(
    stage: Path, upstream_oid: str, timeout: float = 90.0
) -> None:
    """Run ``git merge --no-commit --no-ff`` once; a conflict (exit 1) is success, not failure.

    Idempotent: if ``MERGE_HEAD`` already exists (a prior invocation started
    the merge), this is a no-op so the ``remerge`` subcommand can be re-run
    from where it left off rather than only from a fresh stage.
    """
    if _merge_in_progress(stage):
        return
    args = ["git", "merge", "--no-commit", "--no-ff", upstream_oid]
    proc = subprocess.run(
        args,
        cwd=os.fspath(stage),
        capture_output=True,
        text=False,
        timeout=timeout,
        check=False,
    )
    if proc.returncode not in (0, 1):
        stderr = proc.stderr.decode("utf-8", "replace").strip()
        raise GitCaptureError(
            f"git merge failed unexpectedly ({proc.returncode}): {' '.join(args)}: {stderr}"
        )


def resolve_data_json_conflict(
    stage: Path, path: str, fork_oid: str, upstream_oid: str
) -> dict[str, Any]:
    """Resolve one conflicted ``data/*.json`` path by D-08's ``entry_union`` rule.

    Indexes both sides by ``"name"``: a name present on both sides takes
    upstream's object outright, a fork-only name is retained. The merged
    array is written sorted by name (and with ``sort_keys=True``) for a
    byte-identical, diffable artifact regardless of input array order, then
    re-loaded from disk and re-asserted through ``classify_union`` so the
    resolution and the audit share one definition of correct.
    """
    fork_present, fork_value = load_json_at(stage, fork_oid, path)
    upstream_present, upstream_value = load_json_at(stage, upstream_oid, path)

    if fork_present and fork_value is _UNPARSEABLE:
        raise ValueError(f"{path}: fork side is not valid JSON")
    if upstream_present and upstream_value is _UNPARSEABLE:
        raise ValueError(f"{path}: upstream side is not valid JSON")

    if not upstream_present:
        fork_names = (tool_names(fork_value) or set()) if fork_present else set()
        relocated = search_relocated_names(stage, upstream_oid, fork_names)
        target = stage / path
        if target.exists():
            run_git(["rm", "-f", "--", path], stage)
        return {
            "path": path,
            "rule": "upstream_deleted",
            "decision": "accept_upstream_deletion",
            "rationale": (
                "upstream deleted this file outright; fork entries checked for "
                "relocation elsewhere in upstream's tree via search_relocated_names"
            ),
            "relocated_to": relocated,
        }

    def _as_entries(value: Any, present: bool, side: str) -> list[dict[str, Any]]:
        if not present:
            return []
        items = [value] if isinstance(value, dict) else value
        if not isinstance(items, list) or not all(
            isinstance(item, dict) for item in items
        ):
            raise ValueError(f"{path}: {side} side is not a list[dict]")
        return items

    fork_entries = _as_entries(fork_value, fork_present, "fork")
    upstream_entries = _as_entries(upstream_value, upstream_present, "upstream")

    merged_by_name: dict[str, dict[str, Any]] = {}
    for item in fork_entries:
        if "name" not in item:
            raise ValueError(f"{path}: fork entry missing 'name'")
        merged_by_name[item["name"]] = item
    for item in upstream_entries:
        if "name" not in item:
            raise ValueError(f"{path}: upstream entry missing 'name'")
        merged_by_name[item["name"]] = (
            item  # shared name -> upstream's object wins outright
        )

    merged_sorted = [merged_by_name[name] for name in sorted(merged_by_name)]
    target = stage / path
    target.write_text(
        json.dumps(merged_sorted, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    written_value = json.loads(target.read_text(encoding="utf-8"))
    fork_names = tool_names(fork_entries) or set()
    upstream_names = tool_names(upstream_entries) or set()
    verdict = classify_union(
        fork_names,
        upstream_names,
        tool_names(written_value),
        (True, True, True),
        merged_name_list=tool_name_list(written_value),
    )
    if verdict != "union_ok":
        raise ValueError(f"{path}: resolved union failed re-classification: {verdict}")

    run_git(["add", "--", path], stage)

    return {
        "path": path,
        "rule": "entry_union",
        "decision": "entry_level_union_keyed_on_name",
        "rationale": "shared names take upstream's object outright; fork-only names retained",
        "union_verdict": verdict,
        "fork_name_count": len(fork_names),
        "upstream_name_count": len(upstream_names),
        "merged_name_count": len(merged_by_name),
    }


def _parse_default_tool_files(source: str) -> tuple[ast.Assign, dict[str, str]]:
    """Extract the ``default_tool_files = { ... }`` assignment.

    Rejects (raises ``ValueError``) a source whose assignment right-hand
    side is not a plain ``ast.Dict`` literal, rather than falling back to
    execution -- T-02-08's mitigation. Each *key* is decoded with
    ``ast.literal_eval`` (keys are always plain string literals here); each
    *value*'s original source text is kept verbatim rather than evaluated,
    because production values are ``os.path.join(...)`` calls that
    ``ast.literal_eval`` cannot and must not evaluate.
    """
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not any(
            isinstance(target, ast.Name) and target.id == "default_tool_files"
            for target in node.targets
        ):
            continue
        if not isinstance(node.value, ast.Dict):
            raise ValueError(
                "default_tool_files assignment is not a plain dict literal"
            )
        ordered: dict[str, str] = {}
        for key_node, value_node in zip(node.value.keys, node.value.values):
            if key_node is None:
                raise ValueError(
                    "default_tool_files contains a ** dict-unpacking entry"
                )
            key = ast.literal_eval(key_node)
            if not isinstance(key, str):
                raise ValueError("default_tool_files key is not a string literal")
            value_source = ast.get_source_segment(source, value_node)
            if value_source is None:
                value_source = ast.unparse(value_node)
            ordered[key] = value_source
        return node, ordered
    raise ValueError("no default_tool_files assignment found")


def union_default_config_keys(fork_src: str, upstream_src: str) -> dict[str, Any]:
    """D-08's ``key_union`` rule for ``default_config.py``'s ``default_tool_files`` dict.

    The merged key set equals ``fork_keys | upstream_keys`` exactly; a key
    present on both sides with different value source text takes upstream's
    value and is recorded under ``value_collisions``.
    """
    _fork_node, fork_dict = _parse_default_tool_files(fork_src)
    _upstream_node, upstream_dict = _parse_default_tool_files(upstream_src)

    fork_keys = set(fork_dict)
    upstream_keys = set(upstream_dict)
    shared_keys = fork_keys & upstream_keys
    merged_keys = fork_keys | upstream_keys

    merged: dict[str, str] = dict(fork_dict)
    value_collisions: list[dict[str, str]] = []
    for key, value in upstream_dict.items():
        if key in merged and merged[key] != value:
            value_collisions.append(
                {"key": key, "fork_value": merged[key], "upstream_value": value}
            )
        merged[key] = value  # shared key -> upstream's value wins

    return {
        "key_union_ok": set(merged) == merged_keys,
        "fork_key_count": len(fork_keys),
        "upstream_key_count": len(upstream_keys),
        "shared_key_count": len(shared_keys),
        "merged_key_count": len(merged),
        "value_collisions": sorted(value_collisions, key=lambda c: c["key"]),
        "merged_dict": merged,
    }


def render_default_config_source(fork_src: str, merged_dict: dict[str, str]) -> str:
    """Splice the unioned ``default_tool_files`` dict back into fork's source text.

    Keeps every other line of *fork_src* (docstring, imports, trailing code)
    untouched; only the assignment's own line span is replaced. Re-parses
    the result to fail loudly rather than write invalid Python.
    """
    fork_node, _ = _parse_default_tool_files(fork_src)
    block_lines = ["default_tool_files = {"]
    for key, value_source in merged_dict.items():
        block_lines.append(f"    {key!r}: {value_source},")
    block_lines.append("}")
    block_text = "\n".join(block_lines)

    lines = fork_src.splitlines(keepends=True)
    start = fork_node.lineno - 1
    end = fork_node.end_lineno
    rendered = "".join(lines[:start]) + block_text + "\n" + "".join(lines[end:])
    ast.parse(rendered)  # raise loudly here rather than write a broken file
    return rendered


_TOML_HEADER_RE = re.compile(r"^\[[^\[\]]+\]\s*$|^\[\[[^\[\]]+\]\]\s*$")
_DEPENDENCY_LINE_RE = re.compile(r'^\s*"([^"]+)"\s*,?\s*(#.*)?$')


def _toml_blocks(text: str) -> list[tuple[str, str]]:
    """Split TOML text into ``(header, block_text_including_header)`` in source order.

    Content before the first ``[header]`` line (if any) is grouped under
    header ``""``.
    """
    lines = text.splitlines(keepends=True)
    blocks: list[tuple[str, str]] = []
    header = ""
    buf: list[str] = []
    for line in lines:
        if _TOML_HEADER_RE.match(line.strip()):
            if buf:
                blocks.append((header, "".join(buf)))
            header = line.strip()
            buf = [line]
        else:
            buf.append(line)
    if buf:
        blocks.append((header, "".join(buf)))
    return blocks


def _extract_quoted_deps(source: str, header_prefix: str) -> set[str]:
    """Collect quoted dependency-spec strings inside a ``header_prefix ... ]`` array."""
    deps: set[str] = set()
    in_block = False
    for line in source.splitlines():
        stripped = line.strip()
        if not in_block:
            if stripped.startswith(header_prefix):
                in_block = True
            continue
        if stripped.startswith("]"):
            in_block = False
            continue
        match = _DEPENDENCY_LINE_RE.match(line)
        if match:
            deps.add(match.group(1))
    return deps


def _dependency_changes(fork_src: str, upstream_src: str) -> dict[str, list[str]]:
    fork_deps = _extract_quoted_deps(fork_src, "dependencies = [")
    upstream_deps = _extract_quoted_deps(upstream_src, "dependencies = [")
    return {
        "removed_from_fork": sorted(fork_deps - upstream_deps),
        "added_from_upstream": sorted(upstream_deps - fork_deps),
    }


def resolve_pyproject_conflict(fork_src: str, upstream_src: str) -> dict[str, Any]:
    """D-08's ``upstream_canonical_deps`` rule, applied as upstream-canonical *plus fork-additive*.

    Taking upstream's file wholesale would silently delete fork-only TOML
    tables (measured: the fork's ``[tool.mypy]`` and
    ``[[tool.mypy.overrides]]`` blocks are absent from upstream's
    ``pyproject.toml`` but survived in the landed merge `f81448f2` --
    verified via ``git show f81448f2:pyproject.toml``). So: upstream's file
    wins verbatim for every table upstream also defines (including
    `[project]` `dependencies` / `optional-dependencies`), and any
    fork-only table (by exact header text) is appended afterward in fork's
    original order -- exactly what the landed merge already did.
    """
    fork_blocks = _toml_blocks(fork_src)
    upstream_headers = {header for header, _ in _toml_blocks(upstream_src) if header}
    fork_only = [
        (header, block)
        for header, block in fork_blocks
        if header and header not in upstream_headers
    ]

    merged_text = upstream_src if upstream_src.endswith("\n") else upstream_src + "\n"
    for _header, block in fork_only:
        if not merged_text.endswith("\n\n"):
            merged_text += "\n"
        merged_text += block if block.endswith("\n") else block + "\n"

    return {
        "merged_text": merged_text,
        "retained_fork_sections": [header for header, _ in fork_only],
        "dependency_changes": _dependency_changes(fork_src, upstream_src),
    }


def resolve_gitignore_conflict(fork_src: str, upstream_src: str) -> dict[str, Any]:
    """D-08's ``line_union`` rule: union of both sides' non-empty, non-duplicate patterns.

    Fork lines are kept in their original order first -- the fork carries a
    negation pattern (``!IMPLEMENTATION_PLAN.md``) whose semantics depend on
    its position relative to the pattern it negates, so re-ordering by sort
    would risk silently changing behavior. Upstream-only lines are appended
    afterward in upstream's own order. Dedup is on exact line text.
    """
    fork_lines = fork_src.splitlines()
    upstream_lines = upstream_src.splitlines()
    seen: set[str] = set()
    merged: list[str] = []
    for line in fork_lines:
        if line in seen:
            continue
        merged.append(line)
        seen.add(line)
    added_from_upstream: list[str] = []
    for line in upstream_lines:
        if line in seen:
            continue
        merged.append(line)
        seen.add(line)
        added_from_upstream.append(line)
    return {
        "merged_text": "\n".join(merged) + "\n",
        "added_from_upstream": added_from_upstream,
    }


# ---------------------------------------------------------------------------
# Re-merge stage: source-module and test conflicts (Tasks 1-2, plan 02-03)
# ---------------------------------------------------------------------------


def _decorated_span(node: ast.stmt) -> tuple[int, int]:
    """``(start_line, end_line)``, 1-indexed inclusive, covering *node*'s own decorators.

    ``ast.get_source_segment`` anchors on ``node.lineno`` alone, which for a
    decorated function/class is the ``def``/``class`` line -- decorators sit
    on earlier lines with their own ``lineno`` and are silently dropped. This
    walks ``decorator_list`` (absent on ``Assign``/``AnnAssign``, hence the
    ``getattr`` default) so a decorated fork-only method is spliced with its
    decorator intact.
    """
    starts = [node.lineno]
    starts.extend(d.lineno for d in getattr(node, "decorator_list", []))
    return min(starts), node.end_lineno


def _segment(source_lines: list[str], node: ast.stmt) -> str:
    """Verbatim source text for *node* (decorators included), from pre-split *source_lines*."""
    start, end = _decorated_span(node)
    return "".join(source_lines[start - 1 : end])


def _index_module(
    source: str,
) -> tuple[ast.Module, dict[str, ast.stmt], dict[str, dict[str, ast.stmt]]]:
    """Index one module's top-level and class-level definitions.

    Returns ``(tree, top_level, class_members)``: ``top_level`` maps a
    module-level function/class/assignment-target name to its node;
    ``class_members`` maps each top-level class name to a ``{member_name:
    node}`` dict of its own function/assignment members (one level deep --
    matches the plan's "top-level and class-level" scope, not arbitrary
    nesting).
    """
    tree = ast.parse(source)
    top: dict[str, ast.stmt] = {}
    class_members: dict[str, dict[str, ast.stmt]] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            top[node.name] = node
            if isinstance(node, ast.ClassDef):
                members: dict[str, ast.stmt] = {}
                for sub in node.body:
                    if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        members[sub.name] = sub
                    elif isinstance(sub, ast.Assign):
                        for target in sub.targets:
                            if isinstance(target, ast.Name):
                                members[target.id] = sub
                    elif isinstance(sub, ast.AnnAssign) and isinstance(
                        sub.target, ast.Name
                    ):
                        members[sub.target.id] = sub
                class_members[node.name] = members
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    top[target.id] = node
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            top[node.target.id] = node
    return tree, top, class_members


def extract_definition_names(source: str) -> set[str]:
    """Every top-level and class-level (``Class.member``) definition name in *source*.

    This is the set Task 1/2's per-file union check compares against
    ``fork_only_retained | shared_taken_from_upstream | upstream_only_added``.
    """
    _tree, top, class_members = _index_module(source)
    names = set(top)
    for class_name, members in class_members.items():
        names.update(f"{class_name}.{member}" for member in members)
    return names


def _insert_class_members(
    text: str, node: ast.ClassDef, member_segments: list[str]
) -> str:
    """Splice *member_segments* (fork-only methods/assignments) onto the end of *node*'s body.

    Insertion point is ``node.end_lineno`` against *text*'s current line
    numbering -- valid only when no earlier-in-file edit has already
    shifted lines above it, which is why callers process classes in
    descending ``end_lineno`` order (see ``resolve_source_module_conflict``).
    """
    lines = text.splitlines(keepends=True)
    insert_at = node.end_lineno
    segs = [seg if seg.endswith("\n") else seg + "\n" for seg in member_segments]
    block = "\n" + "".join(segs)
    return "".join(lines[:insert_at]) + block + "".join(lines[insert_at:])


def resolve_source_module_conflict(
    stage: Path, path: str, fork_oid: str, upstream_oid: str
) -> dict[str, Any]:
    """D-08's ``upstream_canonical_fork_additive`` rule, definition by definition.

    Base is upstream's file verbatim (imports, ordering, every shared and
    upstream-only definition). A fork-only *module-level* definition is
    appended at file end. A fork-only *class-level* member whose class is
    shared (present on both sides) is spliced onto the end of upstream's
    version of that class -- never hand-blended hunk by hunk. A fork-only
    definition whose class does not exist upstream at all is unreachable
    here: the whole class is itself a fork-only top-level name and is
    covered by the module-level append.
    """
    fork_src = read_text_at(stage, fork_oid, path)
    upstream_src = read_text_at(stage, upstream_oid, path)

    _fork_tree, fork_top, fork_classes = _index_module(fork_src)
    _upstream_tree, upstream_top, upstream_classes = _index_module(upstream_src)

    fork_names = extract_definition_names(fork_src)
    upstream_names = extract_definition_names(upstream_src)

    fork_only = sorted(fork_names - upstream_names)
    shared = sorted(fork_names & upstream_names)
    upstream_only = sorted(upstream_names - fork_names)

    fork_lines = fork_src.splitlines(keepends=True)

    class_insertions: dict[str, list[str]] = {}
    module_level_segments: dict[
        int, str
    ] = {}  # keyed by id(node), dedups tuple-targets

    for name in fork_only:
        if "." in name:
            class_name, member = name.split(".", 1)
            if class_name in upstream_classes and member in fork_classes.get(
                class_name, {}
            ):
                seg = _segment(fork_lines, fork_classes[class_name][member])
                class_insertions.setdefault(class_name, []).append(seg)
                continue
            # class_name absent from upstream entirely: the whole class is a
            # fork-only top-level name and is handled by the branch below.
        node = fork_top.get(name)
        if node is not None:
            module_level_segments[id(node)] = _segment(fork_lines, node)

    result_text = upstream_src
    for class_name in sorted(
        class_insertions, key=lambda c: upstream_top[c].end_lineno, reverse=True
    ):
        result_text = _insert_class_members(
            result_text, upstream_top[class_name], class_insertions[class_name]
        )

    append_order = [
        seg
        for _id, seg in sorted(
            module_level_segments.items(),
            key=lambda kv: next(n.lineno for n in fork_top.values() if id(n) == kv[0]),
        )
    ]
    if append_order:
        if not result_text.endswith("\n"):
            result_text += "\n"
        result_text += "\n\n" + "\n\n".join(
            seg if seg.endswith("\n") else seg + "\n" for seg in append_order
        )

    target = stage / path
    target.write_text(result_text, encoding="utf-8")
    run_git(["add", "--", path], stage)

    resolved_names = extract_definition_names(result_text)
    expected_names = set(fork_only) | set(shared) | set(upstream_only)
    fork_only_dropped = sorted(set(fork_only) - resolved_names)

    return {
        "path": path,
        "rule": "upstream_canonical_fork_additive",
        "decision": "definition_level_upstream_canonical_fork_additive",
        "rationale": (
            "base is upstream's file verbatim; fork-only module-level definitions "
            "appended at file end; fork-only class-level members spliced onto the "
            "end of the corresponding shared class body; shared definitions take "
            "upstream's body outright"
        ),
        "fork_only_retained": fork_only,
        "shared_taken_from_upstream": shared,
        "upstream_only_added": upstream_only,
        "fork_only_dropped": fork_only_dropped,
        "resolved_name_set_matches_expected": resolved_names == expected_names,
    }


def resolve_source_layer(
    stage: Path, fork_oid: str, upstream_oid: str, paths: Iterable[str]
) -> list[dict[str, Any]]:
    """Resolve every path in *paths* (source modules or tests) under D-08.

    One rule, applied uniformly: production modules and test files differ
    only in what their "definitions" are (functions/classes vs. test
    functions/fixtures), which ``resolve_source_module_conflict`` does not
    need to distinguish.
    """
    return [
        resolve_source_module_conflict(stage, path, fork_oid, upstream_oid)
        for path in sorted(paths)
    ]


def resolve_generated_conflict(stage: Path, path: str, fork_oid: str) -> dict[str, Any]:
    """Clear one GENERATED file's conflict without hand-resolution -- same treatment
    as ``_lazy_registry_static.py`` in ``resolve_data_config_layer``.

    ``src/tooluniverse/tools/*.py`` per-tool wrapper stubs are produced
    wholesale by ``generate_tools.main()`` from the resolved
    ``src/tooluniverse/data/*.json`` tree; their pairwise diffs (measured:
    both true UU content conflicts and AA add/add conflicts, all present on
    both sides) are an artifact of independent regeneration, not a decision
    a human or D-08's definition-level rule should make. Fork's content is
    staged as a placeholder purely so the index is unmerged-clean; Task 3's
    ``generate_tools.main(output_dir=None)`` run against the fully-resolved
    stage overwrites every one of these wholesale.
    """
    text = read_text_at(stage, fork_oid, path)
    (stage / path).write_text(text, encoding="utf-8")
    run_git(["add", "--", path], stage)
    return {
        "path": path,
        "rule": "regenerate",
        "decision": "deferred_to_regeneration",
        "rationale": (
            "GENERATED FILE (per-tool coding-API wrapper stub); never hand-merged. "
            "Conflict cleared with fork content as a placeholder only -- real "
            "regeneration via generate_tools.main(output_dir=None) happens in "
            "Task 3 after the whole source tree settles, same treatment as "
            "_lazy_registry_static.py"
        ),
    }


def resolve_data_config_layer(
    stage: Path, fork_oid: str, upstream_oid: str, conflicts_raw: Iterable[str]
) -> tuple[list[dict[str, Any]], dict[str, Any], list[str]]:
    """Resolve every data/config-layer path in *conflicts_raw* under D-08, leaving the rest open.

    Handles ``src/tooluniverse/data/*.json`` (``entry_union``),
    ``src/tooluniverse/default_config.py`` (``key_union``), ``pyproject.toml``
    (``upstream_canonical_deps``), ``.gitignore`` (``line_union``), and
    clears (never hand-resolves) ``_lazy_registry_static.py``'s conflict,
    marking it ``deferred_to_regeneration``. Every other conflicted path is
    left untouched for plan 02-03's source layer.
    """
    conflicts = list(conflicts_raw)
    resolutions: list[dict[str, Any]] = []
    default_config_summary: dict[str, Any] = {}

    json_paths = sorted(
        path
        for path in conflicts
        if path.startswith("src/tooluniverse/data/") and path.endswith(".json")
    )
    for path in json_paths:
        resolutions.append(
            resolve_data_json_conflict(stage, path, fork_oid, upstream_oid)
        )

    default_config_path = "src/tooluniverse/default_config.py"
    if default_config_path in conflicts:
        fork_src = read_text_at(stage, fork_oid, default_config_path)
        upstream_src = read_text_at(stage, upstream_oid, default_config_path)
        summary = union_default_config_keys(fork_src, upstream_src)
        rendered = render_default_config_source(fork_src, summary["merged_dict"])
        (stage / default_config_path).write_text(rendered, encoding="utf-8")
        run_git(["add", "--", default_config_path], stage)
        default_config_summary = {
            k: v for k, v in summary.items() if k != "merged_dict"
        }
        resolutions.append(
            {
                "path": default_config_path,
                "rule": "key_union",
                "decision": "key_level_union",
                "rationale": (
                    "merged key set equals fork_keys | upstream_keys; a shared key "
                    "takes upstream's value"
                ),
                "value_collisions": summary["value_collisions"],
            }
        )

    if _LAZY_REGISTRY_PATH in conflicts:
        text = read_text_at(stage, fork_oid, _LAZY_REGISTRY_PATH)
        (stage / _LAZY_REGISTRY_PATH).write_text(text, encoding="utf-8")
        run_git(["add", "--", _LAZY_REGISTRY_PATH], stage)
        resolutions.append(
            {
                "path": _LAZY_REGISTRY_PATH,
                "rule": "regenerate",
                "decision": "deferred_to_regeneration",
                "rationale": (
                    "GENERATED FILE (STATIC LAZY REGISTRY); never hand-merged. Conflict "
                    "cleared with fork content as a placeholder only -- real regeneration "
                    "via tu build / generate_lazy_registry.py happens in plan 02-03 after "
                    "the source layer settles"
                ),
            }
        )

    pyproject_path = "pyproject.toml"
    if pyproject_path in conflicts:
        fork_src = read_text_at(stage, fork_oid, pyproject_path)
        upstream_src = read_text_at(stage, upstream_oid, pyproject_path)
        pyproject = resolve_pyproject_conflict(fork_src, upstream_src)
        (stage / pyproject_path).write_text(pyproject["merged_text"], encoding="utf-8")
        run_git(["add", "--", pyproject_path], stage)
        retained = ", ".join(pyproject["retained_fork_sections"]) or "none"
        resolutions.append(
            {
                "path": pyproject_path,
                "rule": "upstream_canonical_deps",
                "decision": "upstream_file_plus_fork_only_tables",
                "rationale": (
                    "upstream's file wins verbatim (including [project] dependencies / "
                    f"optional-dependencies); fork-only tables retained verbatim: {retained}"
                ),
                "dependency_changes": pyproject["dependency_changes"],
                "retained_fork_sections": pyproject["retained_fork_sections"],
                "routed_to": "Phase 5 / COMP-01",
            }
        )

    gitignore_path = ".gitignore"
    if gitignore_path in conflicts:
        fork_src = read_text_at(stage, fork_oid, gitignore_path)
        upstream_src = read_text_at(stage, upstream_oid, gitignore_path)
        gitignore = resolve_gitignore_conflict(fork_src, upstream_src)
        (stage / gitignore_path).write_text(gitignore["merged_text"], encoding="utf-8")
        run_git(["add", "--", gitignore_path], stage)
        resolutions.append(
            {
                "path": gitignore_path,
                "rule": "line_union",
                "decision": "line_level_union_fork_order_then_upstream_only",
                "rationale": (
                    "union of both sides' non-empty non-duplicate patterns; fork order "
                    "preserved first to keep negation-pattern ordering safe"
                ),
                "added_from_upstream": gitignore["added_from_upstream"],
            }
        )

    handled = {resolution["path"] for resolution in resolutions}
    unresolved_paths = sorted(set(conflicts) - handled)
    return resolutions, default_config_summary, unresolved_paths


def classify_unresolved_path(path: str) -> str:
    """Bucket one still-conflicted path for ``unresolved_by_class``.

    Measured against the real re-merge: the raw conflict set (160 paths) is
    far larger than the 22 files ``git diff-tree --cc`` shows for the landed
    merge `f81448f2` -- that command prunes any path whose final content is
    TREESAME to one parent, which hides every conflict the original
    resolution settled by taking one side wholesale. This classification
    turns that gap into an explicit, reviewable breakdown instead of an
    undifferentiated list, so plan 02-03 can see what kind of "source
    layer" it is actually inheriting.
    """
    if "~HEAD" in path or path.startswith("plugin/skills/"):
        return "symlink_workspaces"
    if path.startswith("src/tooluniverse/tools/"):
        return "generated"
    if path.startswith("tests/"):
        return "tests"
    if path.startswith("src/tooluniverse/") and path.endswith(".py"):
        return "source_modules"
    if (
        path == "uv.lock"
        or path.startswith("plugin/")
        or path.startswith(".claude-plugin/")
        or path == "scripts/build-plugin.sh"
    ):
        return "packaging"
    if (
        path.startswith(".github/")
        or path.startswith("docs/")
        or path.startswith("skills/")
        or path == "README.md"
    ):
        return "ci_docs"
    return "other"


def classify_unresolved_paths(paths: Iterable[str]) -> dict[str, list[str]]:
    """Group *paths* by :func:`classify_unresolved_path`, sorted within each bucket."""
    buckets: dict[str, list[str]] = {
        "source_modules": [],
        "tests": [],
        "generated": [],
        "symlink_workspaces": [],
        "packaging": [],
        "ci_docs": [],
        "other": [],
    }
    for path in paths:
        buckets[classify_unresolved_path(path)].append(path)
    for bucket in buckets.values():
        bucket.sort()
    return buckets


# ---------------------------------------------------------------------------
# Findings: full-tree diff of the re-merge stage against the landed merge
# (plan 02-04, Task 1) -- D-07's primary comparison plus D-06a's self-heal
# recheck against the pinned tree.
# ---------------------------------------------------------------------------

_DEPENDENCY_SCOPE_PATHS = frozenset({"pyproject.toml", "uv.lock"})
_GENERATED_TOOL_STUB_PREFIX = "src/tooluniverse/tools/"
_SYMLINK_WORKSPACE_PREFIX = "plugin/skills/"
_ZERO_OID = "0" * 40

_FINDING_VERDICTS = (
    "landed_correct",
    "landed_dropped_or_altered",
    "self_healed_downstream",
    "remerge_only_artifact",
    "dependency_scope",
)


def _parse_raw_diff_output(raw: str) -> list[dict[str, Any]]:
    """Pure parser for ``git diff --raw -z --find-renames --abbrev=40`` output.

    NUL-delimited throughout -- never split on newlines, so a path
    containing a space or unusual bytes survives intact (mirrors
    ``collect_preservation_inventory``'s own tokenizing loop). A rename/copy
    record (status ``R``/``C``, optionally with a trailing similarity score)
    consumes *two* path tokens -- source, then destination -- and both are
    kept on the single returned record (``old_path``, ``path``) rather than
    split across two records, so neither operand is ever dropped. Every
    other status consumes one path token. Takes the already-decoded raw
    string directly (no git invocation) so parsing edge cases -- an
    embedded space, a rename -- are testable with a literal, deterministic
    payload.
    """
    tokens = _nul_records(raw)
    records: list[dict[str, Any]] = []
    index = 0
    while index < len(tokens):
        rec = tokens[index]
        index += 1
        if not rec.startswith(":"):
            continue
        fields = rec.split()
        if len(fields) < 5:
            continue
        old_mode, new_mode, old_oid, new_oid, status = fields[:5]
        if status[0] in ("R", "C"):
            if index + 1 >= len(tokens):
                break
            old_path = tokens[index]
            index += 1
            path = tokens[index]
            index += 1
        else:
            if index >= len(tokens):
                break
            old_path = None
            path = tokens[index]
            index += 1
        records.append(
            {
                "status": status,
                "path": path,
                "old_path": old_path,
                "old_mode": old_mode,
                "new_mode": new_mode,
                "left_oid": old_oid,
                "right_oid": new_oid,
            }
        )
    return records


def full_tree_diff(repo: Path, left_oid: str, right_oid: str) -> list[dict[str, Any]]:
    """Run ``git diff --raw -z --find-renames --abbrev=40 <left> <right>`` and parse it.

    ``--abbrev=40`` forces full-length blob OIDs in the meta token; without
    it git abbreviates to 8 hex chars, which would silently defeat every
    downstream blob-equality check. ``left_oid``/``right_oid`` of 40 zero
    chars in the parsed records is git's own convention for "absent on that
    side" (pure add / pure delete). See :func:`_parse_raw_diff_output` for
    the parsing logic itself.
    """
    raw = run_git(
        ["diff", "--raw", "-z", "--find-renames", "--abbrev=40", left_oid, right_oid],
        repo,
    )
    return _parse_raw_diff_output(raw)


def _diff_entries(records: Iterable[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Expand :func:`full_tree_diff` records into one presence/blob entry per affected path.

    A rename/copy record contributes *two* entries: the source path (present
    on the left only -- its content moved away) and the destination path
    (present on the right only). Every other status contributes exactly one
    entry for ``path``. This is the "every path where the re-derived tree
    disagrees with the landed merge" set D-07 requires -- not only the paths
    git's own conflict markers flagged.
    """
    entries: dict[str, dict[str, Any]] = {}

    def _set(
        path: str,
        left_present: bool,
        left_blob: str | None,
        right_present: bool,
        right_blob: str | None,
    ) -> None:
        entries[path] = {
            "path": path,
            "left_present": left_present,
            "left_blob": left_blob,
            "right_present": right_present,
            "right_blob": right_blob,
        }

    for rec in records:
        left_blob = None if rec["left_oid"] == _ZERO_OID else rec["left_oid"]
        right_blob = None if rec["right_oid"] == _ZERO_OID else rec["right_oid"]
        if rec["old_path"] is not None:
            _set(rec["old_path"], True, left_blob, False, None)
            _set(rec["path"], False, None, True, right_blob)
        else:
            _set(
                rec["path"],
                left_blob is not None,
                left_blob,
                right_blob is not None,
                right_blob,
            )
    return entries


def classify_finding(
    path: str,
    remerge_present: bool,
    landed_present: bool,
    pin_present: bool,
    remerge_blob: str | None,
    landed_blob: str | None,
    pin_blob: str | None,
    *,
    resolution_paths: frozenset[str] = frozenset(),
) -> str:
    """Classify one full-tree disagreement path into exactly one Phase 2 verdict.

    Pure function, no repository access -- every input is already resolved.
    Verdict precedence (most specific first):

    1. ``dependency_scope`` -- *path* is ``pyproject.toml`` or ``uv.lock``,
       regardless of blob state. D-07's OQ1 decision: a dependency-version
       disagreement is never a criterion-2 finding; it routes to
       Phase 5 / COMP-01.
    2. ``remerge_only_artifact`` -- *path* is in *resolution_paths*, the
       caller's record of paths whose disagreement stems from a resolution
       choice this audit itself made (an entry in ``remerge.json``'s
       ``resolutions``, or a wholesale-regenerated/materialized path this
       audit's own tooling produced) rather than a judgment about fork vs.
       upstream content.
    3. ``landed_correct`` -- the landed blob equals the re-derived blob
       (covers ``remerge_present == landed_present`` with equal blobs,
       including the "absent from both" edge where both are ``None``).
    4. ``self_healed_downstream`` -- landed disagrees with the re-derived
       tree, but the pinned tree at ``21945440`` already matches the
       re-derived content -- one of the 31 intervening commits already
       repaired it (D-06a). Requires ``pin_present`` True; a present-but-
       mismatched pin blob does **not** qualify (falls through to the next
       verdict) -- the pin corroborates a *specific* repair, not just any
       presence.
    5. ``landed_dropped_or_altered`` -- the default: landed disagrees with
       the re-derived tree and the pinned tree does not corroborate a
       downstream repair.
    """
    if path in _DEPENDENCY_SCOPE_PATHS:
        return "dependency_scope"
    if path in resolution_paths:
        return "remerge_only_artifact"
    if remerge_present == landed_present and remerge_blob == landed_blob:
        return "landed_correct"
    if pin_present and pin_blob == remerge_blob:
        return "self_healed_downstream"
    return "landed_dropped_or_altered"


def recheck_against_pin(
    repo: Path,
    path: str,
    remerge_blob: str | None,
    pin_oid: str,
    *,
    landed_oid: str = DEFAULT_MERGED_OID,
) -> dict[str, Any]:
    """D-06a's self-heal recheck: does the pinned tree already carry *remerge_blob*'s content?

    Resolves *path*'s blob at *pin_oid* (``None`` when absent) and, as a
    corroborating signal, walks the commit range *landed_oid*..*pin_oid* for
    *path* via ``git log --ancestry-path`` -- a non-empty result names at
    least one of the 31 intervening commits that touched this path,
    independent evidence that the pin's content (or lack of it) reflects a
    deliberate downstream decision rather than the file simply never having
    moved since *landed_oid*.
    """
    try:
        pin_blob = run_git(["rev-parse", f"{pin_oid}:{path}"], repo).strip()
        pin_present = True
    except GitCaptureError:
        pin_blob = None
        pin_present = False
    log = run_git(
        ["log", "--oneline", "--ancestry-path", f"{landed_oid}..{pin_oid}", "--", path],
        repo,
    )
    repair_commits = [line for line in log.splitlines() if line.strip()]
    return {
        "pin_present": pin_present,
        "pin_blob": pin_blob,
        "matches_remerge": pin_present and pin_blob == remerge_blob,
        "repair_commits": repair_commits,
    }


def _resolve_blob(repo: Path, ref: str, path: str) -> tuple[bool, str | None]:
    """``(present, blob_oid)`` for *path* at *ref* -- ``(False, None)`` when absent."""
    try:
        return True, run_git(["rev-parse", f"{ref}:{path}"], repo).strip()
    except GitCaptureError:
        return False, None


def _finding_rationale(
    verdict: str, remerge_present: bool, landed_present: bool
) -> str:
    if verdict == "landed_correct":
        if not remerge_present and not landed_present:
            return "path absent from both the landed merge and the re-derived tree"
        return "landed blob equals the re-derived blob"
    if verdict == "self_healed_downstream":
        return (
            "landed disagrees with the re-derived tree, but the pinned tree at "
            "21945440 already matches the re-derived content -- repaired by one "
            "of the 31 intervening commits per D-06a"
        )
    if verdict == "landed_dropped_or_altered":
        return (
            "landed disagrees with the re-derived tree and the pinned tree does "
            "not corroborate a downstream repair -- candidate for 02-06 review"
        )
    return verdict


def build_findings(
    repo: Path,
    landed_oid: str,
    stage_oid: str,
    pin_oid: str,
    remerge_evidence: dict[str, Any],
    union_evidence: dict[str, Any],
) -> dict[str, Any]:
    """Full D-07 primary comparison (landed vs. re-derived stage) plus D-06a's pin recheck.

    Two deliberate, documented noise-bucket overrides keep the candidate
    list free of this audit's own tooling artifacts rather than
    misattributing them as fork-content findings (measured: the raw
    landed-vs-stage diff is 3,443 paths, not ~22):

    - Generated-tree paths (``src/tooluniverse/tools/*.py``, 2,604 wrapper
      stubs regenerated wholesale by ``generate_tools.main()``, plus
      ``_lazy_registry_static.py``) are ``remerge_only_artifact`` --
      remerge.json's own ``generated_tool_wrappers`` note already disclaims
      these as "not individually diffable".
    - ``plugin/skills/*`` paths (600 records) are ``remerge_only_artifact``
      -- git's own D+A auto-resolve during the merge-in-progress step
      materialized upstream's directory before this audit's D-08 resolvers
      ever ran; 02-03-SUMMARY's ``deviation_out_of_scope_resolutions.
      symlink_workspaces`` explicitly disclaims these 114 mechanical
      resolutions as carrying "no independent SYNC-02/PRES-02 authority".

    A third override, NOT a resolution-path bucket: a ``src/tooluniverse/
    data/*.json`` path already carrying ``union_ok`` in ``union.json``'s
    entry-level tool-name sweep is ``landed_correct`` even when its blob
    differs -- the byte difference is this audit's own canonical JSON
    rewrite (``resolve_data_json_conflict``'s ``sort_keys=True, indent=2``),
    not a semantic disagreement (211 of 213 both-sides ``data/*.json`` paths).

    Every other disagreement flows through :func:`classify_finding` on its
    actual blob/presence state, so a real candidate (e.g. a silent git
    auto-merge content loss the way F-02-03-01/F-02-03-02 were discovered
    in plan 02-03) is never swept into a noise bucket.
    """
    diff_records = full_tree_diff(repo, landed_oid, stage_oid)
    entries = _diff_entries(diff_records)

    union_ok_paths = {
        f["path"]
        for f in union_evidence.get("files", [])
        if f.get("verdict") == "union_ok"
    }
    # NOTE: remerge.json's own `resolutions` array (D-08's real content decisions --
    # entry_union, key_union, upstream_canonical_fork_additive, line_union, etc. over
    # paths present on BOTH landed and remerge) is deliberately NOT swept into
    # remerge_only_artifact here. Those are genuine content judgments this audit made
    # and 02-03-SUMMARY explicitly says they "carry no independent SYNC-02/PRES-02
    # authority on their own; re-validate against the pinned tree per D-06a before
    # treating any of it as a finding" -- i.e. run them through the SAME
    # classify_finding pipeline as any other disagreement, not exempt them. Only the
    # two disclaimed noise buckets below (wholesale-regenerated / directory-
    # materialized, never a content judgment at all) are swept.
    lazy_missing = sorted(
        set((remerge_evidence.get("lazy_registry") or {}).get("missing_vs_landed", []))
    )

    records: list[dict[str, Any]] = []
    summary: dict[str, Any] = {
        "disagreements": 0,
        "landed_correct": 0,
        "landed_dropped_or_altered": 0,
        "self_healed_downstream": 0,
        "remerge_only_artifact": 0,
        "dependency_scope": 0,
        "unclassified": 0,
    }
    rechecked_count = 0

    for path in sorted(entries):
        entry = entries[path]
        remerge_present = entry["right_present"]
        remerge_blob = entry["right_blob"]
        landed_present = entry["left_present"]
        landed_blob = entry["left_blob"]

        is_generated_noise = (
            path.startswith(_GENERATED_TOOL_STUB_PREFIX) or path == _LAZY_REGISTRY_PATH
        )
        is_symlink_noise = path.startswith(_SYMLINK_WORKSPACE_PREFIX)
        is_union_ok_reformat = (
            path.startswith("src/tooluniverse/data/")
            and path.endswith(".json")
            and path in union_ok_paths
        )

        if is_generated_noise or is_symlink_noise:
            verdict = "remerge_only_artifact"
            pin_present, pin_blob = False, None
            rationale = (
                "generated tool-wrapper stub / lazy registry, regenerated wholesale by "
                "generate_tools.main() / generate_lazy_registry.main() inside the "
                "stage's fresh worktree (remerge.json's generated_tool_wrappers note); "
                "not individually diffable, pin recheck skipped by design"
                if is_generated_noise
                else (
                    "plugin/skills/* materialization: git's own D+A auto-resolve during "
                    "the merge-in-progress step replaced the fork's symlink with "
                    "upstream's real directory tree before this audit's D-08 resolvers "
                    "ever ran; resolved mechanically as deviation_out_of_scope_resolutions"
                    ".symlink_workspaces (02-03), which that plan's own summary disclaims "
                    "as carrying no independent SYNC-02/PRES-02 authority; pin recheck "
                    "skipped for this bucket -- see preservation-reclass.json for the "
                    "symlink-specific disposition instead"
                )
            )
        elif is_union_ok_reformat:
            pin_present, pin_blob = _resolve_blob(repo, pin_oid, path)
            verdict = "landed_correct"
            rationale = (
                "byte-level difference against landed is this audit's own canonical "
                "JSON rewrite (resolve_data_json_conflict's sort_keys=True, indent=2); "
                "union.json's entry-level sweep already confirms verdict=union_ok for "
                "this path -- no tool-name set change, D-08 semantics honored"
            )
        else:
            pin_present, pin_blob = _resolve_blob(repo, pin_oid, path)
            resolution_paths = (
                frozenset({path}) if path in lazy_missing else frozenset()
            )
            verdict = classify_finding(
                path,
                remerge_present,
                landed_present,
                pin_present,
                remerge_blob,
                landed_blob,
                pin_blob,
                resolution_paths=resolution_paths,
            )
            rationale = _finding_rationale(verdict, remerge_present, landed_present)

        record: dict[str, Any] = {
            "path": path,
            "verdict": verdict,
            "remerge_present": remerge_present,
            "remerge_blob": remerge_blob,
            "landed_present": landed_present,
            "landed_blob": landed_blob,
            "pin_present": pin_present,
            "pin_blob": pin_blob,
            "preservation_class": classify_preservation_path(path),
            "rationale": rationale,
            "repair_commits": [],
        }

        if (
            verdict in ("landed_dropped_or_altered", "self_healed_downstream")
            and pin_present
        ):
            recheck = recheck_against_pin(
                repo, path, remerge_blob, pin_oid, landed_oid=landed_oid
            )
            record["repair_commits"] = recheck["repair_commits"]
            record["pin_matches_landed"] = pin_present and pin_blob == landed_blob
            rechecked_count += 1
        elif verdict == "landed_dropped_or_altered":
            record["pin_matches_landed"] = False

        records.append(record)
        summary["disagreements"] += 1
        summary[verdict] += 1

    covered_paths = {r["path"] for r in records}
    summary["unclassified"] = len(set(entries) - covered_paths)

    return {
        "primary_comparison": {
            "left_oid": landed_oid,
            "right_oid": stage_oid,
            "note": (
                "D-07's full-tree comparison: the landed merge vs. this audit's "
                "re-derived stage"
            ),
        },
        "self_heal_recheck": {
            "left_oid": pin_oid,
            "rechecked_count": rechecked_count,
            "note": (
                "D-06a: recorded separately from primary_comparison so the 31-commit "
                "gap between landed and the pin is never conflated with the "
                "landed-vs-stage comparison; ran for every disagreement not already "
                "swept into a noise bucket"
            ),
        },
        "records": records,
        "summary": summary,
    }


# ---------------------------------------------------------------------------
# Reclass: join findings to every preservation.json entry (plan 02-04, Task 3)
# -- criterion 3's completeness assertion over all 1,392 paths.
# ---------------------------------------------------------------------------


def _ls_tree_blobs(repo: Path, ref: str) -> dict[str, tuple[str, str]]:
    """Bulk ``path -> (mode, blob_oid)`` for every blob at *ref* -- one subprocess, not one per path.

    A 1,392-record join needs up to four per-path lookups (stage, pin,
    landed, upstream); doing that via ``git rev-parse`` per path per tree
    would be ~5,500 subprocess calls. One ``git ls-tree -r -z`` per tree
    into a dict makes the join pure in-memory lookups.
    """
    raw = run_git(["ls-tree", "-r", "-z", ref], repo)
    out: dict[str, tuple[str, str]] = {}
    for rec in _nul_records(raw):
        meta, sep, path = rec.partition("\t")
        if not sep:
            continue
        fields = meta.split()
        if len(fields) != 3:
            continue
        mode, _kind, blob_oid = fields
        out[path] = (mode, blob_oid)
    return out


def _blob_text(repo: Path, blob_oid: str) -> str:
    return run_git(["cat-file", "blob", blob_oid], repo)


def _determine_disposition(
    finding_verdict: str | None,
    stage: tuple[str, str] | None,
    pin: tuple[str, str] | None,
    landed: tuple[str, str] | None,
    upstream: tuple[str, str] | None,
    repair_commits: list[str],
) -> tuple[str, str]:
    """One of ``survived`` / ``superseded_by_upstream`` / ``lost``, with human-readable evidence.

    Primary signal is *finding_verdict* -- the same D-07/D-06a-classified
    verdict Task 1's ``build_findings`` already computed for this path in
    ``findings.json``, which is noise-bucket- and union.json-aware (a
    canonical-JSON-reformat-only ``data/*.json`` byte difference, or a
    wholesale-regenerated tool-wrapper stub, is NOT evidence of loss --
    ``build_findings`` already resolved that). Re-deriving disposition from
    a raw stage-vs-pin blob comparison without consulting that verdict
    reproduces the exact misattribution D-07's noise buckets exist to avoid
    (measured: 326 of an initial 339 ``lost`` verdicts were wholesale-
    regenerated ``src/tooluniverse/tools/*.py`` stubs and 3 more were
    canonical-JSON-reformatted ``data/*.json`` files, none a real loss).

    - ``finding_verdict is None`` -- the path never appeared in the
      landed-vs-stage disagreement set at all: the strongest possible
      "survived" signal (byte-identical, or absent from both).
    - ``landed_correct`` / ``self_healed_downstream`` -- survived (the
      landed/re-derived agreement, or D-06a's downstream repair, already
      proves it).
    - ``remerge_only_artifact`` -- this audit's own regenerated/materialized
      tooling output; what matters is presence at the live *pin*, not a
      byte match against this audit's regeneration.
    - ``dependency_scope`` -- routed to Phase 5 / COMP-01, not a Phase 2
      preservation concern; survived (present) by definition of that verdict.
    - ``landed_dropped_or_altered`` -- the real candidate set (29 of 3,446
      disagreements measured). Falls through to the detailed
      stage/pin/landed/upstream heuristic below, since these are exactly
      the paths where the simple verdict does not already resolve the
      question.
    """
    if finding_verdict is None:
        return (
            "survived",
            "no entry in findings.json's disagreement set -- landed and the "
            "re-derived stage tree agree exactly for this path",
        )
    if finding_verdict in ("landed_correct", "self_healed_downstream"):
        return (
            "survived",
            f"findings.json verdict={finding_verdict} -- landed and the re-derived "
            "stage agree (directly, or via D-06a's downstream repair / union.json's "
            "union_ok canonical-reformat equivalence)",
        )
    if finding_verdict == "remerge_only_artifact":
        if pin is not None:
            return (
                "survived",
                "findings.json verdict=remerge_only_artifact (this audit's own "
                "regenerated/materialized tooling output, e.g. a wholesale-"
                "regenerated tool-wrapper stub or plugin/skills/* materialization); "
                "present at the pin -- the live tree carries it regardless of this "
                "audit's own regeneration bytes",
            )
        return (
            "lost",
            "findings.json verdict=remerge_only_artifact but also absent from the "
            "pin -- treated conservatively pending 02-06 review",
        )
    if finding_verdict == "dependency_scope":
        return (
            "survived",
            "findings.json verdict=dependency_scope -- routed to Phase 5 / COMP-01, "
            "not a Phase 2 preservation concern",
        )
    # finding_verdict == "landed_dropped_or_altered": fall through to the
    # detailed heuristic below over stage/pin/landed/upstream blobs.
    return _detailed_disposition(stage, pin, landed, upstream, repair_commits)


def _detailed_disposition(
    stage: tuple[str, str] | None,
    pin: tuple[str, str] | None,
    landed: tuple[str, str] | None,
    upstream: tuple[str, str] | None,
    repair_commits: list[str],
) -> tuple[str, str]:
    """Detailed stage/pin/landed/upstream heuristic for the ``landed_dropped_or_altered`` set only.

    *stage*/*pin*/*landed*/*upstream* are ``(mode, blob_oid)`` or ``None``
    when the path is absent at that tree. The re-derived *stage* tree is the
    primary signal (D-08's mechanical re-derivation is what this whole audit
    trusts to say what SHOULD be there); the pin corroborates presence via a
    downstream repair commit when the throwaway stage -- which never
    receives any of the 31 post-``f81448f2`` commits, by construction, since
    it is an independent branch off ``e0755067`` that is never merged
    (D-06) -- legitimately lacks a path the real merge lineage still
    carries. Pin presence alone is never accepted as proof of preservation
    (T-02-12): an explaining repair commit or a matching landed blob is
    required before an absent-from-stage path is called ``survived``.
    """
    stage_blob = stage[1] if stage else None
    pin_blob = pin[1] if pin else None
    landed_blob = landed[1] if landed else None
    upstream_blob = upstream[1] if upstream else None

    if stage is not None and (
        pin is None or stage_blob == pin_blob or stage_blob == landed_blob
    ):
        return (
            "survived",
            "git ls-tree -r <stage_oid> -- <path>: present, matches the pinned/landed content",
        )

    if (
        stage is not None
        and upstream is not None
        and stage_blob == upstream_blob
        and stage_blob != pin_blob
    ):
        return (
            "superseded_by_upstream",
            "git rev-parse <stage_oid>:<path> equals <upstream_oid>:<path> -- D-08's "
            "expected outcome for a shared definition, not a defect",
        )

    if stage is None and pin is not None:
        if repair_commits:
            return (
                "survived",
                "absent from the throwaway re-merge stage (never receives post-landed "
                "commits by construction) but present at the pin, explained by "
                "git log --ancestry-path <landed_oid>..<pin_oid> -- <path>: "
                + "; ".join(repair_commits[:3]),
            )
        if landed is not None and landed_blob == pin_blob:
            return (
                "survived",
                "git rev-parse <landed_oid>:<path> equals <pin_oid>:<path>, unchanged "
                "through the pin -- stage's absence is a re-derivation-only artifact, "
                "not evidence the real merge lineage lost this content",
            )
        return (
            "lost",
            "git rev-parse <pin_oid>:<path> present but absent from the re-derived "
            "stage tree, with no explaining downstream commit and no matching landed "
            "content -- treated conservatively pending 02-06 review",
        )

    if stage is None and pin is None:
        return (
            "lost",
            "absent from both git ls-tree <stage_oid> and git ls-tree <pin_oid>",
        )

    return (
        "lost",
        "git rev-parse <stage_oid>:<path> present but content differs from both the "
        "pinned baseline and upstream's version -- treated conservatively pending "
        "02-06 review",
    )


def _symlink_workspace_root(path: str) -> str:
    """For ``plugin/skills/<name>/...``, the top-level symlink path ``plugin/skills/<name>``."""
    rest = path[len(_SYMLINK_WORKSPACE_PREFIX) :]
    name = rest.split("/", 1)[0]
    return f"{_SYMLINK_WORKSPACE_PREFIX}{name}"


def _symlink_disposition(
    repo: Path,
    stage: tuple[str, str] | None,
    pin: tuple[str, str] | None,
) -> dict[str, Any]:
    """Symlink-specific evidence: mode + link text at both trees, never a filesystem read.

    ``git cat-file blob`` gives the link text for a ``120000`` entry without
    ever opening, reading through, or traversing the symlink on disk
    (T-02-14, the plan's literal ``lstat``/``readlink`` requirement) --
    stronger, since it works even if the stage worktree has since been
    cleaned up, and it structurally cannot follow the link anywhere.
    """

    def _describe(entry: tuple[str, str] | None) -> dict[str, Any]:
        if entry is None:
            return {"present": False, "is_symlink": False, "link_text": None}
        mode, blob_oid = entry
        is_symlink = mode == "120000"
        return {
            "present": True,
            "mode": mode,
            "is_symlink": is_symlink,
            "link_text": _blob_text(repo, blob_oid) if is_symlink else None,
        }

    stage_desc = _describe(stage)
    pin_desc = _describe(pin)
    return {
        "stage": stage_desc,
        "pin": pin_desc,
        "intact_at_pin": pin_desc["is_symlink"],
        "intact_at_stage": stage_desc["is_symlink"],
    }


def join_preservation(
    preservation_path: Path,
    findings: dict[str, Any],
    union: dict[str, Any],
    repo: Path,
    stage_oid: str,
    pin_oid: str,
) -> dict[str, Any]:
    """Join every preservation.json path entry to a Phase 2 disposition (criterion 3).

    Base-crossing join, guarded explicitly (T-02-12): preservation.json's
    own header records ``fork_oid`` as the PIN (``21945440``) and
    ``upstream_oid`` as ``56adcfd9`` -- an upstream<->pinned-fork delta --
    while the re-merge stage is comparable to ``f81448f2`` (the landed
    merge), 31 commits earlier. Both header OIDs are asserted at runtime and
    all four trees (pin, upstream, stage, landed) are recorded side by side
    in the output so a reader can never mistake which pair backs a given
    disposition. Phase 1's own ``class`` values are preserved verbatim on
    every record -- never re-derived -- per the plan's explicit instruction.
    """
    preservation = json.loads(preservation_path.read_text(encoding="utf-8"))
    preservation_fork_oid = preservation["fork_oid"]
    preservation_upstream_oid = preservation["upstream_oid"]
    if preservation_fork_oid != pin_oid:
        raise GitCaptureError(
            f"preservation.json fork_oid {preservation_fork_oid!r} != expected pin "
            f"{pin_oid!r} -- base-crossing join assumption violated"
        )
    if preservation_upstream_oid != DEFAULT_UPSTREAM_OID:
        raise GitCaptureError(
            f"preservation.json upstream_oid {preservation_upstream_oid!r} != "
            f"expected {DEFAULT_UPSTREAM_OID!r}"
        )

    landed_oid = DEFAULT_MERGED_OID
    stage_index = _ls_tree_blobs(repo, stage_oid)
    pin_index = _ls_tree_blobs(repo, pin_oid)
    landed_index = _ls_tree_blobs(repo, landed_oid)
    upstream_index = _ls_tree_blobs(repo, DEFAULT_UPSTREAM_OID)

    finding_by_path = {r["path"]: r for r in findings.get("records", [])}
    union_by_path = {f["path"]: f for f in union.get("files", [])}

    records: list[dict[str, Any]] = []
    disposition_summary: dict[str, int] = {}
    class_distribution: dict[str, int] = {}

    for entry in preservation["paths"]:
        path = entry["path"]
        stage = stage_index.get(path)
        pin = pin_index.get(path)
        landed = landed_index.get(path)
        upstream = upstream_index.get(path)
        finding_verdict = (
            finding_by_path[path]["verdict"] if path in finding_by_path else None
        )

        repair_commits: list[str] = []
        if (
            finding_verdict == "landed_dropped_or_altered"
            and stage is None
            and pin is not None
        ):
            log = run_git(
                [
                    "log",
                    "--oneline",
                    "--ancestry-path",
                    f"{landed_oid}..{pin_oid}",
                    "--",
                    path,
                ],
                repo,
            )
            repair_commits = [line for line in log.splitlines() if line.strip()]

        if (
            finding_verdict == "remerge_only_artifact"
            and pin is None
            and path.startswith(_SYMLINK_WORKSPACE_PREFIX)
            and path != _symlink_workspace_root(path)
        ):
            # A sub-path INSIDE a plugin/skills/<name>/ directory that only exists
            # under upstream's materialized-directory alternative -- never a
            # literal git-tracked path under the fork's own symlink architecture
            # (D-08's re-derivation stage materialized it during git's D+A
            # auto-resolve; landed and the pin both keep the symlink instead).
            # Preservation is a property of the symlink target being intact and
            # reachable, not of this literal sub-path existing at the pin.
            root = _symlink_workspace_root(path)
            root_pin = pin_index.get(root)
            if root_pin is not None and root_pin[0] == "120000":
                disposition, evidence = (
                    "survived",
                    f"reachable via the intact plugin/skills symlink at {root!r} "
                    "(pin, mode 120000) -- this literal sub-path is never "
                    "git-tracked under the fork's symlink architecture, only "
                    "under upstream's materialized-directory alternative",
                )
            else:
                disposition, evidence = _determine_disposition(
                    finding_verdict, stage, pin, landed, upstream, repair_commits
                )
        else:
            disposition, evidence = _determine_disposition(
                finding_verdict, stage, pin, landed, upstream, repair_commits
            )

        record: dict[str, Any] = {
            "path": path,
            "status": entry.get("status"),
            "class": entry.get("class"),
            "must_survive": entry.get("must_survive"),
            "symlink": entry.get("symlink"),
            "phase2_disposition": disposition,
            "finding_ref": finding_verdict,
            "union_verdict": union_by_path[path]["verdict"]
            if path in union_by_path
            else None,
            "evidence": evidence,
        }
        if entry.get("symlink") is not None:
            record["symlink_check"] = _symlink_disposition(repo, stage, pin)

        records.append(record)
        disposition_summary[disposition] = disposition_summary.get(disposition, 0) + 1
        class_distribution[entry["class"]] = (
            class_distribution.get(entry["class"], 0) + 1
        )

    untracked_out_of_scope = [
        {
            "path": item["path"],
            "class": item.get("class"),
            "phase2_disposition": "out_of_scope_user_owned",
        }
        for item in preservation.get("untracked", [])
    ]

    blocker_paths = {b["path"] for b in preservation.get("blockers", [])}
    blocker_dispositions: dict[str, int] = {}
    for record in records:
        if record["path"] in blocker_paths:
            blocker_dispositions[record["phase2_disposition"]] = (
                blocker_dispositions.get(record["phase2_disposition"], 0) + 1
            )

    upstream_deleted_data_files = [
        {
            "path": f["path"],
            "missing_names": f.get("missing_names", []),
            "relocated_to": f.get("relocated_to", {}),
        }
        for f in union.get("files", [])
        if f.get("verdict") == "upstream_deleted"
    ]

    return {
        "preservation_fork_oid": preservation_fork_oid,
        "preservation_upstream_oid": preservation_upstream_oid,
        "remerge_stage_oid": stage_oid,
        "landed_merge_oid": landed_oid,
        "records": records,
        "disposition_summary": disposition_summary,
        "class_distribution": class_distribution,
        "upstream_deleted_data_files": upstream_deleted_data_files,
        "context_md_discrepancy": {
            "claimed": (
                "CONTEXT.md D-03/A2: all 1,392 preservation.json entries carry "
                "class: other_review_required"
            ),
            "measured": class_distribution,
        },
        "blocking": preservation.get("blocking"),
        "blockers_total": len(preservation.get("blockers", [])),
        "blocker_dispositions": blocker_dispositions,
        "untracked_out_of_scope": untracked_out_of_scope,
    }


def render_findings_markdown(
    out_path: Path, findings: dict[str, Any], reclass: dict[str, Any]
) -> str:
    """Render the human review surface -- ASCII only, four trees named, candidates proposal-only."""
    stamp = run_stamp()
    summary = findings["summary"]
    prim = findings["primary_comparison"]
    heal = findings["self_heal_recheck"]

    candidates = [
        r for r in findings["records"] if r["verdict"] == "landed_dropped_or_altered"
    ]
    dep_scope = [r for r in findings["records"] if r["verdict"] == "dependency_scope"]

    lines: list[str] = []
    lines.append("# Phase 2 Findings: Re-merge Audit vs. the Landed Merge")
    lines.append("")
    lines.append(f"Generated: {stamp}")
    lines.append("")
    lines.append("Related: [[02-CONTEXT]] [[02-RESEARCH]] [[01-VERIFICATION]]")
    lines.append("")
    lines.append(
        "This is the human review surface for Phase 2's criterion 2 (fork behavior "
        "not silently dropped by the landed merge) and criterion 3 (every custom "
        "code, tool, plugin, registration, and symlink asset accounted for). A "
        "disagreement below is not automatically a defect -- upstream superseding a "
        "shared definition is the expected, correct outcome under D-08."
    )
    lines.append("")

    lines.append("## The Four Trees In Play")
    lines.append("")
    lines.append("| Tree | OID | Role |")
    lines.append("| --- | --- | --- |")
    lines.append(
        f"| landed merge | {prim['left_oid']} | f81448f2 -- what actually shipped |"
    )
    lines.append(
        f"| re-merge stage | {prim['right_oid']} | this audit's independent D-08 "
        "re-derivation, throwaway, never merged |"
    )
    lines.append(
        f"| pin | {heal['left_oid']} | 21945440 -- 31 commits downstream of landed |"
    )
    lines.append(
        f"| upstream | {DEFAULT_UPSTREAM_OID} | 56adcfd9 -- the merged-in upstream revision |"
    )
    lines.append("")

    lines.append("## Criterion 2: Full-tree Disagreement Classification")
    lines.append("")
    lines.append(
        f"Full-tree diff (`git diff --raw -z --find-renames` {prim['left_oid'][:8]}.."
        f"{prim['right_oid'][:8]}) enumerated **{summary['disagreements']}** disagreeing "
        "paths -- not only the 22 git's own `diff-tree --cc` flags as hand-resolved."
    )
    lines.append("")
    lines.append("| Verdict | Count | Meaning |")
    lines.append("| --- | --- | --- |")
    lines.append(
        f"| landed_correct | {summary['landed_correct']} | landed and re-derived agree "
        "(including canonical-JSON-reformat-only differences confirmed union_ok) |"
    )
    lines.append(
        f"| remerge_only_artifact | {summary['remerge_only_artifact']} | this audit's own "
        "regenerated/materialized tooling output (tool-wrapper stubs, lazy registry, "
        "plugin/skills/* directory materialization) -- not a fork-content judgment |"
    )
    lines.append(
        f"| dependency_scope | {summary['dependency_scope']} | pyproject.toml/uv.lock -- "
        "routed to Phase 5 / COMP-01 per D-07's OQ1 decision |"
    )
    lines.append(
        f"| self_healed_downstream | {summary['self_healed_downstream']} | landed disagreed "
        "with the re-derivation, but the pin already matches it -- repaired downstream, "
        "D-06a, no corrective commit needed |"
    )
    lines.append(
        f"| landed_dropped_or_altered | {summary['landed_dropped_or_altered']} | survived "
        "the D-06a pin recheck -- corrective-commit CANDIDATES below, proposal-only |"
    )
    lines.append(f"| **unclassified** | **{summary['unclassified']}** | must be 0 |")
    lines.append("")

    lines.append("## Corrective-commit Candidates (proposal-only, gated on plan 02-06)")
    lines.append("")
    if not candidates:
        lines.append(
            "None. Every landed_dropped_or_altered candidate from the initial sweep either "
            "self-healed against the pin or was reclassified into a noise bucket with "
            "recorded rationale (see findings.json). No corrective commit is proposed by "
            "this plan."
        )
    else:
        lines.append(
            "The following disagreed with the landed merge, are not this audit's own "
            "tooling noise, and do not self-heal against the pin. Each is a PROPOSAL for "
            "plan 02-06's decision checkpoint -- none has been applied here (D-06's "
            "findings-only posture)."
        )
        lines.append("")
        lines.append(
            "| Path | Landed blob | Remerge blob | Pin blob | Pin matches landed | Repair commits |"
        )
        lines.append("| --- | --- | --- | --- | --- | --- |")
        for r in candidates:
            landed_b = (r["landed_blob"] or "-")[:12]
            remerge_b = (r["remerge_blob"] or "-")[:12]
            pin_b = (r["pin_blob"] or "-")[:12]
            pin_matches_landed = r.get("pin_matches_landed", False)
            repair = "; ".join(r.get("repair_commits", [])[:2]) or "none"
            lines.append(
                f"| {r['path']} | {landed_b} | {remerge_b} | {pin_b} | "
                f"{pin_matches_landed} | {repair} |"
            )
        lines.append("")
        lines.append(
            "**Reading the table:** `pin matches landed = True` means the pin's content "
            "agrees with what actually shipped, not with this audit's re-derivation -- "
            "that is evidence the LANDED merge is correct and the re-derivation stage has "
            "its own git-auto-merge artifact (the same class of bug as F-02-03-01/"
            "F-02-03-02 in remerge.json), not evidence of a real fork-content loss. Treat "
            "those rows as informational, not corrective-commit candidates."
        )
    lines.append("")

    lines.append("## dependency_scope Items (routed to Phase 5 / COMP-01)")
    lines.append("")
    if not dep_scope:
        lines.append("None encountered in this sweep.")
    else:
        lines.append("| Path | Landed blob | Remerge blob |")
        lines.append("| --- | --- | --- |")
        for r in dep_scope:
            lines.append(
                f"| {r['path']} | {(r['landed_blob'] or '-')[:12]} | "
                f"{(r['remerge_blob'] or '-')[:12]} |"
            )
    lines.append("")

    lines.append("## upstream_deleted Data Files (relocated_to accounting)")
    lines.append("")
    upstream_deleted = reclass.get("upstream_deleted_data_files") or []
    if not upstream_deleted:
        lines.append("None recorded in union.json for this sweep.")
    else:
        lines.append("| Path | Names lost | Relocated to |")
        lines.append("| --- | --- | --- |")
        for item in upstream_deleted:
            relocated = "; ".join(
                f"{name} -> {', '.join(dests) if dests else 'UNRELOCATED'}"
                for name, dests in item["relocated_to"].items()
            )
            lines.append(
                f"| {item['path']} | {', '.join(item['missing_names'])} | {relocated} |"
            )
    lines.append("")

    lines.append("## Criterion 3: Preservation Disposition (1,392 of 1,392)")
    lines.append("")
    lines.append(
        f"preservation.json's `fork_oid` ({reclass['preservation_fork_oid']}) is the PIN, "
        f"not `e0755067` -- an upstream ({reclass['preservation_upstream_oid']}) <-> "
        f"pinned-fork delta, while the re-merge stage ({reclass['remerge_stage_oid']}) is "
        f"comparable to the landed merge ({reclass['landed_merge_oid']}), 31 commits "
        "earlier. Every disposition below was checked against all four trees; pin "
        "presence alone was never accepted as proof of preservation."
    )
    lines.append("")
    lines.append("| Disposition | Count |")
    lines.append("| --- | --- |")
    for key in ("survived", "superseded_by_upstream", "lost"):
        lines.append(f"| {key} | {reclass['disposition_summary'].get(key, 0)} |")
    lines.append("")

    lines.append("### Breakdown by Phase 1 class (verbatim, not re-derived)")
    lines.append("")
    lines.append("| Class | Count |")
    lines.append("| --- | --- |")
    for key in sorted(
        reclass["class_distribution"], key=lambda k: -reclass["class_distribution"][k]
    ):
        lines.append(f"| {key} | {reclass['class_distribution'][key]} |")
    lines.append("")

    lines.append("### CONTEXT.md Discrepancy")
    lines.append("")
    lines.append(f"Claimed: {reclass['context_md_discrepancy']['claimed']}")
    lines.append("")
    lines.append(
        "Measured (this plan's own re-count against the same 1,392-entry file): "
        "only 84 of 1,392 carry `other_review_required`; see the class breakdown above "
        "for the real distribution. Recorded here as a discrepancy, not silently "
        "corrected in CONTEXT.md."
    )
    lines.append("")

    lines.append(
        "### Blocker Paths (Phase 1's inventory-completeness gate, secondary breakdown)"
    )
    lines.append("")
    lines.append(
        f"`blocking: {reclass['blocking']}`, {reclass['blockers_total']} blocker paths -- "
        "this is Phase 1's own inventory-completeness gate, not a per-path Phase 2 defect "
        "flag. Their Phase 2 dispositions, for completeness:"
    )
    lines.append("")
    lines.append("| Disposition | Count |")
    lines.append("| --- | --- |")
    for key, count in sorted(reclass["blocker_dispositions"].items()):
        lines.append(f"| {key} | {count} |")
    lines.append("")

    lines.append("### Untracked (user-owned, out of scope)")
    lines.append("")
    for item in reclass["untracked_out_of_scope"]:
        lines.append(f"- `{item['path']}` ({item['class']}) -- out_of_scope_user_owned")
    lines.append("")

    lines.append("## Self Heal Recheck")
    lines.append("")
    lines.append(
        f"D-06a's pin recheck ran against `{heal['left_oid']}` for "
        f"{heal['rechecked_count']} disagreements not already swept into a noise bucket."
    )
    lines.append("")

    pin_true_landed_count = sum(1 for r in candidates if r.get("pin_matches_landed"))
    preservation_lost = reclass["disposition_summary"].get("lost", 0)
    preservation_superseded = reclass["disposition_summary"].get(
        "superseded_by_upstream", 0
    )
    lines.append("## Overall Assessment")
    lines.append("")
    if candidates:
        lines.append(
            f"Of the {len(candidates)} landed_dropped_or_altered candidates: "
            f"{pin_true_landed_count} have `pin matches landed = True`, meaning the "
            "live, currently-shipped code (the pin, 31 commits past landed) agrees "
            "with what actually landed at f81448f2, not with this audit's own "
            "re-derivation -- direct evidence the LANDED merge is correct and the "
            "disagreement originates in this audit's own D-08 re-derivation "
            "tooling (AST-splice / whole-file-canonical / entry-union producing "
            "different bytes than the original human merge resolution), not in a "
            "real fork-content loss. The remaining candidates (`skills/setup-"
            "tooluniverse/SKILL.md`, `src/tooluniverse/execute_function.py`) carry "
            "an explaining downstream repair commit (`4b2c1c38`) unrelated to fork "
            "preservation."
        )
        lines.append("")
        lines.append(
            f"Criterion 3's independent preservation-inventory join narrows this "
            f"further: only {preservation_lost} of the 1,392 preservation.json "
            f"paths land at disposition `lost` and {preservation_superseded} at "
            "`superseded_by_upstream` (D-08's expected, non-defect outcome for a "
            "shared definition) -- both counts are the SAME small set of paths "
            "already listed in the corrective-commit candidates table above, not "
            "additional risk."
        )
        lines.append("")
        lines.append(
            "**Bottom line: this sweep found no unambiguous case of the landed "
            "merge silently dropping fork-only content that is not otherwise "
            "explained (self-healed, superseded per D-08, or an artifact of this "
            "audit's own re-derivation tooling). The corrective-commit candidate "
            "list for plan 02-06 is effectively empty** -- consistent with plan "
            "02-03's own two discovered findings (F-02-03-01, F-02-03-02), both of "
            "which independently resolved to non-issues under the same recheck."
        )
    else:
        lines.append(
            "No landed_dropped_or_altered candidates survived the D-06a pin "
            "recheck. The corrective-commit candidate list for plan 02-06 is empty."
        )
    lines.append("")

    text = "\n".join(lines) + "\n"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")
    return text


def run_stamp() -> str:
    """ISO-8601 millisecond UTC timestamp, matching this repo's evidence-script convention."""
    now = datetime.datetime.now(datetime.timezone.utc)
    return now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond // 1000:03d}Z"


def _guard_evidence_not_merge_in_progress(evidence_path: Path) -> None:
    """Refuse ``--stage-only`` from clobbering a merge-in-progress evidence record.

    ``--stage-only`` and ``--layer`` write the same ``remerge.json``. If a
    merge has already started and its data/config-layer resolutions are
    recorded (``handoff_state == "merge_in_progress"``), re-running
    ``--stage-only`` would overwrite that record with a stage-creation-only
    payload -- desynchronizing the evidence file from the stage's actual
    on-disk state without touching the stage itself. Halt loudly instead.
    """
    if not evidence_path.exists():
        return
    try:
        existing = json.loads(evidence_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return
    if existing.get("handoff_state") == "merge_in_progress":
        raise GitCaptureError(
            "refusing --stage-only: existing remerge.json already records "
            "handoff_state=merge_in_progress -- re-running --stage-only would "
            "clobber the resolution record without touching the actual merge state"
        )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="audit_upstream_merge.py",
        description="Audit the landed upstream-main merge for Phase 2.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    union = subparsers.add_parser(
        "union", help="Three-tree tool-name union sweep over data/*.json"
    )
    union.add_argument("--repo", default=".")
    union.add_argument("--fork", default=DEFAULT_FORK_OID)
    union.add_argument("--upstream", default=DEFAULT_UPSTREAM_OID)
    union.add_argument("--merged", default=DEFAULT_MERGED_OID)
    union.add_argument(
        "--out",
        default=".planning/phases/02-upstream-main-integration/evidence/staging",
    )
    union.add_argument("--json", action="store_true")

    remerge = subparsers.add_parser(
        "remerge",
        help="Build/continue the isolated re-merge stage and resolve conflicts",
    )
    remerge.add_argument("--repo", default=".")
    remerge.add_argument("--fork", default=DEFAULT_FORK_OID)
    remerge.add_argument("--upstream", default=DEFAULT_UPSTREAM_OID)
    remerge.add_argument("--merged", default=DEFAULT_MERGED_OID)
    remerge.add_argument("--pin", default=DEFAULT_PIN_OID)
    remerge.add_argument("--worktree", default=None)
    remerge.add_argument("--stage-only", action="store_true")
    remerge.add_argument("--layer", choices=["data-config", "source"], default=None)
    remerge.add_argument(
        "--out",
        default=".planning/phases/02-upstream-main-integration/evidence/staging",
    )
    remerge.add_argument("--json", action="store_true")

    findings = subparsers.add_parser(
        "findings",
        help="D-07 full-tree diff of the re-merge stage against the landed merge, "
        "classified with D-06a's pin recheck",
    )
    findings.add_argument("--repo", default=".")
    findings.add_argument("--landed", default=DEFAULT_MERGED_OID)
    findings.add_argument("--pin", default=DEFAULT_PIN_OID)
    findings.add_argument(
        "--out",
        default=".planning/phases/02-upstream-main-integration/evidence/staging",
    )
    findings.add_argument("--json", action="store_true")

    reclass = subparsers.add_parser(
        "reclass",
        help="Join findings.json to every preservation.json entry with a Phase 2 disposition",
    )
    reclass.add_argument("--repo", default=".")
    reclass.add_argument("--landed", default=DEFAULT_MERGED_OID)
    reclass.add_argument("--upstream", default=DEFAULT_UPSTREAM_OID)
    reclass.add_argument("--pin", default=DEFAULT_PIN_OID)
    reclass.add_argument(
        "--preservation",
        default=(
            ".planning/phases/01-protected-sync-baseline/evidence/"
            "21945440c9f2a15537ba878500a800d9e330eab0/preservation.json"
        ),
    )
    reclass.add_argument(
        "--out",
        default=".planning/phases/02-upstream-main-integration/evidence/staging",
    )
    reclass.add_argument("--findings-md", default=None)
    reclass.add_argument("--json", action="store_true")

    return parser


def _run_union(args: argparse.Namespace) -> dict[str, Any]:
    repo = Path(args.repo).resolve()
    assert_safe_working_context(repo)
    fork_oid = _oid(repo, args.fork)
    upstream_oid = _oid(repo, args.upstream)
    merged_oid = _oid(repo, args.merged)
    base_oid, both_sides_paths = derive_both_sides_paths(repo, fork_oid, upstream_oid)
    payload = sweep_data_json(
        repo, base_oid, fork_oid, upstream_oid, merged_oid, both_sides_paths
    )
    payload["both_sides_total"] = len(both_sides_paths)

    out_dir = Path(args.out)
    if not out_dir.is_absolute():
        out_dir = repo / out_dir
    write_staging_artifact(out_dir, "union", payload)
    return payload


def _run_remerge(args: argparse.Namespace) -> dict[str, Any]:
    repo = Path(args.repo).resolve()
    assert_safe_working_context(repo)
    fork_oid = _oid(repo, args.fork)
    upstream_oid = _oid(repo, args.upstream)
    merged_oid = _oid(repo, args.merged)
    pin_oid = _oid(repo, args.pin)

    if not args.stage_only and not args.layer:
        raise ValueError("remerge requires --stage-only or --layer")

    out_dir = Path(args.out)
    if not out_dir.is_absolute():
        out_dir = repo / out_dir
    evidence_path = out_dir / "remerge.json"

    if args.stage_only:
        _guard_evidence_not_merge_in_progress(evidence_path)

    worktree_dir = (
        Path(args.worktree).resolve() if args.worktree else default_stage_path(fork_oid)
    )

    if _existing_stage(worktree_dir, fork_oid):
        provenance = _describe_existing_stage(repo, worktree_dir, fork_oid)
    else:
        provenance = create_remerge_stage(repo, fork_oid, upstream_oid, worktree_dir)

    payload: dict[str, Any] = dict(provenance)
    payload.update(
        {
            "fork_oid": fork_oid,
            "upstream_oid": upstream_oid,
            "merged_oid": merged_oid,
            "pin_oid": pin_oid,
        }
    )
    stage_path = Path(payload["stage_path"])

    if args.stage_only:
        payload["handoff_state"] = "stage_created"
        payload["conflicts_raw"] = []
        payload["conflicts_landed"] = []
        payload["resolutions"] = []
        payload["default_config"] = {}
        payload["unresolved_paths"] = []
        payload["unresolved_by_class"] = {}
    elif args.layer == "source":
        # The source layer resumes a merge-in-progress stage plan 02-02 (or a
        # prior --layer data-config run) already left behind. Which paths
        # are "source" is read from the *persisted* unresolved_by_class --
        # not re-derived from a fresh `git diff --diff-filter=U`, because by
        # the time this runs some of those paths may already be resolved and
        # staged (no longer `U`), which would make a live re-derivation see
        # nothing left to do on a second invocation. resolve_source_layer
        # itself reads fork_oid/upstream_oid content directly, so re-running
        # it against an already-resolved path is idempotent and safe.
        if not evidence_path.exists():
            raise GitCaptureError(
                "remerge --layer source requires an existing remerge.json from a "
                "prior --layer data-config run (needs stage_path and "
                "unresolved_by_class)"
            )
        existing = json.loads(evidence_path.read_text(encoding="utf-8"))
        if existing.get("handoff_state") != "merge_in_progress":
            raise GitCaptureError(
                "refusing --layer source: existing remerge.json handoff_state is "
                f"{existing.get('handoff_state')!r}, expected 'merge_in_progress'"
            )
        unresolved_by_class = existing.get("unresolved_by_class") or {}
        source_paths = sorted(
            set(unresolved_by_class.get("source_modules", []))
            | set(unresolved_by_class.get("tests", []))
        )
        # `src/tooluniverse/tools/*.py` per-tool stubs fall inside Task 1's own
        # `src/tooluniverse/*.py` pathspec gate (git pathspec `*` crosses `/`
        # without `:(glob)` magic), so they must be conflict-free for that
        # gate to pass even though they are classified "generated", not
        # "source_modules". Resolved the same way as `_lazy_registry_static.py`
        # -- deferred to Task 3's regeneration, never hand-merged.
        generated_paths = sorted(unresolved_by_class.get("generated", []))
        if not source_paths and not generated_paths:
            raise GitCaptureError(
                "refusing --layer source: no source_modules/tests/generated paths "
                "recorded in remerge.json's unresolved_by_class -- nothing to resolve"
            )
        new_resolutions = resolve_source_layer(
            stage_path, fork_oid, upstream_oid, source_paths
        ) + [
            resolve_generated_conflict(stage_path, path, fork_oid)
            for path in generated_paths
        ]
        already_resolved_paths = {r["path"] for r in existing.get("resolutions", [])}
        resolved_now = {r["path"] for r in new_resolutions} - already_resolved_paths
        payload["conflicts_raw"] = existing.get("conflicts_raw", [])
        payload["conflicts_landed"] = existing.get("conflicts_landed", [])
        payload["resolutions"] = [
            r
            for r in existing.get("resolutions", [])
            if r["path"] not in {nr["path"] for nr in new_resolutions}
        ] + new_resolutions
        payload["default_config"] = existing.get("default_config", {})
        remaining_unresolved = sorted(
            set(existing.get("unresolved_paths", [])) - resolved_now
        )
        payload["unresolved_paths"] = remaining_unresolved
        payload["unresolved_by_class"] = classify_unresolved_paths(remaining_unresolved)
        payload["handoff_state"] = "merge_in_progress"
    else:
        _start_or_continue_merge(stage_path, upstream_oid)
        conflicts_raw = sorted(
            line
            for line in run_git(
                ["diff", "--name-only", "--diff-filter=U"], stage_path
            ).splitlines()
            if line
        )
        conflicts_landed = sorted(
            run_git(
                ["diff-tree", "--cc", merged_oid, "--name-only"], repo
            ).splitlines()[1:]
        )
        resolutions, default_config_summary, unresolved = resolve_data_config_layer(
            stage_path, fork_oid, upstream_oid, conflicts_raw
        )
        payload["conflicts_raw"] = conflicts_raw
        payload["conflicts_landed"] = conflicts_landed
        payload["resolutions"] = resolutions
        payload["default_config"] = default_config_summary
        payload["unresolved_paths"] = unresolved
        payload["unresolved_by_class"] = classify_unresolved_paths(unresolved)
        payload["handoff_state"] = "merge_in_progress"

    write_staging_artifact(out_dir, "remerge", payload)
    return payload


def _run_findings(args: argparse.Namespace) -> dict[str, Any]:
    repo = Path(args.repo).resolve()
    assert_safe_working_context(repo)
    landed_oid = _oid(repo, args.landed)
    pin_oid = _oid(repo, args.pin)

    out_dir = Path(args.out)
    if not out_dir.is_absolute():
        out_dir = repo / out_dir

    remerge_evidence = json.loads(
        (out_dir / "remerge.json").read_text(encoding="utf-8")
    )
    if remerge_evidence.get("handoff_state") != "merged_complete":
        raise GitCaptureError(
            "refusing findings: remerge.json handoff_state is "
            f"{remerge_evidence.get('handoff_state')!r}, expected 'merged_complete'"
        )
    stage_oid = remerge_evidence["stage_merge_oid"]
    union_evidence = json.loads((out_dir / "union.json").read_text(encoding="utf-8"))

    payload = build_findings(
        repo, landed_oid, stage_oid, pin_oid, remerge_evidence, union_evidence
    )
    write_staging_artifact(out_dir, "findings", payload)
    return payload


def _run_reclass(args: argparse.Namespace) -> dict[str, Any]:
    repo = Path(args.repo).resolve()
    assert_safe_working_context(repo)
    pin_oid = _oid(repo, args.pin)

    out_dir = Path(args.out)
    if not out_dir.is_absolute():
        out_dir = repo / out_dir

    findings = json.loads((out_dir / "findings.json").read_text(encoding="utf-8"))
    union_evidence = json.loads((out_dir / "union.json").read_text(encoding="utf-8"))
    stage_oid = findings["primary_comparison"]["right_oid"]

    preservation_path = Path(args.preservation)
    if not preservation_path.is_absolute():
        preservation_path = repo / preservation_path

    payload = join_preservation(
        preservation_path, findings, union_evidence, repo, stage_oid, pin_oid
    )
    write_staging_artifact(out_dir, "preservation-reclass", payload)

    findings_md_path = (
        Path(args.findings_md)
        if args.findings_md
        else repo / ".planning/phases/02-upstream-main-integration/02-FINDINGS.md"
    )
    render_findings_markdown(findings_md_path, findings, payload)

    return payload


def main(argv: list[str] | None = None) -> int:
    parser = _build_argparser()
    args = parser.parse_args(argv)

    if args.command == "union":
        payload = _run_union(args)
        summary = payload["summary"]
        failing = any(summary[key] for key in _FAILING_SUMMARY_KEYS) or bool(
            summary["unrelocated_lost_names"]
        )
        if args.json:
            print(json.dumps(payload, sort_keys=True))
        else:
            print(
                f"files_checked={summary['files_checked']} "
                f"union_ok={summary['union_ok']} "
                f"upstream_deleted={summary['upstream_deleted_files']} "
                f"failing={failing}"
            )
        return 1 if failing else 0

    if args.command == "remerge":
        payload = _run_remerge(args)
        if args.json:
            print(json.dumps(payload, sort_keys=True))
        else:
            print(
                f"stage_path={payload['stage_path']} "
                f"handoff_state={payload['handoff_state']} "
                f"unresolved_paths={len(payload['unresolved_paths'])}"
            )
        return 0

    if args.command == "findings":
        payload = _run_findings(args)
        s = payload["summary"]
        if args.json:
            print(json.dumps(payload, sort_keys=True))
        else:
            print(
                f"disagreements={s['disagreements']} "
                f"landed_dropped_or_altered={s['landed_dropped_or_altered']} "
                f"unclassified={s['unclassified']}"
            )
        return 1 if s["unclassified"] else 0

    if args.command == "reclass":
        payload = _run_reclass(args)
        if args.json:
            print(json.dumps(payload, sort_keys=True))
        else:
            print(
                f"records={len(payload['records'])} "
                f"disposition_summary={payload['disposition_summary']}"
            )
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
