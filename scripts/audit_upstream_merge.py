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
import hashlib
import importlib.util
import json
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

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
