from __future__ import annotations

import importlib.util
import json
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
create_remerge_stage = _MODULE.create_remerge_stage
resolve_data_json_conflict = _MODULE.resolve_data_json_conflict
union_default_config_keys = _MODULE.union_default_config_keys
classify_unresolved_path = _MODULE.classify_unresolved_path


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


# ---------------------------------------------------------------------------
# create_remerge_stage against a synthetic repository (plan 02-02 Task 1)
# ---------------------------------------------------------------------------


def _build_two_branch_repo(tmp_path: Path) -> tuple[Path, str, str]:
    r = repo(tmp_path)
    (r / "shared.json").write_text("[]\n")
    base = _commit(r, "base")

    git(r, "checkout", "-b", "fork-side")
    (r / "shared.json").write_text('[{"name": "fork"}]\n')
    fork_oid = _commit(r, "fork edit")

    git(r, "checkout", base, "-b", "upstream-side")
    (r / "shared.json").write_text('[{"name": "upstream"}]\n')
    upstream_oid = _commit(r, "upstream edit")

    return r, fork_oid, upstream_oid


def test_create_remerge_stage_refuses_nested_target(tmp_path: Path) -> None:
    r, fork_oid, upstream_oid = _build_two_branch_repo(tmp_path)
    nested = r / "nested-stage"
    with pytest.raises(ValueError):
        create_remerge_stage(r, fork_oid, upstream_oid, nested, excluded_paths=[])


def test_create_remerge_stage_refuses_non_empty_target(tmp_path: Path) -> None:
    r, fork_oid, upstream_oid = _build_two_branch_repo(tmp_path)
    target = tmp_path / "stage"
    target.mkdir()
    (target / "junk.txt").write_text("occupied")
    with pytest.raises(FileExistsError):
        create_remerge_stage(r, fork_oid, upstream_oid, target, excluded_paths=[])


def test_create_remerge_stage_leaves_repo_untouched(tmp_path: Path) -> None:
    r, fork_oid, upstream_oid = _build_two_branch_repo(tmp_path)
    target = tmp_path / "stage"
    result = create_remerge_stage(r, fork_oid, upstream_oid, target, excluded_paths=[])
    assert result["repo_head_before"] == result["repo_head_after"]
    assert result["repo_branch_before"] == result["repo_branch_after"]
    assert result["repo_status_before"] == result["repo_status_after"]
    assert git(r, "rev-parse", "HEAD") == result["repo_head_after"]


def test_create_remerge_stage_stage_head_equals_fork_oid(tmp_path: Path) -> None:
    r, fork_oid, upstream_oid = _build_two_branch_repo(tmp_path)
    target = tmp_path / "stage"
    result = create_remerge_stage(r, fork_oid, upstream_oid, target, excluded_paths=[])
    assert result["stage_head"] == fork_oid
    assert result["stage_status"] == []
    assert result["stage_path"] == str(target.resolve())


def test_create_remerge_stage_excludes_preexisting_paths(tmp_path: Path) -> None:
    r, fork_oid, upstream_oid = _build_two_branch_repo(tmp_path)
    target = tmp_path / "stage"
    result = create_remerge_stage(
        r, fork_oid, upstream_oid, target, excluded_paths=["some/untracked/path.json"]
    )
    assert result["excluded_preexisting"] == [
        {"path": "some/untracked/path.json", "present_in_stage": False}
    ]


# ---------------------------------------------------------------------------
# resolve_data_json_conflict (plan 02-02 Task 2/3)
# ---------------------------------------------------------------------------


def _build_json_conflict_repo(
    tmp_path: Path,
    fork_entries: list,
    upstream_entries: list,
    path: str = "shared.json",
) -> tuple[Path, str, str]:
    r = repo(tmp_path)
    (r / path).write_text("[]\n")
    base = _commit(r, "base")

    git(r, "checkout", "-b", "fork-side")
    (r / path).write_text(json.dumps(fork_entries))
    fork_oid = _commit(r, "fork edit")

    git(r, "checkout", base, "-b", "upstream-side")
    (r / path).write_text(json.dumps(upstream_entries))
    upstream_oid = _commit(r, "upstream edit")

    git(r, "checkout", fork_oid)
    return r, fork_oid, upstream_oid


def test_resolve_data_json_conflict_prefers_upstream_on_shared_name(
    tmp_path: Path,
) -> None:
    fork_entries = [{"name": "a", "version": "fork"}, {"name": "b", "version": "fork"}]
    upstream_entries = [
        {"name": "a", "version": "upstream"},
        {"name": "c", "version": "upstream"},
    ]
    r, fork_oid, upstream_oid = _build_json_conflict_repo(
        tmp_path, fork_entries, upstream_entries
    )

    result = resolve_data_json_conflict(r, "shared.json", fork_oid, upstream_oid)

    written = json.loads((r / "shared.json").read_text())
    assert written == [
        {"name": "a", "version": "upstream"},
        {"name": "b", "version": "fork"},
        {"name": "c", "version": "upstream"},
    ]
    assert result["rule"] == "entry_union"
    assert result["union_verdict"] == "union_ok"


def test_resolve_data_json_conflict_byte_identical_regardless_of_array_order(
    tmp_path: Path,
) -> None:
    upstream_entries = [{"name": "c"}]
    (tmp_path / "r1").mkdir()
    (tmp_path / "r2").mkdir()
    r1, fork1, up1 = _build_json_conflict_repo(
        tmp_path / "r1", [{"name": "a"}, {"name": "b"}], upstream_entries
    )
    r2, fork2, up2 = _build_json_conflict_repo(
        tmp_path / "r2", [{"name": "b"}, {"name": "a"}], upstream_entries
    )

    resolve_data_json_conflict(r1, "shared.json", fork1, up1)
    resolve_data_json_conflict(r2, "shared.json", fork2, up2)

    assert (r1 / "shared.json").read_bytes() == (r2 / "shared.json").read_bytes()


def test_resolve_data_json_conflict_raises_on_non_list_side(tmp_path: Path) -> None:
    r = repo(tmp_path)
    (r / "shared.json").write_text("[]\n")
    base = _commit(r, "base")

    git(r, "checkout", "-b", "fork-side")
    (r / "shared.json").write_text('"not an array"')
    fork_oid = _commit(r, "fork edit")

    git(r, "checkout", base, "-b", "upstream-side")
    (r / "shared.json").write_text(json.dumps([{"name": "a"}]))
    upstream_oid = _commit(r, "upstream edit")

    git(r, "checkout", fork_oid)
    with pytest.raises(ValueError):
        resolve_data_json_conflict(r, "shared.json", fork_oid, upstream_oid)


def test_resolve_data_json_conflict_upstream_deletion_records_relocation(
    tmp_path: Path,
) -> None:
    # search_relocated_names walks src/tooluniverse/data specifically, so
    # both the deleted and the relocated-to path must live under it.
    r = repo(tmp_path)
    data_dir = r / "src/tooluniverse/data"
    data_dir.mkdir(parents=True)
    deleted_path = "src/tooluniverse/data/deleted.json"
    relocated_path = "src/tooluniverse/data/broken_apis/relocated.json"
    (data_dir / "deleted.json").write_text("[]\n")
    base = _commit(r, "base")

    git(r, "checkout", "-b", "fork-side")
    (data_dir / "deleted.json").write_text(json.dumps([{"name": "lost_tool"}]))
    fork_oid = _commit(r, "fork edit")

    git(r, "checkout", base, "-b", "upstream-side")
    (data_dir / "deleted.json").unlink()
    (data_dir / "broken_apis").mkdir()
    (data_dir / "broken_apis" / "relocated.json").write_text(
        json.dumps([{"name": "lost_tool"}])
    )
    upstream_oid = _commit(r, "upstream deletes and relocates")

    git(r, "checkout", fork_oid)
    result = resolve_data_json_conflict(r, deleted_path, fork_oid, upstream_oid)

    assert result["rule"] == "upstream_deleted"
    assert result["relocated_to"]["lost_tool"] == [relocated_path]
    assert not (r / deleted_path).exists()


# ---------------------------------------------------------------------------
# union_default_config_keys (plan 02-02 Task 2/3)
# ---------------------------------------------------------------------------

FORK_DEFAULT_CONFIG_SRC = """
default_tool_files = {
    "special_tools": "data/special_tools.json",
    "shared_tool": "data/shared_fork.json",
}
"""
UPSTREAM_DEFAULT_CONFIG_SRC = """
default_tool_files = {
    "shared_tool": "data/shared_upstream.json",
    "new_tool": "data/new_tool.json",
}
"""
NON_DICT_LITERAL_DEFAULT_CONFIG_SRC = """
def _build():
    return {}


default_tool_files = _build()
"""


def test_union_default_config_keys_returns_key_union() -> None:
    result = union_default_config_keys(
        FORK_DEFAULT_CONFIG_SRC, UPSTREAM_DEFAULT_CONFIG_SRC
    )
    assert set(result["merged_dict"]) == {"special_tools", "shared_tool", "new_tool"}
    assert result["key_union_ok"] is True
    assert result["fork_key_count"] == 2
    assert result["upstream_key_count"] == 2
    assert result["shared_key_count"] == 1
    assert result["merged_key_count"] == 3


def test_union_default_config_keys_shared_key_takes_upstream_value_and_records_collision() -> (
    None
):
    result = union_default_config_keys(
        FORK_DEFAULT_CONFIG_SRC, UPSTREAM_DEFAULT_CONFIG_SRC
    )
    assert result["merged_dict"]["shared_tool"] == '"data/shared_upstream.json"'
    assert result["value_collisions"] == [
        {
            "key": "shared_tool",
            "fork_value": '"data/shared_fork.json"',
            "upstream_value": '"data/shared_upstream.json"',
        }
    ]


def test_union_default_config_keys_rejects_non_dict_literal_assignment() -> None:
    with pytest.raises(ValueError):
        union_default_config_keys(
            NON_DICT_LITERAL_DEFAULT_CONFIG_SRC, UPSTREAM_DEFAULT_CONFIG_SRC
        )


def test_union_default_config_keys_handles_call_node_values() -> None:
    # Mirrors the real src/tooluniverse/default_config.py shape: values are
    # os.path.join(...) calls, which ast.literal_eval cannot and must not
    # evaluate. Only keys are literal-eval'd; values are kept as source text.
    fork_src = (
        "import os\n"
        "current_dir = '.'\n"
        "default_tool_files = {\n"
        '    "a": os.path.join(current_dir, "data", "a.json"),\n'
        "}\n"
    )
    upstream_src = (
        "import os\n"
        "current_dir = '.'\n"
        "default_tool_files = {\n"
        '    "b": os.path.join(current_dir, "data", "b.json"),\n'
        "}\n"
    )
    result = union_default_config_keys(fork_src, upstream_src)
    assert result["key_union_ok"] is True
    assert set(result["merged_dict"]) == {"a", "b"}


# ---------------------------------------------------------------------------
# classify_unresolved_path (plan 02-02 Task 2 -- the raw-vs-landed gap)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "path,expected",
    [
        ("plugin/skills/tooluniverse-sdk~HEAD", "symlink_workspaces"),
        ("plugin/skills/setup-tooluniverse~HEAD", "symlink_workspaces"),
        ("src/tooluniverse/tools/UniProt_get_entry_by_accession.py", "generated"),
        ("tests/unit/test_agentic_tool_env_vars.py", "tests"),
        ("src/tooluniverse/agentic_tool.py", "source_modules"),
        ("uv.lock", "packaging"),
        ("plugin/.mcp.json", "packaging"),
        (".claude-plugin/marketplace.json", "packaging"),
        ("scripts/build-plugin.sh", "packaging"),
        (".github/workflows/release-plugin.yml", "ci_docs"),
        ("docs/guide/tools.rst", "ci_docs"),
        ("skills/tooluniverse/REFERENCE.md", "ci_docs"),
        ("README.md", "ci_docs"),
        ("some/entirely/unforeseen/path.txt", "other"),
    ],
)
def test_classify_unresolved_path(path: str, expected: str) -> None:
    assert classify_unresolved_path(path) == expected
