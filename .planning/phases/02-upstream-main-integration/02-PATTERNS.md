# Phase 2: Upstream Main Integration - Pattern Map

**Mapped:** 2026-08-06
**Files analyzed:** 3 new artifacts (Wave 0) + 3 merge-resolution surfaces referenced by plans
**Analogs found:** 4 / 4 primary targets (JSON union checker, findings-classification script, probe harness, registry integrity test already exists)

## File Classification

| New/Modified File (expected) | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `scripts/check_json_union.py` (or similar, new) | utility/CLI script | batch/transform (diff+assert) | `classify_preservation_path()` + `collect_preservation_inventory()` in `scripts/capture_sync_baseline.py:853-990` | role-match (git diff -> classify pattern); no direct JSON-array-union analog exists, closest true analog for "assert set equality" is `tests/unit/test_registry_integrity.py` |
| `scripts/classify_findings.py` (new, central artifact) | utility/CLI script | batch/transform (two-step diff join) | `classify_preservation_path()` + `collect_preservation_inventory()` in `scripts/capture_sync_baseline.py:853-990`, plus `run_git()` at `scripts/capture_sync_baseline.py:634-653` | exact (same author, same repo, same evidence-bundle discipline) |
| `scripts/probe_custom_tools.py` (new, targeted probe harness) | utility/CLI script | request-response (discover->inspect->execute per tool) | `run_python_probe()` (`scripts/capture_sync_baseline.py:134-172`), `run_cli_probe()` (`scripts/capture_sync_baseline.py:187-241`), `create_isolated_worktree()` (`scripts/capture_sync_baseline.py:749-761`) | role-match; these are single-fixed-tool probes (`REFERENCE_TOOL`) that need generalizing to a tool list, not a rewrite |
| N/A — verification only | test | assertion | `tests/unit/test_registry_integrity.py:1-60` (`_load_defined_tool_names`, `_load_type_names`) | exact — already does the "collect all `name` fields from `data/*.json`" scan Wave 0 needs |

## Pattern Assignments

### 1. Entry-level JSON union checker (new)

**Analog:** `tests/unit/test_registry_integrity.py` (name-collection pattern) + `classify_preservation_path()` / `collect_preservation_inventory()` in `scripts/capture_sync_baseline.py`

There is no existing "assert union of two JSON tool arrays" script — nothing in `scripts/` or `tests/unit/` currently diffs `data/literature_search_tools.json` or `data/uspto_tools.json` against a second copy. The two closest patterns to compose are:

**Name-collection pattern** (`tests/unit/test_registry_integrity.py` lines 33-51):
```python
def _load_defined_tool_names() -> set[str]:
    """All tool names from ``name`` fields in data/*.json."""
    names: set[str] = set()
    for jf in DATA_DIR.glob("*.json"):
        if jf.name == "api_keys_catalog.json":
            continue
        try:
            data = json.loads(jf.read_text())
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        items = (
            data if isinstance(data, list) else [data] if isinstance(data, dict) else []
        )
        for item in items:
            if isinstance(item, dict) and "name" in item:
                names.add(item["name"])
    return names
```
Copy this shape (defensive `list`/`dict`/skip-on-decode-error handling) for loading the fork-side, upstream-side, and merged copies of each `data/*.json`, then assert `len(merged_names) == len(fork_names | upstream_names)` — this is literally VALIDATION.md's SYNC-02 command.

**Git-diff-driven classification pattern** (`scripts/capture_sync_baseline.py:853-884`, `classify_preservation_path`):
```python
def classify_preservation_path(path: str) -> str:
    p = path.replace("\\", "/")
    if p.startswith(".planning/"):
        return "planning"
    ...
    if (
        p == "TOOL_MANIFEST.json"
        or p == "uv.lock"
        or "_lazy_registry_static" in p
        or "embedding" in p.lower()
        or p.startswith("src/tooluniverse/")
        and p.endswith("_generated.py")
    ):
        return "generated_asset"
    ...
```
Reuse the enumeration-and-tag idiom (not this exact classification table) for tagging each `data/*.json` file the checker inspects as `union_ok` / `net_removed_fork_entry` / `net_removed_upstream_entry`.

**Verified file location fact:** `src/tooluniverse/data/literature_search_tools.json` is a flat JSON array of 6 dicts, each with `type`/`name`/`description`/... — confirmed by direct read (`IntentAnalyzerAgent`, `KeywordExtractorAgent`, `ResultSummarizerAgent`, `QualityCheckerAgent`, `OverallSummaryAgent`, +1). This is the shape the union checker must handle: `list[dict]` keyed by `"name"`.

---

### 2. Findings-classification script (new, central artifact)

**Analog:** `classify_preservation_path()` and `collect_preservation_inventory()`, both in `scripts/capture_sync_baseline.py`

**`run_git()` helper to reuse verbatim** (`scripts/capture_sync_baseline.py:634-653`):
```python
def run_git(argv: Iterable[str], cwd: Path | str, timeout: float = 60.0) -> str:
    """Run Git with an argv-only boundary and return stdout."""
    args = ["git", *map(str, argv)]
    try:
        proc = subprocess.run(
            args,
            cwd=os.fspath(cwd),
            capture_output=True,
            text=False,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise GitCaptureError(f"git command failed: {' '.join(args)}: {exc}") from exc
    if proc.returncode:
        stderr = proc.stderr.decode("utf-8", "replace").strip()
        raise GitCaptureError(
            f"git command failed ({proc.returncode}): {' '.join(args)}: {stderr}"
        )
    return proc.stdout.decode("utf-8", "surrogateescape")
```
Argv-only boundary, explicit `cwd`, byte-safe decode with `surrogateescape`, checked exit status — this is the project's established Git-invocation contract (per CONTEXT.md's "Established Patterns"). Copy verbatim; do not shell out any other way.

**`classify_preservation_path()` to model the new classifier on** (`scripts/capture_sync_baseline.py:853-884`, shown above in section 1). The findings-classification script needs its own classification function, e.g. `classify_finding(path, remerge_status, landed_status) -> Literal["landed_correct", "landed_dropped_or_altered", "self_healed_downstream"]`, built the same way: a pure function over path/status strings, no I/O, easily unit-testable.

**`collect_preservation_inventory()` join pattern** (`scripts/capture_sync_baseline.py:925-990`):
```python
def collect_preservation_inventory(
    repo: Path | str, upstream_oid: str, fork_oid: str
) -> dict[str, Any]:
    root = Path(repo).resolve()
    raw = run_git(
        ["diff", "--raw", "-z", "--find-renames", upstream_oid, fork_oid], root
    )
    paths: list[dict[str, Any]] = []
    tokens = _nul_records(raw)
    index = 0
    while index < len(tokens):
        rec = tokens[index]
        index += 1
        if "\t" in rec:
            meta, path = rec.split("\t", 1)
        elif rec.startswith(":") and index < len(tokens):
            meta, path = rec, tokens[index]
            index += 1
        else:
            continue
        fields = meta.split()
        if len(fields) < 5:
            continue
        old_mode, new_mode, old_oid, new_oid, status = fields[-5:]
        item = {
            "path": path,
            "old_mode": old_mode,
            "new_mode": new_mode,
            "old_oid": old_oid,
            "new_oid": new_oid,
            "status": status,
            "class": classify_preservation_path(path),
            "must_survive": "fork delta retained pending staged synchronization",
        }
        ...
        paths.append(item)
    ...
    blockers = [p for p in paths if p["class"] == "other_review_required"] + [
        p for p in paths if p.get("symlink", {}).get("blocking")
    ]
    return {
        "upstream_oid": upstream_oid,
        "fork_oid": fork_oid,
        "paths": paths,
        "untracked": untracked,
        "blocking": bool(blockers),
        ...
    }
```
This is the exact shape for D-06a's two-step check: (1) `git diff --raw -z --find-renames <re-merge-tree> <f81448f2-tree>` classified per-path, (2) re-check any `landed_dropped_or_altered` path against the pinned baseline `21945440`'s tree the same way, downgrading to `self_healed_downstream` if present there. Preserve the `path`/`status`/`class`/`must_survive`-style record shape per CONTEXT.md's Integration Points note ("the findings artifact ... should keep the original `path` / `status` / `class` / `must_survive` fields so the two can be joined mechanically").

**Real `preservation.json` schema** (read directly from `.planning/phases/01-protected-sync-baseline/evidence/21945440c9f2a15537ba878500a800d9e330eab0/preservation.json`), top-level keys: `blockers` (list), plus (per `collect_preservation_inventory`'s return shape) `upstream_oid`, `fork_oid`, `paths`, `untracked`, `blocking`. Each blocker/path record:
```json
{
  "class": "other_review_required",
  "must_survive": "fork delta retained pending staged synchronization",
  "new_mode": "100644",
  "new_oid": "d27dfd98",
  "old_mode": ":100644",
  "old_oid": "0e07609c",
  "path": ".env.template",
  "status": "M"
}
```
1,392 total inventoried paths, 87 flagged as blockers, every entry currently carries `class: "other_review_required"` (per CONTEXT.md D-03/canonical_refs — Phase 2's job is to re-classify each of the 1,392, not just the 87 blockers).

**Evidence-bundle layout to follow:** `.planning/phases/01-protected-sync-baseline/evidence/<full-40-char-OID>/` containing `SHA256SUMS`, `git.json`, `environment.json`, `ci.json`, `preservation.json`, `stages.json`, `baseline.json`, `catalog.json`, `probes/`, `tests/`. Directory listing verified directly. Follow the same `evidence/<OID>/` convention with a sorted `SHA256SUMS` for Phase 2's findings bundle (see `publish_evidence()` / `verify_checksums()` at `scripts/capture_sync_baseline.py:1317-1408` for the checksum-set idiom, not excerpted here for space — read on demand).

---

### 3. Fresh custom-tool probe harness (new)

**Analog:** `run_python_probe()`, `run_cli_probe()`, `create_isolated_worktree()` in `scripts/capture_sync_baseline.py`

**What exists today — single fixed-tool probe** (`scripts/capture_sync_baseline.py:65-66, 134-172`):
```python
REFERENCE_TOOL = "DegreesOfUnsaturation_calculate"
REFERENCE_ARGUMENTS = {"operation": "calculate", "formula": "C6H6"}

def run_python_probe() -> dict[str, Any]:
    """Run the reference workflow directly through the Python API."""
    from tooluniverse.execute_function import ToolUniverse

    started = time.monotonic()
    universe = ToolUniverse()
    try:
        universe.load_tools(include_tools=[REFERENCE_TOOL])
        found = universe.find_tools_by_pattern(
            REFERENCE_TOOL, search_in="name", case_sensitive=True
        )
        discover = _stage(
            "discover", started, {"status": "success", "tools": [REFERENCE_TOOL] if found else []},
        )
        spec = universe.tool_specification(REFERENCE_TOOL)
        inspect = _stage("inspect", started, {"status": "success", "spec": spec})
        required = spec.get("parameter", {}).get("required", [])
        if "operation" not in required:
            raise BaselineValidationError("reference schema no longer requires operation")
        result = universe.run_one_function(
            {"name": REFERENCE_TOOL, "arguments": REFERENCE_ARGUMENTS}
        )
        execute = _stage("execute", started, result)
        assertion = _stage("assert", started, _assert_reference(result))
        probe = _probe_contract("python", discover, inspect, execute, assertion)
        ...
        return probe
    finally:
        close = getattr(universe, "close", None)
        if close:
            close()
```
```python
def run_cli_probe() -> dict[str, Any]:
    """Run grep/info/run through the installed ``tu`` executable."""
    code, stdout, stderr = _run_command(
        ["tu", "grep", REFERENCE_TOOL, "--json", "--field", "name", "--limit", "5"]
    )
    ...
    code, stdout, stderr = _run_command(["tu", "info", REFERENCE_TOOL, "--json"])
    ...
    required = spec.get("parameters", spec.get("parameter", {})).get("required", [])
    ...
    code, stdout, stderr = _run_command(
        ["tu", "run", REFERENCE_TOOL, json.dumps(REFERENCE_ARGUMENTS), "--json"]
    )
    ...
```

**What must change to become the D-04 targeted harness:** `REFERENCE_TOOL`/`REFERENCE_ARGUMENTS` are module-level constants baked into `_assert_reference()`'s expectations (calculator-specific). The new harness needs:
1. `REFERENCE_TOOL` and `REFERENCE_ARGUMENTS` promoted to a per-tool parameter (`tool_name: str, arguments: dict`) rather than globals, so `run_python_probe(tool_name, arguments)` can be called once per selected fork-only tool from `preservation.json`'s at-risk set.
2. `_assert_reference()` (not excerpted — calculator-domain-specific) must be replaced with a generic "did it return without a hard error / did required params get enforced" assertion, since the probe list will span heterogeneous domains (not all calculator tools).
3. `run_cli_probe()`'s `tu info` / `tu run` invocation shape (`["tu", "info", tool, "--json"]`, `["tu", "run", tool, json.dumps(args), "--json"]`) is directly reusable as-is, parameterized the same way.
4. Isolation: reuse `create_isolated_worktree()` (`scripts/capture_sync_baseline.py:749-761`) verbatim — branches from a given OID into a detached worktree without touching the caller's checkout — to run these probes against the D-05 re-merge branch rather than the working tree.
```python
def create_isolated_worktree(
    repo: Path | str, fork_oid: str, worktree_dir: Path | str
) -> Path:
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
```

This is genuinely "close analog with parameterization needed," not a rewrite — the subprocess/API plumbing, `_stage()`/`_probe_contract()` result-shape helpers, and worktree isolation are all directly reusable.

---

## Merge-Resolution Surfaces (for plans touching D-08's union rule)

### `src/tooluniverse/default_config.py` — hand-maintained category->path dict

Verified structure (lines 1-9, 13-15):
```python
"""Default tool configuration files mapping.

Separated from __init__.py to avoid circular imports.
"""

import os
import json
from pathlib import Path

current_dir = os.path.dirname(os.path.abspath(__file__))

default_tool_files = {
    "special_tools": os.path.join(current_dir, "data", "special_tools.json"),
    "tooluniverse_page": os.path.join(
        current_dir, "data", "tooluniverse_page_tools.json"
    ),
    ...
```
Flat `dict[str, str]` literal, one entry per category. D-08's "union" resolution here means: key set of the merged dict must equal `fork_keys | upstream_keys`, with no value collisions silently dropped. No existing script checks this dict specifically — the same union-checker idiom from Pattern 1 applies (load both sides as Python via AST or import, diff key sets).

### `src/tooluniverse/_lazy_registry_static.py` — GENERATED FILE, never hand-merged

Verified header (lines 1-11):
```python
"""
STATIC LAZY REGISTRY - GENERATED FILE
Do not edit manually. generated by generate_lazy_registry.py
This file allows lazy loading to work in frozen environments where source files are missing.
"""

# Map of tool_name -> module_name
STATIC_LAZY_REGISTRY = {
    "ADAStandardsTool": "clinical_society_tools",
    "ADMETAITool": "admetai_tool",
    ...
```
Any plan touching this file's conflict must NOT hand-resolve line-by-line — the correct resolution is `tu build` / `python scripts/generate_lazy_registry.py`, regenerating from the post-merge `data/*.json` set, then the registry-integrity test (`tests/unit/test_registry_integrity.py`) is the acceptance check for "type -> class mapping still resolves for every tool". This is CONTEXT.md's explicit distinction and must be called out to the planner as a non-diff resolution.

### `src/tooluniverse/data/literature_search_tools.json`, `src/tooluniverse/data/uspto_tools.json` — JSON arrays keyed by `name`

Verified: `literature_search_tools.json` is `list[dict]`, 6 entries in the current tree, each `{"type": ..., "name": ..., "description": ..., ...}` — e.g. `IntentAnalyzerAgent`, `KeywordExtractorAgent`, `ResultSummarizerAgent`, `QualityCheckerAgent`, `OverallSummaryAgent` (+1 more). Resolution rule (D-08): "definition present on both sides -> upstream wins; fork-only -> retained." The union checker (Pattern 1) is the mechanical proof for these two files specifically, named in both CONTEXT.md and VALIDATION.md as the priority targets.

---

## Shared Patterns

### Git invocation contract
**Source:** `run_git()`, `scripts/capture_sync_baseline.py:634-653`
**Apply to:** all three new Wave 0 scripts
Argv-only subprocess, explicit `cwd`, `text=False` + `surrogateescape` decode, checked returncode raising `GitCaptureError`. Every new script that shells out to `git` should reuse this function directly (import from `scripts/capture_sync_baseline.py` or extract to a shared module) rather than reimplementing subprocess handling.

### Evidence-bundle output convention
**Source:** `.planning/phases/01-protected-sync-baseline/evidence/<full-OID>/` directory (verified via `ls`)
**Apply to:** findings-classification script's output artifact
`evidence/<40-char-OID>/{name}.json` plus a sorted `SHA256SUMS` for tamper-evidence (see `publish_evidence()`/`verify_checksums()` in `scripts/capture_sync_baseline.py`, lines ~1317-1408, read on demand — not excerpted here to control token budget).

### NUL-safe git-diff token parsing
**Source:** `_nul_records()` (`scripts/capture_sync_baseline.py:663-664`) + the tokenizing loop inside `collect_preservation_inventory()` (lines 932-963, excerpted above)
**Apply to:** JSON union checker and findings-classification script, anywhere `git diff --raw -z` output is parsed — never split on newlines, always `-z`/NUL-delimited to survive filenames with spaces or unusual bytes.

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| JSON-array set-equality assertion (`len(merged) == len(fork \| upstream)`) as a standalone reusable function | utility | transform | No file in `scripts/` or `tests/unit/` currently does array-level (as opposed to whole-registry) union checking; compose from `test_registry_integrity.py`'s name-collection loop + a plain Python `set` equality assertion — see Pattern 1 above |

## Metadata

**Analog search scope:** `scripts/`, `tests/unit/`, `src/tooluniverse/default_config.py`, `src/tooluniverse/_lazy_registry_static.py`, `src/tooluniverse/data/*.json`, `.planning/phases/01-protected-sync-baseline/evidence/`
**Files scanned:** `scripts/capture_sync_baseline.py` (1,471 lines, read via 3 non-overlapping targeted ranges), `tests/unit/test_registry_integrity.py` (header + helpers), `src/tooluniverse/default_config.py`, `src/tooluniverse/_lazy_registry_static.py`, `src/tooluniverse/data/literature_search_tools.json`, `.planning/phases/01-protected-sync-baseline/evidence/21945440.../preservation.json`
**Pattern extraction date:** 2026-08-06
