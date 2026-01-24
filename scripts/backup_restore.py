#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Restaura una base de datos PostgreSQL desde el último backup disponible.
El script se ejecuta desde monitoring-python, pero los comandos SQL
y la restauración se realizan dentro de monitoring-postgres.
Usa en el host el comando: bash /opt/monitoring/scripts/backup_restore.sh
Comprueba con el comando: cat /var/log/backup_restore.log
o el comando de Makefile:
make restore-backup
"""

import sys, os, subprocess
sys.path.append("/opt/monitoring")

from datetime import datetime
from src.monitoring.common.config import log_info, send_email
from dotenv import load_dotenv

# ------------------------------------------------------------
# Configuración BBDD
# ------------------------------------------------------------
load_dotenv("/opt/monitoring/smtp_relay/.env")

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "monitoring_db")
DB_DEST = f"{DB_NAME}_restored"
DB_CONTAINER_NAME = os.getenv("DB_CONTAINER_NAME", "monitoring-postgres")

BACKUP_DIR_HOST = "/opt/monitoring/backups"
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
    full_cmd = ["docker", "exec", "-i", DB_CONTAINER_NAME] + cmd
    subprocess.run(full_cmd, check=True)

# ------------------------------------------------------------
# Proceso principal
# ------------------------------------------------------------
try:
    log_info(f"[🚀]: Iniciando restauración de {DB_NAME} dentro de {DB_CONTAINER_NAME}...")

    # Copiar backup al contenedor de Postgres
    subprocess.run(
        ["docker", "cp", BACKUP_FILE_HOST, f"{DB_CONTAINER_NAME}:{BACKUP_CONTAINER_PATH}"],
        check=True
    )

    # Eliminar DB destino si existe
    exec_in_postgres([
        "psql", "-U", DB_USER, "-d", "template1",
        "-c", f"DROP DATABASE IF EXISTS {DB_DEST};"
    ])
    log_info(f"[ℹ️]: Base de datos {DB_DEST} eliminada si existía.")

    # Crear DB destino
    exec_in_postgres([
        "psql", "-U", DB_USER, "-d", "template1",
        "-c", f"CREATE DATABASE {DB_DEST};"
    ])
    log_info(f"[✅]: Base de datos {DB_DEST} creada.")

    # Restaurar dentro del contenedor
    exec_in_postgres([
        "sh", "-c",
        f"pg_restore -U {DB_USER} -F c -f {BACKUP_SQL} {BACKUP_CONTAINER_PATH}"
    ])
    exec_in_postgres([
        "psql", "-U", DB_USER, "-d", DB_DEST, "-f", BACKUP_SQL
    ])
    log_info(f"[✅]: Restauración completada correctamente en {DB_DEST}.")

# ------------------------------------------------------------
# Notificar por mail
# ------------------------------------------------------------
    send_email(
        subject=f"Restauración completada ({DB_DEST})",
        html_content=f"Se ha restaurado correctamente la base de datos desde {latest_backup}."
    )

except subprocess.CalledProcessError as e:
    log_info(f"[❌]: Error en restauración: {e}")
    send_email(
        subject=f"Error restaurando {DB_DEST}",
        html_content=f"Ocurrió un error durante la restauración: {e}"
    )
    raise SystemExit(1)

log_info(f"[🎉]: Proceso de restauración finalizado correctamente.")
