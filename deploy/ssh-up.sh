#!/usr/bin/env bash
# Run on ECS after clone: ./deploy/ssh-up.sh
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ ! -f .env ]]; then
  echo "Missing .env — copy .env.production.example to .env and set DASHSCOPE_API_KEY"
  exit 1
fi
docker compose pull || true
docker compose up -d --build
docker compose ps
echo "Smoke: curl -s http://127.0.0.1/health"
curl -s http://127.0.0.1/health || true
echo
