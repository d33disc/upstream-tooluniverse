# Next Session: Build the Deep Research Skill

Read your memory files first — especially `project_deep_research_skill.md` and `project_session_summary.md`. Then read the full plan at `/Users/davis/.claude/plans/robust-whistling-wall.md`.

## Task

Build `skills/tooluniverse-deep-research/` — the iterative "thinking brain" that searches 1,900+ life science tools, cross-references findings, discovers non-obvious connections, and produces evidence-graded research reports.

This is NOT a tool finder. This is a research agent that thinks.

## What to build

```
skills/tooluniverse-deep-research/
├── SKILL.md                         # <500 lines
├── references/
│   ├── research-loop.md             # Iterative protocol + state file schema
│   ├── entity-resolution.md         # Disambiguate across databases
│   ├── cross-reference.md           # Multi-hop connection patterns
│   ├── evidence-grading.md          # T1-T4 framework
│   └── follow-the-data.md           # Entity → connection table (domain-agnostic)
```

## Critical principles

1. **Domain-agnostic**: Do NOT hardcode tool chains by medical specialty. Follow entities wherever they lead. If heart failure research leads to dental microbiology, chase it.
2. **Iterative**: Each invocation does one research cycle (search → analyze → hypothesize). The skill should be invocable multiple times, building on research_state.json.
3. **Health-aware**: Check `ToolHealthCache().is_live(tool)` before planning tool calls. Plan around broken tools.
4. **Evidence-graded**: Every claim cites its source and tier (T1=regulatory, T2=peer-reviewed, T3=preprints, T4=computational).
5. **Progressive disclosure**: SKILL.md is the overview. Reference docs are loaded on demand.

## Test it with

1. "What are all known treatments for EGFR-mutant non-small cell lung cancer?"
2. "Map the connections between BRCA1, DNA repair, and available therapies"
3. "What is Moderna's current pipeline and competitive position?"

## Context

- Repo: `/Users/davis/code/ToolUniverse` on branch `main`
- 1,900+ working tools (after PRs #13-17)
- tool_health.py at `src/tooluniverse/tool_health.py`
- 68 existing research skills to reference for patterns
- Company-research skill at `skills/company-research/` is the best existing template

## Git workflow

Feature branch → atomic commits → PR → squash merge → clean tree. Never commit to main.
