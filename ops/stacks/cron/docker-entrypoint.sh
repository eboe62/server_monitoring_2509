#!/bin/sh
set -e

CRONFILE="/opt/monitoring/ops/stacks/cron/monitoring.cron"

if [ $# -gt 0 ]; then
    echo "[INFO] Ejecutando comando manual: $@"
    exec "$@"
fi

echo "[INFO] Arrancando supercronic con cronfile: $CRONFILE"

# No matar contenedor si falta cronfile
if [ ! -f "$CRONFILE" ]; then
    echo "[ERROR] Cronfile no encontrado: $CRONFILE"
    echo "[WARN] entrando en modo idle (CI safe)"
    exec tail -f /dev/null
fi

exec /usr/local/bin/supercronic "$CRONFILE"
