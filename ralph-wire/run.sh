#!/usr/bin/env bash
# Ralph Wire: Self-coding loop for health cache → tool finder integration
# Usage: ./ralph-wire/run.sh <cli: qwen|claude|codex>
set -euo pipefail

CLI="${1:?Usage: $0 <cli: qwen|claude|codex>}"
MAX_ITERATIONS="${MAX_ITERATIONS:-20}"

REPO_ROOT="$(git rev-parse --show-toplevel)"
WORKTREE_DIR="/tmp/tu-wire"
TARGET_BRANCH="feat/health-cache-wiring"

# Create worktree
if [[ -d "$WORKTREE_DIR" ]]; then
  echo "Worktree exists, reusing..."
  cd "$WORKTREE_DIR"
else
  cd "$REPO_ROOT"
  git branch "$TARGET_BRANCH" 2>/dev/null || true
  git worktree add "$WORKTREE_DIR" "$TARGET_BRANCH"
  cd "$WORKTREE_DIR"
  cp -r "$REPO_ROOT/ralph-wire" "$WORKTREE_DIR/"
fi

BRANCH=$(git branch --show-current)
if [[ "$BRANCH" == "main" || "$BRANCH" == "master" ]]; then
  echo "Error: On $BRANCH. Aborting." >&2
  exit 1
fi

echo "Ralph Wire: health cache → tool finder"
echo "Worktree: $WORKTREE_DIR"
echo "Branch: $TARGET_BRANCH"
echo "CLI: $CLI"
echo "---"

# Activate venv
if [[ -d "$REPO_ROOT/.venv" ]]; then
  # shellcheck disable=SC1091
  source "$REPO_ROOT/.venv/bin/activate"
fi

export TOOLUNIVERSE_LAZY_LOADING=true
export TOOLUNIVERSE_COERCE_TYPES=true
export TOOLUNIVERSE_LOG_LEVEL=WARNING

PROMPT=$(cat ralph-wire/PROMPT.md)

# Append current task status from git log
DONE_TASKS=$(git log --oneline --all 2>/dev/null | { grep "wire(task-" || true; } | { grep -o "wire(task-[0-9]*)" || true; } | sort -u | tr '\n' ', ')
PROMPT="$PROMPT

## Completed tasks (from git log): $DONE_TASKS
## Next: pick the FIRST incomplete task and implement it."

iteration=0
while :; do
  (( iteration += 1 ))
  if [[ $iteration -gt $MAX_ITERATIONS ]]; then
    echo "Max iterations reached." >&2
    exit 0
  fi

  # Check if all 8 tasks are done
  TASK_COUNT=$(git log --oneline 2>/dev/null | { grep "wire(task-" || true; } | wc -l | tr -d ' ')
  if [[ "$TASK_COUNT" -ge 8 ]]; then
    echo "All 7 tasks complete!"
    exit 0
  fi

  echo "Iteration $iteration/$MAX_ITERATIONS ($TASK_COUNT/7 tasks done)"

  # Run the LLM
  case "$CLI" in
    qwen)
      echo "$PROMPT" | qwen -y --model qwen3-coder-plus --chat-recording false
      ;;
    codex)
      echo "$PROMPT" | codex exec --full-auto --model gpt-5.4 --json -
      ;;
    claude)
      echo "$PROMPT" | claude --model sonnet --dangerously-skip-permissions -p --no-session-persistence
      ;;
    *)
      echo "$PROMPT" | eval "$CLI"
      ;;
  esac

  # Auto-commit if LLM forgot
  if [[ -n "$(git diff --name-only src/ 2>/dev/null)" ]]; then
    echo "Auto-committing..."
    git add src/ && git commit -m "wire: auto-commit iteration $iteration" 2>/dev/null || true
  fi

  # prek hooks
  if command -v prek >/dev/null 2>&1 && [[ -f .pre-commit-config.yaml ]]; then
    prek run --all-files || true
  fi

  echo "---"
  sleep 2
done
