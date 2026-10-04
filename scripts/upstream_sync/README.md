# Upstream sync runbook (fork <- mims-harvard/ToolUniverse)

Written 2026-10-04T00:03:29.671Z after the 2026-10-01 sync (merge
`bccfcbbb`, landed on `main` through `c7367672`). Read this before the next
sync. Memory node: [[project_upstream_sync_2026_10_01]]. Previous sync plan:
`docs/superpowers/plans/2026-04-17-upstream-sync.md`.

## The one rule

Land the sync as a **real merge commit** (fast-forward push, or
`gh pr merge --merge`). Never squash or rebase it. The merge commit is the
new merge-base; squash it and the next sync re-fights every conflict from
the old base (2026-10-01: 275 of them).

## Remotes and safety

```bash
git remote -v          # origin = d33disc fork, upstream = mims-harvard
git remote set-url --push upstream no_push   # already set; never push there
git config rerere.enabled true   # already set; abort+redo replays fixes
```

## Procedure

### 1. Census (zero risk)

`git fetch upstream`, then
`git merge-tree --write-tree --name-only origin/main upstream/main` lists the
conflicts without touching the tree. Group them by directory; the classes in
step 3 covered about 95% last time.

### 2. Worktree and merge

New worktree on `chore/upstream-sync-<date>`, then
`git merge upstream/main --no-ff --no-commit`. Build a venv there:
`uv venv .venv && uv pip install -e '.[dev]'`.

### 3. Resolve by class

| Class | Resolution | Tool |
| --- | --- | --- |
| `plugin/skills/*` | Ours is symlinks-only to `../../skills/<name>` (PR #76). Rebuild as the union of both sides' names; first check upstream's `plugin/` copies are not newer than its `skills/` copies. | `relink_plugin_skills.sh` |
| `src/tooluniverse/data/*.json` | Structural 3-way merge per tool name, per key. Where both sides rewrote a `return_schema`, take one side WHOLE (never leaf-mix); the other is logged. | `json3way.py --policy --write` |
| `tools/*.py`, `.tool_metadata.json`, `_lazy_registry_static.py` | Generated. Take theirs, then regenerate (step 4). | - |
| Generated docs (`skills_showcase.rst`) | Take theirs, run `docs/generate_skills_showcase.py`. | - |
| Hand-written code, tests, docs | Resolve per hunk. `git checkout --theirs` drops our non-conflicting edits in the same file. | `hunks.py <file> show`, then `hunks.py <file> otb` |

### 4. Regenerate, then prove idempotence

```bash
PATH="$PWD/.venv/bin:$PATH" .venv/bin/python -c \
  "from tooluniverse.generate_tools import main
main(format_enabled=True, force_regenerate=True)"
.venv/bin/python -m tooluniverse.generate_lazy_registry
git add -A src/tooluniverse/tools src/tooluniverse/_lazy_registry_static.py
# run both again: `git diff --name-only` must be empty
```

### 5. Gates

Lint with `.venv/bin/pre-commit run --files ...`, never bare `ruff` (it picks
up a global config). Run the CI suite:

```bash
pytest tests/unit tests/integration -n auto --maxfail=100000 \
  -m "not slow and not require_api_keys and not network and not require_gpu"
```

Also run hand-merged files under `tests/tools/` directly; CI's markers skip
them.

### 6. Triage every failure against clean upstream

Export upstream's tests with `export_tests.py upstream/main <dir>`
(`git archive` skips `tests/` via export-ignore) and run the failing ids
there. Fails on upstream too: environment. Passes on upstream: our code
against a new upstream invariant, so fix it.

### 7. Schema evidence

`SYNC_DIR=<dir> python scripts/upstream_sync/schema_ab.py` gives a live A/B,
a junk probe, and a tested-contract flag per schema. Flip a schema back to
ours only for listed candidates, then regenerate (step 4) and **rerun the
full suite**.

### 8. Workflows, before the first push

List workflows the merge added:
`git diff --name-status <old-main> HEAD -- .github/`. On the fork every
publishing workflow is `disabled_manually`, but a NEW workflow cannot be
disabled until a push registers it, so guard it in the branch with
`if: github.repository == 'mims-harvard/ToolUniverse'`.

### 9. Land

```bash
git fetch origin && git merge-base --is-ancestor origin/main HEAD \
  && git push origin HEAD:main
```

Watch the Test Suite run on that sha to completion. Refresh the global
editable install:
`/Users/davis/miniforge3/bin/python -m pip install -e '.[openai,gemini]'`.

## What broke last time (recurring classes)

- **Our code against new upstream invariants**, invisible as text conflicts:
  tools reading `os.environ` (upstream requires request-scoped
  `credential()`); keyless local LLM backends making `has_any_api_keys()`
  always true; our soft guideline scoring against upstream's filter. Only the
  test suite finds these.
- **A schema can be a tested contract.** b5dfdba4 restored our stricter FAERS
  schemas; 3 upstream tests asserted upstream's keys; CI failed; c7367672
  reverted. The full suite had run before that commit, not after. Rerun the
  gate after EVERY commit.
- **Load-sensitive test**: `test_http_api_thread_pool` env-var case times out
  under `-n auto` locally and passes alone.
- **Known local-only failures** (also fail on clean upstream):
  `test_remote_data_path` x2, `test_remote_tool_boundaries` x2,
  `test_faers_count_truncation_disclosure` (API key in env).

## Open after this sync

- Scheduled `MCP contract drift` failed 2026-10-03: external server
  `mcp_auto_loader_gi` changed 1 of 15 tool contracts. Not caused by the
  sync; re-record with `scripts/sync_mcp_contracts.py` if wanted.
- Schemas kept as upstream's without live evidence (server 500s or missing
  fixtures): Ensembl lookup/VEP x3, MobiDB x2, VCF x3, phykit,
  coding_variant_fraction, Cellpose, RDKit_pharmacophore_features.
