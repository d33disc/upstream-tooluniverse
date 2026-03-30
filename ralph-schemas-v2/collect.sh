#!/usr/bin/env bash
# Collect results from 4 schema v2 worktrees into base branch
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BASE_BRANCH="fix/remaining-return-schemas"
WORKTREE_BASE="/tmp/ralph-schema-v2"
NUM_PARTITIONS=4

cd "$REPO_ROOT"
git checkout "$BASE_BRANCH"

for i in $(seq 0 $((NUM_PARTITIONS - 1))); do
  BRANCH="${BASE_BRANCH}-p${i}"

  if ! git rev-parse --verify "$BRANCH" >/dev/null 2>&1; then
    echo "Partition $i: branch not found, skipping"
    continue
  fi

  COMMITS=$(git rev-list --count "${BASE_BRANCH}..${BRANCH}" 2>/dev/null || echo 0)
  echo "Partition $i: $COMMITS commit(s)"

  if [ "$COMMITS" -eq 0 ]; then
    echo "  No commits, skipping"
    continue
  fi

  git merge --no-edit "$BRANCH" || {
    echo "  CONFLICT — resolve manually"
    continue
  }
done

# Summary
echo ""
echo "=== Results ==="
TOTAL_DONE=0
TOTAL_SKIP=0
for i in $(seq 0 $((NUM_PARTITIONS - 1))); do
  WT="${WORKTREE_BASE}-${i}"
  DONE=$(grep -c '^\[DONE\]' "${WT}/ralph-schemas-v2/progress_${i}.txt" 2>/dev/null) || true
  SKIP=$(grep -c '^\[SKIP\]' "${WT}/ralph-schemas-v2/progress_${i}.txt" 2>/dev/null) || true
  DONE="${DONE:-0}"
  SKIP="${SKIP:-0}"
  echo "Partition $i: $DONE written, $SKIP skipped"
  TOTAL_DONE=$((TOTAL_DONE + DONE))
  TOTAL_SKIP=$((TOTAL_SKIP + SKIP))
done
echo "Total: $TOTAL_DONE written, $TOTAL_SKIP skipped"

echo ""
echo "Validate: find src/tooluniverse/data -name '*.json' -exec python3 -c 'import json,sys; json.load(open(sys.argv[1]))' {} \\;"
echo "Cleanup:  for i in 0 1 2 3; do git worktree remove ${WORKTREE_BASE}-\$i --force; git branch -D ${BASE_BRANCH}-p\$i; done"
