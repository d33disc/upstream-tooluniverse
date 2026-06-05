# Fleet Handoff — 71-Schema Cluster (paste THIS into a fresh session)

The bug-fix + repo-sync work is DONE (PRs #44/#45/#46 merged to
`d0854414..bbb61560`, main synced, perf rebased clean). The next job is the
**71 over-strict `return_schema` tools** — a textbook fleet batch. Copy the
block between the `---` lines verbatim.

---

You are picking up the **71-schema FLEET cluster** on this ToolUniverse repo
(origin = `d33disc/upstream-tooluniverse`; NEVER push to upstream/mims-harvard).

**Load the hard-won context first — do not relearn it:**

- Memory index:
  `/Users/davis/.claude/projects/-Users-davis-code-ToolUniverse/memory/MEMORY.md`.
  Read these nodes: `project_health_triage_2026_06_05` (the task, the 71-tool
  list, the green-but-wrong guard), `project_local_fleet`,
  `reference_fleet_token_economics`, `feedback_tu_root_cause_discipline`,
  `feedback_never_push_upstream`, `feedback_upstream_ruff_format`.
- Harvested truth (already on disk — the real API output for each tool is here,
  so each fix is well-specified):
  `memory/data_health_triage_2026-06-05_harvest.tsv` + `..._buckets.json`.
- Fleet playbook: `ralph-specs/fleet/README.md` +
  `ralph-specs/fleet/DEPLOY_PROMPT.md` +
  `ralph-specs/fleet/TOKEN_ECONOMICS.md`.

**The task.** 71 tools fail their health check because the authored
`return_schema` over-fits one sample (wrong type / nullability / list-at-root)
and false-rejects valid live output. The fix per tool: **align `return_schema`
to the real output shape; do NOT change tool code.** The harvested error string
already contains the real output, so the spec for each worker is precise and the
verify is `cli test <tool> --json` going error→success. Tool list is in
`project_health_triage_2026_06_05` ("NEXT SESSION — the 71").

**Why fleet, not direct.** N=71 >> the crossover point;
mechanical-but-individual; truth already harvested. This is exactly where local
workers win on token + context economics (see
`reference_fleet_token_economics`). The 4 done directly were small one-offs —
these are not.

**The non-negotiable guard (green-but-wrong).** A passing test over the wrong
shape is a failure, not a fix. Several are NOT pure nullable-relax and must be
judged per-diff, never rubber-stamped:

- `NvidiaNIM_vista3d` returns `{'message':'Inference success'}` where the schema
  wants a string-at-root.
- `ols_*`, `PubTator3_LiteratureSearch`, `DailyMed_get_spl_by_setid` return
  `None` at root on empty — decide: should the TOOL return `[]`/`{}` (real code
  bug) vs. should the SCHEMA allow null? Inspect output sanity before relaxing.
  "Well-formed ≠ true."

**Procedure.**

1. Invoke `using-superpowers`; plan with `writing-plans`.
2. Confirm both lanes up (Ollama :11434, MLX :8081); `git status` clean, on a
   fresh branch off `main` (NOT perf — fleet infra is untracked off main; never
   `git clean -fd` there).
3. Feed each worker its harvested output string + "align return_schema to this
   real shape; do NOT touch tool code." Route the mechanical nullable-relaxes to
   the fast lane; route the ~handful of judgement cases (vista3d, ols_*,
   None-at-root) to the hard lane or do them yourself.
4. YOU review every diff (the only merge gate). KEEP → commit; DISCARD →
   requeue. NEVER trust a worker's green test.
5. Call the advisor with your plan before starting and before declaring done.
6. Open ONE PR to `d33disc` base `main` when the batch is reviewed. Match
   `pyproject.toml` ruff (not global `~/.ruff.toml`).

Re-derive the count before trusting it: the "broken" totals are ~85%
phantom/external/key-gated/fixture (see
`project_fda_cluster_phantom_failures`). Fix only the real 71.

---

(Everything between the `---` lines is the paste. Append it after the general
fleet [`HANDOFF.md`](HANDOFF.md) block if you also want the full guardrails.)
