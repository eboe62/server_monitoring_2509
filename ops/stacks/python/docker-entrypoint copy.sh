#!/bin/sh
set -e

# --------------------------------------------------
# Preparar secrets accesibles para appuser
# --------------------------------------------------
if [ -d "/run/secrets" ]; then
    echo "[INFO] Copiando secrets para appuser..."
    mkdir -p /run/secrets-copy
    cp -r /run/secrets/* /run/secrets-copy/ 2>/dev/null || true
    chown -R appuser:appuser /run/secrets-copy
    chmod -R 600 /run/secrets-copy || true
fi

# --------------------------------------------------
# Si se pasa comando → ejecutar como appuser
# --------------------------------------------------
if [ "$#" -gt 0 ]; then
    exec su appuser -c "$@"
fi

# --------------------------------------------------
# Modo idle (contenedor vivo para docker exec)
# --------------------------------------------------
echo "[INFO] monitoring-python en modo idle (listo para docker exec)"
exec tail -f /dev/null
