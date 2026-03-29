#!/usr/bin/env bash
# Collect results from 4 schema worktrees into the base branch
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BASE_BRANCH="fix/regenerate-missing-return-schemas"
WORKTREE_BASE="/tmp/ralph-schema"
NUM_PARTITIONS=4

cd "$REPO_ROOT"

echo "Collecting schema results into $BASE_BRANCH..."
echo ""

git checkout "$BASE_BRANCH"

for i in $(seq 0 $((NUM_PARTITIONS - 1))); do
  BRANCH="${BASE_BRANCH}-p${i}"
  WORKTREE="${WORKTREE_BASE}-${i}"

  if ! git rev-parse --verify "$BRANCH" >/dev/null 2>&1; then
    echo "Partition $i: branch $BRANCH not found, skipping"
    continue
  fi

  # Count commits on partition branch vs base
  COMMITS=$(git rev-list --count "${BASE_BRANCH}..${BRANCH}" 2>/dev/null || echo 0)
  echo "Partition $i: $COMMITS commit(s) on $BRANCH"

  if [ "$COMMITS" -eq 0 ]; then
    echo "  No new commits, skipping"
    continue
  fi

  # Merge partition branch (no-ff to preserve history, or squash for clean)
  echo "  Merging $BRANCH..."
  git merge --no-edit "$BRANCH" || {
    echo "  CONFLICT merging $BRANCH — resolve manually"
    continue
  }

  # Copy progress file from worktree to main repo
  if [ -f "${WORKTREE}/ralph-schemas/progress_${i}.txt" ]; then
    cp "${WORKTREE}/ralph-schemas/progress_${i}.txt" "ralph-schemas/progress_${i}.txt"
  fi
done

# Summary
echo ""
echo "=== Results ==="
for i in $(seq 0 $((NUM_PARTITIONS - 1))); do
  DONE=$(grep -cE '^\[(DONE|SKIP)\]' "ralph-schemas/progress_${i}.txt" 2>/dev/null || echo 0)
  TOTAL=$(python3 -c "import json; print(len(json.load(open('ralph-schemas/partition_${i}.json'))))" 2>/dev/null || echo "?")
  echo "Partition $i: $DONE / $TOTAL"
done

echo ""
echo "Validate all JSON files:"
echo '  find src/tooluniverse/data -name "*.json" -exec python3 -c "import json,sys; json.load(open(sys.argv[1])); print(\"OK:\", sys.argv[1])" {} \;'
echo ""
echo "Clean up worktrees:"
echo "  for i in 0 1 2 3; do git worktree remove /tmp/ralph-schema-\$i --force; done"
echo "  for i in 0 1 2 3; do git branch -D fix/regenerate-missing-return-schemas-p\$i; done"
