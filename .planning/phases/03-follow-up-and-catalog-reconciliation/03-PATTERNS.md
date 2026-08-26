# Phase 3: Follow-up and Catalog Reconciliation - Pattern Map

**Mapped:** 2026-08-07
**Files analyzed:** 5 (all extend/reuse existing modules; no net-new architectural surface)
**Analogs found:** 5 / 5

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|--------------------|------|-----------|-----------------|----------------|
| `tests/unit/test_registry_integrity.py` (extend) | test | batch/transform (static structural check) | itself (existing file, extend in place) | exact |
| `scripts/audit_registration_chain.py` (new, Tier 1 + Tier 2 six-link audit) | utility/script | batch/transform | `scripts/audit_upstream_merge.py` | exact (same author, same repo convention: AST/JSON structural diffing -> verdict dict) |
| `scripts/capture_pr161_evidence.py` (new, SYNC-03 evidence) or an evidence-only stage appended to an existing capture script | utility/script | CRUD (single git-ancestry read -> evidence write) | `scripts/capture_sync_baseline.py` | exact (identical evidence-bundle shape needed) |
| `scripts/smoke_discovery_sample.py` (new, CAT-02 grep_tools/get_tool_info smoke check) | utility/script | request-response (calls discovery primitives, asserts on results) | `src/tooluniverse/tool_discovery_tools.py` (as the thing under test) + `tests/unit/test_lazy_load_cache_consistency.py` (as the "pick a safe tool name" pattern) | role-match |
| `.planning/phases/03-.../evidence/<HEAD-oid>/{git.json,registration_chain.json,SHA256SUMS,...}` (new, evidence artifacts) | config/data (output, not code) | file-I/O | `.planning/phases/01-protected-sync-baseline/evidence/<oid>/` and `.planning/phases/02-upstream-main-integration/evidence/` | exact |

No controller/component/middleware/model files are in scope — this phase is entirely internal package/catalog reconciliation (scripts + tests + evidence artifacts), consistent with RESEARCH.md's Architectural Responsibility Map (all work is API/Backend + Database/Storage tier, in-process, no browser/CDN tier).

## Pattern Assignments

### `tests/unit/test_registry_integrity.py` (test, batch/transform) — EXTEND IN PLACE

**Analog:** itself — do not fork a parallel test file (D-04).

**Imports pattern** (lines 1-24, already in file):
```python
import json
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).parent.parent.parent
SRC = REPO / "src" / "tooluniverse"
DATA_DIR = SRC / "data"
SKILLS_DIR = REPO / "skills"
RULES_DIR = REPO / "claude" / "rules"

sys.path.insert(0, str(REPO / "src"))
```
Note (Pitfall 4): `RULES_DIR = REPO / "claude" / "rules"` — no leading dot. This is correct for this repo; do not "fix" it when extending.

**Core structural-check pattern to copy** (lines 34-69, `_load_defined_tool_names` / `_load_type_names`):
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
**Gap to fill (per RESEARCH.md Wave 0):** this glob is non-recursive (misses `data/broken_apis/*.json` — Pitfall 3) and has no module-file / `__init__.py` / duplicate-name checks. New Tier-2 helper functions should follow the exact same shape: `for jf in DATA_DIR.glob("**/*.json")` (recursive) plus a `default_config.py` category cross-reference (see Common Pattern below) to distinguish "live" duplicates from intentionally-archived ones.

**Test class pattern to copy** (lines 138-161):
```python
@pytest.mark.unit
class TestRegistryIntegrity:
    """Every referenced tool name must exist in the JSON-defined tool set."""

    @pytest.fixture(scope="class")
    def defined_names(self) -> set[str]:
        return _load_defined_tool_names()

    def test_defined_names_is_nonempty(self, defined_names):
        assert len(defined_names) > 100, (
            f"Expected 100+ tools, got {len(defined_names)}"
        )

    def test_required_tools_refs_exist(self, defined_names):
        """Every name in a required_tools array must be a real tool."""
        refs = _load_required_tools_refs()
        missing: list[str] = []
        for source, names in refs.items():
            for name in names:
                if name not in defined_names:
                    missing.append(f"  {name}  (referenced in {source})")
        assert not missing, "Ghost tools in required_tools arrays:\n" + "\n".join(
            sorted(set(missing))
        )
```
New tests for CAT-01's remaining 4 links (module-file existence, `__init__.py` completeness, `.tool_metadata.json` freshness, cross-file duplicate names) should follow this exact `fixture -> collect -> diff -> assert not missing, "<message>\n" + joined-list` shape — it is the established assertion-message convention in this file (readable diff output, not bare `assert a == b`).

**Class-name resolution pattern** (lines 175-197, `test_json_type_fields_exist_in_lazy_registry`) — reuse directly for any new check that needs to resolve a JSON `"type"` to Link 2 (`<domain>_tool.py` implementation):
```python
def test_json_type_fields_exist_in_lazy_registry(self):
    types = _load_type_names()
    registry = _load_lazy_registry_class_names()
    from tooluniverse.tool_registry import _tool_registry
    all_known = registry | set(_tool_registry.keys())
    missing = types - all_known
    special = {
        "BaseRESTTool", "VisualizationTool", "ClaudeCodeSkill", "SpecialTool",
    }
    missing -= special
    assert not missing, (
        "JSON configs reference unknown Python classes:\n"
        + "\n".join(f"  {t}" for t in sorted(missing))
    )
```

**Marker convention:** structural/static checks (file existence, name-set comparison) need no `network`/`require_api_keys`/`slow` marker and run in the default fast lane (`pytest.ini`'s default `addopts` already excludes those three). Only mark a new test if it actually calls `tu.load_tools()` or hits `grep_tools`/`get_tool_info` against a real credential-gated tool.

---

### `scripts/audit_registration_chain.py` (new utility, batch/transform) — Tier 1 + Tier 2 six-link audit

**Analog:** `scripts/audit_upstream_merge.py` (2,951 lines; same repo, same author-established pattern for structural diffing over the tool catalog).

**Reusable function 1 — AST-based definition extraction** (`extract_definition_names`, lines 1043-1053):
```python
def extract_definition_names(source: str) -> set[str]:
    """Every top-level and class-level (``Class.member``) definition name in *source*."""
    _tree, top, class_members = _index_module(source)
    names = set(top)
    for class_name, members in class_members.items():
        names.update(f"{class_name}.{member}" for member in members)
    return names
```
Use this to confirm a `<domain>_tool.py` implementation module actually defines the class a JSON `"type"` field names (Link 2 verification) — call directly, do not reimplement an AST walker.

**Reusable function 2 — two-stage verdict pattern** (`classify_finding`, starts line 1523) — read the surrounding ~80 lines before writing Tier 1's per-tool verdict function; the established shape is: primary comparison first, then a pin/self-heal recheck before finalizing a verdict, matching Phase 2's `findings.json` convention (verdict field is the primary signal, not re-derived comparisons downstream). Reuse this two-stage shape for Tier 1's per-tool six-link verdicts (`{defined, has_category, has_module_file, in_init, has_test}` per RESEARCH.md's architecture diagram) so Tier 1 and Tier 2 output stay joinable on a shared `verdict` field, per the Claude's-discretion note in CONTEXT.md.

**Category cross-reference pattern (for Pitfall 3's duplicate-vs-archived distinction)** — copy the existing convention this repo already uses to mark intentionally-disabled categories, read from `src/tooluniverse/default_config.py:762-765`:
```python
    # EBI OxO - Ontology cross-reference mappings across biomedical databases
    # Archived at: src/tooluniverse/data/broken_apis/oxo_tools.json
    # EBI retired the OxO service (all endpoints hang); use OLS (ols_* tools) instead.
    # "oxo": os.path.join(current_dir, "data", "oxo_tools.json"),
```
A Tier 2 duplicate-name check must treat any category whose `default_config.py` entry is commented out with an `# Archived at:` marker as intentionally excluded, not a stale/duplicate finding — cross-reference `default_config.py`'s live category map against `data/*.json` presence, don't just diff JSON files against each other.

---

### `scripts/capture_pr161_evidence.py` (new, or an appended stage) — SYNC-03 evidence

**Analog:** `scripts/capture_sync_baseline.py` (`publish_evidence` / `verify_checksums`, lines 1317-1404+).

**Evidence-bundle publish pattern to copy** (lines 1317-1369, `publish_evidence`):
```python
def publish_evidence(
    evidence: dict[str, Any],
    output_root: Path | str,
    secrets: Iterable[str] = (),
    required_stages: Iterable[str] = (),
    worktree_root: Path | str | None = None,
) -> Path:
    """Validate and atomically publish a canonical evidence tree."""
    output = Path(output_root).expanduser().resolve()
    ...
    stage = Path(tempfile.mkdtemp(prefix="baseline-", dir=output.parent))
    try:
        for name, value in sorted(evidence.items()):
            target = stage / (name if name.endswith(".json") else f"{name}.json")
            target.parent.mkdir(parents=True, exist_ok=True)
            _canonical_json(target, value)
        ...
        entries = []
        for path in sorted(p for p in stage.rglob("*") if p.is_file()):
            rel = path.relative_to(stage).as_posix()
            entries.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {rel}")
        (stage / "SHA256SUMS").write_text("\n".join(entries) + "\n", encoding="utf-8")
        ...
        stage.rename(output)
        return output
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise
```
Key properties to preserve: atomic staging directory + rename (never write partial evidence in place), sorted `SHA256SUMS` covering exactly the published files, `verify_checksums` companion for later re-verification. SYNC-03's evidence content is minimal (the exact command block already verified in RESEARCH.md):
```bash
git rev-parse HEAD
git merge-base --is-ancestor 16af425c053c306a658c96e254b4c4114338dd11 HEAD
echo "exit: $?"
```
Write `{head_oid, pr161_merge_oid, is_ancestor: bool, exit_code}` as `git.json` inside a `evidence/<head-oid>/` directory, matching Phase 1's `git.json` shape exactly (`.planning/phases/01-protected-sync-baseline/evidence/<oid>/git.json`).

---

### `scripts/smoke_discovery_sample.py` (new) — CAT-02 grep_tools/get_tool_info smoke check

**Analog 1 (system under test):** `src/tooluniverse/tool_discovery_tools.py` — every discovery primitive reads `self.tooluniverse.all_tool_dict` directly (verified at lines 99, 114, 281, 311, 429, 581, 813). The gated-tool error shape to assert against (not a bare "not found"):
```python
# Source: src/tooluniverse/tool_discovery_tools.py:808-819
{"name": tool_name, "error": "requires API key(s) not set: ..."}
```

**Analog 2 (safe-sample-selection pattern):** `tests/unit/test_lazy_load_cache_consistency.py` — read its `_SAFE_TOOL_NAMES` / `_SKIP_KEYWORDS` constants before writing the representative sample; reuse the same discipline (exclude GPU/model-loading and, per this phase's finding, exclude any tool whose `required_api_keys` are unmet on the running machine — check `tu._excluded_api_key_tools` rather than hardcoding key-family names).

**Call shape to copy** — smoke test should call the actual CLI/SDK discovery primitives, not re-derive results:
```python
tu run <TOOL>   # via `tu` CLI, or
from tooluniverse import ToolUniverse
tu = ToolUniverse(); tu.load_tools()
spec = tu.tool_specification("SomeToolName")
```

---

## Shared Patterns

### Evidence artifact convention (applies to SYNC-03 and CAT-01/CAT-02 audit output)
**Source:** `scripts/capture_sync_baseline.py::publish_evidence` / `verify_checksums`; directory shape at `.planning/phases/01-protected-sync-baseline/evidence/<full-oid>/`
**Apply to:** every new evidence-producing script this phase adds.
- Directory name = full git OID the evidence was captured against (not phase number).
- Every file inside is canonical JSON except `SHA256SUMS`, which is sorted `sha256  relative/path` lines covering exactly the other files.
- Publish via a temp-stage-then-atomic-`rename` — never write partial evidence into the final directory in place.

### Findings-first, human-gated posture (D-05, D-06)
**Source:** CONTEXT.md D-05/D-06, `.planning/phases/02-upstream-main-integration/02-CONTEXT.md` D-06/D-06a/D-06b (established last phase; this phase's own scripts must not invent a new posture).
**Apply to:** any script or test that discovers a genuine duplicate-name collision or a regeneration-output regression — record as a finding (JSON entry with a `verdict` field), never silently auto-fix or auto-commit. Regeneration itself (clean, additive/rename-only diffs) is the one case that IS auto-run per D-05 — the dividing line is whether the diff is a pure addition/rename consistent with Phase 2's merged JSON changes, or a name-set reduction/genuine collision (hard-stop, route to `checkpoint:human-verify`).

### Diff-before-commit regression guard (RESEARCH.md primary recommendation)
**Source:** RESEARCH.md "Concurrent State Investigation" root-cause section; no existing script implements this yet — new code, but the diffing style should match `scripts/forensic_trace_findings.py`'s "diff definitions, then check if a stage-only name is actually absent from HEAD or just renamed" discipline.
**Apply to:** any regeneration step (`tu build`, `generate_coding_api.py`, `generate_lazy_registry.py`) this phase's audit script triggers or verifies. Before treating regenerated `tools/__init__.py` as valid: diff its import-name set against the currently-committed HEAD's import-name set; any name present in HEAD but absent from the new output is a blocking finding requiring human review, not a self-resolving staleness case.

## No Analog Found

None — every file this phase touches extends an existing module or directly copies an established script/evidence pattern from Phase 1/2 of this same project. There is no genuinely new architectural surface in Phase 3.

## Metadata

**Analog search scope:** `tests/unit/`, `scripts/`, `src/tooluniverse/` (`tool_discovery_tools.py`, `default_config.py`, `execute_function.py`, `_lazy_registry_static.py`), `.planning/phases/01-protected-sync-baseline/evidence/`, `.planning/phases/02-upstream-main-integration/evidence/`
**Files scanned:** `tests/unit/test_registry_integrity.py` (full, 198 lines), `scripts/audit_upstream_merge.py` (targeted: `extract_definition_names` 1043-1053, `classify_finding` 1523+), `scripts/capture_sync_baseline.py` (header 1-80, `publish_evidence`/`verify_checksums` 1317-1404), `src/tooluniverse/default_config.py` (OxO comment block, 755-770, via RESEARCH.md quote), `src/tooluniverse/tool_discovery_tools.py` (via RESEARCH.md quotes, lines 99-819)
**Pattern extraction date:** 2026-08-07

## PATTERN MAPPING COMPLETE

**Phase:** 3 - follow-up-and-catalog-reconciliation
**Files classified:** 5

### Coverage
- Files with exact analog: 3 (`test_registry_integrity.py` extend-in-place, `audit_registration_chain.py` <- `audit_upstream_merge.py`, evidence artifacts <- Phase 1/2 `evidence/<oid>/` convention)
- Files with role-match analog: 2 (`capture_pr161_evidence.py` <- `capture_sync_baseline.py`'s evidence functions; `smoke_discovery_sample.py` <- `tool_discovery_tools.py` + `test_lazy_load_cache_consistency.py`)
- Files with no analog: 0

### Key Patterns Identified
- Every structural check in this phase follows `tests/unit/test_registry_integrity.py`'s existing shape: `_load_*()` helper returns a name-set from `data/*.json`, a `@pytest.fixture(scope="class")` wraps it, and the test body does `missing = ...; assert not missing, "<message>:\n" + "\n".join(sorted(...))` — extend this file, do not fork.
- Evidence output always follows Phase 1/2's `evidence/<full-oid>/{*.json,SHA256SUMS}` convention via `capture_sync_baseline.py::publish_evidence` (atomic temp-stage + rename, sorted checksums covering exactly the published set).
- Any regeneration step (`tu build`/`generate_coding_api.py`/`generate_lazy_registry.py`) must be wrapped in a diff-before-commit guard (compare `tools/__init__.py` import-name sets against HEAD) because both generators are credential-gated via `ToolUniverse.load_tools()` and will silently drop real tools on this machine — this is new logic with no direct in-repo analog, modeled on `forensic_trace_findings.py`'s diff-then-classify discipline.
- Genuine duplicate-name collisions and regeneration regressions are findings routed to human review (D-05/D-06 posture inherited from Phase 2's D-06/D-06a/D-06b), never silently auto-resolved; only additive/rename-consistent regeneration diffs are auto-applied.

### File Created
`/Users/davis/code/ToolUniverse/.planning/phases/03-follow-up-and-catalog-reconciliation/03-PATTERNS.md`

### Ready for Planning
Pattern mapping complete. Planner can now reference analog patterns in PLAN.md files.
