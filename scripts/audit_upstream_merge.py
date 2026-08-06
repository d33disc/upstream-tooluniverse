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
)

_PHASE1_GIT_JSON = (
    Path(__file__).resolve().parents[1]
    / ".planning/phases/01-protected-sync-baseline/evidence"
    / "21945440c9f2a15537ba878500a800d9e330eab0/git.json"
)

_LAZY_REGISTRY_PATH = "src/tooluniverse/_lazy_registry_static.py"

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
    remerge.add_argument("--layer", choices=["data-config"], default=None)
    remerge.add_argument(
        "--out",
        default=".planning/phases/02-upstream-main-integration/evidence/staging",
    )
    remerge.add_argument("--json", action="store_true")

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

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
