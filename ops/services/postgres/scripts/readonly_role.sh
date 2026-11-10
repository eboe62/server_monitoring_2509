#!/usr/bin/env bash
# readonly_role.sh — usuario de solo lectura para el análisis de datos (DBeaver), B9-1d, ADR-0014.
#
# Uso (desde el host; lo lanza make deploy):
#   make postgres-readonly-role
#
# Se ejecuta DENTRO de monitoring-postgres (el Makefile lo pasa por stdin con docker exec) y
# conecta por el socket local como el dueño de la BBDD. Idempotente: crea el rol si no existe y
# aplica siempre la contraseña del fichero, así que cambiarla es editar el fichero y redesplegar.
#   - Contraseña: /run/secrets/postgres_ro_password (host: ops/services/postgres/secrets/).
#     Sin el fichero, avisa y no hace nada.
#   - La contraseña entra por stdin a psql: nunca en la línea de comandos ni en la salida.
#   - pg_read_all_data (PG14): lectura de todas las tablas, también las futuras y <db>_restored.
#   - default_transaction_read_only y máximo 3 conexiones.
set -eu

ROLE="${POSTGRES_RO_USER:-monitoring_ro}"
PW_FILE=/run/secrets/postgres_ro_password

if [ ! -s "$PW_FILE" ]; then
    echo "[WARN] ${PW_FILE} no existe o está vacío: no se crea el usuario de solo lectura ${ROLE}"
    exit 0
fi

PW=$(cat "$PW_FILE")
case "$PW" in
    *"'"*|*"\\"*) echo "[ERROR] la contraseña de ${ROLE} no puede contener comillas simples ni barras invertidas"; exit 1 ;;
esac

# Espera breve: make deploy acaba de recrear el contenedor
for _ in $(seq 1 30); do
    pg_isready -q -U "$POSTGRES_USER" -d "$POSTGRES_DB" && break
    sleep 2
done

psql -q -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" <<SQL
SET client_min_messages = warning;
\set role '${ROLE}'
\set pw '${PW}'
SELECT format('CREATE ROLE %I LOGIN', :'role')
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = :'role') \gexec
SELECT format('ALTER ROLE %I WITH LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE CONNECTION LIMIT 3 PASSWORD %L', :'role', :'pw') \gexec
SELECT format('ALTER ROLE %I SET default_transaction_read_only = on', :'role') \gexec
SELECT format('GRANT pg_read_all_data TO %I', :'role') \gexec
SQL

# En PG14 cualquier usuario puede crear tablas en el esquema public (PG15 ya lo quita): sin esto,
# el usuario de solo lectura podría desactivar read_only y crear tablas. El dueño no se ve afectado.
for db in $(psql -tA -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT datname FROM pg_database WHERE NOT datistemplate"); do
    psql -q -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$db" -c "REVOKE CREATE ON SCHEMA public FROM PUBLIC"
done

echo "[OK] usuario de solo lectura ${ROLE} listo"
