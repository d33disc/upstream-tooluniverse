from __future__ import annotations

import argparse
import importlib.util
import subprocess
from pathlib import Path

import pytest

_SPEC = importlib.util.spec_from_file_location("capture_sync_baseline", Path(__file__).parents[2] / "scripts/capture_sync_baseline.py")
_MODULE = importlib.util.module_from_spec(_SPEC)
assert _SPEC and _SPEC.loader
_SPEC.loader.exec_module(_MODULE)
GitCaptureError = _MODULE.GitCaptureError
capture_git_snapshot = _MODULE.capture_git_snapshot
classify_preservation_path = _MODULE.classify_preservation_path
collect_preservation_inventory = _MODULE.collect_preservation_inventory
create_isolated_worktree = _MODULE.create_isolated_worktree
inspect_symlink = _MODULE.inspect_symlink
prove_plugin_link_mapping = _MODULE.prove_plugin_link_mapping
validate_capture_mode = _MODULE.validate_capture_mode


def git(path: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=path, text=True, capture_output=True, check=True).stdout.strip()


def repo(tmp_path: Path) -> Path:
    r = tmp_path / "repo"
    r.mkdir()
    git(r, "init", "-b", "main")
    git(r, "config", "user.email", "test@example.com")
    git(r, "config", "user.name", "Test")
    (r / "tracked.txt").write_text("one\n")
    git(r, "add", ".")
    git(r, "commit", "-m", "initial")
    return r


def test_capture_snapshot_separates_state_and_full_oid(tmp_path: Path) -> None:
    r = repo(tmp_path)
    (r / "tracked.txt").write_text("two\n")
    (r / "unusual name.txt").write_text("untracked\n")
    git(r, "add", "tracked.txt")
    snap = capture_git_snapshot(r)
    assert len(snap["head"]) == 40
    assert snap["staged_records"]
    assert any("unusual name.txt" in p for p in snap["untracked_paths"])


def test_isolated_worktree_does_not_change_original(tmp_path: Path) -> None:
    r = repo(tmp_path)
    before = capture_git_snapshot(r)
    w = create_isolated_worktree(r, before["head"], tmp_path / "isolated")
    assert git(w, "rev-parse", "HEAD") == before["head"]
    git(r, "worktree", "remove", "--force", str(w))
    assert capture_git_snapshot(r)["status_records"] == before["status_records"]


def test_classification_and_symlink_never_traverse(tmp_path: Path) -> None:
    r = repo(tmp_path)
    (r / "target").write_text("secret")
    (r / "link").symlink_to("target")
    git(r, "add", "target", "link")
    info = inspect_symlink(r, {"path": "link", "mode": "120000", "blob_oid": "x"})
    assert info["link_text"] == "target"
    assert info["in_repo"] and info["exists"]
    assert classify_preservation_path("src/tool.py") == "custom_code"
    assert classify_preservation_path("unknown.bin") == "other_review_required"


def test_inventory_records_delta_and_untracked_metadata(tmp_path: Path) -> None:
    r = repo(tmp_path)
    upstream = git(r, "rev-parse", "HEAD")
    (r / "custom.py").write_text("x\n")
    (r / "ralph-specs").mkdir()
    (r / "ralph-specs" / "fleet.json").write_text("do not read")
    git(r, "add", ".")
    git(r, "commit", "fork")
    fork = git(r, "rev-parse", "HEAD")
    inv = collect_preservation_inventory(r, upstream, fork)
    assert any(p["path"] == "custom.py" for p in inv["paths"])
    assert any(p["path"].endswith("fleet.json") and p["metadata_only"] for p in inv["untracked"])


def test_parser_disposable_contract() -> None:
    base = dict(repo="/repo", worktree_dir="/tmp/w", output_dir="/tmp/o", ci_evidence=None, publish_root=None, result_json=None)
    validate_capture_mode(argparse.Namespace(**base))
    with pytest.raises(ValueError):
        validate_capture_mode(argparse.Namespace(**{**base, "output_dir": None}))
    with pytest.raises(ValueError):
        validate_capture_mode(argparse.Namespace(**{**base, "ci_evidence": "/tmp/e"}))


def test_plugin_mapping_requires_authoritative_ancestry(tmp_path: Path) -> None:
    r = repo(tmp_path)
    with pytest.raises(GitCaptureError):
        prove_plugin_link_mapping(r, git(r, "rev-parse", "HEAD"), {"a": "skills/missing"})
