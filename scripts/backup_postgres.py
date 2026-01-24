#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# backup_postgres.py
"""
Realiza un backup completo de la base de datos PostgreSQL dentro del contenedor monitoring-postgres
y envía notificación por correo usando smtp_relay.
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

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

DB_NAME = os.getenv("DB_NAME")
DB_CONTAINER_NAME = os.getenv("DB_CONTAINER_NAME")

# Ruta en host y contenedor
BACKUP_DIR_HOST = "/opt/monitoring/backups"
BACKUP_DIR_CONTAINER = "/backups"

timestamp = datetime.now().strftime("%Y%m%d%H%M")
# Nombre del archivo
BACKUP_FILE_NAME = f"{DB_NAME}-{timestamp}.backup"

# Archivos finales
BACKUP_FILE_HOST = f"{BACKUP_DIR_HOST}/{BACKUP_FILE_NAME}"
BACKUP_FILE_CONTAINER = f"{BACKUP_DIR_CONTAINER}/{BACKUP_FILE_NAME}"

os.makedirs(BACKUP_DIR_HOST, exist_ok=True)
log_info(f"[🚀]: Iniciando backup de {DB_NAME}...")

env = os.environ.copy()
env["DB_USER"] = DB_USER
env["DB_PASSWORD"] = DB_PASSWORD

# ------------------------------------------------------------
# Proceso principal
# ------------------------------------------------------------
try:
    subprocess.run(
        [
            "docker", "exec", "-i", DB_CONTAINER_NAME,
            "pg_dump", "-U", DB_USER, "-F", "c", "-b",
            "-v", "-f", BACKUP_FILE_CONTAINER, DB_NAME
        ],
        check=True,
        env=env
    )
    log_info(f"[✅]: Backup realizado con éxito: {BACKUP_FILE_HOST}")

# ------------------------------------------------------------
# Notificar por mail
# ------------------------------------------------------------
    send_email(
        subject=f"Backup exitoso de {DB_NAME}",
        html_content=f"Backup completado correctamente.<br>Ubicación: {BACKUP_FILE_HOST}"
             f" Para restaurar utilice: /opt/monitoring/scripts/backup_restore.py"
    )
except subprocess.CalledProcessError as e:
    log_info(f"[❌]: Error durante el backup de {DB_NAME}: {e}")
    send_email(
        subject=f"Error en backup de {DB_NAME}",
        html_content=f"Fallo en la creación del backup.<br>Detalles: {e}"
    )
    raise SystemExit(1)

# ------------------------------------------------------------
# Eliminar copias con más de 7 días
# ------------------------------------------------------------
try:
    subprocess.run(
        ["find", BACKUP_DIR_HOST, "-type", "f", "-name", "*.backup", "-mtime", "+7", "-delete"],
        check=False
    )
    log_info(f"[🧹]: Copias antiguas eliminadas (>7 días).")
except Exception as e:
    log_info(f"[⚠️]: Error limpiando backups antiguos: {e}")

log_info(f"[✅]: Proceso de backup finalizado correctamente.")
