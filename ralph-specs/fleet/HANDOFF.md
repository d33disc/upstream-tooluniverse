# Fleet Handoff — paste THIS into a fresh session (it points to everything else)

Keep it short so nothing gets mangled. Copy the block below verbatim:

---

Read and follow `ralph-specs/fleet/DEPLOY_PROMPT.md` — that file is your full mission briefing for
running the local-LLM maintenance fleet on this ToolUniverse repo. Execute it exactly.

First, load the prior knowledge base so you don't relearn anything (this is hard-won context):

- Memory index: `/Users/davis/.claude/projects/-Users-davis-code-ToolUniverse/memory/MEMORY.md` —
  read it, then read the fleet-relevant nodes it lists, especially `project_local_fleet`,
  `reference_fleet_token_economics`, `project_fda_cluster_phantom_failures`,
  `project_health_check_truth_and_workflow`, `feedback_tu_root_cause_discipline`,
  `feedback_never_push_upstream`, `feedback_upstream_ruff_format`.
- Fleet docs: `ralph-specs/fleet/README.md` (playbook) and `ralph-specs/fleet/TOKEN_ECONOMICS.md`.
- Repo orientation: `.claude/CLAUDE.md` (mental models + file map).

Then: invoke `using-superpowers`, plan with `writing-plans`, confirm both lanes are up
(Ollama :11434, MLX :8081), call the advisor with your plan, and start the loop — RE-TRIAGE FIRST
(the broken-tool count is phantom-inflated; do not fix what isn't broken).

---

(Everything above the lower `---` is the paste. The deploy prompt carries the full guardrails.)
