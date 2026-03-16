#!/bin/sh
set -e

CRONFILE="/opt/monitoring/ops/stacks/cron/monitoring.cron"

if [ $# -gt 0 ]; then
    echo "[INFO] Ejecutando comando manual: $@"
    exec "$@"
fi

echo "[INFO] Arrancando supercronic con cronfile: $CRONFILE"

if [ ! -f "$CRONFILE" ]; then
    echo "[ERROR] Cronfile no encontrado: $CRONFILE"
    exit 1
fi

exec /usr/local/bin/supercronic "$CRONFILE"
