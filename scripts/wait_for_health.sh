#!/usr/bin/env sh

# ----------------------------------------
# wait_for_health.sh
# ----------------------------------------
# Uso:
#   wait_for_health.sh <container> <mode> <timeout>
#
# mode:
#   strict  -> solo healthy
#   ci      -> healthy o starting
#
# ejemplo:
#   ./wait_for_health.sh monitoring-python strict 90
#   ./wait_for_health.sh monitoring-python ci 60
# ----------------------------------------

CONTAINER="$1"
MODE="$2"
TIMEOUT="${3:-60}"

if [ -z "$CONTAINER" ] || [ -z "$MODE" ]; then
    echo "[ERROR] uso: wait_for_health.sh <container> <mode> [timeout]"
    exit 1
fi

echo "[INFO] container=$CONTAINER mode=$MODE timeout=${TIMEOUT}s"

START_TIME=$(date +%s)

while true; do
    STATUS=$(docker inspect "$CONTAINER" --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' 2>/dev/null)

    NOW=$(date +%s)
    ELAPSED=$((NOW - START_TIME))

    echo "[DEBUG] status=$STATUS elapsed=${ELAPSED}s"

    if [ "$MODE" = "ci" ]; then
        if [ "$STATUS" = "healthy" ] || [ "$STATUS" = "starting" ]; then
            echo "[OK] estado válido en CI: $STATUS"
            exit 0
        fi
    else
        if [ "$STATUS" = "healthy" ]; then
            echo "[OK] estado healthy"
            exit 0
        fi
    fi

    if [ "$ELAPSED" -ge "$TIMEOUT" ]; then
        echo "[FAIL] timeout alcanzado (status=$STATUS)"
        docker inspect "$CONTAINER" --format='State={{.State.Status}} Health={{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}'
        exit 1
    fi

    sleep 2
done
