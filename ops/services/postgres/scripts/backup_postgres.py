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
from monitoring.common.config import send_email
from dotenv import load_dotenv
from monitoring.common.secrets import load_secret
from monitoring.common.utils import log_info

# ------------------------------------------------------------
# Configuración BBDD
# ------------------------------------------------------------
load_dotenv(os.getenv("SMTP_RELAY_ENV_PATH", "ops/services/smtp_relay/.env"))

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = None
try:
    POSTGRES_PASSWORD = load_secret('POSTGRES_PASSWORD_FILE', 'POSTGRES_PASSWORD')
except Exception as e:
    log_info(f"[ERROR] Error al cargar secreto Postgres: {e}")
    raise

POSTGRES_NAME = os.getenv("POSTGRES_NAME")
POSTGRES_CONTAINER_NAME = os.getenv("POSTGRES_CONTAINER_NAME")

# Ruta en contenedor donde se depositarán los backups (debe mapearse a un volume)
BACKUP_DIR_CONTAINER = os.getenv("BACKUP_DIR_CONTAINER", "/backups")

timestamp = datetime.now().strftime("%Y%m%d%H%M")
BACKUP_FILE_NAME = f"{POSTGRES_NAME}-{timestamp}.backup"
BACKUP_FILE_CONTAINER = f"{BACKUP_DIR_CONTAINER}/{BACKUP_FILE_NAME}"

# Rutas en host (si se ejecuta desde el host, pueden estar definidas en env);
# por defecto se usan las rutas de contenedor para evitar NameError en entornos aislados
BACKUP_DIR_HOST = os.getenv("BACKUP_DIR_HOST", BACKUP_DIR_CONTAINER)
BACKUP_FILE_HOST = os.getenv("BACKUP_FILE_HOST", BACKUP_FILE_CONTAINER)

log_info(f"[INFO] Iniciando backup de {POSTGRES_NAME} (destino: {BACKUP_FILE_CONTAINER})...")

# Determinar host/puerto para conectar a Postgres por TCP
PG_HOST = os.getenv("POSTGRES_HOST") or os.getenv("POSTGRES_CONTAINER_NAME") or "postgres"
PG_PORT = os.getenv("POSTGRES_PORT", "5432")

env = os.environ.copy()
if POSTGRES_USER:
    env["PGUSER"] = POSTGRES_USER
if POSTGRES_PASSWORD:
    env["PGPASSWORD"] = POSTGRES_PASSWORD

os.makedirs(BACKUP_DIR_CONTAINER, exist_ok=True)

try:
    cmd = [
        "pg_dump",
        "-h", PG_HOST,
        "-p", str(PG_PORT),
        "-U", POSTGRES_USER,
        "-F", "c",
        "-b",
        "-v",
        "-f", BACKUP_FILE_CONTAINER,
        POSTGRES_NAME,
    ]

    subprocess.run(cmd, check=True, env=env)
    log_info(f"[OK] Backup realizado con éxito: {BACKUP_FILE_CONTAINER}")

# ------------------------------------------------------------
# Notificar por mail
# ------------------------------------------------------------
    send_email(
        subject=f"Backup exitoso de {POSTGRES_NAME}",
        html_content=f"Backup completado correctamente.<br>Ubicación: {BACKUP_FILE_HOST}"
             f" Para restaurar utilice: scripts/backup_restore.py"
    )
except subprocess.CalledProcessError as e:
    log_info(f"[ERROR] Error durante el backup de {POSTGRES_NAME}: {e}")
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
    log_info(f"[OK] Copias antiguas eliminadas (>7 días).")
except Exception as e:
    log_info(f"[WARN] Error limpiando backups antiguos: {e}")

log_info(f"[OK] Proceso de backup finalizado correctamente.")
