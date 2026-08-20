#!/usr/bin/env bash
# Local development launcher for the IXPANSION organism.
# Starts the Organism Console (and optionally the control-room funding app).
set -euo pipefail
cd "$(dirname "$0")/.."

PORT="${PORT:-8890}"
CONSOLE_ONLY="${CONSOLE_ONLY:-1}"

echo "==> Starting Organism Console on :${PORT}"
python3 ixpansion/organism-console/server.py --port "${PORT}" &
CONSOLE_PID=$!

if [ "${CONSOLE_ONLY}" != "1" ] && [ -d ixpansion/control-room/node_modules ]; then
  echo "==> Starting Control Room (Vite + API)"
  (cd ixpansion/control-room && npm run dev) &
  CONTROL_PID=$!
fi

trap 'echo "==> stopping"; kill ${CONSOLE_PID} ${CONTROL_PID:-} 2>/dev/null || true' EXIT INT TERM

echo "==> Open http://127.0.0.1:${PORT} (Organism Console)"
wait
