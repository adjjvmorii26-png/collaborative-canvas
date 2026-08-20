#!/usr/bin/env bash
# Readiness probe for the IXPANSION devcontainer.
set -uo pipefail
cd "$(dirname "$0")/.."

echo "==> workspace: $(pwd)"
python3 -m py_compile ixpansion/organism-console/server.py 2>/dev/null && echo "==> server.py compiles" || echo "==> server.py FAILED to compile"

if curl -s -m 2 http://127.0.0.1:8890/api/body >/dev/null 2>&1; then
  echo "==> organism console: RUNNING on :8890"
else
  echo "==> organism console: not running (start with: scripts/dev.sh)"
fi

if [ -f .env ] && grep -q "OPENAI_API_KEY=" .env && [ "$(grep -c 'OPENAI_API_KEY=.\+' .env || true)" -gt 0 ]; then
  echo "==> OPENAI_API_KEY: present"
else
  echo "==> OPENAI_API_KEY: missing (add to .env)"
fi
if [ -f .env ] && grep -q "XAI_API_KEY=.\+" .env; then
  echo "==> XAI_API_KEY: present"
else
  echo "==> XAI_API_KEY: missing (optional)"
fi
