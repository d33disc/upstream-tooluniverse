# Ralph Loop Learnings

Bugs found and fixed while building the parallel schema regeneration loop.

## Bug 1: grep -c exit code kills subshells

**Symptom**: All 4 workers die silently after printing "progress: 0/23".

**Root cause**: `grep -c` returns exit code 1 when the count is 0 (no matches).
Combined with `|| echo 0`, the variable captures both grep's "0" output AND the
echo's "0" output, producing `"0\n0"`. The subsequent `[ "$DONE" -ge "$TOTAL" ]`
fails on the malformed integer. Under `set -euo pipefail`, this kills the subshell.

**Fix**:

```bash
# WRONG — double output on zero matches
DONE=$(grep -cE 'pattern' file 2>/dev/null || echo 0)

# RIGHT — capture then default
DONE=$(grep -cE 'pattern' file 2>/dev/null) || true
DONE="${DONE:-0}"
```

## Bug 2: claude --print blocks on stdin when backgrounded

**Symptom**: Workers launch, Claude CLI starts but produces zero output. All 15
iterations complete instantly with empty logs.

**Root cause**: `claude --print` mode waits up to 3 seconds for stdin data. In a
background subshell `(...)&`, stdin is inherited from the parent but may be in an
ambiguous state. Claude's stdin timeout fires, it sees no prompt on stdin, and
returns immediately with empty output — exit code 0, no error.

**Fix**: Redirect stdin explicitly:

```bash
# WRONG — stdin ambiguous in background
claude --print --max-turns 40 "prompt" >> log 2>&1

# RIGHT — explicit /dev/null
claude --print --max-turns 40 "prompt" < /dev/null >> log 2>&1
```

## Bug 3: tee -a sends noise to parent stdout

**Symptom**: Cosmetic — `echo | tee -a "$LOG"` in background subshells sends
output to the parent process stdout, creating interleaved noise.

**Fix**: Use `>> "$LOG"` directly instead of `| tee -a "$LOG"` for background workers.

## Design Notes

- **Partition by source file**: Group tools by their JSON source file so no two
  workers edit the same file. Eliminates merge conflicts.
- **Separate branches per worker**: Each worker gets its own git branch to avoid
  push/pull lock contention. `collect.sh` merges them afterward.
- **Symlink venv**: Worktrees don't have their own venv. Symlink the main repo's
  `.venv` into each worktree.
- **Claude cwd reset**: Claude CLI may log "Shell cwd was reset to <repo_root>"
  but still operates in the launched directory. Not a real issue.
