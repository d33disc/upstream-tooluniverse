#!/usr/bin/env bash
# Ralph Loop - ToolUniverse Stress Test
set -euo pipefail

PROMPT_FILE="${PROMPT_FILE:-PROMPT.md}"
CLI="${CLI:-claude}"
MAX_ITERATIONS="${MAX_ITERATIONS:-100}"

# Validate git repository
if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "Error: Not a git repository." >&2
  exit 1
fi

# Branch safety: never run on main
BRANCH=$(git branch --show-current)
if [[ "$BRANCH" == "main" || "$BRANCH" == "master" ]]; then
  echo "Error: On $BRANCH branch. Switch to a feature branch first." >&2
  exit 1
fi

if [[ ! -f "$PROMPT_FILE" ]]; then
  echo "Error: $PROMPT_FILE not found" >&2
  exit 1
fi

# Activate ToolUniverse venv
if [[ -d .venv ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

# ToolUniverse environment
export TOOLUNIVERSE_LAZY_LOADING=true
export TOOLUNIVERSE_COERCE_TYPES=true
export TOOLUNIVERSE_LOG_LEVEL=WARNING

# Map CLI name to command
case "$CLI" in
  claude) CLI_CMD="claude --model opus --dangerously-skip-permissions -p --no-session-persistence" ;;
  amp)    CLI_CMD="amp" ;;
  gemini) CLI_CMD="gemini" ;;
  *)      CLI_CMD="$CLI" ;;
esac

echo "Ralph loop (ToolUniverse stress test): $CLI_CMD < $PROMPT_FILE"
echo "Branch: $BRANCH"
echo "Max iterations: $MAX_ITERATIONS"
echo "Press Ctrl+C to stop"
echo "---"

iteration=0
while :; do
  (( iteration += 1 ))

  if [[ $iteration -gt $MAX_ITERATIONS ]]; then
    echo "Error: Max iterations ($MAX_ITERATIONS) reached" >&2
    exit 1
  fi

  # Safety: verify still on feature branch
  CURRENT=$(git branch --show-current)
  if [[ "$CURRENT" == "main" || "$CURRENT" == "master" ]]; then
    echo "Error: Switched to $CURRENT during loop. Aborting." >&2
    exit 1
  fi

  echo "Iteration $iteration/$MAX_ITERATIONS"
  if ! cat "$PROMPT_FILE" | eval "$CLI_CMD"; then
    echo "Error: CLI command failed" >&2
    exit 1
  fi

  # Run prek hooks
  if command -v prek >/dev/null 2>&1 && [[ -f .pre-commit-config.yaml ]]; then
    echo "Running prek hooks..."
    prek run --all-files || echo "prek found issues - next iteration will fix"
  fi

  # Check for completion
  if grep -q '<promise>COMPLETE</promise>' progress.txt 2>/dev/null; then
    echo "---"
    echo "Ralph complete. All domains tested, all HIGH issues fixed."
    exit 0
  fi

  echo "---"
  echo "Iteration done. Fresh context in 2s..."
  sleep 2
done
