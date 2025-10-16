#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# backup_restore.py
"""
Restaura una base de datos PostgreSQL desde el último backup disponible.
"""
import sys, os
sys.path.append("/opt/monitoring")

import subprocess
import os
from datetime import datetime
from common.config import log_info, send_email
from dotenv import load_dotenv

# Configuración de la Base de Datos
load_dotenv("/opt/observability/smtp_relay/.env")

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_SOURCE = os.getenv("DB_NAME")
DB_DEST = os.getenv("DB_NAME" + "_restored")
DB_CONTAINER_NAME = os.getenv("DB_CONTAINER_NAME")

# Ruta en host y contenedor
BACKUP_DIR_HOST = "/var/lib/postgresql/data/backups"
BACKUP_CONTAINER_PATH = "/tmp/restore.backup"
BACKUP_SQL = "/tmp/restore.sql"

# Verificar si el archivo de backup está vacio o no existe
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

env = os.environ.copy()
env["DB_USER"] = DB_USER
env["DB_PASSWORD"] = DB_PASSWORD

def exec_docker_cmd(cmd):
    subprocess.run(["docker", "exec", "-i", DB_CONTAINER_NAME] + cmd, check=True, env=env)

try:
    # Copiar el backup al contenedor
    subprocess.run(["docker", "cp", BACKUP_FILE_HOST, f"{DB_CONTAINER_NAME}:{BACKUP_CONTAINER_PATH}"], check=True)

    # Eliminar DB destino si existe
    exec_docker_cmd([
        "psql", "-U", "postgres", "-d", "template1",
        "-c", f"DROP DATABASE IF EXISTS {DB_DEST};"
    ])

    # Crear la base de datos
    exec_docker_cmd([
        "psql", "-U", "postgres", "-d", "template1",
        "-c", f"CREATE DATABASE {DB_DEST};"
    ])

    # Convertir y restaurar
    exec_docker_cmd([
        "sh", "-c",
        f"pg_restore -U postgres -f {BACKUP_SQL} -F c {BACKUP_CONTAINER_PATH}"
    ])
    exec_docker_cmd([
        "psql", "-U", "postgres", "-d", DB_DEST, "-f", BACKUP_SQL
    ])

    log_info(f"[✅]: Restauración completada con éxito en {DB_DEST}")
    send_email(
        subject=f"Restauración completada ({DB_DEST})",
        html_content=f"Se ha restaurado correctamente la base de datos desde {latest_backup}."
    )


except subprocess.CalledProcessError as e:
    log_info(f"[❌]: Error en restauración: {e}")
    send_email(
        subject=f"Error restaurando {DB_DEST}",
        html_content=f"Error durante la restauración: {e}"
    )
    raise SystemExit(1)

log_info(f"[🎉]: Proceso de restauración finalizado correctamente.")
