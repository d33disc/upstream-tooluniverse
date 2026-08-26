#!/usr/bin/env python3
"""Discovery smoke suite over a mechanically selected, gated-aware sample.

Phase 3 (``docs/gsd-codebase-map``) plan 03-03, requirement CAT-02: prove
that the two live discovery primitives -- ``grep_tools`` (backed by
``ToolUniverse.find_tools_by_pattern``) and ``get_tool_info`` (backed by
``ToolUniverse.tool_specification``) -- see the same credential-gated
catalog the codegen/registration scripts see, across a small but
provenance-diverse sample, without the sample being hand-picked to
flatter the result.

The sample is drawn mechanically from three pools (see ``select_sample``):

1. ``preserved-custom`` -- tool names from the two ``data/*.json`` files
   ``git diff-tree --cc f81448f2047a6f35bd552956a0d9990019a39eb1
   --name-only`` reported as hand-resolved during Phase 2's merge
   (``literature_search_tools.json``, ``uspto_tools.json``).
2. ``new-upstream`` -- tool names the upstream side of Phase 2's recorded
   both-sides union (``union.json``) introduced that the fork side lacked.
   ``union.json`` records only per-file *counts* and mostly-empty anomaly
   lists, not literal per-side name sets, so the actual names are
   re-derived here from the exact git blobs those counts were computed
   from (``fork_oid``/``upstream_oid``, both recorded in ``union.json``
   itself) -- a faithful completion of the artifact, not a substitute
   methodology.
3. ``offline-control`` -- ``DegreesOfUnsaturation_calculate``, a single
   credential-free, deterministic reference tool.

Pools 1 and 2 are each capped at five names in flat, globally sorted
order (cap *before* gate-removal, never backfilled -- see
``select_sample``'s docstring for why). Any capped name that
``ToolUniverse._excluded_api_key_tools`` marks as gated is pulled out of
the schema-inspection sample into a separate ``gated`` record instead of
being probed for a schema; a gated tool is never "found" by design (it is
excluded from ``all_tool_dict`` entirely at load time), so classifying
gating must happen before any found/schema conclusion is drawn
(``classify_discovery``).

Every selection/classification function here is pure and importable
without the ``tooluniverse`` package -- ``tests/unit/test_smoke_discovery_sample.py``
exercises them directly against hand-built fixtures and a ``tmp_path``
mini git repository. Only ``run_discovery_suite`` (called from ``main``)
needs a real, unfiltered ``ToolUniverse`` instance.

Git/evidence helpers are reused from ``scripts/capture_sync_baseline.py``
via ``importlib.util`` -- ``scripts/`` has no ``__init__.py``, so a plain
import fails; ``scripts/audit_registration_chain.py`` and
``tests/unit/test_sync_baseline_git.py`` use the same idiom.

Run with this repository's own interpreter (``.venv/bin/python``) -- the
``tooluniverse`` package is not guaranteed to be importable under any
other Python on the machine.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Reused helpers -- loaded via importlib, never reimplemented. Same idiom as
# scripts/audit_registration_chain.py and tests/unit/test_sync_baseline_git.py.
# ---------------------------------------------------------------------------

_CAPTURE_SPEC = importlib.util.spec_from_file_location(
    "capture_sync_baseline",
    Path(__file__).resolve().parent / "capture_sync_baseline.py",
)
_CAPTURE_MODULE = importlib.util.module_from_spec(_CAPTURE_SPEC)
assert _CAPTURE_SPEC and _CAPTURE_SPEC.loader
_CAPTURE_SPEC.loader.exec_module(_CAPTURE_MODULE)
publish_evidence = _CAPTURE_MODULE.publish_evidence
verify_checksums = _CAPTURE_MODULE.verify_checksums
_canonical_json = _CAPTURE_MODULE._canonical_json
_contains_secret = _CAPTURE_MODULE._contains_secret

REPO_ROOT_DEFAULT = Path(__file__).resolve().parents[1]

# Pool 1 (rule 1): the two data/*.json files git diff-tree --cc flagged as
# hand-resolved during Phase 2's merge. Order here is for readability only;
# selection sorts names, not files.
HAND_RESOLVED_FILES: tuple[str, ...] = (
    "literature_search_tools.json",
    "uspto_tools.json",
)

# Pool 2 (rule 2): Phase 2's recorded both-sides union artifact, relative to
# repo root. select_sample's union_json_path parameter overrides this so
# tests can point it at a tmp fixture instead of this real evidence path.
UNION_JSON_RELPATH = (
    ".planning/phases/02-upstream-main-integration/evidence/"
    "a4d3d95a096a14ce4d147faa20334d24f8db9f9a/union.json"
)

# Pool 3 (rule 3): the offline, credential-free control -- same control
# plan 03-01's tracer and Phase 2 plan 02-05 used.
OFFLINE_CONTROL_NAME = "DegreesOfUnsaturation_calculate"
OFFLINE_CONTROL_SOURCE = "src/tooluniverse/data/degrees_of_unsaturation_tools.json"

POOL_CAP = 5

# Pool 2 anomaly filters, spelled out once here so select_sample's body
# doesn't need inline prose: (a) only verdict == "union_ok" files are
# considered -- union.json's upstream_deleted entries describe deletions,
# not additions; (b) only files where merged_name_count ==
# upstream_name_count are considered -- a conservative soundness filter
# that skips files where the fork *also* added names (merged > upstream),
# so upstream-minus-fork is guaranteed to be exactly what the merge
# introduced; this can under-collect candidates but never over-collects,
# and the real union.json yields well over POOL_CAP candidates even with
# this filter; (c) broken_apis/ definitions are excluded -- they are not
# part of the live catalog.
_BROKEN_APIS_PREFIX = "src/tooluniverse/data/broken_apis/"


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _names_from_data_file(path: Path) -> list[str]:
    """Sorted, deduplicated tool ``name`` fields from one data/*.json file.

    Returns ``[]`` if the file is absent or malformed rather than raising,
    so a missing fixture file just yields an empty pool instead of
    crashing selection.
    """
    if not path.is_file():
        return []
    try:
        data = _load_json(path)
    except json.JSONDecodeError:
        return []
    if not isinstance(data, list):
        return []
    return sorted(
        {item["name"] for item in data if isinstance(item, dict) and item.get("name")}
    )


def _git_show_names(repo_root: Path, oid: str, path: str) -> set[str] | None:
    """Tool ``name`` fields in *path* at git blob *oid*.

    Returns ``None`` if the blob cannot be resolved or parsed (never
    raises) -- a missing/invalid blob just drops that file from the pool 2
    candidate set rather than aborting the whole run.
    """
    result = subprocess.run(
        ["git", "show", f"{oid}:{path}"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    try:
        parsed = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, list):
        return None
    return {
        item["name"] for item in parsed if isinstance(item, dict) and item.get("name")
    }


def _resolve_hand_resolved_pool(repo_root: Path) -> list[dict[str, str]]:
    """All rule-1 candidates (pre-cap): names from the two hand-resolved
    data/*.json files, read from their current on-disk content."""
    records = []
    for filename in HAND_RESOLVED_FILES:
        source_path = f"src/tooluniverse/data/{filename}"
        for name in _names_from_data_file(repo_root / source_path):
            records.append(
                {
                    "name": name,
                    "pool": "preserved-custom",
                    "selection_rule": (
                        "rule_1_hand_resolved: name defined in "
                        f"{source_path}, one of the files git diff-tree --cc "
                        "f81448f2047a6f35bd552956a0d9990019a39eb1 --name-only "
                        "reported as hand-resolved"
                    ),
                    "source_path": source_path,
                }
            )
    return records


def _resolve_new_upstream_pool(
    repo_root: Path, union_json_path: Path
) -> list[dict[str, str]]:
    """All rule-2 candidates (pre-cap): names present in the upstream side
    of union.json's both-sides union but absent from the fork side.

    See the module docstring and the anomaly-filter comment above
    ``_BROKEN_APIS_PREFIX`` for why this re-derives names from git blobs
    instead of reading name lists directly out of union.json (which does
    not carry them).
    """
    if not union_json_path.is_file():
        return []
    union = _load_json(union_json_path)
    fork_oid = union["fork_oid"]
    upstream_oid = union["upstream_oid"]

    candidates: dict[str, str] = {}
    for entry in union.get("files", []):
        path = entry.get("path", "")
        if not path or path.startswith(_BROKEN_APIS_PREFIX):
            continue
        if entry.get("verdict") != "union_ok":
            continue
        if entry.get("upstream_name_count", 0) <= entry.get("fork_name_count", 0):
            continue
        if entry.get("merged_name_count") != entry.get("upstream_name_count"):
            continue
        fork_names = _git_show_names(repo_root, fork_oid, path)
        upstream_names = _git_show_names(repo_root, upstream_oid, path)
        if fork_names is None or upstream_names is None:
            continue
        for name in upstream_names - fork_names:
            candidates.setdefault(name, path)

    return [
        {
            "name": name,
            "pool": "new-upstream",
            "selection_rule": (
                "rule_2_new_upstream: name present in the upstream side "
                f"(git show {upstream_oid}:<path>) of a union.json "
                "union_ok file but absent from the fork side "
                f"(git show {fork_oid}:<path>); restricted to files where "
                "merged_name_count == upstream_name_count, excluding "
                f"{_BROKEN_APIS_PREFIX}"
            ),
            "source_path": candidates[name],
        }
        for name in sorted(candidates)
    ]


def select_sample(
    repo_root: Path | str,
    excluded_api_key_tools: dict[str, list[str]],
    union_json_path: Path | str | None = None,
) -> dict[str, Any]:
    """Mechanically select the discovery-suite sample.

    Applies the plan's ``<sample_selection_rule>`` in order: cap pools 1
    and 2 at ``POOL_CAP`` names each in flat, globally sorted order, add
    the single offline control, THEN remove any capped name present in
    *excluded_api_key_tools* into a separate ``gated`` list -- cap first,
    gate second, never backfilled. Gating a name after the cap has
    already been taken can shrink the returned sample below the cap; that
    is the intended, documented behavior, not a bug -- silently
    substituting the next-sorted name would let an accident of which
    credentials happen to be configured quietly reshape the sample
    (T-03-19).

    *excluded_api_key_tools* is a plain ``dict`` (``name ->
    [missing_key, ...]``), not a live ``ToolUniverse`` -- callers read
    ``tu._excluded_api_key_tools`` and pass it in, which keeps this
    function importable and testable without instantiating the package.

    *union_json_path* defaults to Phase 2's real recorded union artifact
    (``UNION_JSON_RELPATH``, relative to *repo_root*); tests override it
    with a tmp fixture path instead of replicating that deep, hash-named
    directory structure.
    """
    repo_root = Path(repo_root)
    resolved_union_path = (
        Path(union_json_path)
        if union_json_path is not None
        else repo_root / UNION_JSON_RELPATH
    )

    pool1 = sorted(_resolve_hand_resolved_pool(repo_root), key=lambda r: r["name"])[
        :POOL_CAP
    ]
    pool2 = sorted(
        _resolve_new_upstream_pool(repo_root, resolved_union_path),
        key=lambda r: r["name"],
    )[:POOL_CAP]
    control = [
        {
            "name": OFFLINE_CONTROL_NAME,
            "pool": "offline-control",
            "selection_rule": (
                "rule_3_offline_control: credential-free, deterministic "
                "reference tool -- a failure here means the environment, "
                "not the catalog"
            ),
            "source_path": OFFLINE_CONTROL_SOURCE,
        }
    ]

    sample: list[dict[str, str]] = []
    gated: list[dict[str, Any]] = []
    emptied_pools: list[dict[str, str]] = []

    for pool_records in (pool1, pool2, control):
        survivors = []
        for record in pool_records:
            missing = excluded_api_key_tools.get(record["name"])
            if missing:
                gated.append(
                    {
                        "name": record["name"],
                        "pool": record["pool"],
                        "missing_keys": sorted(missing),
                    }
                )
            else:
                survivors.append(record)
        if pool_records and not survivors:
            emptied_pools.append(
                {
                    "pool": pool_records[0]["pool"],
                    "reason": (
                        "every candidate name in this pool's cap was "
                        "removed by gating; no substitution was performed"
                    ),
                }
            )
        sample.extend(survivors)

    return {
        "sample": sorted(sample, key=lambda r: (r["pool"], r["name"])),
        "gated": sorted(gated, key=lambda r: r["name"]),
        "emptied_pools": emptied_pools,
    }


def probe_grep_tools(universe: Any, tool_name: str) -> dict[str, Any]:
    """Probe the ``grep_tools`` primitive (``ToolUniverse.find_tools_by_pattern``).

    Records exact-name membership, not just match count: ``find_tools_by_pattern``
    does an unanchored ``re.search`` over tool names, so a shorter name
    that happens to be a substring of another real tool's name produces a
    non-empty match list even when the shorter name itself is not in the
    catalog. This diverges from ``scripts/audit_registration_chain.py``'s
    ``probe_discovery`` (which treats ``bool(matches)`` as "found") for
    exactly that reason.
    """
    matches = universe.find_tools_by_pattern(
        tool_name, search_in="name", case_sensitive=True
    )
    match_names = sorted(
        {m.get("name") for m in matches if isinstance(m, dict) and m.get("name")}
    )
    return {
        "found": tool_name in match_names,
        "match_count": len(matches),
        "match_names": match_names,
    }


def probe_get_tool_info(universe: Any, tool_name: str) -> dict[str, Any]:
    """Probe the ``get_tool_info`` primitive (``ToolUniverse.tool_specification``).

    ``tool_specification`` returns ``None`` for both a gated tool and a
    genuinely-missing one -- it does not itself construct the gated error
    shape (that happens one layer up, in ``GetToolInfoTool._not_found_error``).
    This function reconstructs that same shape here (``{"error": "requires
    API key(s) not set: ..."}``) whenever the missing-keys mapping explains
    the ``None``, so the caller sees the same signal a live ``get_tool_info``
    call would produce. Records parameter *names* only -- never a full
    response payload or a credential value.
    """
    spec = universe.tool_specification(tool_name)
    if spec is None:
        missing_keys = sorted(
            getattr(universe, "_excluded_api_key_tools", {}).get(tool_name) or []
        )
        return {
            "name": tool_name,
            "gated": bool(missing_keys),
            "missing_keys": missing_keys,
            "has_schema": False,
            "parameter_names": [],
            "error": (
                f"requires API key(s) not set: {', '.join(missing_keys)}"
                if missing_keys
                else "not found"
            ),
        }

    params_obj = spec.get("parameter") if isinstance(spec, dict) else None
    if not isinstance(params_obj, dict):
        params_obj = spec.get("parameters") if isinstance(spec, dict) else None
    has_schema = isinstance(params_obj, dict)
    parameter_names = (
        sorted(params_obj["properties"].keys())
        if has_schema and isinstance(params_obj.get("properties"), dict)
        else []
    )
    return {
        "name": tool_name,
        "gated": False,
        "missing_keys": [],
        "has_schema": has_schema,
        "parameter_names": parameter_names,
        "error": None,
    }


def classify_discovery(
    grep_result: dict[str, Any] | None,
    info_result: dict[str, Any] | None,
    gated_keys: list[str] | None,
) -> dict[str, Any]:
    """Pure verdict over one tool's already-gathered discovery facts.

    Gating is checked FIRST, before drawing any found/schema conclusion --
    mirroring ``scripts/audit_registration_chain.py``'s
    ``assert_discovery_contract`` and ``scripts/probe_custom_tools.py``'s
    ``assert_probe_contract`` -- because a gated tool is excluded from
    ``all_tool_dict`` entirely at ``load_tools()`` time, so it will never
    be "found"; checking gating first prevents that structural absence
    from being misread as a catalog failure. An empty result with no
    gating signal is always ``fail``, never ``pass`` -- this repository
    has a recorded history (the literature-search OverallSummaryAgent
    incident) of an empty result silently masquerading as success.
    """
    grep_result = grep_result or {}
    info_result = info_result or {}

    if gated_keys or info_result.get("gated"):
        missing_keys = sorted(gated_keys or info_result.get("missing_keys") or [])
        return {
            "verdict": "gated",
            "reason": "required_api_keys unmet",
            "missing_keys": missing_keys,
        }

    found = bool(grep_result.get("found"))
    parameter_names = info_result.get("parameter_names") or []
    has_schema = bool(info_result.get("has_schema")) and len(parameter_names) > 0

    if not found:
        return {
            "verdict": "fail",
            "reason": "grep_tools found no exact name match",
            "missing_keys": [],
        }
    if not has_schema:
        return {
            "verdict": "fail",
            "reason": "get_tool_info returned no non-empty parameter schema",
            "missing_keys": [],
        }
    return {
        "verdict": "pass",
        "reason": (
            "grep_tools found the tool and get_tool_info returned a parameter schema"
        ),
        "missing_keys": [],
    }


def _collect_secrets(excluded_api_key_tools: dict[str, list[str]]) -> tuple[str, ...]:
    """Live env values for every credential name this run's gated map
    mentions, plus the well-known LLM key fallback chain
    (``execute_function.py``'s ``AgenticTool`` gate) and ``USPTO_API_KEY`` --
    so the secret guard inside ``publish_evidence`` has real values to
    check against, even though this script only ever records key *names*,
    never values.
    """
    key_names = {k for names in excluded_api_key_tools.values() for k in names}
    key_names |= {
        "AZURE_OPENAI_API_KEY",
        "OPENAI_API_KEY",
        "OPENROUTER_API_KEY",
        "GEMINI_API_KEY",
        "VLLM_SERVER_URL",
        "USPTO_API_KEY",
    }
    return tuple(v for v in (os.environ.get(k) for k in sorted(key_names)) if v)


def run_discovery_suite(
    repo_root: Path | str, only_tool: str | None = None
) -> dict[str, Any]:
    """Load the full catalog once, select the sample, probe each survivor,
    and return the complete evidence payload (not yet written to disk).

    ``ToolUniverse.close()`` runs in a ``finally`` block (T-03-20); no tool
    is ever executed, only located and inspected.
    """
    repo_root = Path(repo_root)
    src_path = str(repo_root / "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

    from tooluniverse import ToolUniverse

    universe = ToolUniverse()
    try:
        universe.load_tools()
        excluded_api_key_tools = dict(
            getattr(universe, "_excluded_api_key_tools", {}) or {}
        )
        catalog_size = len(universe.all_tool_dict)

        selection = select_sample(repo_root, excluded_api_key_tools)
        sample_records = selection["sample"]

        if only_tool:
            filtered = [r for r in sample_records if r["name"] == only_tool]
            sample_records = filtered or [
                {
                    "name": only_tool,
                    "pool": "adhoc",
                    "selection_rule": (
                        "rule_adhoc_single_tool_flag: requested directly "
                        "via --tool, not part of the mechanical sample"
                    ),
                    "source_path": "",
                }
            ]

        results = []
        for record in sample_records:
            name = record["name"]
            grep_result = probe_grep_tools(universe, name)
            info_result = probe_get_tool_info(universe, name)
            gated_keys = excluded_api_key_tools.get(name)
            verdict_info = classify_discovery(grep_result, info_result, gated_keys)
            results.append(
                {
                    "name": name,
                    "pool": record["pool"],
                    "selection_rule": record["selection_rule"],
                    "source_path": record["source_path"],
                    "grep": grep_result,
                    "info": info_result,
                    "verdict": verdict_info["verdict"],
                    "reason": verdict_info["reason"],
                    "missing_keys": verdict_info["missing_keys"],
                }
            )
    finally:
        universe.close()

    results.sort(key=lambda r: r["name"])
    passed = sum(1 for r in results if r["verdict"] == "pass")
    gated_count = sum(1 for r in results if r["verdict"] == "gated")
    failed = sum(1 for r in results if r["verdict"] == "fail")

    gated_sample_note = (
        f"this run's sample drew {len(selection['gated'])} gated name(s) "
        "live: " + ", ".join(g["name"] for g in selection["gated"])
        if selection["gated"]
        else (
            "this run's mechanically-selected sample happened to draw none "
            "of them, so the gated array is empty for this run -- the "
            "exclusion mechanism itself is proven separately by "
            "tests/unit/test_smoke_discovery_sample.py's dedicated "
            "gated-exclusion test, not by this run's live sample"
        )
    )

    exclusions = [
        (
            "this plan certifies the shared-core discovery primitives "
            "(grep_tools/get_tool_info) only; it does not certify "
            "discovery, inspection, or execution across the CLI, MCP "
            "stdio, MCP HTTP, or REST transport surfaces -- that "
            "certification is Phase 5 / SURF-01 per ROADMAP.md"
        ),
        (
            f"{len(excluded_api_key_tools)} catalog-wide tool(s) are "
            "currently excluded via ToolUniverse._excluded_api_key_tools "
            "(missing required_api_keys) in this environment; "
            f"{gated_sample_note}"
        ),
        (
            "pool 1's flat, globally-sorted cap-5 selected 5 of 14 "
            "candidates, all from literature_search_tools.json; "
            "uspto_tools.json's pair (USPTO_get_patent_assignment, "
            "USPTO_get_patent_transactions -- the same pair Phase 2 plan "
            "02-05 probed for execution) sorts after the literature "
            "agents and so is not represented in this run's sample or "
            "gated arrays, even though both are gated on USPTO_API_KEY in "
            "this environment"
        ),
        (
            "pool 2's candidate names are re-derived from git blobs "
            "(fork_oid/upstream_oid recorded in union.json) rather than "
            "read from union.json directly, which records only per-file "
            "counts; restricted to verdict==union_ok files with "
            "merged_name_count==upstream_name_count, excluding "
            f"{_BROKEN_APIS_PREFIX}"
        ),
        (
            "catalog_size and the excluded_api_key_tools population are "
            "environment-dependent -- this run resolved LLM keys via "
            ".tooluniverse/env.py + .env.1password even though the "
            "ambient shell had none exported, so a future run with "
            "different credentials loaded will show different counts; "
            "that is not catalog drift"
        ),
    ]

    return {
        "catalog_size": catalog_size,
        "sample": selection["sample"],
        "gated": selection["gated"],
        "emptied_pools": selection["emptied_pools"],
        "results": results,
        "passed": passed,
        "gated_count": gated_count,
        "failed": failed,
        "exclusions": exclusions,
        "_secrets": _collect_secrets(excluded_api_key_tools),
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, help="evidence output directory")
    parser.add_argument(
        "--tool",
        default=None,
        help=(
            "restrict the run to a single tool name (debug affordance; "
            "re-run without --tool afterward to restore the full "
            "sample's evidence -- this flag replaces discovery.json, it "
            "does not merge into it)"
        ),
    )
    parser.add_argument(
        "--json", action="store_true", help="print a JSON summary to stdout"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    repo_root = REPO_ROOT_DEFAULT

    out_dir = Path(args.out)
    if not out_dir.is_absolute():
        out_dir = (Path.cwd() / out_dir).resolve()

    # Clear this run's own prior output *before* writing -- otherwise a
    # second run would fail publish_evidence's empty-or-absent precondition.
    # Guarded so a mistaken --out (repo root or above) never triggers a wide
    # deletion. Same idiom as scripts/audit_registration_chain.py's main().
    if out_dir.exists():
        if out_dir == repo_root or repo_root not in out_dir.parents:
            print(
                f"error: refusing to clear --out {out_dir} -- it is not a "
                f"strict subdirectory of the repository root {repo_root}",
                file=sys.stderr,
            )
            return 2
        shutil.rmtree(out_dir)

    payload = run_discovery_suite(repo_root, only_tool=args.tool)
    secrets = payload.pop("_secrets")

    published = publish_evidence({"discovery": payload}, out_dir, secrets=secrets)
    verify_checksums(published)

    summary = {
        "catalog_size": payload["catalog_size"],
        "passed": payload["passed"],
        "gated": payload["gated_count"],
        "failed": payload["failed"],
        "out": str(published),
    }
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(
            f"discovery: {payload['passed']} pass, {payload['gated_count']} "
            f"gated, {payload['failed']} failed "
            f"(catalog_size={payload['catalog_size']}) -> {published}"
        )
    return 1 if payload["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
