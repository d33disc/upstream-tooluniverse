from __future__ import annotations

import argparse
import json
import importlib.util
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).parents[2] / "scripts/capture_sync_baseline.py"
_SPEC = importlib.util.spec_from_file_location("capture_sync_baseline_ci", _SCRIPT)
_MODULE = importlib.util.module_from_spec(_SPEC)
assert _SPEC and _SPEC.loader
_SPEC.loader.exec_module(_MODULE)
EXPECTED_CI_JOB_NAMES = _MODULE.EXPECTED_CI_JOB_NAMES
GitCaptureError = _MODULE.GitCaptureError
collect_ci_evidence = _MODULE.collect_ci_evidence
validate_ci_jobs = _MODULE.validate_ci_jobs
validate_capture_mode = _MODULE.validate_capture_mode
main = _MODULE.main


def _args(**overrides):
    values = {
        "repo": "/repo",
        "worktree_dir": "/tmp/worktree",
        "output_dir": None,
        "ci_evidence": None,
        "publish_root": None,
        "result_json": None,
    }
    values.update(overrides)
    return argparse.Namespace(**values)


def test_workflow_declares_exact_matrix_and_312_comprehensive_lane():
    workflow = Path(__file__).parents[2] / ".github/workflows/tests.yml"
    text = workflow.read_text(encoding="utf-8")
    for version in ("3.10", "3.11", "3.12", "3.13", "3.14"):
        assert f"'{version}'" in text
        assert f"Python ${{{{ matrix.python-version }}}} compatibility" in text
    assert "if: matrix.python-version == '3.12'" in text
    assert "workflow_dispatch:" not in text
    assert "test-results-${{ matrix.python-version }}" in text


def test_validate_ci_jobs_accepts_exact_success_set():
    run = {
        "headSha": "a" * 40,
        "conclusion": "success",
        "jobs": [
            {"name": name, "status": "completed", "conclusion": "success"}
            for name in EXPECTED_CI_JOB_NAMES
        ],
    }
    result = validate_ci_jobs(run)
    assert result["comprehensive_job"] == "Python 3.12 compatibility"


@pytest.mark.parametrize(
    "jobs",
    [
        [],
        [{"name": EXPECTED_CI_JOB_NAMES[0], "status": "completed", "conclusion": "success"}],
        [
            {"name": name, "status": "completed", "conclusion": "success"}
            for name in EXPECTED_CI_JOB_NAMES
        ]
        + [{"name": EXPECTED_CI_JOB_NAMES[0], "status": "completed", "conclusion": "success"}],
        [
            {"name": name, "status": "completed", "conclusion": "success" if i else "failure"}
            for i, name in enumerate(EXPECTED_CI_JOB_NAMES)
        ],
    ],
)
def test_validate_ci_jobs_fails_closed(jobs):
    with pytest.raises(GitCaptureError):
        validate_ci_jobs({"headSha": "a" * 40, "jobs": jobs})


def test_collect_ci_evidence_requires_exact_head_and_uses_argv():
    calls = []
    responses = [
        (0, json.dumps([{"databaseId": 7, "headSha": "a" * 40}]), ""),
        (0, "", ""),
        (0, json.dumps({"headSha": "a" * 40, "conclusion": "success", "jobs": [
            {"name": name, "status": "completed", "conclusion": "success"}
            for name in EXPECTED_CI_JOB_NAMES
        ]}), ""),
    ]

    def command(argv, timeout=0):
        calls.append((argv, timeout))
        return responses.pop(0)

    result = collect_ci_evidence("/repo", "a" * 40, command)
    assert result["headSha"] == "a" * 40
    assert all(isinstance(argv, list) for argv, _ in calls)
    assert calls[0][0][:5] == ["gh", "run", "list", "--repo", "/repo"]
    assert calls[1][0][:3] == ["gh", "run", "watch"]


def test_collect_ci_evidence_rejects_stale_or_ambiguous_runs():
    def stale(argv, timeout=0):
        return 0, json.dumps([{"databaseId": 1, "headSha": "b" * 40}]), ""

    with pytest.raises(GitCaptureError):
        collect_ci_evidence("/repo", "a" * 40, stale)


def test_capture_modes_are_exactly_disposable_or_final():
    validate_capture_mode(_args(output_dir="/tmp/evidence"))
    validate_capture_mode(_args(ci_evidence="/tmp/ci", publish_root="/tmp/pub", result_json="/tmp/result"))
    invalid = [
        _args(),
        _args(ci_evidence="/tmp/ci"),
        _args(ci_evidence="/tmp/ci", publish_root="/tmp/pub"),
        _args(output_dir="/tmp/e", ci_evidence="/tmp/ci"),
        _args(output_dir="/tmp/e", publish_root="/tmp/pub"),
        _args(output_dir="/tmp/e", result_json="/tmp/result"),
    ]
    for args in invalid:
        with pytest.raises(ValueError):
            validate_capture_mode(args)


def test_parser_rejects_mode_less_and_partial_invocations():
    for argv in (
        ["--repo", "/repo", "--worktree-dir", "/tmp/w"],
        ["--repo", "/repo", "--worktree-dir", "/tmp/w", "--ci-evidence", "/tmp/c"],
    ):
        with pytest.raises(SystemExit):
            main(argv)
