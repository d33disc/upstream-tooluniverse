#!/usr/bin/env python3
"""Capture a protected, reproducible Git baseline for ToolUniverse.

The capture command is intentionally disposable in this first phase.  It never
changes the caller's checkout; all mutable work is performed in a detached
secondary worktree and caller-provided output directory.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable

PR161_MERGE = "16af425c053c306a658c96e254b4c4114338dd11"
PRESERVATION_CLASSES = (
    "custom_code", "tool_definition", "plugin_asset", "skill", "test",
    "workflow", "documentation", "generated_asset", "planning",
    "other_review_required",
)
FINAL_FLAGS = ("ci_evidence", "publish_root", "result_json")


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
    untracked = [r[2:] if r.startswith("??") else r for r in _nul_records(status_raw) if r.startswith("??")]
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
    for rec in _nul_records(raw):
        parts = rec.split("\t", 1)
        if len(parts) != 2:
            continue
        meta, path = parts
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
