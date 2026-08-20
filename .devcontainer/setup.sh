#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

echo "[setup] installing python deps"
pip install --quiet PyYAML

if [ -d ixpansion/control-room/node_modules ]; then
  echo "[setup] control-room deps already present"
else
  echo "[setup] installing control-room deps"
  (cd ixpansion/control-room && npm install --silent) || echo "[setup] npm install skipped/failed (network may be offline)"
fi

echo "[setup] creating .env from template if missing"
if [ ! -f .env ]; then
  cp .env.example .env
  echo "[setup] .env created from example (fill in keys)"
fi

echo "[setup] preparing console data dirs"
mkdir -p ixpansion/content_output/console data/runs ixpansion/content_output/reports

echo "[setup] verifying python imports + syntax"
python3 -m py_compile ixpansion/organism-console/server.py
python3 -c "import ixpansion.services.bodylink; print('[setup] bodylink ok')"

echo "[setup] running console test suite"
if python3 -m unittest discover -s ixpansion/tests -q; then
  echo "[setup] console tests: OK"
else
  echo "[setup] WARNING: console tests failed (fix before shipping)"
fi

echo "[setup] ready. Run: python3 ixpansion/organism-console/server.py --port 8890"
