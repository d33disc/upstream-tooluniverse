#!/usr/bin/env bash
# Launch 8 parallel ralph health checks
# 4 Qwen + 2 Codex + 2 Claude Sonnet
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

echo "=== Ralph Health: 8 Parallel Sessions ==="
echo "  a1-a4: Qwen qwen3-coder-plus"
echo "  a5-a6: Codex gpt-5.4"
echo "  a7-a8: Claude Sonnet"
echo ""

# Qwen (4 sessions)
./ralph-health/run.sh a1 qwen &
echo "  a1 qwen PID: $!"
sleep 3
./ralph-health/run.sh a2 qwen &
echo "  a2 qwen PID: $!"
sleep 3
./ralph-health/run.sh a3 qwen &
echo "  a3 qwen PID: $!"
sleep 3
./ralph-health/run.sh a4 qwen &
echo "  a4 qwen PID: $!"
sleep 3

# Codex (2 sessions)
./ralph-health/run.sh a5 codex &
echo "  a5 codex PID: $!"
sleep 3
./ralph-health/run.sh a6 codex &
echo "  a6 codex PID: $!"
sleep 3

# Claude Sonnet (2 sessions)
./ralph-health/run.sh a7 claude &
echo "  a7 claude PID: $!"
sleep 3
./ralph-health/run.sh a8 claude &
echo "  a8 claude PID: $!"

echo ""
echo "=== All 8 launched ==="
echo "Monitor: for P in a1 a2 a3 a4 a5 a6 a7 a8; do echo \"\$P: \$(cat /tmp/tu-health-\$P/ralph-health/results_\$P.json 2>/dev/null | python3 -c 'import json,sys; print(len(json.load(sys.stdin)))' 2>/dev/null || echo 0)/256\"; done"

wait
echo "All 8 complete."
