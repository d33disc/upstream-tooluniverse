#!/usr/bin/env bash
# Ralph Schema Loop — 4 parallel worktrees, each on its own branch
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BASE_BRANCH="fix/regenerate-missing-return-schemas"
CLI="${CLI:-claude}"
MAX_ITERATIONS="${MAX_ITERATIONS:-15}"
WORKTREE_BASE="/tmp/ralph-schema"
VENV_PYTHON="${REPO_ROOT}/.venv/bin/python"
NUM_PARTITIONS=4

cd "$REPO_ROOT"

# Validate
if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "Error: Not a git repository." >&2
  exit 1
fi

if [ ! -x "$VENV_PYTHON" ]; then
  echo "Error: venv not found at $VENV_PYTHON" >&2
  exit 1
fi

# Ensure base branch exists and is up to date
git checkout "$BASE_BRANCH" 2>/dev/null || {
  echo "Error: Branch $BASE_BRANCH does not exist." >&2
  exit 1
}
git checkout main

PIDS=()

cleanup() {
  echo ""
  echo "Shutting down..."
  for pid in "${PIDS[@]}"; do
    kill "$pid" 2>/dev/null || true
  done
  wait 2>/dev/null
  # Don't auto-remove worktrees — they have commits we want
  echo "Workers stopped. Worktrees preserved at ${WORKTREE_BASE}-{0..3}"
  echo "To collect results: ralph-schemas/collect.sh"
}
trap cleanup INT TERM

for i in $(seq 0 $((NUM_PARTITIONS - 1))); do
  BRANCH="${BASE_BRANCH}-p${i}"
  WORKTREE="${WORKTREE_BASE}-${i}"
  LOG="${REPO_ROOT}/ralph-schemas/worker_${i}.log"

  # Create per-worker branch from base
  git branch -D "$BRANCH" 2>/dev/null || true
  git branch "$BRANCH" "$BASE_BRANCH"

  # Create worktree
  if [ -d "$WORKTREE" ]; then
    git worktree remove "$WORKTREE" --force 2>/dev/null || true
    git worktree prune
  fi
  git worktree add "$WORKTREE" "$BRANCH"

  # Symlink venv into worktree so tools resolve
  ln -sfn "${REPO_ROOT}/.venv" "${WORKTREE}/.venv"

  echo "Created worktree $i: $WORKTREE on $BRANCH"
done

echo ""

# Launch workers
for i in $(seq 0 $((NUM_PARTITIONS - 1))); do
  BRANCH="${BASE_BRANCH}-p${i}"
  WORKTREE="${WORKTREE_BASE}-${i}"
  LOG="${REPO_ROOT}/ralph-schemas/worker_${i}.log"

  (
    cd "$WORKTREE"
    export PATH="${REPO_ROOT}/.venv/bin:$PATH"
    export VIRTUAL_ENV="${REPO_ROOT}/.venv"

    for iter in $(seq 1 "$MAX_ITERATIONS"); do
      echo "=== [worker-$i] iteration $iter/$MAX_ITERATIONS ===" | tee -a "$LOG"

      # Check completion
      TOTAL=$("$VENV_PYTHON" -c "import json; print(len(json.load(open('ralph-schemas/partition_${i}.json'))))")
      DONE=$(grep -cE '^\[(DONE|SKIP)\]' "ralph-schemas/progress_${i}.txt" 2>/dev/null || echo 0)

      if [ "$DONE" -ge "$TOTAL" ]; then
        echo "[worker-$i] COMPLETE ($DONE/$TOTAL)" | tee -a "$LOG"
        break
      fi

      echo "[worker-$i] progress: $DONE/$TOTAL" | tee -a "$LOG"

      $CLI --print \
        --dangerously-skip-permissions \
        --max-turns 40 \
        "You are schema worker $i. Follow instructions in ralph-schemas/PROMPT.md exactly.
Your partition: ralph-schemas/partition_${i}.json
Your progress: ralph-schemas/progress_${i}.txt
Process the next 5-8 unprocessed tools. Validate JSON after each edit. Commit when done. Then exit." \
        >> "$LOG" 2>&1 || {
          echo "[worker-$i] iteration $iter exited with error" | tee -a "$LOG"
        }

      sleep 2
    done

    echo "[worker-$i] finished all iterations" | tee -a "$LOG"
  ) &

  PIDS+=($!)
  echo "Started worker $i (PID ${PIDS[-1]}) → $LOG"
  sleep 3  # stagger to avoid resource contention
done

echo ""
echo "All $NUM_PARTITIONS workers launched."
echo "Monitor: tail -f ralph-schemas/worker_*.log"
echo "Stop:    Ctrl+C"
echo ""

wait
echo "All workers complete."
echo "Run ralph-schemas/collect.sh to merge results."
