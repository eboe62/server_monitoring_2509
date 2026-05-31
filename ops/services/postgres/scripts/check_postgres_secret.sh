#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="ops/services/postgres"
SECRET_DIR="$BASE_DIR/secrets"
SECRET_FILE="$SECRET_DIR/postgres_password"
ENV_FILE="$BASE_DIR/.env"
TEMPLATE_FILE="$BASE_DIR/.env.template"
COMPOSE_FILE="$BASE_DIR/compose.yml"

ERR=0

echo "[INFO] Comprobando secreto Postgres: $SECRET_FILE"

if [ ! -d "$SECRET_DIR" ]; then
  echo "[ERROR] Directorio de secrets ausente: $SECRET_DIR"
  ERR=1
fi

if [ ! -f "$SECRET_FILE" ]; then
  echo "[ERROR] Fichero secreto ausente: $SECRET_FILE"
  ERR=1
else
  if [ ! -s "$SECRET_FILE" ]; then
    echo "[ERROR] Fichero secreto vacío: $SECRET_FILE"
    ERR=1
  fi

  # File perms
  PERMS_FILE=$(stat -c "%a" "$SECRET_FILE" || echo 0)
    if [ "$PERMS_FILE" -gt 600 ]; then
    echo "[WARN] Permisos del fichero secreto: $PERMS_FILE; se recomienda 600"
  else
    echo "[OK] Permisos del fichero secreto: $PERMS_FILE"
  fi
fi

# Directory perms
if [ -d "$SECRET_DIR" ]; then
  PERMS_DIR=$(stat -c "%a" "$SECRET_DIR" || echo 0)
  if [ "$PERMS_DIR" -gt 700 ]; then
    echo "[WARN] Permisos del directorio de secrets: $PERMS_DIR; se recomienda 700"
  else
    echo "[OK] Permisos del directorio de secrets: $PERMS_DIR"
  fi
fi

# Owner checks
if [ -f "$SECRET_FILE" ]; then
  OWNER=$(stat -c "%U" "$SECRET_FILE" || echo "")
  if [ -z "$OWNER" ]; then
    echo "[WARN] No se pudo determinar el propietario de $SECRET_FILE"
  else
    echo "[OK] Propietario del fichero secreto: $OWNER"
    if [ "$OWNER" = "nobody" ]; then
      echo "[ERROR] El propietario del secreto es 'nobody', inseguro"
      ERR=1
    fi
    if [ "$OWNER" = "root" ]; then
      echo "[WARN] El propietario del secreto es 'root' - considere usar un usuario menos privilegiado"
    fi
  fi
fi

# Ensure no POSTGRES_PASSWORD hardcoded in env/template/compose
for f in "$ENV_FILE" "$TEMPLATE_FILE" "$COMPOSE_FILE"; do
  if [ -f "$f" ]; then
    if grep -nE "^[[:space:]]*POSTGRES_PASSWORD[[:space:]]*=" "$f" >/dev/null 2>&1; then
      echo "[ERROR] Se ha encontrado POSTGRES_PASSWORD hardcodeado en $f"
      ERR=1
    else
      echo "[OK] No se ha encontrado POSTGRES_PASSWORD hardcodeado en $f"
    fi
  else
    echo "[WARN] Fichero no presente (saltando check): $f"
  fi
done

# Ensure compose contains POSTGRES_PASSWORD_FILE and secret mount
if [ -f "$COMPOSE_FILE" ]; then
  if grep -q "POSTGRES_PASSWORD_FILE" "$COMPOSE_FILE"; then
    echo "[OK] compose contiene POSTGRES_PASSWORD_FILE"
  else
    echo "[ERROR] compose no contiene POSTGRES_PASSWORD_FILE en $COMPOSE_FILE"
    ERR=1
  fi

  # Check mount mapping
  if grep -q "./secrets/postgres_password" "$COMPOSE_FILE" && grep -q "/run/secrets/postgres_password" "$COMPOSE_FILE"; then
    echo "[OK] compose monta el secreto en /run/secrets/postgres_password"
  else
    echo "[ERROR] compose no monta ./secrets/postgres_password en /run/secrets/postgres_password:ro"
    ERR=1
  fi

  # Check for manual wrapper entrypoint patterns
  if grep -nE "entrypoint:|export POSTGRES_PASSWORD|cat .*postgres_password" "$COMPOSE_FILE" >/dev/null 2>&1; then
    echo "[ERROR] compose contiene entrypoint sospechoso o export manual del secreto (wrapper). Elimínelo."
    ERR=1
  else
    echo "[OK] No se ha detectado entrypoint wrapper en compose"
  fi
else
  echo "[ERROR] fichero compose no encontrado: $COMPOSE_FILE"
  ERR=1
fi

if [ "$ERR" -ne 0 ]; then
  echo "[ERROR] La validación del secreto Postgres ha fallado"
  exit 1
fi

echo "[OK] Comprobaciones del secreto PostgreSQL superadas"
exit 0
