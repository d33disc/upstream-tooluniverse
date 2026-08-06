from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "audit_upstream_merge",
    Path(__file__).parents[2] / "scripts/audit_upstream_merge.py",
)
_MODULE = importlib.util.module_from_spec(_SPEC)
assert _SPEC and _SPEC.loader
_SPEC.loader.exec_module(_MODULE)

classify_union = _MODULE.classify_union
tool_names = _MODULE.tool_names
tool_name_list = _MODULE.tool_name_list
derive_both_sides_paths = _MODULE.derive_both_sides_paths


def git(path: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=path, text=True, capture_output=True, check=True
    ).stdout.strip()


def repo(tmp_path: Path) -> Path:
    r = tmp_path / "repo"
    r.mkdir()
    git(r, "init", "-b", "main")
    return r


def _commit(r: Path, message: str) -> str:
    git(r, "add", ".")
    git(
        r,
        "-c",
        "user.name=Test",
        "-c",
        "user.email=test@example.com",
        "commit",
        "-m",
        message,
    )
    return git(r, "rev-parse", "HEAD")


# ---------------------------------------------------------------------------
# classify_union verdict table
# ---------------------------------------------------------------------------


UNION_OK_BASIC = (
    {"a", "b"},
    {"b", "c"},
    {"a", "b", "c"},
    (True, True, True),
    {"merged_name_list": ["a", "b", "c"]},
    "union_ok",
)
UNION_OK_REORDERED = (
    {"a", "b"},
    {"b", "c"},
    {"a", "b", "c"},
    (True, True, True),
    {"merged_name_list": ["c", "a", "b"]},
    "union_ok",
)
UNION_OK_EMPTY_EDGE = (
    set(),
    set(),
    set(),
    (True, True, True),
    {"merged_name_list": []},
    "union_ok",
)
NET_REMOVED_FORK = (
    {"a", "b"},
    {"c"},
    {"b", "c"},
    (True, True, True),
    {"merged_name_list": ["b", "c"]},
    "net_removed_fork_entry",
)
NET_REMOVED_UPSTREAM = (
    {"a"},
    {"b", "c"},
    {"a", "b"},
    (True, True, True),
    {"merged_name_list": ["a", "b"]},
    "net_removed_upstream_entry",
)
UNEXPECTED_ADDED = (
    {"a"},
    {"b"},
    {"a", "b", "z"},
    (True, True, True),
    {"merged_name_list": ["a", "b", "z"]},
    "unexpected_added_entry",
)
DUPLICATE_NAME = (
    {"a", "b"},
    {"a", "b"},
    {"a", "b"},
    (True, True, True),
    {"merged_name_list": ["a", "b", "a"]},
    "duplicate_name",
)
UPSTREAM_DELETED = (
    {"a", "b"},
    None,
    None,
    (True, False, False),
    {},
    "upstream_deleted",
)
FORK_DELETED = (
    None,
    {"a"},
    None,
    (False, True, False),
    {},
    "fork_deleted",
)
NOT_AN_ARRAY_STRING = (
    None,
    {"a"},
    {"a"},
    (True, True, True),
    {},
    "not_an_array",
)
NOT_AN_ARRAY_INT = (
    {"a"},
    None,
    {"a"},
    (True, True, True),
    {},
    "not_an_array",
)
UNPARSEABLE_FORK = (
    None,
    {"a"},
    {"a"},
    (True, True, True),
    {"unparseable": (True, False, False)},
    "unparseable",
)
UNPARSEABLE_MERGED = (
    {"a"},
    {"a"},
    None,
    (True, True, True),
    {"unparseable": (False, False, True)},
    "unparseable",
)


@pytest.mark.parametrize(
    "fork_names,upstream_names,merged_names,present,kwargs,expected",
    [
        pytest.param(
            *UNION_OK_BASIC[:4], UNION_OK_BASIC[4], UNION_OK_BASIC[5], id="union_ok"
        ),
        pytest.param(
            *UNION_OK_REORDERED[:4],
            UNION_OK_REORDERED[4],
            UNION_OK_REORDERED[5],
            id="union_ok_order_insensitive",
        ),
        pytest.param(
            *UNION_OK_EMPTY_EDGE[:4],
            UNION_OK_EMPTY_EDGE[4],
            UNION_OK_EMPTY_EDGE[5],
            id="union_ok_empty_edge",
        ),
        pytest.param(
            *NET_REMOVED_FORK[:4],
            NET_REMOVED_FORK[4],
            NET_REMOVED_FORK[5],
            id="net_removed_fork_entry",
        ),
        pytest.param(
            *NET_REMOVED_UPSTREAM[:4],
            NET_REMOVED_UPSTREAM[4],
            NET_REMOVED_UPSTREAM[5],
            id="net_removed_upstream_entry",
        ),
        pytest.param(
            *UNEXPECTED_ADDED[:4],
            UNEXPECTED_ADDED[4],
            UNEXPECTED_ADDED[5],
            id="unexpected_added_entry",
        ),
        pytest.param(
            *DUPLICATE_NAME[:4],
            DUPLICATE_NAME[4],
            DUPLICATE_NAME[5],
            id="duplicate_name",
        ),
        pytest.param(
            *UPSTREAM_DELETED[:4],
            UPSTREAM_DELETED[4],
            UPSTREAM_DELETED[5],
            id="upstream_deleted",
        ),
        pytest.param(
            *FORK_DELETED[:4], FORK_DELETED[4], FORK_DELETED[5], id="fork_deleted"
        ),
        pytest.param(
            *NOT_AN_ARRAY_STRING[:4],
            NOT_AN_ARRAY_STRING[4],
            NOT_AN_ARRAY_STRING[5],
            id="not_an_array_string",
        ),
        pytest.param(
            *NOT_AN_ARRAY_INT[:4],
            NOT_AN_ARRAY_INT[4],
            NOT_AN_ARRAY_INT[5],
            id="not_an_array_int",
        ),
        pytest.param(
            *UNPARSEABLE_FORK[:4],
            UNPARSEABLE_FORK[4],
            UNPARSEABLE_FORK[5],
            id="unparseable_fork",
        ),
        pytest.param(
            *UNPARSEABLE_MERGED[:4],
            UNPARSEABLE_MERGED[4],
            UNPARSEABLE_MERGED[5],
            id="unparseable_merged",
        ),
    ],
)
def test_classify_union_verdicts(
    fork_names, upstream_names, merged_names, present, kwargs, expected
) -> None:
    assert (
        classify_union(fork_names, upstream_names, merged_names, present, **kwargs)
        == expected
    )


def test_classify_union_covers_all_nine_verdicts() -> None:
    expected_verdicts = {
        "union_ok",
        "net_removed_fork_entry",
        "net_removed_upstream_entry",
        "unexpected_added_entry",
        "duplicate_name",
        "upstream_deleted",
        "fork_deleted",
        "not_an_array",
        "unparseable",
    }
    cases = [
        UNION_OK_BASIC,
        NET_REMOVED_FORK,
        NET_REMOVED_UPSTREAM,
        UNEXPECTED_ADDED,
        DUPLICATE_NAME,
        UPSTREAM_DELETED,
        FORK_DELETED,
        NOT_AN_ARRAY_STRING,
        UNPARSEABLE_FORK,
    ]
    produced = {
        classify_union(fork, upstream, merged, present, **kwargs)
        for fork, upstream, merged, present, kwargs, _expected in cases
    }
    assert produced == expected_verdicts


# ---------------------------------------------------------------------------
# tool_names / tool_name_list
# ---------------------------------------------------------------------------


def test_tool_names_skips_items_with_no_name_key() -> None:
    value = [{"name": "a"}, {"description": "no name field"}, {"name": "b"}]
    assert tool_names(value) == {"a", "b"}


def test_tool_names_wraps_bare_dict() -> None:
    assert tool_names({"name": "solo"}) == {"solo"}


def test_tool_names_returns_none_for_non_list_non_dict() -> None:
    assert tool_names("not an array") is None
    assert tool_names(42) is None
    assert tool_names(None) is None


def test_tool_name_list_preserves_repeated_names() -> None:
    value = [{"name": "a"}, {"name": "b"}, {"name": "a"}]
    assert tool_name_list(value) == ["a", "b", "a"]


# ---------------------------------------------------------------------------
# derive_both_sides_paths against a synthetic repository
# ---------------------------------------------------------------------------


def test_derive_both_sides_paths_against_synthetic_repo(tmp_path: Path) -> None:
    r = repo(tmp_path)
    (r / "shared.json").write_text("[]\n")
    (r / "fork_only.json").write_text("[]\n")
    base = _commit(r, "base")

    git(r, "checkout", "-b", "fork-side")
    (r / "shared.json").write_text('[{"name": "fork"}]\n')
    fork_oid = _commit(r, "fork edit")

    git(r, "checkout", base, "-b", "upstream-side")
    (r / "shared.json").write_text('[{"name": "upstream"}]\n')
    (r / "upstream_only.json").write_text("[]\n")
    upstream_oid = _commit(r, "upstream edit")

    expected_base = git(r, "merge-base", fork_oid, upstream_oid)
    assert expected_base == base

    returned_base, both_sides = derive_both_sides_paths(
        r, fork_oid, upstream_oid, expected_base=None
    )
    assert returned_base == base
    assert both_sides == ["shared.json"]


def test_derive_both_sides_paths_raises_on_base_mismatch(tmp_path: Path) -> None:
    r = repo(tmp_path)
    (r / "shared.json").write_text("[]\n")
    base = _commit(r, "base")

    git(r, "checkout", "-b", "fork-side")
    (r / "shared.json").write_text('[{"name": "fork"}]\n')
    fork_oid = _commit(r, "fork edit")

    git(r, "checkout", base, "-b", "upstream-side")
    (r / "shared.json").write_text('[{"name": "upstream"}]\n')
    upstream_oid = _commit(r, "upstream edit")

    with pytest.raises(_MODULE.GitCaptureError):
        derive_both_sides_paths(r, fork_oid, upstream_oid, expected_base="0" * 40)
