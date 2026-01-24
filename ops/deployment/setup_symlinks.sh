#!/bin/bash
set -e

BASE_DIR="/opt/monitoring/resource_monitor"
SCRIPTS=(
    "configure_docker_limits.sh"
    "docker_resources.py"
    "docker_resources.sh"
)

for script in "${SCRIPTS[@]}"; do
    SRC="$BASE_DIR/$script"
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

