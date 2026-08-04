# Phase 1: Protected Sync Baseline - Research

**Researched:** 2026-08-03
**Domain:** Git synchronization provenance, preservation inventory, and reproducible multi-surface validation
**Confidence:** HIGH for repository/runtime facts; MEDIUM for external procedural guidance

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

### Baseline Depth
- **D-01:** The pre-sync baseline must be comprehensive: targeted high-risk suites, the broader offline suite, catalog loading, and representative Python, CLI, MCP stdio/HTTP, and REST probes.
- **D-02:** The baseline must be fully green before synchronization. Existing failures are not accepted as baseline debt; they must be diagnosed and fixed before upstream integration.
- **D-03:** Every live provider that is currently configured must pass its selected checks. Transient timeouts and rate limits receive bounded retries with fixed backoff; a persistent configured-provider failure blocks synchronization and retains diagnostics.
- **D-04:** Run the comprehensive baseline locally on Python 3.12. CI must prove compatibility across the full declared Python 3.10+ support range; the current Python-3.12-only CI matrix is insufficient for this decision.
- **D-05:** Each public surface must prove the complete discovery-to-execution chain: list or search, inspect the exact schema, execute a deterministic tool, and return a structured success or error.
- **D-06:** Use a tiered probe matrix covering deterministic credential-free local tools, representative fork-specific tools, configured remote scientific providers, and a catalog-driven sample across major categories.
- **D-07:** Compare normalized schemas and semantic invariants rather than volatile byte-for-byte output. Normalize timestamps, generated IDs, and unstable remote ordering while enforcing status, required keys, types, documented ordering guarantees, and domain invariants.

### the agent's Discretion
- Select the exact representative tools and category sample, provided every tier in D-06 is present and the choices are recorded.
- Choose bounded retry counts and backoff intervals that keep live checks finite and reproducible.
- Choose the baseline artifact layout and machine-readable formats, provided exact revisions, commands, environment facts, outcomes, and diagnostics remain auditable.
- Order targeted and broad checks to fail quickly without reducing the required coverage.

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| BASE-01 | Maintainer can identify the exact fork revision, upstream revision, divergence, worktree state, and staged integration targets before synchronization begins | Immutable revision capture, porcelain-v2 worktree capture, ancestry checks, and isolated-worktree pattern below. [VERIFIED: `.planning/REQUIREMENTS.md:10-14`; verbatim ID/value: `BASE-01`] |
| BASE-02 | Maintainer has a reproducible pre-sync baseline for relevant tests, catalog loading, and representative discovery/execution behavior | Prescriptive test lanes, catalog evidence, five-surface probes, normalization, retries, and checksummed evidence below. [VERIFIED: `.planning/REQUIREMENTS.md:10-14`; verbatim ID/value: `BASE-02`] |
| PRES-01 | Maintainer has an explicit inventory of fork-specific code, tools, plugins, generated assets, and symlinks that must survive synchronization | Git-object-based preservation manifest, generated-asset classification, untracked-file policy, and symlink target verification below. [VERIFIED: `.planning/REQUIREMENTS.md:10-14`; verbatim ID/value: `PRES-01`] |
</phase_requirements>

## Summary

Phase 1 should be implemented as a fail-closed evidence pipeline, not as a merge preparation checklist. Pin the fork and upstream by full object ID, create the future synchronization branch in a separate Git worktree at the pinned fork commit, leave the user's original checkout and untracked files untouched, then produce one checksummed evidence bundle containing Git topology, the preservation manifest, environment facts, test reports, catalog facts, and normalized surface/provider probes. [VERIFIED: `.planning/phases/01-protected-sync-baseline/01-CONTEXT.md:7-29`; locked decisions quoted above]

The live topology invalidates the April plan's dated counts. Fork `HEAD` is `05243fd33d533e50d4abd69869fb9760fa37a647`; canonical `mims-harvard/ToolUniverse` `main` is `56adcfd9c299078d0c40fde642b0be006510ccf3`; their merge base is the upstream commit; and `git rev-list --left-right --count HEAD...upstream/main` returned `97 0`. Historical PR #161 is closed and merged, and merge commit `16af425c053c306a658c96e254b4c4114338dd11` is already an ancestor of current upstream. These are observations for the pinned 2026-08-03 baseline, not timeless assumptions. [VERIFIED: `git rev-parse`, `git merge-base`, `git rev-list`, `git ls-remote`, and GitHub API queries executed 2026-08-03] [CITED: https://github.com/mims-harvard/ToolUniverse/commit/56adcfd9c299078d0c40fde642b0be006510ccf3] [CITED: https://github.com/mims-harvard/ToolUniverse/pull/161]

The current checkout has no staged or unstaged tracked changes, but has four untracked JSON files under `ralph-specs/fleet/results/`. The fork-versus-upstream content delta is large (`1373` paths, `137018` additions, `157815` deletions), including `120` tracked symlinks. Three tracked plugin-skill links are currently broken; Phase 1 must repair them or obtain an explicit intentional-broken classification before the preservation gate can be green. [VERIFIED: `git status --porcelain=v2`, `git diff --numstat upstream/main...HEAD`, `git ls-files -s`, and `find ... -type l` executed 2026-08-03]

**Primary recommendation:** Build one stdlib-only `scripts/capture_sync_baseline.py` orchestrator plus focused pytest coverage; make it emit deterministic JSON/JUnit/log artifacts to a caller-supplied directory outside the integration worktree, and block progression unless every required lane and preservation invariant is green. [VERIFIED: `pyproject.toml:1-56,73-84`; existing Python and pytest stack quoted in Standard Stack]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|--------------|----------------|-----------|
| Revision pinning and divergence | Repository / Git object database | Evidence bundle | Git owns commit identity and ancestry; JSON records the result without becoming the source of truth. [CITED: https://git-scm.com/docs/git-merge-base] |
| Worktree isolation | Repository / Git worktree | Filesystem | A second worktree separates synchronization from the user's dirty checkout while preserving common object history. [CITED: https://git-scm.com/docs/git-worktree] |
| Preservation inventory | Repository / filesystem metadata | Evidence bundle | Git modes/object IDs protect tracked content; `lstat`/`readlink` protect link identity without traversal. [VERIFIED: current `git ls-files -s` reports mode `120000` for tracked links] |
| Baseline orchestration | Developer tooling / Python script | pytest + subprocesses | The script sequences existing tools and writes evidence; it must not own ToolUniverse execution semantics. [VERIFIED: `.planning/codebase/ARCHITECTURE.md:39-66`] |
| Discovery and execution probes | Shared `ToolUniverse` core | Python, CLI, MCP, REST adapters | Every transport must delegate scientific execution to the shared core. [VERIFIED: `.planning/codebase/ARCHITECTURE.md:107-120`] |
| CI compatibility | GitHub Actions | uv/pytest | CI owns the supported-runtime matrix; pytest owns behavioral assertions. [VERIFIED: `.github/workflows/tests.yml:9-67`] |
| Live-provider gating | Baseline orchestrator | Existing adapters/tests | The orchestrator selects configured providers and retries only transient failures; adapters retain provider semantics. [VERIFIED: `src/tooluniverse/execute_function.py:758-797`] |

## Live Baseline Facts

| Fact | Current evidence | Planning consequence |
|------|------------------|----------------------|
| Fork revision | `05243fd33d533e50d4abd69869fb9760fa37a647` on `docs/gsd-codebase-map` | Pin this exact object for Phase 1; do not use a moving branch name. [VERIFIED: `git rev-parse HEAD` and `git status --porcelain=v2 --branch`, 2026-08-03] |
| Canonical upstream revision | `56adcfd9c299078d0c40fde642b0be006510ccf3` | Record both `git ls-remote` result and local ref; fail if they disagree. [VERIFIED: `git ls-remote` and GitHub API, 2026-08-03] |
| Divergence | `97 0` for `HEAD...upstream/main` | Upstream is already contained; Phase 2 is a no-op against this pin unless a later upstream revision is deliberately selected. [VERIFIED: `git rev-list --left-right --count` and `git merge-base`, 2026-08-03] |
| PR #161 | state `closed`, `merged=true`, merge commit `16af425c...`; merge commit is upstream ancestor | Preserve as provenance evidence; do not re-merge or cherry-pick it. [VERIFIED: GitHub API and `git merge-base --is-ancestor`, 2026-08-03] |
| Worktree | exactly four untracked files under `ralph-specs/fleet/results/`; no tracked index/worktree delta | Leave these files in the original checkout and inventory metadata only. [VERIFIED: `git status --short` and `git ls-files --others --exclude-standard`, 2026-08-03] |
| Runtime catalog | `2690` loaded tools, `605` categories, `54` gated tools, package `1.4.0` | Capture fresh runtime facts; do not compare against `TOOL_MANIFEST.json` counts. [VERIFIED: `uv run tu status --json`, 2026-08-03] |
| Configured credential names | `DEEPSEEK_API_KEY`, `FDA_API_KEY`, `HF_TOKEN`, `ICD_CLIENT_ID`, `JINA_API_KEY`, `NCBI_API_KEY`, `NVIDIA_API_KEY`, `OPENAI_API_KEY`, `OPENROUTER_API_KEY`, `SEMANTIC_SCHOLAR_API_KEY`, `TAVILY_API_KEY`, `USPTO_API_KEY` | Select at least one bounded live probe for every configured provider family without recording values. [VERIFIED: environment-name intersection with `ToolUniverseConfig.CREDENTIAL_SPECS`, 2026-08-03] |
| Tracked symlinks | `120`; three broken targets | Add a hard preservation check before integration. [VERIFIED: `git ls-files -s` and non-following filesystem scan, 2026-08-03] |

The three broken tracked links are, verbatim: `plugin/skills/tooluniverse-computational-biophysics-workspace -> ../../skills/tooluniverse-computational-biophysics-workspace`, `plugin/skills/tooluniverse-organic-chemistry-workspace -> ../../skills/tooluniverse-organic-chemistry-workspace`, and `plugin/skills/tooluniverse-drug-drug-interaction-workspace -> ../../skills/tooluniverse-drug-drug-interaction-workspace`. [VERIFIED: `readlink` scan executed 2026-08-03]

## Project Constraints (from AGENTS.md)

- Use `tu status` for current runtime inventory; `TOOL_MANIFEST.json` is only a dated health snapshot. [VERIFIED: `AGENTS.md:3-7`; verbatim path/value: `TOOL_MANIFEST.json`]
- Preserve all five connection surfaces: embedded Python, MCP stdio, MCP HTTP, REST, and CLI. [VERIFIED: `AGENTS.md:9-17`; verbatim entry points: `ToolUniverse`, `tooluniverse`, `tooluniverse-mcp`, `tooluniverse-http-api`, `tu`]
- Always follow discover → inspect → execute; never guess parameter names. [VERIFIED: `AGENTS.md:19-31`; verbatim primitives: `grep_tools`, `find_tools`, `list_tools`, `get_tool_info`, `execute_tool`]
- Keep every transport routed through the same `ToolUniverse` core. [VERIFIED: `AGENTS.md:3-17`]
- In compact MCP mode, retain the four proxy tools plus `find_tools` when search is enabled; backend tools remain reachable through `execute_tool`. [VERIFIED: `AGENTS.md:47-54`; verbatim proxies: `list_tools`, `grep_tools`, `get_tool_info`, `execute_tool`, `find_tools`]
- Credentials remain environment based; missing keys gate tools rather than becoming committed data. [VERIFIED: `AGENTS.md:55-58`]
- No new dependencies, no package-manager change, no unrelated reformat/refactor, and use the existing `uv.lock`/uv workflow. [VERIFIED: `.planning/PROJECT.md` Constraints; `pyproject.toml` and `uv.lock` present]

## Standard Stack

### Core

| Tool | Verified version/contract | Purpose | Why standard here |
|------|---------------------------|---------|-------------------|
| Git | `2.55.0` | Revision identity, ancestry, worktrees, object IDs, and diff inventory | It is the authoritative repository model; porcelain/raw formats are machine-readable. [VERIFIED: `git --version`, 2026-08-03] [CITED: https://git-scm.com/docs/git-status] |
| CPython | local baseline `3.12.11`; declared floor `>=3.10` | Baseline orchestrator and package runtime | Python 3.12 is the locked local primary; the exact declaration is `requires-python = ">=3.10"`. [VERIFIED: `pyproject.toml:5-56`; quoted value: `>=3.10`] |
| uv | `0.12.0` | Locked environment and command execution | Repository has `uv.lock` and project policy forbids mixing managers. [VERIFIED: `uv --version`, `uv.lock`, and `.planning/PROJECT.md`]
| pytest | environment `8.4.2`; project minimum `>=7.0` | Baseline lanes, Nyquist tests, JUnit evidence | Existing framework and plugins already cover unit/integration/timeout/parallel behavior. [VERIFIED: `pytest --version` and `pyproject.toml:73-84`; quoted minimum: `pytest>=7.0`] |
| Python stdlib | bundled with CPython | `json`, `hashlib`, `subprocess`, `pathlib`, `os`, `time`, `datetime`, `platform` | Sufficient for deterministic evidence; adding an orchestration dependency would not improve correctness. [VERIFIED: Python standard library availability in local runtime] |

### Supporting

| Tool | Verified contract | Purpose | When to use |
|------|-------------------|---------|-------------|
| Ruff | environment `0.14.6`; project minimum `>=0.14.5` | Check new Python script/tests | Run only on touched paths with project config. [VERIFIED: `ruff --version`, `pyproject.toml:73-84,186-198`; quoted ignore values: `E203`, `E402`, `E501`, `F401`, `F541`] |
| MCP/FastMCP client APIs | `mcp>=1.29.0,<2.0.0`, `fastmcp>=3.4.5,<4.0.0` | Real stdio and streamable-HTTP probes | Use existing client APIs; raw POST is not a valid MCP HTTP test. [VERIFIED: `pyproject.toml:25-26`; `tests/integration/test_smcp_http_server.py:5-18`] |
| FastAPI `TestClient` / Uvicorn | existing dependencies | REST in-process test and process-level smoke probe | Use `TestClient` for fast contract tests and a loopback subprocess for a true surface probe. [VERIFIED: `tests/integration/test_http_api_server.py:9-19`; `pyproject.toml:17-19`] |
| GitHub Actions `setup-python` | existing workflow uses `actions/setup-python@v5` | Python compatibility matrix | Expand matrix values without adding a new action family. [VERIFIED: `.github/workflows/tests.yml:17-24`; quoted action: `actions/setup-python@v5`] [CITED: https://github.com/actions/setup-python/blob/main/docs/advanced-usage.md#matrix-testing] |

### Alternatives Considered

| Instead of | Could use | Tradeoff |
|------------|-----------|----------|
| Separate Git worktree | stash/current checkout | Stash mixes user-owned state into sync preparation and is easier to misapply; a worktree preserves isolation and reviewability. [CITED: https://git-scm.com/docs/git-worktree] |
| JSON evidence + JUnit XML | Markdown-only transcript | Markdown is useful for humans but weak for automated invariant checks, normalization, and checksum verification. [VERIFIED: pytest supports configured JUnit output via `--junitxml`; official reference cited below] |
| Existing MCP client | raw HTTP requests | Streamable HTTP has protocol/session semantics; current tests explicitly document that raw POSTs were invalid. [VERIFIED: `tests/integration/test_smcp_http_server.py:5-18`] |

**Installation:** none. This phase must add no external packages. [VERIFIED: locked project dependency constraint]

## Package Legitimacy Audit

Not applicable: the recommended implementation uses only Git, uv, installed project dependencies, and the Python standard library. No package installation is planned, so the legitimacy gate has no packages to evaluate. [VERIFIED: Standard Stack above]

## Architecture Patterns

### System Architecture Diagram

```text
operator / CI
    |
    v
preflight gate ---- dirty tracked state? ---- yes ---> stop; preserve/isolate first
    | no
    v
pin full fork/upstream/PR object IDs
    |
    +--> original checkout: inventory untracked paths; never modify them
    |
    v
isolated Git worktree at pinned fork SHA
    |
    +--> Git inventory --> commits, raw diff, modes, blobs, symlink targets
    |
    +--> local Python 3.12 baseline
    |       targeted -> broad offline -> catalog load
    |
    +--> public-surface probes
    |       Python -> CLI -> MCP stdio -> MCP HTTP -> REST
    |
    +--> configured provider manifest
            configured? -- no --> record not-selected
                 |
                yes
                 v
            attempt -> transient? -> fixed 2s retry (max 2 retries)
                 |                     |
              success              persistent failure
                 |                     |
                 +----------+----------+
                            v
normalize + validate invariants + redact
                            |
                            v
JSON/JUnit/log evidence + SHA-256 manifest
                            |
                any required failure? -- yes --> BLOCK
                            |
                           no
                            v
                 protected green baseline
```

The retry values in the diagram are the recommended discretionary choice: `3` total attempts, `2` retries, and a fixed `2.0` second delay, with a per-attempt timeout and an overall deadline. The existing health script's verbatim defaults are `RETRIES = ... "2"` and `RETRY_BACKOFF = ... "2.0"`, but its delay is linear (`2s`, then `4s`); the Phase 1 wrapper should keep the locked fixed interval instead. [VERIFIED: `scripts/tool_health_check.py:27-31,100-115`; quoted values: `2`, `2.0`]

### Recommended Project Structure

```text
scripts/
└── capture_sync_baseline.py             # orchestration only; caller supplies output dir
tests/
├── unit/test_sync_baseline_git.py        # temp-repo Git and symlink inventory
├── unit/test_sync_baseline_normalize.py  # redaction, ordering, invariants, retry policy
└── integration/test_sync_baseline_surfaces.py  # deterministic five-surface chain
.planning/phases/01-protected-sync-baseline/
└── evidence/
    └── <full-fork-sha>/
        ├── baseline.json                 # root manifest and all gate statuses
        ├── git.json                      # refs, merge-base, divergence, status
        ├── preservation.json             # tracked/custom/generated/symlink inventory
        ├── environment.json              # versions and credential-name booleans only
        ├── tests/                        # JUnit + concise command metadata/logs
        ├── probes/                       # one normalized JSON result per surface/tier
        └── SHA256SUMS                    # integrity manifest for evidence files
```

The directory name must be the full fork SHA, not a timestamp alone; timestamps belong inside JSON as informational metadata. Generate into a temporary directory first, validate and hash it, then copy the bounded evidence set into the phase directory so evidence creation does not contaminate the captured initial worktree state. [VERIFIED: BASE-01 auditability requirement and current dirty-state observations]

### Pattern 1: Two-snapshot Git model

Capture repository state twice: `initial_checkout` before creating any worktree/artifact and `isolated_baseline` inside the new worktree. Each snapshot records `HEAD`, branch/detached state, upstream remote URL, remote main OID, merge base, left/right counts, porcelain-v2 `-z` status, staged/unstaged raw diffs, and untracked paths. The invariant is: original user state is unchanged; isolated worktree has no staged/unstaged/untracked files before baseline execution. [CITED: https://git-scm.com/docs/git-status] [CITED: https://git-scm.com/docs/git-rev-list]

### Pattern 2: Object-based preservation inventory

Generate the fork delta from the selected upstream merge base with both `git diff --raw -z --find-renames <upstream>...<fork>` and `git diff --name-status -z --find-renames`. For every tracked delta path record status, old/new mode, old/new object ID, size, top-level preservation class, and whether it is generated. For mode `120000`, record the link blob text and separately resolve the target lexically without following it; if the target is a tracked directory/file, record its Git tree/blob object ID too. [CITED: https://git-scm.com/docs/git-diff] [VERIFIED: current tracked link mode quote: `120000`]

Use explicit preservation classes: `custom_code`, `tool_definition`, `plugin_asset`, `skill`, `test`, `workflow`, `documentation`, `generated_asset`, `planning`, and `other_review_required`. Classification rules must be path-prefix data in one function and every `other_review_required` entry must block sign-off until classified. [ASSUMED]

### Pattern 3: One probe contract across transports

Each surface emits the same logical stages:

1. `discover`: selected tool appears in `list_tools` or `grep_tools`.
2. `inspect`: exact schema includes expected required parameters.
3. `execute`: the exact inspected arguments are used.
4. `assert`: normalized envelope and domain invariants pass.

The deterministic credential-free reference tool should be `DegreesOfUnsaturation_calculate` with arguments `{"operation":"calculate","formula":"C6H6"}`. Its source definition quotes the allowed operation `"calculate"`, requires `"operation"`, and examples include formula `"C6H6"`; the expected invariant is numeric `degrees_of_unsaturation == 4.0` and `is_integer is true`. [VERIFIED: `src/tooluniverse/data/degrees_of_unsaturation_tools.json`; inspected with `tu info` and executed through Python/CLI on 2026-08-03]

### Pattern 4: Secret-safe configured-provider manifest

Build the configured-key set only inside the baseline process: gather required/optional credential names from loaded tool definitions and the credential registry, evaluate each with `bool(os.environ.get(name))`, and emit only the variable name, boolean configured flag, provider/tool mapping, selected test node, and probe outcome. Never emit values, lengths, prefixes, hashes, request headers, full URLs with query strings, or environment dumps. [VERIFIED: `src/tooluniverse/config_env.py:227-252`; `src/tooluniverse/execute_function.py:758-797`]

The existing `.tooluniverse/.env.1password` file is present and mode `-rw-r--r--`; Phase 1 must not read or copy it into evidence. If credentials must be resolved for live tests, use the established loader in-process and redact before subprocess/log persistence. [VERIFIED: filesystem `stat` and `.tooluniverse/env.py:27-31,111-125`]

### Pattern 5: Normalized evidence with semantic invariants

Normalization is allowlist-based, not a recursive delete-everything heuristic. Preserve all keys by default; replace only declared volatile paths such as timestamps, request IDs, trace IDs, generated task IDs, and explicitly unordered remote collections. Sort maps by key. Sort arrays only when the tool contract declares them unordered, using a documented stable identity key; otherwise retain and test ordering. Keep raw sanitized output beside normalized output when it contains no secrets. [VERIFIED: D-07 quoted in User Constraints]

Every probe must enforce: result is JSON-serializable; status is a recognized structured success/error; required schema keys and types match; deterministic local domain values match; live results meet provider-specific non-emptiness/identity invariants; and an error is accepted only when the probe explicitly targets structured-error behavior. [VERIFIED: `src/tooluniverse/base_tool.py` structured-error convention summarized in `.planning/codebase/CONVENTIONS.md:52-59`]

### Anti-Patterns to Avoid

- **Parsing human Git output:** colors/localization/spacing are unstable. Use `--porcelain=v2 -z`, `--raw -z`, and full OIDs. [CITED: https://git-scm.com/docs/git-status]
- **Calling `git diff upstream/main HEAD` without ancestry evidence:** it obscures whether the reference is an ancestor and how the range was selected. Record merge base and symmetric counts first. [CITED: https://git-scm.com/docs/git-merge-base]
- **Using `find -L`, `cp -L`, or recursive writes under `plugin/skills`:** these follow symlinks and can duplicate or mutate targets. Inventory link text and target metadata separately. [VERIFIED: 120 tracked symlinks found in current repository]
- **Treating a deleted path beneath a replaced symlink as content loss:** the current fork delta includes directory-to-symlink transitions; inspect mode and target tree before classifying. [VERIFIED: `git diff --summary upstream/main...HEAD` reports 120 `create mode 120000` entries]
- **Letting default pytest selection stand for comprehensive coverage:** current addopts ignores `tests/tools`, `tests/examples`, and `tests/api`. [VERIFIED: `pytest.ini:1-10`; quoted ignored paths: `tests/tools`, `tests/examples`, `tests/api`]
- **Accepting skips or existing failures as green:** D-02 requires zero unexplained required failures; each skip must be expected by a recorded capability rule. [VERIFIED: D-02 quoted above]
- **Using mocked/direct MCP tests as transport certification:** current streamable-HTTP coverage is explicitly absent, and several MCP tests call Python methods directly. Add real client/server transport probes. [VERIFIED: `tests/integration/test_smcp_http_server.py:5-18`; `tests/integration/test_mcp_protocol.py:66-165`]
- **Dumping environment or credential files:** emit names/booleans only. [VERIFIED: locked secrets constraint in `.planning/PROJECT.md`]
- **Retrying validation, authentication, 4xx-not-429, schema, or domain-invariant failures:** only timeout/connection/408/429/500/502/503/504-style transient failures are retryable. [VERIFIED: existing transient set in `scripts/tool_health_check.py:34-55`; quoted codes: `429`, `500`, `502`, `503`, `504`]

## Don't Hand-Roll

| Problem | Don't build | Use instead | Why |
|---------|-------------|-------------|-----|
| Repository identity | Filename/date-based snapshot logic | Git full OIDs, merge-base, rev-list, diff raw | Git already defines ancestry, modes, renames, and object identity. [CITED: https://git-scm.com/docs/git-rev-parse] |
| Dirty-state parser | Parser for human `git status` | `git status --porcelain=v2 -z` | Stable machine format and NUL-safe paths. [CITED: https://git-scm.com/docs/git-status] |
| Symlink copier | Recursive copy/follow logic | `git ls-files -s`, `git cat-file`, `os.lstat`, `os.readlink` | Preserves link identity and avoids crossing roots. [VERIFIED: current repository contains tracked links]
| Test runner/report format | Custom pass/fail subprocess protocol | pytest plus JUnit XML and per-command metadata | Existing markers, timeout plugin, and CI integrate directly. [CITED: https://docs.pytest.org/en/stable/reference/reference.html]
| JSON Schema validator | Ad hoc type checks for every tool | existing `jsonschema` dependency and tool `return_schema` | Schema semantics are already declared and installed. [VERIFIED: `pyproject.toml:50-55`; quoted dependency: `jsonschema>=4.23.0`]
| MCP HTTP transport | Raw JSON POST approximation | installed MCP/FastMCP client | Streamable HTTP is a protocol session, not a generic REST endpoint. [VERIFIED: `tests/integration/test_smcp_http_server.py:5-18`]
| Secret redactor after logging | Regex scrub of arbitrary logs | do not serialize values at source; capture only names/booleans | Prevention is safer than attempting to find every secret representation. [VERIFIED: project secrets constraint]

**Key insight:** This phase should compose authoritative primitives and preserve their raw machine evidence; custom code is justified only for orchestration, classification, normalization, and invariant enforcement. [VERIFIED: stack and architecture evidence above]

## Git and Preservation Inventory Specification

### Required Git evidence

`git.json` should contain these fields and commands, recording argv as an array rather than a shell string. [ASSUMED]

| Field | Authoritative command/invariant |
|-------|---------------------------------|
| `fork_oid` | `git rev-parse --verify HEAD^{commit}` [CITED: https://git-scm.com/docs/git-rev-parse] |
| `upstream_remote` | `git remote get-url upstream`; require canonical `https://github.com/mims-harvard/ToolUniverse.git` for this milestone. [VERIFIED: `git remote -v`, 2026-08-03] |
| `upstream_remote_oid` | `git ls-remote --exit-code upstream refs/heads/main`; pin returned OID. [CITED: https://git-scm.com/docs/git-ls-remote] |
| `upstream_local_oid` | `git rev-parse --verify refs/remotes/upstream/main^{commit}`; require equality with remote OID after an explicit fetch stage or record stale mismatch and block. [ASSUMED] |
| `merge_base` | `git merge-base <fork_oid> <upstream_oid>` [CITED: https://git-scm.com/docs/git-merge-base] |
| `divergence` | `git rev-list --left-right --count <fork_oid>...<upstream_oid>` [CITED: https://git-scm.com/docs/git-rev-list] |
| `worktree_status` | `git status --porcelain=v2 -z --branch --untracked-files=all` [CITED: https://git-scm.com/docs/git-status] |
| `fork_commits` | `git log --format=... <upstream_oid>..<fork_oid>` with full hashes [CITED: https://git-scm.com/docs/git-log] |
| `content_delta` | both `git diff --raw -z --find-renames` and `git diff --name-status -z --find-renames` over `<upstream_oid>...<fork_oid>` [CITED: https://git-scm.com/docs/git-diff] |
| `pr161` | GitHub PR metadata plus `git merge-base --is-ancestor <merge_commit> <upstream_oid>`; never infer inclusion from similar filenames. [VERIFIED: current PR/API ancestry checks]

### Preservation record per path

Each tracked delta record should include: path bytes represented safely, change status, old/new modes, old/new blob/tree OIDs, tracked size, preservation class, generated/authored classification, owning subsystem, and `must_survive` rationale. Renames retain both paths. Deletions require a disposition rather than silently disappearing. [ASSUMED]

Each symlink record should additionally include: link path, mode `120000`, link blob OID, exact link text, absolute/relative flag, normalized lexical target, target-inside-repo boolean, target existence, target trackedness, and target blob/tree OID when tracked. Never recursively hash through the link; hash the tracked target path separately. [VERIFIED: mode value `120000` from current Git index] [ASSUMED: proposed record schema]

Each untracked record should include path, type, mode, byte size, modification time, and SHA-256 only when approved for hashing; do not include contents. The current four `ralph-specs/fleet/results/*.json` files remain in the original checkout and must not be copied into the integration worktree. [VERIFIED: current untracked inventory and CONTEXT.md:73-76]

Generated assets must not be dismissed as disposable. Inventory current generated items (`TOOL_MANIFEST.json`, tool graph JSON/pickle files, `src/tooluniverse/_lazy_registry_static.py`, generated public modules under `src/tooluniverse/tools/`, embeddings under `data/embeddings/`, documentation indexes, and `uv.lock`) with generator command/source when known and current OID. Phase 1 protects their pre-sync state; later phases may regenerate them deliberately. [VERIFIED: `.planning/PROJECT.md` registration/embeddings constraints and `.planning/codebase/CONCERNS.md:13-17`]

## Baseline Test and Probe Matrix

### Fast fail ordering

1. Preflight, exact Git facts, clean isolated worktree, symlink integrity.
2. Baseline-script unit tests and targeted registry/discovery/error tests.
3. Catalog load and deterministic Python/CLI probes.
4. Real MCP stdio, MCP HTTP, and REST probes.
5. Broad offline core suite.
6. Explicit offline tools/examples/API suite excluded by default.
7. Configured live-provider probes with bounded retry.
8. Python compatibility CI matrix.

This order minimizes wasted live calls while preserving all required coverage. [VERIFIED: D-01 and discretion quoted above]

### Pytest lanes

Use `-o addopts=''` in baseline commands, then restate every required option explicitly. This prevents hidden global selection from being mistaken for comprehensive execution. The repository marker names are quoted verbatim as `unit`, `integration`, `fast`, `network`, `slow`, `require_api_keys`, `require_gpu`, `mcp`, and `stdio`. [VERIFIED: `pytest.ini:1-36`]

| Lane | Required command shape | Evidence/invariant |
|------|------------------------|--------------------|
| Targeted high risk | `uv run pytest -o addopts='' <selected nodes> -q --strict-markers --strict-config --timeout=60 --junitxml=<out>` | Zero failures; no unexpected skips; covers registry, gated discovery, CLI, HTTP, MCP, stdio, normalization. [VERIFIED: relevant files collected successfully 2026-08-03] |
| Broad offline core | `uv run pytest -o addopts='' tests/unit tests/integration tests/test_database_setup -m 'not slow and not require_api_keys and not network and not require_gpu' ...` | Fully green under Python 3.12 locally. [VERIFIED: current exclusions/markers in `pytest.ini`] |
| Explicit excluded suites | `uv run pytest -o addopts='' tests/tools tests/examples tests/api -m 'not slow and not require_api_keys and not network and not require_gpu' ...` | Fully green; paths are explicit because defaults ignore them. [VERIFIED: `pytest.ini:3-9`] |
| Configured live | generated exact node list, one or more probes per configured provider family, with network/API-key markers as applicable | After bounded retries: all selected configured-provider checks pass; sanitized diagnostics retained on failure. [VERIFIED: D-03]
| Compatibility | GitHub Actions matrix `['3.10','3.11','3.12','3.13','3.14']`; Python 3.12 remains primary/full lane | Installation plus targeted/offline tests pass on each current stable interpreter at or above the declared floor. [VERIFIED: declared `>=3.10`; current CI only `['3.12']` at `.github/workflows/tests.yml:13-16`] [CITED: https://github.com/actions/setup-python/blob/main/docs/advanced-usage.md#matrix-testing] |

The local collection audit found existing relevant nodes, including `4` registry-integrity tests, `9` gated-discovery tests, `10` REST tests, `14` MCP-protocol tests, `2` direct SMCP tests, `7` stdio tests, `359` CLI tests, and `26` scientific-calculator tests. Collection proves availability, not pass status. [VERIFIED: `pytest --collect-only` executed 2026-08-03]

### Tiered probe selection

| Tier | Recommended representative | Invariants |
|------|----------------------------|------------|
| Credential-free deterministic local | `DegreesOfUnsaturation_calculate`, formula `C6H6` | discovered; schema requires `operation`; success envelope; DoU `4.0`; boolean `is_integer=true`. [VERIFIED: tool definition and executions, 2026-08-03] |
| Fork-specific | `DegreesOfUnsaturation_calculate` plus one custom registration/skill route sampled from the preservation manifest | path classified `must_survive`; tool loads through runtime registry; exact schema and deterministic result preserved. [VERIFIED: historical plan identifies this tool among fork/upstream conflict inventory at `docs/superpowers/plans/2026-04-17-upstream-sync.md:36-52`] |
| Configured scientific provider | `SemanticScholar_search_papers` and `USPTO_patent_number_to_application`, plus generated selections covering every configured provider family | required/optional credential name is configured; schema inspected first; result is nonempty/well-shaped or a structured non-retryable error blocks. [VERIFIED: both schemas inspected with `tu info`; configured names listed above] |
| Catalog-driven category sample | deterministic seed derived from fork SHA; at least one eligible tool from each recorded major category family | selected names recorded; discovery/info succeeds; execute only tools with safe deterministic examples; no gated tool is silently omitted. [ASSUMED] |

Sampling must be deterministic. Sort eligible names and choose by `sha256(fork_oid + category + tool_name)`, taking the lowest score; record seed, candidate count, and selected name. This avoids nondeterministic random samples while preventing a handpicked-only baseline. [ASSUMED]

### Surface contracts

| Surface | Discover | Inspect | Execute | Current gap |
|---------|----------|---------|---------|-------------|
| Python | invoke discovery tool/core API | `tool_specification(name)` | `run_one_function({...})` | Existing architecture supports all stages; add one normalized baseline probe. [VERIFIED: `docs/dev_docs/Interaction_Surfaces.md:56-111`] |
| CLI | `tu grep` or `tu list` | `tu info NAME --json` | `tu run NAME ... --json` | Existing CLI tests are extensive, but baseline must record one complete chained transcript. [VERIFIED: `docs/dev_docs/Interaction_Surfaces.md:194-215`] |
| MCP stdio | MCP `tools/list`, then `grep_tools` call | `get_tool_info` call | `execute_tool` call | Existing stdio tests handshake/list and call `get_server_info`; they do not prove the locked chain. [VERIFIED: `tests/integration/test_stdio_mode.py:86-237`] |
| MCP HTTP | proper MCP client session and proxy call | `get_tool_info` | `execute_tool` | Current file explicitly says transport coverage is absent. [VERIFIED: `tests/integration/test_smcp_http_server.py:5-18`] |
| REST | `/api/call` discovery method | `/api/call` `tool_specification` | `/api/call` `run_one_function` | Existing tests cover methods and loading but not deterministic end-to-end execution. [VERIFIED: `tests/integration/test_http_api_server.py:22-177`] |

Each process-level probe must allocate a free loopback port, impose startup/operation/teardown deadlines, capture stdout and stderr separately, and terminate the child in `finally`. Never bind MCP/REST baseline servers to `0.0.0.0`. [VERIFIED: repository security concern on network binding in `.planning/codebase/CONCERNS.md:51-75`] [ASSUMED: probe harness details]

## Bounded Retry and Diagnostic Design

- Total attempts: `3`; retries after first attempt: `2`; fixed delay: `2.0s`; per-attempt timeout: provider-specific but explicitly recorded; overall deadline: `attempts * timeout + 4s + startup allowance`. [ASSUMED]
- Retry only explicit transient categories: timeout, connection failure, HTTP `408`, `429`, `500`, `502`, `503`, `504`, or a structured `retryable=true` provider response. [VERIFIED: existing health markers and tool patterns; exact existing codes quoted in Anti-Patterns]
- Do not retry missing credential, authentication/authorization, validation, schema mismatch, tool-not-found, unsupported operation, or violated domain invariant. [VERIFIED: existing structured error categories in `.planning/codebase/CONVENTIONS.md:52-59`]
- Record every attempt with monotonic duration, classified error type/status, retry decision, and sanitized diagnostic. Record no response headers except allowlisted status/rate-limit metadata, and cap any recorded `Retry-After`. [VERIFIED: `tests/unit/test_http_retry_after_cap.py:1-55` demonstrates the need to cap server delays]
- A recovery after retry is a pass with `recovered_after_attempt`; a persistent configured-provider failure is a hard phase blocker. [VERIFIED: D-03]

## Common Pitfalls

### Pitfall 1: Moving upstream during the milestone
**What goes wrong:** evidence and later merge refer to different upstream commits.  
**Why it happens:** planners use `upstream/main` as a name instead of storing the OID.  
**How to avoid:** pin the full remote OID once and pass it through every artifact and plan.  
**Warning sign:** rerunning the baseline changes divergence without a recorded target change. [VERIFIED: BASE-01]

### Pitfall 2: Confusing fork delta with dirty worktree
**What goes wrong:** committed fork customizations and uncommitted user changes are mixed into one preservation list.  
**Why it happens:** `git diff` and `git status` answer different questions.  
**How to avoid:** record committed upstream-to-fork delta, staged delta, unstaged delta, and untracked paths as separate collections.  
**Warning sign:** an inventory item has no provenance class. [CITED: https://git-scm.com/docs/git-diff] [CITED: https://git-scm.com/docs/git-status]

### Pitfall 3: Silent suite exclusion
**What goes wrong:** a green `pytest` omits most tool/API/example coverage.  
**Why it happens:** repository addopts ignore three directories and exclude network/key/slow markers.  
**How to avoid:** clear addopts and specify each lane explicitly.  
**Warning sign:** no JUnit report names a tool/API/example test. [VERIFIED: `pytest.ini:1-10`]

### Pitfall 4: Mocked surface mistaken for transport evidence
**What goes wrong:** direct Python calls pass while stdio/HTTP framing, startup, serialization, or proxy registration is broken.  
**Why it happens:** existing tests use direct server methods and mocks for speed.  
**How to avoid:** retain unit tests but add one real process/client chain per transport.  
**Warning sign:** no child process, MCP client session, or REST HTTP request appears in probe metadata. [VERIFIED: current MCP test sources cited above]

### Pitfall 5: Symlink traversal or false deletion
**What goes wrong:** backup/generation follows a plugin link into its source, or a directory-to-link change looks like mass content deletion.  
**Why it happens:** ordinary recursive filesystem tools dereference or flatten links.  
**How to avoid:** inventory Git mode/link blob first, target second; reject out-of-root/broken targets.  
**Warning sign:** source and plugin copies have independent hashes instead of one source plus link metadata. [VERIFIED: 120 tracked links and three broken targets]

### Pitfall 6: Secret-bearing evidence
**What goes wrong:** environment dumps, subprocess commands, headers, or errors leak keys.  
**Why it happens:** capture is added after the provider client formats diagnostics.  
**How to avoid:** pass credentials only via process environment and serialize names/booleans; sanitize stderr before persistence.  
**Warning sign:** evidence contains `=`, bearer headers, `op://`, or credential-file contents in provider metadata. [VERIFIED: credential loading files and project constraints]

### Pitfall 7: Over-normalization
**What goes wrong:** a breaking missing field/order/schema change is deleted as “volatile.”  
**Why it happens:** generic recursive stripping replaces contract-aware comparison.  
**How to avoid:** allowlist exact volatile JSON paths and pair normalization with invariant/schema validation.  
**Warning sign:** normalized output has fewer structural fields than raw output without a rule entry. [VERIFIED: D-07]

### Pitfall 8: Treating collection as execution
**What goes wrong:** planner cites test counts as a green baseline.  
**Why it happens:** `--collect-only` was used during research.  
**How to avoid:** Phase execution must produce actual JUnit reports and zero required failures.  
**Warning sign:** evidence command contains `--collect-only`. [VERIFIED: this research ran collection only, not the baseline]

## Code Examples

These are implementation patterns, not commands already executed as a complete baseline.

### Safe Git command execution

```python
# Source: https://git-scm.com/docs/git-status
result = subprocess.run(
    ["git", "status", "--porcelain=v2", "-z", "--branch", "--untracked-files=all"],
    cwd=repo,
    check=True,
    capture_output=True,
)
```

The exact status flags above are the recommended machine interface; output must be parsed as NUL-delimited bytes so unusual filenames remain representable. [CITED: https://git-scm.com/docs/git-status]

### Secret-safe configured-name capture

```python
# Source: src/tooluniverse/config_env.py:234-252
configured = {
    name: bool(os.environ.get(name))
    for name in sorted(ToolUniverseConfig.CREDENTIAL_SPECS)
}
```

The source definition uses verbatim fields `env_var` and `is_set`, and computes configuration with `env_var in os.environ and bool(os.environ[env_var])`; emit only the equivalent boolean result. [VERIFIED: `src/tooluniverse/config_env.py:15-25,234-252`; quoted values: `env_var`, `is_set`]

### Deterministic reference probe

```python
# Source: src/tooluniverse/data/degrees_of_unsaturation_tools.json
name = "DegreesOfUnsaturation_calculate"
arguments = {"operation": "calculate", "formula": "C6H6"}
spec = tu.tool_specification(name)
result = tu.run_one_function({"name": name, "arguments": arguments})
assert result["status"] == "success"
assert result["data"]["degrees_of_unsaturation"] == 4.0
assert result["data"]["is_integer"] is True
```

The source and live execution verified verbatim values `DegreesOfUnsaturation_calculate`, `calculate`, `C6H6`, `status`, `success`, `data`, `degrees_of_unsaturation`, `4.0`, `is_integer`, and `true`. [VERIFIED: tool JSON definition plus Python/CLI executions, 2026-08-03]

### Fixed bounded retry

```python
for attempt in range(1, 4):
    outcome = run_once(timeout=attempt_timeout)
    if outcome.ok or not outcome.transient or attempt == 3:
        break
    time.sleep(2.0)
```

Values `3` attempts and `2.0` seconds are a discretionary recommendation aligned with the existing health script's quoted retry count/backoff defaults, while satisfying the locked fixed-backoff requirement. [VERIFIED: `scripts/tool_health_check.py:27-31`] [ASSUMED: fixed-interval adaptation]

## State of the Art

| Dated approach | Current evidence-based approach | Impact |
|----------------|---------------------------------|--------|
| April plan: upstream was `2` commits ahead and PR #161 was an unmerged `11`-commit stage | Pin live upstream `56adcfd9...`; divergence is now `97 0`; PR #161 merge commit is already contained | Phase 1 must record current provenance; later planning must not replay the historical merges. [VERIFIED: historical values at `docs/superpowers/specs/2026-04-17-upstream-sync-design.md:9-17`; current Git/API checks]
| “Run pytest” and accept pre-existing failures/skips | Fully green targeted + broad offline + explicitly excluded suites + configured live lanes | Meets locked D-01 through D-04 and closes silent selection gaps. [VERIFIED: CONTEXT decisions and `pytest.ini`]
| Tool count from `TOOL_MANIFEST.json` | Runtime `tu status` and loaded catalog | Avoids stale snapshot-driven conclusions. [VERIFIED: `AGENTS.md:3-7`]
| Direct/mock MCP testing | One real discovery→inspect→execute chain over stdio and streamable HTTP | Tests transport framing and proxy exposure, not only Python behavior. [VERIFIED: existing coverage gap]
| Random health sample | SHA-derived deterministic category sample | Makes the selected catalog sample reproducible from the pinned commit. [ASSUMED]

**Deprecated/outdated:** The branch names, revision counts, and separate PR #161 merge instructions in the 2026-04-17 plan are historical evidence only. Its core preservation rule—canonical upstream definitions for shared tools, manual combination for structural files—remains relevant to later phases, but not as a description of current topology. [VERIFIED: historical plan and current Git/API checks]

## Environment Availability

| Dependency | Required by | Available | Version/state | Fallback |
|------------|-------------|-----------|---------------|----------|
| Git | BASE-01/PRES-01 | ✓ | `2.55.0` | none [VERIFIED: local command]
| uv | all test/probe lanes | ✓ | `0.12.0` | none; package-manager mixing forbidden [VERIFIED: local command]
| Python 3.12 | local comprehensive baseline | ✓ | `3.12.11` | none [VERIFIED: local command]
| Python 3.10/3.11/3.13/3.14 | CI compatibility | CI-provisioned | not all locally probed | GitHub Actions matrix [VERIFIED: current local runtimes and CI config]
| pytest | tests/JUnit | ✓ | `8.4.2` | none [VERIFIED: local command]
| MCP/FastMCP | MCP probes | ✓ via project env | declared ranges in Standard Stack | none [VERIFIED: `pyproject.toml`]
| GitHub API/remote | upstream/PR provenance | ✓ during research | canonical repo reachable | `git ls-remote` for main; record PR metadata failure as blocker if PR evidence cannot be refreshed [VERIFIED: live calls]
| Configured providers | D-03 live checks | mixed/external | 12 known configured names in current process | no fallback; persistent failure blocks [VERIFIED: safe name-only audit]

**Missing dependencies with no fallback:** none for local Phase 1 implementation. CI must provision every supported Python version, and configured providers must be reachable when the live lane runs. [VERIFIED: availability audit]

**Missing dependencies with fallback:** optional visualization/graph/bioinformatics/smolagents extras are missing according to `tu status`, but the baseline matrix should select tools that do not require them unless an affected custom asset explicitly depends on one; any such dependency becomes an explicit lane prerequisite. [VERIFIED: `tu status --json`, 2026-08-03]

## Validation Architecture

Nyquist validation is enabled because `.planning/config.json` does not set `workflow.nyquist_validation` to `false`. [VERIFIED: `.planning/config.json`, read 2026-08-03]

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest `8.4.2` locally; project minimum `7.0` [VERIFIED: local command and `pytest.ini:1-3`] |
| Config file | `pytest.ini`; database override `tests/test_database_setup/pytest.ini` [VERIFIED: repository files]
| Quick run | `uv run pytest -o addopts='' tests/unit/test_sync_baseline_git.py tests/unit/test_sync_baseline_normalize.py -q --strict-markers --timeout=60` [ASSUMED: Wave 0 files]
| Full phase run | baseline orchestrator running all required lanes and emitting JUnit/probe evidence [ASSUMED]

### Phase Requirements → Test Map

| Req ID | Behavior | Test type | Automated command | File exists? |
|--------|----------|-----------|-------------------|--------------|
| BASE-01 | exact revisions, divergence, dirty-state separation, isolated clean worktree | unit/integration with temporary Git repository | `uv run pytest -o addopts='' tests/unit/test_sync_baseline_git.py -q --strict-markers --timeout=60` | ❌ Wave 0 [ASSUMED] |
| BASE-02 | reproducible test/catalog/probe evidence and hard green gate | integration + subprocess | `uv run pytest -o addopts='' tests/integration/test_sync_baseline_surfaces.py -q --strict-markers --timeout=60` | ❌ Wave 0 [ASSUMED] |
| PRES-01 | complete classified delta, generated assets, link text/target identity, untracked isolation | unit with temp trees/symlinks | `uv run pytest -o addopts='' tests/unit/test_sync_baseline_git.py -q -k preservation --strict-markers --timeout=60` | ❌ Wave 0 [ASSUMED] |

### Sampling Rate

- **Per task commit:** new baseline unit tests plus the smallest affected existing test file. [ASSUMED]
- **Per wave merge:** targeted high-risk lane with JUnit. [ASSUMED]
- **Phase gate:** full local Python 3.12 baseline green, configured live providers green after bounded retry, evidence checksum validation green, and CI Python matrix green. [VERIFIED: D-01 through D-04]

### Wave 0 Gaps

- [ ] `tests/unit/test_sync_baseline_git.py` — temporary-repo tests for OIDs, divergence, staged/unstaged/untracked separation, rename/mode records, in-root/out-of-root/broken symlinks, and no link traversal. [ASSUMED]
- [ ] `tests/unit/test_sync_baseline_normalize.py` — volatile-path allowlist, stable/unordered collection handling, structured success/error invariants, redaction, deterministic sampling, retry classification, and attempt bounds. [ASSUMED]
- [ ] `tests/integration/test_sync_baseline_surfaces.py` — real Python/CLI/MCP stdio/MCP HTTP/REST discovery→inspect→execute chain using the deterministic local tool. [ASSUMED]
- [ ] Configured-provider manifest test — every configured provider maps to at least one selected node/probe; missing mapping fails before network execution. [ASSUMED]
- [ ] CI matrix expansion and job-shape test — current `.github/workflows/tests.yml` contains only Python `3.12`. [VERIFIED: `.github/workflows/tests.yml:13-16`; quoted value: `['3.12']`]
- [ ] Broken-symlink gate — three current tracked broken links must be repaired or explicitly resolved before Phase 1 can pass. [VERIFIED: link scan]

## Security Domain

Security enforcement is enabled because `.planning/config.json` does not explicitly disable it. [VERIFIED: `.planning/config.json`, read 2026-08-03]

### Applicable ASVS Categories

| ASVS category | Applies | Standard control |
|---------------|---------|------------------|
| V2 Authentication | no for local baseline; indirectly for providers | Do not test credential values; adapters/providers own auth. [VERIFIED: phase scope]
| V3 Session Management | yes for MCP transport lifecycle | Use installed MCP client session and bounded teardown; no hand-built session tokens. [VERIFIED: MCP dependencies]
| V4 Access Control | yes for CI/repository boundaries | Never push upstream; use origin/feature branch and loopback-only servers. [VERIFIED: `claude/rules/upstream-sync.md:26-31`]
| V5 Validation/Sanitization/Encoding | yes | argv arrays, NUL-delimited Git formats, JSON parsing/schema validation, allowlisted normalization/redaction. [VERIFIED: project stack]
| V6 Cryptography | yes for artifact integrity, not authenticity | Python `hashlib.sha256`; record that checksums detect accidental change but are not signatures. [VERIFIED: stdlib availability]
| V8 Data Protection | yes | no secret values/files in evidence; sanitize provider diagnostics. [VERIFIED: project secrets constraint]
| V12 File and Resource | yes | caller-supplied bounded output root, `lstat`/`readlink`, reject traversal/out-of-root paths, no symlink following. [VERIFIED: current symlink risk]
| V14 Configuration | yes | pin tool/runtime versions, refs, commands, and CI matrix in evidence. [VERIFIED: BASE-01/02]

### Known Threat Patterns

| Pattern | STRIDE | Mitigation |
|---------|--------|------------|
| Malicious branch/path/tool/provider text injected into shell | Tampering/Elevation | never `shell=True`; argv arrays; NUL-safe parsing; treat all external text as data. [CITED: https://git-scm.com/docs/git-status]
| Symlink escapes repository or targets missing path | Tampering/Information disclosure | lexical containment check, `lstat`, no traversal, hard failure for out-of-root/broken protected targets. [VERIFIED: three current broken links]
| Credential leakage in JSON/JUnit/stderr | Information disclosure | names/booleans only; value-free environment projection; sanitized diagnostics; evidence scan before commit. [VERIFIED: credential constraints]
| Provider hangs or attacker-controlled `Retry-After` | Denial of service | per-attempt and global deadlines, maximum attempts, fixed delay, capped header metadata. [VERIFIED: `tests/unit/test_http_retry_after_cap.py:1-55`]
| Evidence modified after capture | Tampering | SHA-256 manifest generated after all files; verify before phase gate and later comparison. [ASSUMED]
| Moving remote ref changes target silently | Tampering/Repudiation | full OID pin, remote/local equality check, record timestamp/URL and command. [VERIFIED: BASE-01]

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|-------|---------|---------------|
| A1 | The proposed preservation class names are sufficient and should block on `other_review_required`. | Architecture / inventory | An asset class could be omitted or mislabeled; planner should validate against actual delta. |
| A2 | Full-fork-SHA evidence directory under the phase is the preferred committed layout. | Project structure | Maintainers may prefer an external artifact store; exact path is discretionary. |
| A3 | SHA-derived lowest-score sampling is the desired deterministic category policy. | Probe matrix | Another deterministic sampler may offer better category balance. |
| A4 | Three attempts with fixed 2-second delays fit every selected live provider. | Retry design | Some provider contracts may require a different explicit timeout/backoff; lock per-provider exceptions in manifest. |
| A5 | Python 3.10 through 3.14 represent the current stable declared range for CI. | Test matrix | A newly stable interpreter could appear before implementation; planner should query current setup-python availability and append it. |
| A6 | The three broken tracked links should block preservation sign-off. | Git inventory / Wave 0 | Maintainers may explicitly classify them as intentionally dangling, but silent acceptance is unsafe. |

## Open Questions (RESOLVED)

1. **Resolved — repair the three broken tracked plugin workspace links only from authoritative PR #161 evidence.**
   - The three current entries remain verified tracked mode-`120000` links whose `-workspace` targets do not exist. [VERIFIED: Git/filesystem scan]
   - Read-only history establishes that each link was introduced in or represented by PR #161 ancestry. The authoritative PR #161 merge commit `16af425c053c306a658c96e254b4c4114338dd11` tracks populated sibling directories without the `-workspace` suffix: `skills/tooluniverse-computational-biophysics`, `skills/tooluniverse-organic-chemistry`, and `skills/tooluniverse-drug-drug-interaction`. [VERIFIED: `git merge-base --is-ancestor`, `git ls-tree`, and GitHub PR #161 metadata] [CITED: https://github.com/mims-harvard/ToolUniverse/pull/161]
   - Resolution: before mutation, prove the merge-commit ancestry, authoritative tree entries, populated tracked targets, and existing sibling plugin convention `../../skills/<directory>`. Then change only the three link blobs to `../../skills/tooluniverse-computational-biophysics`, `../../skills/tooluniverse-organic-chemistry`, and `../../skills/tooluniverse-drug-drug-interaction`. Never create or infer target content. If any proof fails, leave all links unchanged and halt at an explicit disposition checkpoint. [VERIFIED: authoritative tree/path evidence described above]

2. **Resolved — refresh upstream exactly once at Phase 1 execution start, then freeze it.**
   - The research-time canonical main OID `56adcfd9c299078d0c40fde642b0be006510ccf3` remains dated evidence from 2026-08-03, not a timeless target. [VERIFIED: live Git/GitHub checks performed 2026-08-03]
   - Resolution: at Phase 1 execution start, perform one explicit remote refresh, require the fetched local upstream ref to equal the remote full OID, and record URL, timestamp, and full OID in `git.json`. Reuse that immutable OID throughout Phase 1 and every later synchronization phase. Any later upstream movement is reported as drift and cannot silently retarget the milestone. [CITED: https://git-scm.com/docs/git-ls-remote] [CITED: https://git-scm.com/docs/git-rev-parse]

3. **Resolved — require a checked provider manifest before any live call.**
   - Twelve credential names were configured in the research process, and current marker/test coverage is heterogeneous. [VERIFIED: safe name-only environment audit and test scan]
   - Resolution: generate and validate a value-free `credential family → credential variable names → selected tool → exact test/probe node → invariant` manifest. Every currently configured family must have at least one bounded selected probe; a missing or ambiguous mapping blocks before network execution. Unconfigured families remain recorded as unconfigured and do not become failures. Selected configured-provider probes retain D-03's three total attempts, fixed two-second backoff, finite deadlines, and persistent-failure block. [VERIFIED: D-03 and `ToolUniverseConfig.CREDENTIAL_SPECS`]

4. **Resolved — commit normalized summaries and only bounded sanitized excerpts needed for diagnosis.**
   - Reproducibility requires outcome/invariant diagnostics, while remote payloads can be volatile, large, proprietary, or sensitive. [VERIFIED: D-03/D-07]
   - Resolution: commit normalized summaries, schemas/invariant verdicts, timings, retry classifications, and bounded sanitized excerpts only when needed to diagnose a failure. Never commit full provider payloads, credential values, headers, query-string secrets, environment dumps, or user-owned untracked contents. Apply explicit size bounds and pre-publication secret scanning to JSON, JUnit, stdout, stderr, and probe artifacts. [VERIFIED: project secrets constraint and D-07]

## Sources

### Primary (HIGH confidence)

- Repository source-of-truth files opened this session: `AGENTS.md`, phase context/requirements/project/roadmap/state, `pyproject.toml`, `pytest.ini`, `tests/README.md`, `.github/workflows/tests.yml`, architecture/testing maps, historical sync spec/plan, transport tests, credential/config sources, tool definition, and health/retry code. [VERIFIED: files cited inline]
- Live local Git object graph and worktree commands, including `rev-parse`, `merge-base`, `rev-list`, `diff`, `ls-files`, `status`, and `ls-remote`. [VERIFIED: commands executed 2026-08-03]
- Live `tu status`, `tu grep`, `tu info`, local deterministic execution, and secret-safe environment-name intersection. [VERIFIED: commands executed 2026-08-03]

### Secondary (MEDIUM confidence)

- [Canonical ToolUniverse commit](https://github.com/mims-harvard/ToolUniverse/commit/56adcfd9c299078d0c40fde642b0be006510ccf3) and [PR #161](https://github.com/mims-harvard/ToolUniverse/pull/161) — current upstream provenance. [CITED: https://github.com/mims-harvard/ToolUniverse/commit/56adcfd9c299078d0c40fde642b0be006510ccf3] [CITED: https://github.com/mims-harvard/ToolUniverse/pull/161]
- [Git status](https://git-scm.com/docs/git-status), [rev-list](https://git-scm.com/docs/git-rev-list), [merge-base](https://git-scm.com/docs/git-merge-base), [diff](https://git-scm.com/docs/git-diff), [worktree](https://git-scm.com/docs/git-worktree) — official machine-state and ancestry semantics. [CITED: https://git-scm.com/docs/git-status]
- [pytest markers](https://docs.pytest.org/en/stable/how-to/mark.html) and [pytest reference](https://docs.pytest.org/en/stable/reference/reference.html) — official selection, collection, ignore, strictness, and JUnit options. [CITED: https://docs.pytest.org/en/stable/how-to/mark.html]
- [setup-python matrix testing](https://github.com/actions/setup-python/blob/main/docs/advanced-usage.md#matrix-testing) — official runtime-matrix pattern. [CITED: https://github.com/actions/setup-python/blob/main/docs/advanced-usage.md#matrix-testing]

### Tertiary (LOW confidence)

- None. All unverified design recommendations are explicitly tagged `[ASSUMED]` and listed in the Assumptions Log.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — versions and declarations were read or executed locally.
- Architecture: HIGH — transport/core/test sources were opened; proposed artifact layout is explicitly assumed.
- Git topology: HIGH — local Git, remote ls-remote, and GitHub API agree.
- Preservation inventory: HIGH for current counts/gaps; MEDIUM for proposed classification schema.
- Test/CI design: HIGH for current gaps; MEDIUM for proposed new files/commands until implemented.
- Live-provider design: MEDIUM — configured names are verified, but the complete provider-to-test manifest remains Wave 0 work.
- Pitfalls/security: HIGH where tied to current repository facts; MEDIUM for recommended new controls.

**Research date:** 2026-08-03
**Valid until:** 2026-08-10 for moving upstream/provider facts; Git/tooling patterns remain valid longer but must be rechecked at execution.
