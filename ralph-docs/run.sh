#!/usr/bin/env bash
# Ralph Docs - Test example generator + description auditor
# Usage: ./ralph-docs/run.sh [partition: aa|ab|ac|ad] [cli: codex|claude]
set -euo pipefail

PARTITION="${1:?Usage: $0 <partition: aa|ab|ac|ad> [cli: codex|claude]}"
CLI="${2:-codex}"
MAX_ITERATIONS="${MAX_ITERATIONS:-50}"

REPO_ROOT="$(git rev-parse --show-toplevel)"
WORKTREE_DIR="/tmp/tu-docs-$PARTITION"
TARGET_BRANCH="docs/test-examples-$PARTITION"

# Create worktree
if [[ -d "$WORKTREE_DIR" ]]; then
  echo "Worktree $WORKTREE_DIR exists, reusing..."
  cd "$WORKTREE_DIR"
else
  cd "$REPO_ROOT"
  git branch "$TARGET_BRANCH" 2>/dev/null || true
  git worktree add "$WORKTREE_DIR" "$TARGET_BRANCH"
  cd "$WORKTREE_DIR"
  cp -r "$REPO_ROOT/ralph-docs" "$WORKTREE_DIR/"
fi

BRANCH=$(git branch --show-current)
if [[ "$BRANCH" == "main" || "$BRANCH" == "master" ]]; then
  echo "Error: On $BRANCH. Aborting." >&2
  exit 1
fi

PARTITION_FILE="ralph-docs/partition_$PARTITION"
FILE_COUNT=$(wc -l < "$PARTITION_FILE" | tr -d ' ')

# Map CLI
case "$CLI" in
  codex)  CLI_CMD="codex --approval-mode full-auto -q" ;;
  claude) CLI_CMD="claude --model sonnet --dangerously-skip-permissions -p --no-session-persistence" ;;
  *)      CLI_CMD="$CLI" ;;
esac

echo "Ralph docs: partition $PARTITION ($FILE_COUNT files)"
echo "Worktree: $WORKTREE_DIR"
echo "Branch: $TARGET_BRANCH"
echo "CLI: $CLI_CMD"
echo "---"

# Activate venv
if [[ -d "$REPO_ROOT/.venv" ]]; then
  # shellcheck disable=SC1091
  source "$REPO_ROOT/.venv/bin/activate"
fi

export TOOLUNIVERSE_LAZY_LOADING=true
export TOOLUNIVERSE_COERCE_TYPES=true
export TOOLUNIVERSE_LOG_LEVEL=WARNING
export PARTITION

PROMPT=$(cat ralph-docs/PROMPT.md)
PROMPT="$PROMPT

## Your Partition: $PARTITION
File: $PARTITION_FILE
Total files: $FILE_COUNT"

iteration=0
while :; do
  (( iteration += 1 ))
  if [[ $iteration -gt $MAX_ITERATIONS ]]; then
    echo "Max iterations reached." >&2
    exit 0
  fi

  RESULTS_FILE="ralph-docs/results_$PARTITION.json"
  if [[ -f "$RESULTS_FILE" ]]; then
    TESTED=$(python3 -c "
import json
d = json.load(open('$RESULTS_FILE'))
files_done = set(r.get('file','') for r in d)
print(len(files_done))
" 2>/dev/null || echo 0)
    if [[ "$TESTED" -ge "$FILE_COUNT" ]]; then
      echo "All $FILE_COUNT files audited. Done."
      exit 0
    fi
    echo "Iteration $iteration/$MAX_ITERATIONS ($TESTED/$FILE_COUNT files audited)"
  else
    echo "Iteration $iteration/$MAX_ITERATIONS (0/$FILE_COUNT files audited)"
  fi

  echo "$PROMPT" | eval "$CLI_CMD"

  # prek hooks
  if command -v prek >/dev/null 2>&1 && [[ -f .pre-commit-config.yaml ]]; then
    prek run --all-files || true
  fi

  echo "---"
  sleep 2
done
