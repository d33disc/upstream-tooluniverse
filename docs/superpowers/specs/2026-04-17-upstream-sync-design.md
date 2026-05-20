# Upstream Sync Design — 2026-04-17

## Goal

Bring ToolUniverse fork up to date with `mims-harvard/ToolUniverse` upstream/main
and incorporate PR #161 (`feat/claude-code-plugin`), while preserving all custom
code in this repo (skills, ralph infra, claude rules, tests, workflows, papers).

## Current State

| Metric | Value |
|--------|-------|
| Commits behind upstream/main | 2 |
| Commits ahead (custom) | 58 |
| PR #161 commits (not yet in upstream/main) | 11 |
| PR #161 changed files | 170 (+6,696 / -12) |
| Upstream/main changed files | 338 (+35,882 / -14,552) |

## Identified Conflict Files

Four files are modified on both sides:

| File | Our changes | Upstream changes | Resolution |
|------|------------|------------------|------------|
| `.gitignore` | Custom ignores (ralph, paper, cache) | New ignores (evals, memory, API keys) | Union both sides |
| `src/tooluniverse/__init__.py` | Backend refactor (ClaudeCliClient default) | torch CPU fix for MPS segfault | Keep ours, add torch fix |
| `src/tooluniverse/_lazy_registry_static.py` | Added SEC EDGAR + custom entries | 31 new tool class entries | Keep ours, append theirs |
| `src/tooluniverse/default_config.py` | Custom config paths | 3 new JSON paths for compound tools | Keep ours, append theirs |

## Approach: Staged Merge (Option A)

### Phase 1 — Merge upstream/main

1. Create branch `feat/upstream-sync-2026-04-17` from `main`
2. Run `git merge upstream/main`
3. Resolve conflicts in the 4 identified files using "keep ours + add theirs" strategy
4. Run `pytest` to verify
5. Commit the merge

### Phase 2 — Merge PR #161 branch

1. Fetch: `git fetch upstream feat/claude-code-plugin`
2. Run `git merge upstream/feat/claude-code-plugin`
3. Resolve conflicts (same 3-4 src files, same strategy)
4. New content lands cleanly: `plugin/`, compound tools, benchmark harness, skill updates
5. Run `pytest` to verify
6. Commit the merge

## Conflict Resolution Strategy

For all conflicts: keep our custom code, layer in upstream additions. Never drop our
lines. Specifically:

- **Additive files** (`.gitignore`, `_lazy_registry_static.py`, `default_config.py`):
  accept both sides — these are append-style, no structural conflict expected.
- **`__init__.py`**: our refactor (ClaudeCliClient default, backend cleanup) is
  structural. Upstream adds `torch.set_default_device('cpu')` near the top. Apply
  upstream's torch lines into our version of the file — do not revert our backend changes.
- If git cannot auto-merge, manually inspect the conflict markers and apply the above
  rules. Do not blindly accept either `--ours` or `--theirs`.

## Rollback Plan

- Phase 1 breaks: `git reset --hard main` — nothing lost
- Phase 1 clean, Phase 2 breaks: `git reset --hard` to Phase 1 merge commit — keep upstream/main sync
- Both clean: squash-merge to main via PR

## What NOT to touch

- `claude/` directory (our rules, commands, hooks, scripts)
- `ralph-*` directories (our infra)
- `paper/`, `docs/SI_*`, `emotional_dysregulation_*` (our papers)
- `.github/workflows/` custom workflows (CODEOWNERS, labeler, tool-health, sync-upstream)
- `TOOL_MANIFEST.json`, `tool_composition_graph*` (our generated artifacts)

## Success Criteria

1. All 4 conflict files resolved with both sides' content preserved
2. `pytest` passes (same or better than current pass rate)
3. New upstream tools load correctly (`grep_tools`, `get_tool_info` spot checks)
4. Plugin directory present and structurally intact
5. Our custom code unchanged (git diff confirms no regressions)
