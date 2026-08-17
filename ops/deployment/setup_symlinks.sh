#!/bin/bash
set -e

DEPLOY_DIR="/opt/monitoring/ops/deployment"
RESOURCE_MONITOR_DIR="/opt/monitoring/src/resource_monitor"
SOURCES=(
    "$DEPLOY_DIR/configure_docker_limits.sh"
    "$RESOURCE_MONITOR_DIR/docker_resources.py"
    "$DEPLOY_DIR/docker_resources.sh"
)

for SRC in "${SOURCES[@]}"; do
    script="$(basename "$SRC")"
    DEST="/usr/local/bin/$script"

    if [ ! -f "$SRC" ]; then
        echo "[ERROR] Script no encontrado: $SRC"
        exit 1
    fi

    # Borrar enlace o archivo existente
    if [ -L "$DEST" ] || [ -f "$DEST" ]; then
        rm -f "$DEST"
    fi

    ln -s "$SRC" "$DEST"
    chmod +x "$SRC"
    echo "[OK] $DEST → $SRC"
done

