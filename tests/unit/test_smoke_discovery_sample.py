"""Unit coverage for scripts/smoke_discovery_sample.py's pure selection and
verdict logic.

Loads the module under test via ``importlib.util.spec_from_file_location``
(``scripts/`` has no ``__init__.py``, so a plain import fails -- same idiom
as ``tests/unit/test_sync_baseline_git.py``). Every fixture is built by
hand: grep-result/info-result dicts constructed in-line, and a real
``tmp_path`` mini git repository for ``select_sample``. No ``tooluniverse``
package import and no ``ToolUniverse`` instantiation anywhere in this file
-- both functions under test are pure and must be provable without either,
exactly as Phase 2 proved ``assert_probe_contract`` in
``tests/unit/test_probe_custom_tools.py``.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "smoke_discovery_sample",
    Path(__file__).parents[2] / "scripts" / "smoke_discovery_sample.py",
)
_MODULE = importlib.util.module_from_spec(_SPEC)
assert _SPEC and _SPEC.loader
_SPEC.loader.exec_module(_MODULE)

classify_discovery = _MODULE.classify_discovery
select_sample = _MODULE.select_sample
POOL_CAP = _MODULE.POOL_CAP


# ---------------------------------------------------------------------------
# classify_discovery -- pure verdict function, hand-built fixtures only.
# ---------------------------------------------------------------------------

FOUND_WITH_SCHEMA = {"found": True, "match_count": 1, "match_names": ["Tool"]}
NOT_FOUND = {"found": False, "match_count": 0, "match_names": []}

SCHEMA_OK = {
    "gated": False,
    "missing_keys": [],
    "has_schema": True,
    "parameter_names": ["a"],
}
SCHEMA_MISSING = {
    "gated": False,
    "missing_keys": [],
    "has_schema": False,
    "parameter_names": [],
}
INFO_GATED = {
    "gated": True,
    "missing_keys": ["USPTO_API_KEY"],
    "has_schema": False,
    "parameter_names": [],
    "error": "requires API key(s) not set: USPTO_API_KEY",
}


@pytest.mark.parametrize(
    "grep_result, info_result, gated_keys, expected_verdict",
    [
        pytest.param(
            FOUND_WITH_SCHEMA, SCHEMA_OK, None, "pass", id="found-plus-schema-is-pass"
        ),
        pytest.param(
            NOT_FOUND,
            INFO_GATED,
            None,
            "gated",
            id="info-gated-error-object-is-gated",
        ),
        pytest.param(
            NOT_FOUND,
            {},
            ["USPTO_API_KEY"],
            "gated",
            id="gated-mapping-hit-is-gated-even-when-grep-empty",
        ),
        pytest.param(
            NOT_FOUND, SCHEMA_MISSING, None, "fail", id="not-found-no-gating-is-fail"
        ),
        pytest.param(
            FOUND_WITH_SCHEMA,
            SCHEMA_MISSING,
            None,
            "fail",
            id="no-parameter-or-parameters-key-is-fail",
        ),
    ],
)
def test_classify_discovery_verdict_table(
    grep_result, info_result, gated_keys, expected_verdict
):
    result = classify_discovery(grep_result, info_result, gated_keys)
    assert result["verdict"] == expected_verdict


def test_classify_discovery_empty_result_with_no_gating_signal_is_fail_never_pass():
    """Named regression guard for the empty-result rejection.

    An empty grep result and an empty info result, with no gating signal
    at all, must classify as ``fail`` -- never ``pass``. This repository
    has a recorded history (the literature-search OverallSummaryAgent
    incident) of an empty result silently masquerading as success past a
    health gate; Phase 2 plan 02-05 added the same-shaped named guard for
    ``assert_probe_contract`` in ``tests/unit/test_probe_custom_tools.py``.
    """
    result = classify_discovery({}, {}, None)
    assert result["verdict"] == "fail"
    assert result["verdict"] != "pass"


def test_classify_discovery_none_inputs_are_treated_as_empty_and_fail():
    result = classify_discovery(None, None, None)
    assert result["verdict"] == "fail"


def test_classify_discovery_gated_verdict_carries_missing_key_names():
    from_info_object = classify_discovery(NOT_FOUND, INFO_GATED, None)
    assert from_info_object["missing_keys"] == ["USPTO_API_KEY"]

    from_gated_mapping = classify_discovery(
        NOT_FOUND, {}, ["OTHER_KEY", "USPTO_API_KEY"]
    )
    assert from_gated_mapping["missing_keys"] == ["OTHER_KEY", "USPTO_API_KEY"]


# ---------------------------------------------------------------------------
# select_sample -- real tmp_path mini git repository, real git commits.
#
# select_sample's pool-2 path shells out to `git show <oid>:<path>`, so a
# mocked git response would not exercise the real code path. Same house
# pattern as tests/unit/test_sync_baseline_git.py's `repo()` helper: a
# genuine tiny repo with repo-local git config and real commits.
# ---------------------------------------------------------------------------


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=repo, text=True, capture_output=True, check=True
    ).stdout.strip()


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


@pytest.fixture
def mini_repo(tmp_path: Path) -> dict:
    """A tiny real git repository shaped enough like ToolUniverse's layout
    for ``select_sample`` to run against end-to-end.

    Pool 1 (preserved-custom): 7 names across the two hand-resolved
    data/*.json files, deliberately mirroring the real repository's own
    result -- 6 in ``literature_search_tools.json`` (``ZAgent``..``DAgent``)
    plus 1 in ``uspto_tools.json`` (``USPTO_get_thing``) -- so that a flat
    global sort-then-cap-5 keeps the five alphabetically-first literature
    names and excludes the USPTO one, the same shape Task 1's live run
    produced against the real catalog. select_sample reads pool 1 straight
    off disk, so these files need not be committed.

    Pool 2 (new-upstream): one real file committed twice -- a "fork"
    commit with one name, then an "upstream" commit adding seven more --
    so ``select_sample`` re-derives the seven new names via two
    `git show <oid>:<path>` calls and the cap keeps the first five, sorted.
    Three additional union.json file entries exercise the three pool-2
    anomaly filters (verdict != union_ok, merged_name_count !=
    upstream_name_count, and the broken_apis/ path exclusion) without
    needing real blobs for those paths, since select_sample's filters
    reject them before ever shelling out to git for those entries.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test")

    _write_json(
        repo / "src/tooluniverse/data/literature_search_tools.json",
        [
            {"name": n}
            for n in ["ZAgent", "AAgent", "MAgent", "BAgent", "CAgent", "DAgent"]
        ],
    )
    _write_json(
        repo / "src/tooluniverse/data/uspto_tools.json",
        [{"name": "USPTO_get_thing"}],
    )

    pool2_rel = "src/tooluniverse/data/pool2_tools.json"
    _write_json(repo / pool2_rel, [{"name": "SharedTool"}])
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "fork state")
    fork_oid = _git(repo, "rev-parse", "HEAD")

    new_names = [f"NewUpstreamTool{i}" for i in range(7)]
    _write_json(
        repo / pool2_rel, [{"name": "SharedTool"}] + [{"name": n} for n in new_names]
    )
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "upstream state")
    upstream_oid = _git(repo, "rev-parse", "HEAD")

    union = {
        "fork_oid": fork_oid,
        "upstream_oid": upstream_oid,
        "files": [
            {
                "path": pool2_rel,
                "fork_name_count": 1,
                "upstream_name_count": 1 + len(new_names),
                "merged_name_count": 1 + len(new_names),
                "duplicate_names": [],
                "extra_names": [],
                "missing_names": [],
                "verdict": "union_ok",
            },
            {
                # merged_name_count != upstream_name_count -- must be
                # skipped by the soundness filter, never reaches git show.
                "path": "src/tooluniverse/data/skip_me_mismatched.json",
                "fork_name_count": 1,
                "upstream_name_count": 3,
                "merged_name_count": 2,
                "duplicate_names": [],
                "extra_names": [],
                "missing_names": [],
                "verdict": "union_ok",
            },
            {
                # verdict != union_ok -- must be skipped outright.
                "path": "src/tooluniverse/data/skip_me_deleted.json",
                "fork_name_count": 0,
                "upstream_name_count": 0,
                "merged_name_count": 0,
                "duplicate_names": [],
                "extra_names": [],
                "missing_names": ["Whatever"],
                "verdict": "upstream_deleted",
            },
            {
                # broken_apis/ path -- must be excluded regardless of counts.
                "path": "src/tooluniverse/data/broken_apis/skip_me_broken.json",
                "fork_name_count": 1,
                "upstream_name_count": 5,
                "merged_name_count": 5,
                "duplicate_names": [],
                "extra_names": [],
                "missing_names": [],
                "verdict": "union_ok",
            },
        ],
    }
    union_path = tmp_path / "union.json"
    _write_json(union_path, union)

    return {
        "repo": repo,
        "union_path": union_path,
        "new_upstream_names": sorted(new_names),
    }


def test_select_sample_caps_pools_sorts_and_is_deterministic(mini_repo):
    result1 = select_sample(
        mini_repo["repo"], {}, union_json_path=mini_repo["union_path"]
    )
    result2 = select_sample(
        mini_repo["repo"], {}, union_json_path=mini_repo["union_path"]
    )

    assert result1 == result2  # identical output across calls on identical input

    preserved = [r for r in result1["sample"] if r["pool"] == "preserved-custom"]
    new_upstream = [r for r in result1["sample"] if r["pool"] == "new-upstream"]
    control = [r for r in result1["sample"] if r["pool"] == "offline-control"]

    assert len(preserved) == POOL_CAP
    preserved_names = [r["name"] for r in preserved]
    assert preserved_names == sorted(preserved_names)
    assert preserved_names == ["AAgent", "BAgent", "CAgent", "DAgent", "MAgent"]
    assert "USPTO_get_thing" not in preserved_names  # sorts 6th, excluded by the cap
    assert "ZAgent" not in preserved_names  # sorts 7th, excluded by the cap

    assert len(new_upstream) == POOL_CAP
    new_upstream_names = [r["name"] for r in new_upstream]
    assert new_upstream_names == sorted(new_upstream_names)
    assert new_upstream_names == mini_repo["new_upstream_names"][:POOL_CAP]

    assert len(control) == 1
    assert control[0]["name"] == _MODULE.OFFLINE_CONTROL_NAME

    assert result1["gated"] == []
    assert result1["emptied_pools"] == []


def test_select_sample_gated_exclusion_removes_names_without_backfill(mini_repo):
    """Named gated-exclusion test -- the single rule that keeps CAT-02
    from failing for a credential reason instead of a catalog reason
    (T-03-15): a gated name never appears in the returned sample, it does
    appear in the gated list with its missing key names, and no
    substitution silently backfills the vacated slot.
    """
    excluded = {
        "AAgent": ["SOME_API_KEY"],
        "NewUpstreamTool0": ["OTHER_KEY", "OTHER_KEY2"],
    }
    result = select_sample(
        mini_repo["repo"], excluded, union_json_path=mini_repo["union_path"]
    )

    sample_names = {r["name"] for r in result["sample"]}
    assert "AAgent" not in sample_names
    assert "NewUpstreamTool0" not in sample_names

    gated_by_name = {g["name"]: g for g in result["gated"]}
    assert set(gated_by_name) == {"AAgent", "NewUpstreamTool0"}
    assert gated_by_name["AAgent"]["missing_keys"] == ["SOME_API_KEY"]
    assert gated_by_name["NewUpstreamTool0"]["missing_keys"] == [
        "OTHER_KEY",
        "OTHER_KEY2",
    ]

    # No name appears in both sample and gated.
    assert sample_names.isdisjoint(gated_by_name)

    # No silent backfill: the pools shrink below the cap rather than being
    # topped back up with the next-sorted name that the cap had already
    # excluded (ZAgent/USPTO_get_thing for pool 1, NewUpstreamTool5 for
    # pool 2 -- neither entered the capped pool, so neither may appear now).
    preserved_names = [
        r["name"] for r in result["sample"] if r["pool"] == "preserved-custom"
    ]
    assert len(preserved_names) == POOL_CAP - 1
    assert "ZAgent" not in preserved_names
    assert "USPTO_get_thing" not in preserved_names

    new_upstream_names = [
        r["name"] for r in result["sample"] if r["pool"] == "new-upstream"
    ]
    assert len(new_upstream_names) == POOL_CAP - 1
    assert "NewUpstreamTool5" not in new_upstream_names

    assert result["emptied_pools"] == []  # neither pool was emptied entirely


def test_select_sample_records_emptied_pool_without_substituting(mini_repo):
    """select_sample records an emptied pool explicitly rather than
    substituting another name when gating removes every candidate."""
    excluded = {
        name: ["SOME_API_KEY"]
        for name in ["AAgent", "BAgent", "CAgent", "DAgent", "MAgent"]
    }
    result = select_sample(
        mini_repo["repo"], excluded, union_json_path=mini_repo["union_path"]
    )

    preserved = [r for r in result["sample"] if r["pool"] == "preserved-custom"]
    assert preserved == []

    emptied = {p["pool"] for p in result["emptied_pools"]}
    assert "preserved-custom" in emptied
    assert "new-upstream" not in emptied
    assert "offline-control" not in emptied

    # the 5 gated names are still recorded, not silently dropped
    assert {g["name"] for g in result["gated"]} == set(excluded)
