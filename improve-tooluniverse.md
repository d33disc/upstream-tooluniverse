# ToolUniverse Improvement Guide

## Current State (2026-03-07)

### Active PR
- **PR #126** on branch `fix/researcher-sim-bugs` — OPEN, MERGEABLE
- URL: https://github.com/mims-harvard/ToolUniverse/pull/126
- Contains 27 commits fixing bugs found through researcher persona simulations

### What Has Been Done

#### Simulation-Driven Bug Fix Process
We run **researcher persona simulations** — Agent subagents that simulate real scientific workflows (e.g., "computational immunologist studying PD-L1 resistance") using ToolUniverse tools via MCP. These simulations surface bugs that unit tests miss: wrong API URLs, changed parameter names, deprecated IDs, missing required fields, etc.

#### Bugs Fixed in PR #126 (27 commits)

**API Parameter/Endpoint Changes:**
- GTEx: `medianGeneExpression` → `clusteredMedianGeneExpression`; default to `gtex_v8` (v10 returns empty)
- HumanBase: API now requires `giant_version=v1|v3` parameter (without it → HTTP 500)
- OpenTargets: Alzheimer's disease ID migrated from `EFO_0000249` → `MONDO_0004975` (EFO deprecated)
- PMC: NCBI esummary XML key changed from `"pubmed"` → `"pmid"` for PMID extraction
- ClinicalTrials: migrated to v2 API; limit parameter mapping fixed
- ENCODE: histone search graceful 404 on invalid biosample

**Tool Logic Fixes:**
- ChEMBL: mechanism search now case-insensitive; target/assay IDs use `__exact` params
- ClinVar: condition search uses `[dis]` field tag for eSearch
- COSMIC: deduplication of mutation results
- Enrichr: output size limited to prevent combinatorial explosion
- GxA: gene_id filter uses exact match instead of substring
- GWAS: `disease_trait` auto-resolves to `efo_id` for reliable filtering
- STRING: category filter simplified
- IntAct: interactor endpoint fixes
- Monarch: strips 0/empty values; category parameter fix
- CTD: mitochondrial gene name handling
- GDC: mutation frequency calculation fix
- OncoKB: demo mode handling

**Infrastructure Improvements:**
- `_truncate_response` saves full response to `/tmp/tooluniverse_result_*.json` and returns file path
- `BaseRESTTool._process_response` detects HTML error pages (e.g., MSigDB "Gene Set Not Found") → returns `status: "error"` instead of raw HTML
- `BaseTool.get_schema_const_operation()` extracted; auto-fills redundant `operation` param across 90 tools
- Removed dead code from HPA PPI tool

**Test Coverage:**
- `tests/tools/test_researcher_simulation_fixes.py` — 105 tests covering all fixes
- `tests/tools/test_pharmacogenomics_workflow.py` — 132 tests

### Unstaged Changes (Not Part of PR)
- `.env.template` — new API key entries (BIOGRID, CLUE, HF_TOKEN, LLM keys)
- `src/tooluniverse/_lazy_registry_static.py` — minor change

---

## How to Continue This Work

### 1. Run Researcher Persona Simulations

Launch 2 Agent subagents simulating different research domains. Each agent:
1. Uses `mcp__tooluniverse__find_tools` to discover relevant tools
2. Calls `mcp__tooluniverse__execute_tool` with realistic parameters
3. Examines responses for errors, empty results, or unexpected behavior
4. Reports a categorized summary (CRITICAL / MODERATE / MINOR)

**Example agent prompt:**
```
You are a [domain] researcher studying [topic]. Simulate a realistic
research workflow using ToolUniverse tools via mcp__tooluniverse__execute_tool.
For each tool call, examine the response for: HTTP errors, empty results,
missing fields, incorrect parameter handling, truncated responses.
Report bugs categorized as CRITICAL/MODERATE/MINOR.
```

**Good research domains to simulate:**
- Structural biology (PDB, AlphaFold, UniProt, STRING)
- Rare disease diagnosis (Orphanet, OMIM, ClinVar, Monarch)
- Cancer genomics (CIViC, OncoKB, COSMIC, GDC)
- Metabolomics (HMDB, MetaboLights, MetabolomicsWorkbench, ChEBI)
- Epigenomics (ENCODE, Roadmap, GEO, HPA)
- Drug safety (FAERS, DailyMed, OpenFDA, CTD)
- Population genetics (GWAS Catalog, Ensembl, dbSNP, gnomAD)
- Microbiome / infectious disease (NCBI Taxonomy, UniProt, PubMed)

### 2. Fix Bugs Found by Simulations

**Workflow:**
1. Read the tool's Python source (e.g., `src/tooluniverse/some_tool.py`)
2. Read the tool's JSON config (e.g., `src/tooluniverse/data/some_tools.json`)
3. Identify root cause (API change? wrong parameter? missing field?)
4. Test the API directly with `curl` to confirm the fix
5. Edit the Python source and/or JSON config
6. Write unit tests in `tests/tools/test_researcher_simulation_fixes.py`
7. Run tests: `python -m pytest tests/tools/test_researcher_simulation_fixes.py -x`

**Common bug patterns:**
- API parameter renamed or now required (e.g., HumanBase `giant_version`)
- Ontology/ID migration (e.g., EFO → MONDO)
- API response key renamed (e.g., PMC `"pubmed"` → `"pmid"`)
- API returns HTML error page instead of JSON 404
- Default values no longer valid (e.g., GTEx v10 returning empty)
- Test examples using deprecated IDs

### 3. Stale MCP Server Caveat

**CRITICAL:** The MCP server may run cached/older code. If a simulation reports a bug, first check if the fix already exists in local code before implementing. Common pattern:
```bash
# Check if the fix is already in local code
grep -n "the_fix_pattern" src/tooluniverse/some_tool.py
```
If the fix exists locally but the MCP server shows the bug, it's a **stale server** issue, not a code bug. Note it and move on.

### 4. Git Workflow Rules

```bash
# NEVER push to main directly
# ALWAYS use the existing open PR branch (or create a new one if merged)

# Check for open PRs first
gh pr list --state open

# If PR exists and is not merged, add commits to it:
git checkout fix/researcher-sim-bugs
# ... make changes ...
git add <specific-files>
git commit -m "fix: description of fix"

# Rebase before pushing
git fetch origin && git stash && git rebase origin/main && git stash pop
git push --force-with-lease origin fix/researcher-sim-bugs

# If previous PR was merged, create new branch:
git checkout -b fix/round-XX-bugs origin/main

# NEVER add Co-Authored-By: Claude to commits
# NEVER use "BUG" in commit messages — use "fix:" or "feat:" prefix
# NEVER commit temp files, .env, or credentials
# Use `git add <specific-files>` not `git add -A`
```

### 5. Pre-commit Hook

ruff-format runs on commit. If first commit fails:
```bash
git add <same-files>  # re-add reformatted files
git commit -m "same message"  # second attempt passes
```

### 6. JSON Config Rules

- `return_schema` MUST have `oneOf`: `[{data+metadata}, {error}]`
- Test examples MUST use real IDs (no DUMMY/PLACEHOLDER)
- Mutually exclusive params: make both `["type", "null"]`
- No trailing commas in JSON — validate: `python3 -c "import json; json.load(open('file.json'))"`

### 7. Code Quality

After making changes, run the code-simplifier:
- Available as Agent subagent type `code-simplifier:code-simplifier`
- Or use the `/simplify` skill

### 8. Key File Locations

| File | Purpose |
|------|---------|
| `src/tooluniverse/<api>_tool.py` | Tool Python implementation |
| `src/tooluniverse/data/<api>_tools.json` | Tool JSON configuration |
| `src/tooluniverse/base_rest_tool.py` | Base class for REST API tools |
| `src/tooluniverse/base_tool.py` | Base class for all tools |
| `src/tooluniverse/smcp.py` | MCP server entry point, truncation logic |
| `src/tooluniverse/_lazy_registry_static.py` | Tool class → module mapping |
| `tests/tools/test_researcher_simulation_fixes.py` | Main test file (105 tests) |
| `src/tooluniverse/data/broken_apis/` | Known broken APIs |

### 9. Known Broken/Unstable APIs

- **MetaboAnalyst REST**: HTTP 500 since Dec 2024
- **HMDB**: No open API for disease endpoint → returns error status
- **HumanBase**: Network endpoint requires `giant_version` param (fixed)
- **MSigDB**: Some KEGG gene sets renamed to KEGG_MEDICUS collection

### 10. Testing

```bash
# Run specific test class
python -m pytest tests/tools/test_researcher_simulation_fixes.py::TestClassName -xvs

# Run all simulation tests
python -m pytest tests/tools/test_researcher_simulation_fixes.py --tb=short

# Run all tests
python -m pytest tests/ --tb=short -q
```
