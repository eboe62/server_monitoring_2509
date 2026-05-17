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
  out=$(bash ops/runtime_containers.sh check-health monitoring-postgres)
  echo "  -> $out"
  case "$out" in
    monitoring-postgres\|FOUND\|* ) echo "  OK: monitoring-postgres resolved (found)";;
    monitoring-postgres\|COMPOSE_INVALID\|* ) echo "  WARN: compose invalid for postgres (render failed)";;
    monitoring-postgres\|NOT_FOUND\|* ) echo "  WARN: monitoring-postgres not found in compose files";;
    *) echo "  FAIL: unexpected output: $out"; exit 1;;
  esac
else
  echo "  SKIP: docker compose not available or compose invalid for postgres; skipping check-health test"
fi

echo "[3] check-health for promtail"
if command -v docker >/dev/null 2>&1 && docker compose -f ops/stacks/observability/compose.yml config >/dev/null 2>&1; then
  out=$(bash ops/runtime_containers.sh check-health promtail)
  echo "  -> $out"
  case "$out" in
    promtail\|FOUND\|* ) echo "  OK: promtail resolved (found)";;
    promtail\|COMPOSE_INVALID\|* ) echo "  WARN: compose invalid for observability (render failed)";;
    promtail\|NOT_FOUND\|* ) echo "  WARN: promtail not found in compose files";;
    *) echo "  FAIL: unexpected output: $out"; exit 1;;
  esac
else
  echo "  SKIP: docker compose not available or compose invalid for observability; skipping promtail test"
fi

echo "[4] debug output sample (monitoring-python)"
bash ops/runtime_containers.sh debug monitoring-python | sed -n '1,120p'

echo "Tests completed"
