#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# backup_postgres.py
"""
Realiza un backup completo de la base de datos PostgreSQL dentro del contenedor monitoring-postgres
y envía notificación por correo usando smtp_relay solo si falla.
"""

import sys, os, subprocess
MONITORING_ROOT = os.getenv("MONITORING_ROOT", os.getcwd())
sys.path.append(MONITORING_ROOT)

from datetime import datetime
from src.monitoring.common.config import log_info, send_email
from dotenv import load_dotenv
from monitoring.common.secrets import load_secret

# ----------------------------------------
# Configuración BBDD
# ----------------------------------------
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
# Retención: backup semanal -> 28 días conserva las 4 últimas copias
RETENTION_DAYS = int(os.getenv("BACKUP_RETENTION_DAYS", "28"))

timestamp = datetime.now().strftime("%Y%m%d%H%M")
BACKUP_FILE_NAME = f"{POSTGRES_NAME}-{timestamp}.backup"
BACKUP_FILE_CONTAINER = f"{BACKUP_DIR_CONTAINER}/{BACKUP_FILE_NAME}"

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

    # Sin correo en caso de éxito (cuota de correo limitada): solo se notifica el fallo.
    # Prueba de restauración: make restore-backup (desde el host, ADR-0009)
except subprocess.CalledProcessError as e:
    log_info(f"[ERROR] Error durante el backup de {POSTGRES_NAME}: {e}")
    send_email(
        subject=f"Error en backup de {POSTGRES_NAME}",
        html_content=f"Fallo en la creación del backup.<br>Detalles: {e}"
    )
    raise SystemExit(1)

# ----------------------------------------
# Eliminar copias más antiguas que RETENTION_DAYS
# ----------------------------------------
# Se limpia el directorio del contenedor (/backups), que es donde escribe pg_dump.
try:
    result = subprocess.run(
        ["find", BACKUP_DIR_CONTAINER, "-type", "f", "-name", "*.backup", "-mtime", f"+{RETENTION_DAYS}", "-print", "-delete"],
        check=True, capture_output=True, text=True
    )
    removed = [l for l in result.stdout.splitlines() if l]
    log_info(f"[OK] Copias antiguas eliminadas (>{RETENTION_DAYS} días): {len(removed)}")
except subprocess.CalledProcessError as e:
    log_info(f"[WARN] Error limpiando backups antiguos: {e.stderr.strip()}")
except Exception as e:
    log_info(f"[WARN] Error limpiando backups antiguos: {e}")

log_info(f"[OK] Proceso de backup finalizado correctamente.")
