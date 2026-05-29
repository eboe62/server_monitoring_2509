#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Restaura una base de datos PostgreSQL desde el último backup disponible.
El script se ejecuta desde monitoring-python, pero los comandos SQL
y la restauración se realizan dentro de monitoring-postgres.
Usa en el host el comando: bash scripts/backup_restore.sh
Comprueba con el comando: cat /var/log/backup_restore.log
o el comando de Makefile:
make restore-backup
"""

import sys, os, subprocess

# Ensure `src` is on sys.path so `from monitoring...` imports work whether the
# script runs in a container, via cron, or on the host. Honor MONITORING_ROOT
# env var if provided; otherwise compute project root relative to this file.
MONITORING_ROOT = os.getenv("MONITORING_ROOT")
if not MONITORING_ROOT:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    MONITORING_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
SRC_PATH = os.path.join(MONITORING_ROOT, "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from datetime import datetime
from monitoring.common.config import send_email
from dotenv import load_dotenv
from monitoring.common.secrets import load_secret
from monitoring.common.utils import log_info

# ------------------------------------------------------------
# Configuración BBDD
# ------------------------------------------------------------
load_dotenv(os.getenv("SMTP_RELAY_ENV_PATH", "ops/services/smtp_relay/.env"))

POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
try:
    POSTGRES_PASSWORD = load_secret('POSTGRES_PASSWORD_FILE', 'POSTGRES_PASSWORD')
except Exception as e:
    log_info(f"[❌]: Error loading Postgres secret: {e}")
    raise
POSTGRES_NAME = os.getenv("POSTGRES_NAME", "monitoring_db")
POSTGRES_DEST = f"{POSTGRES_NAME}_restored"
POSTGRES_CONTAINER_NAME = os.getenv("POSTGRES_CONTAINER_NAME", "monitoring-postgres")

BACKUP_DIR_HOST = os.getenv("BACKUP_DIR_HOST", "/opt/monitoring/ops/backups")
BACKUP_CONTAINER_PATH = "/tmp/restore.backup"
BACKUP_SQL = "/tmp/restore.sql"

# ------------------------------------------------------------
# Seleccionar backup más reciente
# ------------------------------------------------------------
try:
    backups = sorted(
        [f for f in os.listdir(BACKUP_DIR_HOST) if f.endswith(".backup")],
        reverse=True
    )
    if not backups:
        raise FileNotFoundError("No se encontró ningún archivo de backup.")
    latest_backup = backups[0]
    BACKUP_FILE_HOST = os.path.join(BACKUP_DIR_HOST, latest_backup)
    log_info(f"[✅]: Backup encontrado: {BACKUP_FILE_HOST}")
except Exception as e:
    log_info(f"[❌]: Error buscando backup: {e}")
    raise SystemExit(1)

# ------------------------------------------------------------
# Función auxiliar
# ------------------------------------------------------------
def exec_in_postgres(cmd):
    """Ejecuta comandos dentro del contenedor de PostgreSQL"""
    full_cmd = ["docker", "exec", "-i", POSTGRES_CONTAINER_NAME] + cmd
    subprocess.run(full_cmd, check=True)

# ------------------------------------------------------------
# Proceso principal
# ------------------------------------------------------------
try:
    log_info(f"[INFO] Iniciando restauración de {POSTGRES_NAME} dentro de {POSTGRES_CONTAINER_NAME}...")

    # Copiar backup al contenedor de Postgres
    subprocess.run(
        ["docker", "cp", BACKUP_FILE_HOST, f"{POSTGRES_CONTAINER_NAME}:{BACKUP_CONTAINER_PATH}"],
        check=True
    )

    # Eliminar DB destino si existe
    exec_in_postgres([
        "psql", "-U", POSTGRES_USER, "-d", "template1",
        "-c", f"DROP DATABASE IF EXISTS {POSTGRES_DEST};"
    ])
    log_info(f"[INFO] Base de datos {POSTGRES_DEST} eliminada si existía.")

    # Crear DB destino
    exec_in_postgres([
        "psql", "-U", POSTGRES_USER, "-d", "template1",
        "-c", f"CREATE DATABASE {POSTGRES_DEST};"
    ])
    log_info(f"[OK] Base de datos {POSTGRES_DEST} creada.")

    # Restaurar dentro del contenedor
    exec_in_postgres([
        "sh", "-c",
        f"pg_restore -U {POSTGRES_USER} -F c -f {BACKUP_SQL} {BACKUP_CONTAINER_PATH}"
    ])
    exec_in_postgres([
        "psql", "-U", POSTGRES_USER, "-d", POSTGRES_DEST, "-f", BACKUP_SQL
    ])
    log_info(f"[OK] Restauración completada correctamente en {POSTGRES_DEST}.")

# ------------------------------------------------------------
# Notificar por mail
# ------------------------------------------------------------
    send_email(
        subject=f"Restauración completada ({POSTGRES_DEST})",
        html_content=f"Se ha restaurado correctamente la base de datos desde {latest_backup}."
    )

except subprocess.CalledProcessError as e:
    log_info(f"[ERROR] Error en restauración: {e}")
    send_email(
        subject=f"Error restaurando {POSTGRES_DEST}",
        html_content=f"Ocurrió un error durante la restauración: {e}"
    )
    raise SystemExit(1)

log_info(f"[OK] Proceso de restauración finalizado correctamente.")
