#!/bin/sh
set -e

CRONFILE="/opt/monitoring/ops/stacks/cron/monitoring.cron"
LOG_DIR="/opt/monitoring/logs"

# Aseguramos logs en runtime, SOLO crear logs si no existen (sin romper runtime)
# - NO usar chown (no somos root)
# - Crear solo si no existe
# - No fallar nunca (CI safe)

if [ ! -d "$LOG_DIR" ]; then
    mkdir -p "$LOG_DIR" || true
fi

# Exec manual
if [ $# -gt 0 ]; then
    echo "[INFO] Ejecutando comando manual: $@"
    exec "$@"
fi

echo "[INFO] Arrancando supercronic con cronfile: $CRONFILE"

# Validación cronfile, n matar contenedor si falta cronfile
if [ ! -f "$CRONFILE" ]; then
    echo "[ERROR] Cronfile no encontrado: $CRONFILE"
    echo "[WARN] entrando en modo idle (CI safe)"
    exec tail -f /dev/null
fi

exec /usr/local/bin/supercronic "$CRONFILE"
