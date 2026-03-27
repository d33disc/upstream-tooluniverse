#!/usr/bin/env bash
# Launch 4 parallel ralph health check sessions via git worktrees
# Usage: ./ralph-health/launch.sh
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

echo "=== Ralph Health Check: 4 Parallel Sessions ==="
echo "Model: ${CLI_MODEL:-sonnet} (override: CLI_MODEL=opus)"
echo "Max iterations/partition: ${MAX_ITERATIONS:-30}"
echo ""

# Create branches for each partition
for P in aa ab ac ad; do
  git branch "fix/tool-health-$P" 2>/dev/null || true
done

mkdir -p ralph-health/logs

PIDS=()
for P in aa ab ac ad; do
  TOOL_COUNT=$(wc -l < "ralph-health/partition_$P" | tr -d ' ')
  echo "Starting partition $P ($TOOL_COUNT tools)..."
  ./ralph-health/run.sh "$P" > "ralph-health/logs/$P.log" 2>&1 &
  PIDS+=($!)
  echo "  PID: ${PIDS[-1]} -> branch fix/tool-health-$P"
  sleep 5  # stagger for worktree creation
done

echo ""
echo "=== All 4 partitions launched ==="
echo ""
echo "Monitor:"
echo "  tail -f ralph-health/logs/aa.log"
echo "  for P in aa ab ac ad; do echo \"\$P: \$(cat ralph-health/results_\$P.json 2>/dev/null | python3 -c 'import json,sys; print(len(json.load(sys.stdin)))' 2>/dev/null || echo 0) tested\"; done"
echo ""
echo "Token budget (Sonnet, 20 tools/iteration):"
echo "  ~8 iterations × 4 partitions = ~32 iterations"
echo "  ~50K tokens/iteration = ~1.6M total"
echo ""

# Wait for all to complete
for i in "${!PIDS[@]}"; do
  P=("aa" "ab" "ac" "ad")
  wait "${PIDS[$i]}" 2>/dev/null || true
  echo "Partition ${P[$i]} complete (PID ${PIDS[$i]})"
done

echo ""
echo "=== All partitions complete ==="
echo "Merge results:"
echo "  git worktree list"
echo "  for P in aa ab ac ad; do git merge fix/tool-health-\$P; done"
