#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# backup_postgres.py
"""
Realiza un backup completo de la base de datos PostgreSQL dentro del contenedor monitoring-postgres
y envía notificación por correo usando smtp_relay.
"""

import sys, os, subprocess
MONITORING_ROOT = os.getenv("MONITORING_ROOT", os.getcwd())
sys.path.append(MONITORING_ROOT)

from datetime import datetime
from src.monitoring.common.config import log_info, send_email
from dotenv import load_dotenv

# ------------------------------------------------------------
# Configuración BBDD
# ------------------------------------------------------------
load_dotenv(os.getenv("SMTP_RELAY_ENV_PATH", "ops/services/smtp_relay/.env"))

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

POSTGRES_NAME = os.getenv("POSTGRES_NAME")
POSTGRES_CONTAINER_NAME = os.getenv("POSTGRES_CONTAINER_NAME")

# Ruta en host y contenedor
BACKUP_DIR_HOST = os.getenv("BACKUP_DIR_HOST", "ops/backups")
BACKUP_DIR_CONTAINER = "/backups"

timestamp = datetime.now().strftime("%Y%m%d%H%M")
# Nombre del archivo
BACKUP_FILE_NAME = f"{POSTGRES_NAME}-{timestamp}.backup"

# Archivos finales
BACKUP_FILE_HOST = f"{BACKUP_DIR_HOST}/{BACKUP_FILE_NAME}"
BACKUP_FILE_CONTAINER = f"{BACKUP_DIR_CONTAINER}/{BACKUP_FILE_NAME}"

os.makedirs(BACKUP_DIR_HOST, exist_ok=True)
log_info(f"[🚀]: Iniciando backup de {POSTGRES_NAME}...")

env = os.environ.copy()
env["POSTGRES_USER"] = POSTGRES_USER
env["POSTGRES_PASSWORD"] = POSTGRES_PASSWORD

# ------------------------------------------------------------
# Proceso principal
# ------------------------------------------------------------
try:
    subprocess.run(
        [
            "docker", "exec", "-i", POSTGRES_CONTAINER_NAME,
            "pg_dump", "-U", POSTGRES_USER, "-F", "c", "-b",
            "-v", "-f", BACKUP_FILE_CONTAINER, POSTGRES_NAME
        ],
        check=True,
        env=env
    )
    log_info(f"[✅]: Backup realizado con éxito: {BACKUP_FILE_HOST}")

# ------------------------------------------------------------
# Notificar por mail
# ------------------------------------------------------------
    send_email(
        subject=f"Backup exitoso de {POSTGRES_NAME}",
        html_content=f"Backup completado correctamente.<br>Ubicación: {BACKUP_FILE_HOST}"
             f" Para restaurar utilice: scripts/backup_restore.py"
    )
except subprocess.CalledProcessError as e:
    log_info(f"[❌]: Error durante el backup de {POSTGRES_NAME}: {e}")
    send_email(
        subject=f"Error en backup de {POSTGRES_NAME}",
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
