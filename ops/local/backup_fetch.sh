#!/usr/bin/env bash
# backup_fetch.sh — custodia local del último backup de PRO (B8, ADR-0009).
#
# Se ejecuta en el EQUIPO DEL OPERADOR (WSL), nunca en el servidor:
#   make backup-fetch
#
# 1. Pregunta a PRO por SSH cuál es el último backup y su sha256.
# 2. Si no está ya en local, lo descarga a LOCAL_BACKUP_DIR con el mismo nombre.
# 3. Comprueba el sha256: si no coincide, borra la descarga y falla.
# 4. Rotación local: conserva los KEEP más recientes (monitoring_db-*.backup de esa carpeta,
#    sin entrar en subcarpetas) y borra el resto, mostrando cuáles.
#
# Conexión: el alias PRO_SSH de ~/.ssh/config de Windows (ssh.exe), sin IPs en el repo.
set -euo pipefail

PRO_SSH="${PRO_SSH:-vps-server}"
SSH="${SSH:-ssh.exe}"
LOCAL_BACKUP_DIR="${LOCAL_BACKUP_DIR:-/mnt/d/DataBase/BackUps}"
KEEP="${KEEP:-2}"
PATTERN="monitoring_db-*.backup"

[ -d "$LOCAL_BACKUP_DIR" ] || { echo "[ERROR] No existe $LOCAL_BACKUP_DIR"; exit 1; }

# 1. Último backup en PRO: "sha256  /backups/<nombre>"
# (comando remoto sin comillas dobles: ssh.exe recibe los argumentos a través de Windows)
REMOTE="$($SSH "$PRO_SSH" "docker exec monitoring-cron sh -c 'sha256sum \$(ls -1t /backups/$PATTERN | head -1)'" | tr -d '\r')"
SHA="${REMOTE%% *}"
NAME="$(basename "${REMOTE##* }")"
case "$NAME" in
    monitoring_db-*.backup) ;;
    *) echo "[ERROR] No hay backups en PRO (/backups de monitoring-cron)"; exit 1 ;;
esac
DEST="$LOCAL_BACKUP_DIR/$NAME"
echo "[INFO] Último backup en PRO: $NAME"
trap 'rm -f "$DEST.part"' EXIT   # una descarga cortada no deja restos

# 2-3. Descarga y verificación
if [ -f "$DEST" ] && [ "$(sha256sum "$DEST" | cut -d' ' -f1)" = "$SHA" ]; then
    echo "[OK] Ya estaba en local: $DEST"
else
    $SSH "$PRO_SSH" "docker exec monitoring-cron cat /backups/$NAME" > "$DEST.part"
    if [ "$(sha256sum "$DEST.part" | cut -d' ' -f1)" != "$SHA" ]; then
        rm -f "$DEST.part"
        echo "[ERROR] sha256 distinto: descarga descartada"
        exit 1
    fi
    mv "$DEST.part" "$DEST"
    echo "[OK] Descargado y verificado (sha256): $DEST ($(du -h "$DEST" | cut -f1))"
fi

# 4. Rotación local (los nombres llevan la fecha: orden alfabético = orden cronológico)
mapfile -t ALL < <(cd "$LOCAL_BACKUP_DIR" && ls -1 $PATTERN 2>/dev/null | sort)
if [ "${#ALL[@]}" -gt "$KEEP" ]; then
    for old in "${ALL[@]:0:${#ALL[@]}-KEEP}"; do
        rm -f "$LOCAL_BACKUP_DIR/$old"
        echo "[ROTACIÓN] Eliminado: $old"
    done
fi
echo "[OK] En local quedan:"
(cd "$LOCAL_BACKUP_DIR" && ls -la $PATTERN)
