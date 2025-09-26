#!/usr/bin/env python3
# config.py
import os
import smtplib
from dotenv import load_dotenv
import psycopg2
from email.mime.text import MIMEText
from email.utils import formataddr
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Cargar variables desde .env
load_dotenv("/opt/monitoring/smtp_relay/.env")

# ------------------------------------------------------------------
# CONFIG SMTP / EMAIL
# ------------------------------------------------------------------
# Configuración SMTP
# Excluimos las credenciales SMTP (SMTP_USER, SMTP_PASS) cuando usemos el servicio SMTP
SMTP_SERVER = os.getenv("SMTP_SERVER", "127.0.0.1")     # smtp.postmarkapp.com (servicio host) ó localhost (servicio contenedor)
SMTP_PORT = int(os.getenv("SMTP_PORT", "2526"))         # 2525 (servicio host) ó 2526 (servicio contenedor)
with open("/opt/monitoring/smtp_relay/secrets/smtp_user") as f:
    SMTP_USER = f.read().strip()
with open("/opt/monitoring/smtp_relay/secrets/smtp_pass") as f:
    SMTP_PASS = f.read().strip()

# Configuración de correo desde .env
# cuando usemos el contenedor smtp-relay. Este contenedor actúa como relay local y no necesita login TLS.
EMAIL_FROM = os.getenv("EMAIL_FROM")       # Ej: noreply@appvisibility.es
EMAIL_TO = os.getenv("EMAIL_TO")           # Ej: contacto@appvisibility.es
CC_LIST = os.getenv("CC_LIST", "").split(",") if os.getenv("CC_LIST") else []

# ------------------------------------------------------------------
# CONFIG BBDD
# ------------------------------------------------------------------
DB = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "name": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

# ------------------------------------------------------------------
# CONEXION A PostgreSQL
# ------------------------------------------------------------------
def connect_db():
    try:
        conn = psycopg2.connect(
            host=DB["host"],
            port=DB["port"],
            dbname=DB["name"],
            user=DB["user"],
            password=DB["password"],
            connect_timeout=5,
            keepalives=1,
        )
        log_info(f"[✅]: Conexión a la base de datos exitosa.")
        return conn
    except Exception as e:
        log_info(f"[❌]: Error conectando a la base de datos: {e}")
        return None

# ------------------------------------------------------------------
# CIERRE DE CURSOR Y CONEXIÓN
# ------------------------------------------------------------------
def close_db(cursor=None, conn=None):
    """Cierra cursor y conexión de forma segura."""
    if cursor:
        try:
            cursor.close()
        except Exception as e:
            log_info(f"[⚠️]: Error cerrando cursor: {e}")

    if conn:
        try:
            conn.close()
            log_info("[✅]: Conexión a la base de datos cerrada.")
        except Exception as e:
            log_info(f"[⚠️]: Error cerrando conexión: {e}")

# ------------------------------------------------------------------
# ENVIAR CORREO con smtplib
# ------------------------------------------------------------------
def send_email(subject: str, html_content: str):
    """Preparar mensaje MIME con HTML para enviar un correo usando smtp-relay."""
    msg = MIMEMultipart("alternative")
    msg.attach(MIMEText(html_content, "html"))

    msg["From"] = formataddr(("AppVisibility Monitoring", EMAIL_FROM))
    msg["To"] = EMAIL_TO
    msg["Subject"] = subject

    # Enviar correo
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            log_info(f"[ℹ️]: Conectando al servidor SMTP...")
#            server.set_debuglevel(1)
            server.ehlo()
            if SMTP_SERVER not in ("localhost", "127.0.0.1"):
                log_info("[ℹ️]: Usando servidor SMTP externo, iniciando TLS...")
                server.starttls() # Usar TLS si el relay lo soporta
                server.ehlo()
                log_info("[ℹ️]: Conexión TLS iniciada: Autenticando...")
                server.login(SMTP_USER, SMTP_PASS)
                log_info(f"[ℹ️]: Autenticación SMTP exitosa.")

            server.sendmail(EMAIL_FROM, [EMAIL_TO] + CC_LIST, msg.as_string())
        log_info("[✅]: Correo enviado correctamente")
    except Exception as e:
        log_info(f"[❌]: Error enviando correo: {e}")

# ------------------------------------------------------------------
# CONFIG LOGS
# ------------------------------------------------------------------
def log_info(msg: str):
    print(f"mnt-info: {datetime.now().isoformat()} - {msg}")
