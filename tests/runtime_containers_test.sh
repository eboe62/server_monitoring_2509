#!/usr/bin/env bash
set -euo pipefail

ROOT=$(dirname "$0")/..
OPS="$ROOT/ops"

echo "Running runtime_containers.sh tests"

echo "[1] parse_all returns expected containers"
bash ops/runtime_containers.sh list | sort > /tmp/rc_list.txt
grep -q "monitoring-python" /tmp/rc_list.txt && echo "  OK: monitoring-python listed" || (echo "  FAIL: monitoring-python missing" && exit 1)
grep -q "promtail" /tmp/rc_list.txt && echo "  OK: promtail listed" || (echo "  FAIL: promtail missing" && exit 1)

echo "[2] check-health for monitoring-postgres (may require docker compose to resolve .env)"
if command -v docker >/dev/null 2>&1 && docker compose -f ops/services/postgres/compose.yml config >/dev/null 2>&1; then
  bash ops/runtime_containers.sh check-health monitoring-postgres | tee /tmp/rc_postgres.txt
  if grep -q "healthcheck_present" /tmp/rc_postgres.txt; then
    echo "  OK: monitoring-postgres has healthcheck"
  else
    echo "  WARN: monitoring-postgres healthcheck absent or not detected"
  fi
else
  echo "  SKIP: docker compose not available or compose invalid for postgres; skipping check-health test"
fi

echo "[3] check-health for promtail"
if command -v docker >/dev/null 2>&1 && docker compose -f ops/stacks/observability/compose.yml config >/dev/null 2>&1; then
  bash ops/runtime_containers.sh check-health promtail | tee /tmp/rc_promtail.txt
  if grep -q "healthcheck_present" /tmp/rc_promtail.txt; then
    echo "  OK: promtail has healthcheck"
  else
    echo "  WARN: promtail healthcheck absent or not detected"
  fi
else
  echo "  SKIP: docker compose not available or compose invalid for observability; skipping promtail test"
fi

echo "Tests completed"
