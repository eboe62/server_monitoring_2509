#!/bin/sh
set -e

if [ $# -eq 0 ]; then
    echo "[INFO] No command specified. Container running idle (encendido pero ocioso para facilitar supervisión de logs)."
    exec tail -f /dev/null
fi

echo "[INFO] Ejecutando comando manual: $@"
exec "$@"
