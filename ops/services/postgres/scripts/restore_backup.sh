#!/usr/bin/env bash
# restore_backup.sh — restaura un backup en una BBDD paralela <db>_restored (B8, ADR-0009).
#
# Uso (desde el host):
#   make restore-backup                         # último backup -> monitoring_db_restored
#   make restore-backup FILE=<nombre.backup>    # un backup concreto de /backups
#   make restore-backup-clean                   # borra monitoring_db_restored
#
# Deja las dos bases de datos (original y restaurada) para compararlas, copiar lo que haga
# falta o sustituir una por otra a mano (pasos en el README, "Sustituir producción").
#
# Se ejecuta DENTRO de monitoring-cron (el Makefile lo pasa por stdin con docker exec):
#   - mismo pg_restore que el pg_dump que hizo el backup (misma versión de cliente);
#   - conecta a Postgres por TCP, igual que backup_postgres.py; sin socket de Docker (ADR-0018).
# Nunca modifica la base de datos de producción. Sin correo (cuota limitada).
set -euo pipefail

DB="${POSTGRES_NAME:-monitoring_db}"
DEST="${DB}_restored"
export PGHOST="${POSTGRES_HOST:-${POSTGRES_CONTAINER_NAME:-postgres}}"
export PGPORT="${POSTGRES_PORT:-5432}"
export PGUSER="${POSTGRES_USER:-postgres}"
PGPASSWORD="$(cat "${POSTGRES_PASSWORD_FILE:-/run/secrets/postgres_password}")"
export PGPASSWORD

if [ -n "${CLEAN:-}" ]; then
    dropdb --if-exists "$DEST"
    echo "[OK] $DEST eliminada (si existía)"
    exit 0
fi

if [ -n "${FILE:-}" ]; then
    BACKUP="/backups/$(basename "$FILE")"
    [ -f "$BACKUP" ] || { echo "[ERROR] No existe $BACKUP"; ls -1t /backups/*.backup 2>/dev/null | head -10; exit 1; }
else
    BACKUP="$(ls -1t /backups/*.backup 2>/dev/null | head -1 || true)"
    [ -n "$BACKUP" ] || { echo "[ERROR] No hay backups en /backups (volumen monitoring-backups)"; exit 1; }
fi
echo "[INFO] Backup: $(basename "$BACKUP") ($(du -h "$BACKUP" | cut -f1), $(date -r "$BACKUP" '+%Y-%m-%d %H:%M UTC'))"

dropdb --if-exists "$DEST" 2>/dev/null
createdb "$DEST"
# El cliente de monitoring-cron (pg_dump/pg_restore) es más nuevo que el servidor (Postgres 14):
# su cabecera incluye "SET transaction_timeout", que el 14 no conoce. Se genera el SQL, se quita
# esa línea y psql lo aplica parando en el primer error (ON_ERROR_STOP).
pg_restore --no-owner -f - "$BACKUP" \
    | sed '/^SET transaction_timeout/d' \
    | psql -q -v ON_ERROR_STOP=1 -d "$DEST" >/dev/null
echo "[OK] Restaurado en $DEST"

# Verificación: filas por tabla. Producción puede tener más (se han añadido después del backup).
count() { psql -tA -d "$1" -c "SELECT count(*) FROM public.\"$2\"" 2>/dev/null || echo "falta"; }
TABLES="$(psql -tA -d "$DB" -c "SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY 1")"
status=0
printf '%-28s %14s %14s\n' "Tabla" "$DB" "$DEST"
for t in $TABLES; do
    prod="$(count "$DB" "$t")"
    rest="$(count "$DEST" "$t")"
    mark=""
    if [ "$rest" = "falta" ]; then mark="  ⚠️ no está en el backup"; status=1; fi
    printf '%-28s %14s %14s%s\n' "$t" "$prod" "$rest" "$mark"
done

if [ "$status" -eq 0 ]; then
    echo "[OK] Restauración verificada. Están disponibles $DB y $DEST."
    echo "     Para borrar la copia: make restore-backup-clean"
else
    echo "[ERROR] Faltan tablas en $DEST: no la uses para sustituir producción"
fi
exit "$status"
