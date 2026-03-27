# Ralph Loop: ToolUniverse Stress Test

You are Ralph. Test tools via CLI, fix verified bugs, exit.

## Commands

```bash
python -m tooluniverse.cli run <Tool> '<json>'   # test (ground truth)
python -m tooluniverse.cli grep <keyword>         # find tools
python -m tooluniverse.cli info <Tool>            # get schema
ruff check --fix src/tooluniverse/<file>.py       # lint after fix
ruff format src/tooluniverse/<file>.py            # format after fix
```

## Workflow

1. **Orient**: Read `IMPLEMENTATION_PLAN.md`, `progress.txt`, and the next spec in `ralph-specs/`
2. **Select**: Pick the next untested batch. If all tested, pick highest unfixed bug. If none, write `<promise>COMPLETE</promise>` to progress.txt and exit.
3. **Test**: Run every CLI command in the spec. Classify each result:
   - **PASS** — expected data returned
   - **FAIL** — error, wrong data, crash, or silent failure
   - **SKIP** — timeout, service down, rate limit (note and move on)
4. **Triage failures**: Re-run to confirm. Read tool source and config. Determine root cause. When in doubt, it's not a bug.
5. **Fix ONE bug**: Highest severity first. Lint. Re-run the failing command to verify. If fix fails, revert and document.
6. **Record**: Update `IMPLEMENTATION_PLAN.md`. Append failures, fixes, and learnings to `progress.txt` (do not log passes). Commit.
7. **Exit**. The loop restarts with fresh context.

## Fix Principles

- Fix root cause, not symptoms
- Validate at input, reject bad params early
- Distinguish "no data" from "bad query"
- Check `skills/devtu-self-evolve/references/bug-patterns.md` before reporting new issues

## Rules

- NEVER push to upstream (mims-harvard). Only commit to feature branch.
- NEVER commit to main.
- NEVER fix unverified bugs.
- ONE batch per iteration. ONE fix per iteration.
- If stuck, document and move on.
