#!/bin/sh
set -e

if [ $# -eq 0 ]; then
    echo "[INFO] No command specified. Container running idle."
    exec tail -f /dev/null
fi

echo "[INFO] Ejecutando comando: $@"
exec "$@"
