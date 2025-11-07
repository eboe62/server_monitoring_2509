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
import requests

# ==========================================
# 🔧 CARGA DE VARIABLES DE ENTORNO (.env)
# ==========================================
load_dotenv("/opt/monitoring/smtp_relay/.env")

# ==========================================
# CONFIG SMTP / EMAIL
# ==========================================
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

# ==========================================
# CONFIG BBDD
# ==========================================
DB = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "name": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

# ==========================================
# CONEXION A PostgreSQL
# ==========================================
def connect_db():
    """Establece conexión con PostgreSQL."""
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

# ==========================================
# CIERRE DE CURSOR Y CONEXIÓN
# ==========================================
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

# ==========================================
# ENVIAR CORREO con smtplib
# ==========================================
def send_email(subject: str, html_content: str, cc_list=None):
    """
    Envía un correo en formato HTML usando el servidor SMTP configurado.
    Compatible con relays sin autenticación (como smtp-relay local).
    """
    if cc_list is None:
        cc_list = []
    msg = MIMEMultipart("alternative")
    msg.attach(MIMEText(html_content, "html"))

    msg = MIMEText(html_content, "html", "utf-8")
    msg["From"] = formataddr(("AppVisibility Monitoring", EMAIL_FROM))
    msg["To"] = EMAIL_TO
    msg["Cc"] = ", ".join(cc_list)
    msg["Subject"] = subject

    # Enviar correo
    try:
        # Resolución IPv4 explícita
        smtp_host_ipv4 = socket.getaddrinfo(SMTP_SERVER, SMTP_PORT, socket.AF_INET)[0][4][0]
        with smtplib.SMTP(smtp_host_ipv4, SMTP_PORT, timeout=10) as server:

            log_info(f"[ℹ️ ]: Conectando al servidor SMTP...")
#            server.set_debuglevel(1)
            server.ehlo()

            # Solo usa TLS si el servidor lo soporta
            if SMTP_SERVER not in ("localhost", "127.0.0.1"):
                log_info(f"[ℹ️ ]: Usando servidor SMTP externo, iniciando TLS...")
                server.starttls()
                server.ehlo()
                log_info(f"[ℹ️ ]: Conexión TLS iniciada: Autenticando...")

            # Autenticación opcional
            if SMTP_USER and SMTP_PASS:
                server.login(SMTP_USER, SMTP_PASS)
                log_info(f"[ℹ️ ]: Autenticación SMTP exitosa.")

            # Enviar mensaje
            server.sendmail(EMAIL_FROM, [EMAIL_TO] + CC_LIST, msg.as_string())

        log_info(f"[📧]: Enviado a {EMAIL_TO} con CC a {', '.join(cc_list) or '(sin CC)'}")
        return True

    except Exception as e:
        log_info(f"[❌]: Error enviando correo: {e}")
        return False

# ==========================================
# CONVERSORES
# ==========================================

def to_snake_case(name: str) -> str:
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

def normalize_date(value):
    """Convierte fechas 'dd/mm/yyyy' a 'yyyy-mm-dd' y mantiene el resto igual."""
    if isinstance(value, str):
        try:
            if "/" in value:
                # detectamos formato español de fecha
                return datetime.strptime(value, "%d/%m/%Y").strftime("%Y-%m-%d")
        except Exception:
            pass
    return value

# ==========================================
# CONFIG LOGS
# ==========================================
def log_info(msg: str):
    """Logger simple con fecha ISO y prefijo GDA."""
    print(f"gda-info: {datetime.now().isoformat()} - {msg}")

# ==========================================
# GEOLOCALIZACIÓN IP
# ==========================================

IPINFO_TOKEN = os.getenv("IPINFO_TOKEN") # Token IP Geolocalización https://ipinfo.io/

# Función para obtener datos de geolocalización
def get_ip_info(ip):
    """Consulta IPInfo.io y devuelve país, ciudad, latitud y longitud."""
    url = f"https://ipinfo.io/{ip}/json?token={IPINFO_TOKEN}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Lanza error si la solicitud falla
        data = response.json()
        return {
            "country": data.get("country", "Unknown"),
            "city": data.get("city", "Unknown"),
            "lat": data.get("loc", "0,0").split(",")[0],
            "long": data.get("loc", "0,0").split(",")[1]
        }
    except requests.exceptions.RequestException as e:
        log_info(f"[❌] Error obteniendo datos para {ip}: {e}")
        return None
