"""Unit coverage for scripts/audit_registration_chain.py's pure link-verdict,
category-parsing, and discovery-contract logic.

``classify_chain``, ``load_live_categories``, ``load_definitions``,
``audit_names``, and ``assert_discovery_contract`` are provable without
importing ``tooluniverse`` -- these tests build link-record dicts and a
``tmp_path`` mini repository by hand, matching the shapes the real functions
actually produce, and never instantiate ``ToolUniverse``. Mirrors
``tests/unit/test_probe_custom_tools.py``'s approach to
``assert_probe_contract`` for the same reason: the verdict and parsing logic
must be provable without the package.
"""

from __future__ import annotations

import json
import importlib.util
from pathlib import Path

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "audit_registration_chain",
    Path(__file__).parents[2] / "scripts" / "audit_registration_chain.py",
)
_MODULE = importlib.util.module_from_spec(_SPEC)
assert _SPEC and _SPEC.loader
_SPEC.loader.exec_module(_MODULE)

classify_chain = _MODULE.classify_chain
load_live_categories = _MODULE.load_live_categories
load_definitions = _MODULE.load_definitions
audit_names = _MODULE.audit_names
assert_discovery_contract = _MODULE.assert_discovery_contract


# ---------------------------------------------------------------------------
# classify_chain
# ---------------------------------------------------------------------------

_LINK_NAMES = (
    "definition",
    "implementation",
    "category",
    "lazy_metadata",
    "generated_module",
    "tests",
)


def _link(name: str, ok: bool, *, archived: bool = False) -> dict:
    record = {"link": name, "ok": ok, "evidence": f"fixture evidence for {name}"}
    if name == "category":
        record["archived"] = archived
    return record


def _six_links(*, missing: str | None = None, archived_category: bool = False) -> list:
    """All six links ok, except optionally one missing link or an archived category."""
    links = []
    for name in _LINK_NAMES:
        if name == "category" and archived_category:
            links.append(_link(name, ok=False, archived=True))
        else:
            links.append(_link(name, ok=(name != missing)))
    return links


@pytest.mark.parametrize(
    "links, gated, expected_verdict",
    [
        pytest.param(
            _six_links(),
            [],
            "intact",
            id="all_six_links_ok_no_unmet_keys_yields_intact",
        ),
        pytest.param(
            _six_links(missing="generated_module"),
            [],
            "broken",
            id="missing_link_no_required_keys_yields_broken",
        ),
        pytest.param(
            _six_links(archived_category=True),
            [],
            "archived",
            id="archived_category_yields_archived_not_broken",
        ),
        pytest.param(
            [],
            [],
            "broken",
            id="empty_links_list_yields_broken_not_vacuous_intact",
        ),
    ],
)
def test_classify_chain_verdicts(links, gated, expected_verdict):
    assert classify_chain(links, gated) == expected_verdict


def test_credential_gated_downgrade_missing_link_yields_gated_with_key_names():
    """Named per 03-01-PLAN.md Task 2: research proved ``load_tools`` silently
    skips tools whose ``required_api_keys`` are unmet, so a missing
    generated-module/__init__-import link on a tool with unmet keys must
    downgrade to 'gated', never 'broken' -- otherwise a full-catalog audit
    would manufacture roughly eighty false findings in Wave 2 out of a
    credential gap that isn't a chain break at all."""
    links = _six_links(missing="generated_module")
    verdict = classify_chain(links, gated=["USPTO_API_KEY"])
    assert verdict == "gated"


def test_archived_category_wins_over_gated_precedence():
    """Precedence check: classify_chain resolves 'archived' before it ever
    consults the gated list, so an intentionally excluded category is never
    misreported as a credential gap either."""
    links = _six_links(archived_category=True)
    links = [
        link if link["link"] != "generated_module" else _link("generated_module", False)
        for link in links
    ]
    assert classify_chain(links, gated=["SOME_KEY"]) == "archived"


# ---------------------------------------------------------------------------
# assert_discovery_contract -- the CAT-02 discovery-stage pure verdict.
# ---------------------------------------------------------------------------


def _discovery(
    *,
    grep_found: bool = True,
    schema_has_parameters: bool = True,
    gated: bool = False,
    missing_keys: list | None = None,
) -> dict:
    return {
        "grep_found": grep_found,
        "schema_has_parameters": schema_has_parameters,
        "gated": gated,
        "missing_keys": missing_keys or [],
    }


def test_empty_discovery_result_with_no_gating_signal_is_rejected_not_passed():
    """Named regression guard, same failure mode as
    test_probe_custom_tools.py::test_empty_list_result_with_no_gating_signal_is_rejected_not_passed
    (T-02-17): grep_tools finding nothing and get_tool_info returning no
    parameter schema, with no missing-credential signal, must be 'fail',
    never a silent pass -- this repository has a recorded history of an
    empty result masquerading as success past a health gate."""
    result = assert_discovery_contract(
        _discovery(grep_found=False, schema_has_parameters=False, gated=False)
    )
    assert result["verdict"] == "fail"
    assert "empty" in result["reason"].lower()


def test_discovery_gated_yields_gated_with_missing_key_names():
    result = assert_discovery_contract(
        _discovery(
            grep_found=False,
            schema_has_parameters=False,
            gated=True,
            missing_keys=["USPTO_API_KEY"],
        )
    )
    assert result["verdict"] == "gated"
    assert result["missing_keys"] == ["USPTO_API_KEY"]


def test_discovery_complete_result_yields_pass():
    result = assert_discovery_contract(_discovery())
    assert result["verdict"] == "pass"


# ---------------------------------------------------------------------------
# load_live_categories -- the three default_config.py entry forms.
# ---------------------------------------------------------------------------

# Mirrors src/tooluniverse/default_config.py's real shapes verbatim (same
# category names, same three-physical-line os.path.join form, same
# "Archived at:" marker convention) so this fixture stays a faithful analog
# rather than a guessed shape a real edit could silently drift away from.
_DEFAULT_CONFIG_FRAGMENT = """import os

current_dir = "/fake/dir"

default_tool_files = {
    "interpro_entry": os.path.join(current_dir, "data", "interpro_entry_tools.json"),
    "uniprot_proteomes": os.path.join(
        current_dir, "data", "uniprot_proteomes_tools.json"
    ),
    # EBI OxO - Ontology cross-reference mappings across biomedical databases
    # Archived at: src/tooluniverse/data/broken_apis/oxo_tools.json
    # EBI retired the OxO service (all endpoints hang); use OLS instead.
    # "oxo": os.path.join(current_dir, "data", "oxo_tools.json"),
}
"""


def _write_default_config(tmp_path: Path) -> Path:
    config_path = tmp_path / "default_config.py"
    config_path.write_text(_DEFAULT_CONFIG_FRAGMENT, encoding="utf-8")
    return config_path


def test_load_live_categories_single_line_entry_is_live(tmp_path):
    config_path = _write_default_config(tmp_path)
    live, archived = load_live_categories(config_path)
    assert live["interpro_entry"] == tmp_path / "data" / "interpro_entry_tools.json"
    assert "interpro_entry" not in archived


def test_load_live_categories_multiline_entry_spanning_three_lines_is_live(tmp_path):
    config_path = _write_default_config(tmp_path)
    live, archived = load_live_categories(config_path)
    assert (
        live["uniprot_proteomes"] == tmp_path / "data" / "uniprot_proteomes_tools.json"
    )
    assert "uniprot_proteomes" not in archived


def test_load_live_categories_commented_entry_with_archived_marker_is_archived(
    tmp_path,
):
    config_path = _write_default_config(tmp_path)
    live, archived = load_live_categories(config_path)
    assert "oxo" not in live
    assert archived["oxo"] == tmp_path / "data" / "oxo_tools.json"


# ---------------------------------------------------------------------------
# load_definitions -- exclusion, JSON-shape handling, sorted required keys.
# ---------------------------------------------------------------------------


def test_load_definitions_excludes_api_keys_catalog_and_handles_both_json_shapes(
    tmp_path,
):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "alpha_tools.json").write_text(
        json.dumps(
            [
                {
                    "name": "ZAlphaTool",
                    "type": "FixtureOnlyType",
                    "required_api_keys": ["Z_KEY", "A_KEY"],
                }
            ]
        ),
        encoding="utf-8",
    )
    (data_dir / "beta_tools.json").write_text(
        json.dumps({"name": "ABetaTool", "type": "FixtureOnlyType"}),
        encoding="utf-8",
    )
    (data_dir / "api_keys_catalog.json").write_text(
        json.dumps([{"name": "ShouldBeExcluded", "type": "FixtureOnlyType"}]),
        encoding="utf-8",
    )

    definitions = load_definitions(data_dir, recursive=False)

    assert "ShouldBeExcluded" not in definitions
    assert definitions["ZAlphaTool"][0]["required_api_keys"] == ["A_KEY", "Z_KEY"]
    assert definitions["ABetaTool"][0]["required_api_keys"] == []


# ---------------------------------------------------------------------------
# audit_names -- empty/single/ordering contracts.
# ---------------------------------------------------------------------------

_MINI_REPO_CONFIG = """import os

current_dir = os.path.dirname(os.path.abspath(__file__))

default_tool_files = {
    "alpha": os.path.join(current_dir, "data", "alpha_tools.json"),
    "beta": os.path.join(current_dir, "data", "beta_tools.json"),
}
"""


def _write_mini_repo(tmp_path: Path) -> Path:
    """A minimal repo_root with src/tooluniverse/{default_config.py,data/*.json}.

    ``check_link_generated_module``/``check_link_tests`` fall back to a clean
    'not found' result against a non-git tmp_path (``git show`` fails, and
    ``_git_show`` returns ``None`` rather than raising) -- exactly the
    no-raise contract these tests check, so no ``tests/`` or ``tools/``
    tree is needed here.
    """
    tooluniverse_dir = tmp_path / "src" / "tooluniverse"
    data_dir = tooluniverse_dir / "data"
    data_dir.mkdir(parents=True)
    (tooluniverse_dir / "default_config.py").write_text(
        _MINI_REPO_CONFIG, encoding="utf-8"
    )
    (data_dir / "alpha_tools.json").write_text(
        json.dumps(
            [{"name": "ZTool", "type": "FixtureOnlyType", "required_api_keys": []}]
        ),
        encoding="utf-8",
    )
    (data_dir / "beta_tools.json").write_text(
        json.dumps(
            [{"name": "ATool", "type": "FixtureOnlyType", "required_api_keys": []}]
        ),
        encoding="utf-8",
    )
    return tmp_path


def test_audit_names_over_empty_collection_returns_empty_list_without_raising(tmp_path):
    repo_root = _write_mini_repo(tmp_path)
    assert audit_names([], repo_root) == []


def test_audit_names_over_single_name_returns_exactly_one_record(tmp_path):
    repo_root = _write_mini_repo(tmp_path)
    records = audit_names(["ZTool"], repo_root)
    assert len(records) == 1
    assert records[0]["name"] == "ZTool"


def test_audit_names_orders_records_by_name_and_sorts_source_paths(tmp_path):
    repo_root = _write_mini_repo(tmp_path)
    records = audit_names(["ZTool", "ATool"], repo_root)
    assert [record["name"] for record in records] == ["ATool", "ZTool"]
    for record in records:
        assert record["source_paths"] == sorted(record["source_paths"])
