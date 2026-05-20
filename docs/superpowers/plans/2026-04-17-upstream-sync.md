# Upstream Sync Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Merge upstream/main (2 commits) and PR #161 (11 commits) into our fork while preserving all 58 custom commits.

**Architecture:** Two-phase staged merge on a feature branch. Phase 1 merges upstream/main. Phase 2 merges PR #161's branch. Each phase resolves conflicts, runs tests, and commits before proceeding.

**Tech Stack:** git merge, pytest

**Critical context:** Our commit `26bb9d19` was a squash-integration of upstream PR #153 (not a merge commit), so git doesn't know we already have that content. The dry-run found 20 conflicting files — mostly add/add conflicts where both sides independently created the same tool files. The resolution strategy is: take upstream's version for canonical tool definitions (`--theirs`), manually merge structural files where we have custom additions.

---

### Task 1: Create Feature Branch and Merge upstream/main

**Files:**

- All 338 files from upstream/main's 2 commits land here
- 20 files will conflict (see conflict list below)

- [ ] **Step 1: Create feature branch**

```bash
git checkout -b feat/upstream-sync-2026-04-17
```

- [ ] **Step 2: Start the merge**

```bash
git merge upstream/main
```

Expected: `Automatic merge failed` with ~20 conflicts.

- [ ] **Step 3: Batch-resolve add/add tool file conflicts with `--theirs`**

These 5 files are new tool implementations that both sides created independently. Upstream is the canonical source. Our versions had `Optional[str | Any]` type annotations; upstream has cleaner `Optional[str]`.

```bash
git checkout --theirs -- \
  src/tooluniverse/tools/AgingCohort_search.py \
  src/tooluniverse/tools/DataQuality_assess.py \
  src/tooluniverse/tools/DegreesOfUnsaturation_calculate.py \
  src/tooluniverse/tools/MetaAnalysis_run.py \
  src/tooluniverse/tools/NHANES_download_and_parse.py
git add \
  src/tooluniverse/tools/AgingCohort_search.py \
  src/tooluniverse/tools/DataQuality_assess.py \
  src/tooluniverse/tools/DegreesOfUnsaturation_calculate.py \
  src/tooluniverse/tools/MetaAnalysis_run.py \
  src/tooluniverse/tools/NHANES_download_and_parse.py
```

- [ ] **Step 4: Batch-resolve JSON data file conflicts with `--theirs`**

These 8 JSON files contain tool definitions. Upstream is the source of truth. We did not add custom tool definitions to any of these.

```bash
git checkout --theirs -- \
  src/tooluniverse/data/admetai_tools.json \
  src/tooluniverse/data/datacite_tools.json \
  src/tooluniverse/data/ena_portal_tools.json \
  src/tooluniverse/data/iedb_tools.json \
  src/tooluniverse/data/mgi_tools.json \
  src/tooluniverse/data/rcsb_advanced_search_tools.json \
  src/tooluniverse/data/unpaywall_tools.json \
  src/tooluniverse/data/wikipathways_tools.json
git add \
  src/tooluniverse/data/admetai_tools.json \
  src/tooluniverse/data/datacite_tools.json \
  src/tooluniverse/data/ena_portal_tools.json \
  src/tooluniverse/data/iedb_tools.json \
  src/tooluniverse/data/mgi_tools.json \
  src/tooluniverse/data/rcsb_advanced_search_tools.json \
  src/tooluniverse/data/unpaywall_tools.json \
  src/tooluniverse/data/wikipathways_tools.json
```

- [ ] **Step 5: Batch-resolve remaining `--theirs` files**

These files have conflicts where upstream's version is correct and we have no custom modifications beyond what came from PR #153:

```bash
git checkout --theirs -- \
  src/tooluniverse/restful_tool.py \
  src/tooluniverse/tools/.tool_metadata.json \
  tests/tools/test_semantic_scholar_tool_resilience.py
git add \
  src/tooluniverse/restful_tool.py \
  src/tooluniverse/tools/.tool_metadata.json \
  tests/tools/test_semantic_scholar_tool_resilience.py
```

- [ ] **Step 6: Manually resolve `src/tooluniverse/tools/__init__.py`**

This file has 3 conflict regions. Both sides added tool registrations. Open the file, find `<<<<<<<` markers, and merge both sides' import/registration lines. Keep our entries AND upstream's entries. Remove all conflict markers.

After editing, run:

```bash
git add src/tooluniverse/tools/__init__.py
```

- [ ] **Step 7: Manually resolve `src/tooluniverse/_lazy_registry_static.py`**

This file has 3 conflict regions. Our version added entries (e.g., `AgingCohortSearchTool`, `SEC*` entries) that upstream doesn't have. Upstream's version may have entries in different positions. Resolution: keep ALL entries from both sides, maintaining alphabetical order.

After editing, run:

```bash
git add src/tooluniverse/_lazy_registry_static.py
```

- [ ] **Step 8: Resolve `skills/tooluniverse/SKILL.md` conflict**

Both sides modified the router skill. Check the conflict — our version has custom routing (deep-research, company-research); upstream rewrote it as a reasoning framework. Resolution: take upstream's version and re-add our custom skill routes.

Also clean up the `skills/tooluniverse~HEAD` artifact file if it exists:

```bash
rm -f skills/tooluniverse~HEAD
git add skills/tooluniverse/SKILL.md
```

- [ ] **Step 9: Verify no remaining conflicts**

```bash
git diff --name-only --diff-filter=U
```

Expected: empty output (no remaining conflicts).

- [ ] **Step 10: Commit Phase 1 merge**

```bash
git commit -m "merge: sync with upstream/main (PR #153 + server.json v1.1.11)"
```

---

### Task 2: Run Tests After Phase 1

**Files:** No files modified — verification only.

- [ ] **Step 1: Run the test suite**

```bash
cd /Users/davis/code/ToolUniverse
python -m pytest tests/ -x -q --timeout=60 2>&1 | tail -30
```

Expected: Tests pass at same or better rate than before the merge. Some tests may skip due to missing API keys — that's expected.

- [ ] **Step 2: Spot-check tool loading**

```bash
cd /Users/davis/code/ToolUniverse
python -c "from tooluniverse import ToolUniverse; tu = ToolUniverse(); print(f'Tools loaded: {len(tu.tool_names)}')"
```

Expected: Tool count should be equal to or greater than before.

- [ ] **Step 3: If tests fail, diagnose and fix**

If failures are caused by merge resolution errors, fix the affected files, stage them, and amend the merge commit:

```bash
git add <fixed-files>
git commit --amend --no-edit
```

If failures are pre-existing (present on main before the merge), note them and proceed.

---

### Task 3: Merge PR #161 Branch (feat/claude-code-plugin)

**Files:**

- 170 files from PR #161 branch
- Most are NEW files in `plugin/`, `skills/devtu-*`, `skills/tooluniverse-claude-code-plugin/`
- 4 files will conflict: `.gitignore`, `__init__.py`, `_lazy_registry_static.py`, `default_config.py`

- [ ] **Step 1: Merge PR #161 branch**

```bash
git merge FETCH_HEAD --no-edit
```

(We already fetched `upstream feat/claude-code-plugin` earlier. If FETCH_HEAD is stale, re-fetch first: `git fetch upstream feat/claude-code-plugin`)

Expected: Conflicts in up to 4 files.

- [ ] **Step 2: Resolve `.gitignore`**

PR #161 appends 20 lines (benchmark outputs, memory, API keys). Our version already has custom ignores. Open the file, find conflict markers, keep BOTH sides. The upstream additions go at the end.

```bash
git add .gitignore
```

- [ ] **Step 3: Resolve `src/tooluniverse/__init__.py`**

PR #161 adds a torch CPU block near the top (lines 5-15 in upstream's version):

```python
# Force CPU before torch is imported anywhere — prevents MPS (Metal) segfaults
# in forked subprocesses (uvx MCP server, tu CLI, Claude Code plugin).
os.environ.setdefault("PYTORCH_MPS_HIGH_WATERMARK_RATIO", "0.0")
os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
try:
    import torch

    if hasattr(torch, "set_default_device"):
        torch.set_default_device("cpu")
except ImportError:
    pass
```

Insert this block after line 3 (`from typing import ...`) and before the `extend_path` comment in our version. Keep everything else from our version unchanged.

```bash
git add src/tooluniverse/__init__.py
```

- [ ] **Step 4: Resolve `src/tooluniverse/_lazy_registry_static.py`**

PR #161 adds 4 entries after `"ComposeTool"`:

```python
    "CompoundDiseaseProfileTool": "compound_disease_tool",
    "MSigDBTool": "msigdb_tool",
    "CompoundGeneDiseaseAssociationTool": "compound_gene_disease_tool",
    "CompoundVariantAnnotationTool": "compound_variant_tool",
```

Add these 4 entries in alphabetical order into the registry dict, preserving all our existing custom entries.

```bash
git add src/tooluniverse/_lazy_registry_static.py
```

- [ ] **Step 5: Resolve `src/tooluniverse/default_config.py`**

PR #161 adds 3 compound tool config paths after the `"compose"` entry:

```python
    # Compound tools — multi-database queries in a single call
    "compound_gene_disease": os.path.join(
        current_dir, "data", "compound_gene_disease_tools.json"
    ),
    "compound_variant": os.path.join(
        current_dir, "data", "compound_variant_tools.json"
    ),
    "compound_disease": os.path.join(
        current_dir, "data", "compound_disease_tools.json"
    ),
```

Add these entries after the `"compose"` line in our version, preserving all our existing entries.

```bash
git add src/tooluniverse/default_config.py
```

- [ ] **Step 6: Handle any other unexpected conflicts**

```bash
git diff --name-only --diff-filter=U
```

If any remain, inspect each. For new plugin files, take `--theirs`. For files with our custom code, merge manually.

- [ ] **Step 7: Verify no remaining conflicts and commit**

```bash
git diff --name-only --diff-filter=U
# Should be empty
git commit -m "merge: integrate upstream PR #161 (Claude Code plugin + compound tools)"
```

---

### Task 4: Run Tests After Phase 2

**Files:** No files modified — verification only.

- [ ] **Step 1: Run the test suite**

```bash
cd /Users/davis/code/ToolUniverse
python -m pytest tests/ -x -q --timeout=60 2>&1 | tail -30
```

Expected: Same or better pass rate as after Phase 1.

- [ ] **Step 2: Spot-check tool loading (includes new compound tools)**

```bash
cd /Users/davis/code/ToolUniverse
python -c "
from tooluniverse import ToolUniverse
tu = ToolUniverse()
print(f'Tools loaded: {len(tu.tool_names)}')
# Check compound tools from PR #161
for name in ['gather_gene_disease_associations', 'annotate_variant_multi_source', 'gather_disease_profile']:
    info = tu.get_tool_info(name)
    print(f'{name}: {\"found\" if info else \"MISSING\"}')"
```

- [ ] **Step 3: Verify plugin directory structure**

```bash
ls -la plugin/
ls plugin/skills/ | head -10
ls plugin/.claude-plugin/
```

Expected: `plugin/` directory exists with `.claude-plugin/plugin.json`, `.mcp.json`, `settings.json`, `agents/`, `commands/`, `skills/` subdirectories.

- [ ] **Step 4: Verify our custom code is intact**

```bash
# Check custom directories still exist and are unmodified
ls claude/rules/
ls ralph-health/
ls ralph-schemas/
ls skills/tooluniverse-deep-research/ 2>/dev/null || echo "check symlink"
git diff main -- claude/ ralph-health/ ralph-schemas/ ralph-docs/ paper/ | head -5
```

Expected: Our custom directories are untouched. The `git diff` against main for these dirs should show no changes (they weren't part of any upstream change).

- [ ] **Step 5: If tests fail, diagnose and fix before proceeding**

---

### Task 5: Final Verification and PR

**Files:** No new files — wrap-up only.

- [ ] **Step 1: Review the full diff against main**

```bash
git diff --stat main...HEAD
```

Verify: no unexpected deletions of our custom files, new upstream files present.

- [ ] **Step 2: Check commit log**

```bash
git log --oneline main..HEAD
```

Expected: 2 merge commits (Phase 1 + Phase 2).

- [ ] **Step 3: Push branch and create PR**

```bash
git push -u origin feat/upstream-sync-2026-04-17
```

Then create PR against main:

```bash
gh pr create --title "merge: sync upstream/main + PR #161 (plugin + compound tools)" --body "$(cat <<'EOF'
## Summary
- Merges 2 commits from upstream/main (PR #153 reasoning frameworks + 31 new tools, server.json v1.1.11)
- Merges 11 commits from upstream PR #161 (Claude Code plugin packaging, compound tools, benchmark harness, skill hardening, torch MPS fix)
- All custom code preserved (claude rules, ralph infra, workflows, papers)

## Conflict Resolution
- 20 conflicts in Phase 1 (squash vs merge of same PR #153 content) — resolved by taking upstream for canonical tool files, manual merge for structural files
- 4 conflicts in Phase 2 (new compound tool registrations) — resolved by adding upstream entries to our versions

## Test plan
- [ ] pytest passes at same or better rate
- [ ] Tool count equal or greater than before
- [ ] Compound tools (gather_gene_disease_associations, etc.) load correctly
- [ ] Plugin directory structure intact
- [ ] Custom code (claude/, ralph-*, paper/) unchanged

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

- [ ] **Step 4: Squash-merge PR to main once approved**

```bash
gh pr merge --squash
```
