#!/usr/bin/env bash
# Ralph Health Check - Parallel runner using git worktrees
# Usage: ./ralph-health/run.sh [partition_suffix]
# Example: ./ralph-health/run.sh aa
set -euo pipefail

PARTITION="${1:?Usage: $0 <partition: aa|ab|ac|ad>}"
CLI_MODEL="${CLI_MODEL:-sonnet}"
MAX_ITERATIONS="${MAX_ITERATIONS:-30}"

REPO_ROOT="$(git rev-parse --show-toplevel)"
WORKTREE_DIR="/tmp/tu-health-$PARTITION"
TARGET_BRANCH="fix/tool-health-$PARTITION"

# Create worktree for this partition (isolated git checkout)
if [[ -d "$WORKTREE_DIR" ]]; then
  echo "Worktree $WORKTREE_DIR exists, reusing..."
  cd "$WORKTREE_DIR"
else
  cd "$REPO_ROOT"
  git branch "$TARGET_BRANCH" 2>/dev/null || true
  git worktree add "$WORKTREE_DIR" "$TARGET_BRANCH"
  cd "$WORKTREE_DIR"

  # Copy partition files and prompt into worktree
  cp -r "$REPO_ROOT/ralph-health" "$WORKTREE_DIR/"
fi

BRANCH=$(git branch --show-current)
if [[ "$BRANCH" == "main" || "$BRANCH" == "master" ]]; then
  echo "Error: On $BRANCH. Aborting." >&2
  exit 1
fi

PARTITION_FILE="ralph-health/partition_$PARTITION"
if [[ ! -f "$PARTITION_FILE" ]]; then
  echo "Error: $PARTITION_FILE not found" >&2
  exit 1
fi

TOOL_COUNT=$(wc -l < "$PARTITION_FILE" | tr -d ' ')
echo "Ralph health check: partition $PARTITION ($TOOL_COUNT tools)"
echo "Worktree: $WORKTREE_DIR"
echo "Branch: $TARGET_BRANCH"
echo "Model: $CLI_MODEL, Max iterations: $MAX_ITERATIONS"
echo "---"

# Activate venv from main repo
if [[ -d "$REPO_ROOT/.venv" ]]; then
  # shellcheck disable=SC1091
  source "$REPO_ROOT/.venv/bin/activate"
fi

export TOOLUNIVERSE_LAZY_LOADING=true
export TOOLUNIVERSE_COERCE_TYPES=true
export TOOLUNIVERSE_LOG_LEVEL=WARNING
export PARTITION

PROMPT=$(cat ralph-health/PROMPT.md)
PROMPT="$PROMPT

## Your Partition: $PARTITION
File: $PARTITION_FILE
Tools: $TOOL_COUNT"

iteration=0
while :; do
  (( iteration += 1 ))
  if [[ $iteration -gt $MAX_ITERATIONS ]]; then
    echo "Max iterations reached." >&2
    exit 0
  fi

  RESULTS_FILE="ralph-health/results_$PARTITION.json"
  if [[ -f "$RESULTS_FILE" ]]; then
    TESTED=$(python3 -c "import json; print(len(json.load(open('$RESULTS_FILE'))))" 2>/dev/null || echo 0)
    if [[ "$TESTED" -ge "$TOOL_COUNT" ]]; then
      echo "All $TOOL_COUNT tools tested. Done."
      exit 0
    fi
    echo "Iteration $iteration/$MAX_ITERATIONS ($TESTED/$TOOL_COUNT tested)"
  else
    echo "Iteration $iteration/$MAX_ITERATIONS (0/$TOOL_COUNT tested)"
  fi

  echo "$PROMPT" | claude --model "$CLI_MODEL" --dangerously-skip-permissions -p --no-session-persistence

  # prek hooks: catch formatting/syntax drift between iterations
  if command -v prek >/dev/null 2>&1 && [[ -f .pre-commit-config.yaml ]]; then
    echo "Running prek hooks..."
    prek run --all-files || echo "prek found issues — next iteration will fix"
  fi

  # Drift check: verify no tool that previously passed now fails
  if [[ -f "$RESULTS_FILE" ]]; then
    echo "Running drift check on previously fixed tools..."
    python3 -c "
import json, subprocess, sys
results = json.load(open('$RESULTS_FILE'))
fixed = [r['tool'] for r in results if r.get('fixed')]
drifted = []
for tool in fixed:
    out = subprocess.run(['python', '-m', 'tooluniverse.cli', 'test', tool],
        capture_output=True, text=True, timeout=15)
    if 'passed' not in out.stdout:
        drifted.append(tool)
if drifted:
    print(f'DRIFT DETECTED: {drifted}', file=sys.stderr)
else:
    print(f'  {len(fixed)} fixed tools still passing')
" 2>&1 || echo "Drift check errored"
  fi

  echo "---"
  sleep 2
done
