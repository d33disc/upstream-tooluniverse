#!/usr/bin/env bash
# Ralph Schema Loop v2 — 4 parallel worktrees for remaining 36 schemas
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BASE_BRANCH="fix/remaining-return-schemas"
CLI="${CLI:-claude}"
MAX_ITERATIONS="${MAX_ITERATIONS:-8}"
WORKTREE_BASE="/tmp/ralph-schema-v2"
VENV_PYTHON="${REPO_ROOT}/.venv/bin/python"
NUM_PARTITIONS=4

cd "$REPO_ROOT"

if ! git rev-parse --verify "$BASE_BRANCH" >/dev/null 2>&1; then
  echo "Error: Branch $BASE_BRANCH does not exist." >&2
  exit 1
fi

if [ ! -x "$VENV_PYTHON" ]; then
  echo "Error: venv not found at $VENV_PYTHON" >&2
  exit 1
fi

git checkout "$BASE_BRANCH" 2>/dev/null
git checkout main 2>/dev/null

PIDS=()

cleanup() {
  echo ""
  echo "Shutting down..."
  for pid in "${PIDS[@]}"; do
    kill "$pid" 2>/dev/null || true
  done
  wait 2>/dev/null
  echo "Workers stopped. Worktrees at ${WORKTREE_BASE}-{0..3}"
  echo "Collect: ralph-schemas-v2/collect.sh"
}
trap cleanup INT TERM

# Create worktrees
for i in $(seq 0 $((NUM_PARTITIONS - 1))); do
  BRANCH="${BASE_BRANCH}-p${i}"
  WORKTREE="${WORKTREE_BASE}-${i}"

  git branch -D "$BRANCH" 2>/dev/null || true
  git branch "$BRANCH" "$BASE_BRANCH"

  if [ -d "$WORKTREE" ]; then
    git worktree remove "$WORKTREE" --force 2>/dev/null || true
    git worktree prune
  fi
  git worktree add "$WORKTREE" "$BRANCH"
  ln -sfn "${REPO_ROOT}/.venv" "${WORKTREE}/.venv"

  echo "Worktree $i: $WORKTREE on $BRANCH"
done

echo ""

# Launch workers
for i in $(seq 0 $((NUM_PARTITIONS - 1))); do
  WORKTREE="${WORKTREE_BASE}-${i}"
  LOG="${REPO_ROOT}/ralph-schemas-v2/worker_${i}.log"
  > "$LOG"

  (
    cd "$WORKTREE"
    export PATH="${REPO_ROOT}/.venv/bin:$PATH"
    export VIRTUAL_ENV="${REPO_ROOT}/.venv"

    # Source API keys
    # shellcheck disable=SC1091
    [ -f ~/.env.secure ] && source ~/.env.secure

    for iter in $(seq 1 "$MAX_ITERATIONS"); do
      echo "=== [worker-$i] iteration $iter/$MAX_ITERATIONS ===" >> "$LOG"

      TOTAL=$("$VENV_PYTHON" -c "import json; print(len(json.load(open('ralph-schemas-v2/partition_${i}.json'))))" 2>/dev/null)
      TOTAL="${TOTAL:-0}"
      DONE=$(grep -cE '^\[(DONE|SKIP)\]' "ralph-schemas-v2/progress_${i}.txt" 2>/dev/null) || true
      DONE="${DONE:-0}"

      if [ "$DONE" -ge "$TOTAL" ]; then
        echo "[worker-$i] COMPLETE ($DONE/$TOTAL)" >> "$LOG"
        break
      fi

      echo "[worker-$i] progress: $DONE/$TOTAL" >> "$LOG"

      $CLI --print \
        --dangerously-skip-permissions \
        --max-turns 50 \
        "You are schema worker $i. Follow instructions in ralph-schemas-v2/PROMPT.md exactly.
Your partition: ralph-schemas-v2/partition_${i}.json
Your progress: ralph-schemas-v2/progress_${i}.txt
Process ALL remaining unprocessed tools. Validate JSON after each edit. Commit when done. Then exit." \
        < /dev/null >> "$LOG" 2>&1 || {
          echo "[worker-$i] iteration $iter exited with error" >> "$LOG"
        }

      sleep 2
    done

    echo "[worker-$i] finished" >> "$LOG"
  ) &

  PIDS+=($!)
  echo "Started worker $i (PID ${PIDS[-1]}) → $LOG"
  sleep 5
done

echo ""
echo "All $NUM_PARTITIONS workers launched."
echo "Monitor: tail -f ralph-schemas-v2/worker_*.log"
echo "Stop:    Ctrl+C"
echo ""

wait
echo "All workers complete."
echo "Run ralph-schemas-v2/collect.sh to merge results."
