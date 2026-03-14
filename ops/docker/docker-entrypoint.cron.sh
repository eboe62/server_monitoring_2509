#!/bin/sh
set -e

CRONFILE="/opt/monitoring/ops/cron/monitoring.cron"

if [ $# -gt 0 ]; then
    echo "[INFO] Ejecutando comando manual: $@"
    exec "$@"
fi

echo "[INFO] Arrancando supercronic con cronfile: $CRONFILE"
exec /usr/local/bin/supercronic "$CRONFILE"
