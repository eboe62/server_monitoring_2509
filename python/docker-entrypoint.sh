#!/bin/sh
set -e
if [ -z "$1" ]; then
    echo "[INFO] No se especificó script. Arrancando en modo interactivo (bash)."
    exec bash -c "tail -f /dev/null"
else
    echo "[INFO] Ejecutando script: $@"
    exec python3 "$@"
fi

