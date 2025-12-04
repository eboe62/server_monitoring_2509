#!/usr/bin/env python3
# config.py
import os
import smtplib
from dotenv import load_dotenv
import psycopg2
from email.mime.text import MIMEText
from email.utils import formataddr
from email.mime.multipart import MIMEMultipart
from datetime import datetime, date
import re
import socket
import html

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
SMTP_PORT   = int(os.getenv("SMTP_PORT", "2526"))         # 2525 (servicio host) ó 2526 (servicio contenedor)
with open("/opt/monitoring/smtp_relay/secrets/smtp_user") as f:
    SMTP_USER = f.read().strip()

with open("/opt/monitoring/smtp_relay/secrets/smtp_pass") as f:
    SMTP_PASS = f.read().strip()

# Configuración de correo desde .env
# cuando usemos el contenedor smtp-relay. Este contenedor actúa como relay local y no necesita login TLS.
EMAIL_FROM  = os.getenv("EMAIL_FROM")       # Ej: noreply@appvisibility.es
EMAIL_TO    = os.getenv("EMAIL_TO")           # Ej: contacto@appvisibility.es
CC_LIST     = os.getenv("CC_LIST", "").split(",") if os.getenv("CC_LIST") else []
SUBJECT     = os.getenv("SUBJECT", "📊 Informe del estado de droplet")

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
def send_email(subject: str, html_content: str = None, email_to: str = None, cc_list: list = None):
    """
    Envía un correo en formato HTML usando el servidor SMTP configurado con fallback a texto plano.
    Compatible con smtp-relay sin autenticación o con STARTTLS o autenticación TLS.
    Si no se especifica subject/email_to/cc_list, usa los valores por defecto definidos en config.py.
    Si detecta etiquetas HTML, envía multipart/alternative (HTML + texto plano);
    en caso contrario, solo texto plano.
    """
    if cc_list is None:
        cc_list = []

    # Fallbacks a valores por defecto
    subject  = subject  or SUBJECT
    email_to = email_to or EMAIL_TO
    cc_list  = cc_list  or CC_LIST

    # Detectar si el contenido es HTML
    is_html = bool(re.search(r"<[^>]+>", html_content))

    if is_html:
        # Si contiene etiquetas, construimos multipart con HTML y texto plano

        plain_text = re.sub(r"<[^>]+>", "", html_content)
        msg = MIMEMultipart("alternative")
        msg.attach(MIMEText(plain_text, "plain", "utf-8"))
        msg.attach(MIMEText(html_content, "html", "utf-8"))
    else:
        # Si no hay etiquetas, solo cuerpo texto
        msg = MIMEText(html_content, "plain", "utf-8")

    msg["From"] = formataddr(("AppVisibility Monitoring", EMAIL_FROM))
    msg["To"] = email_to
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
            recipients = [email_to] + cc_list
            server.sendmail(EMAIL_FROM, recipients, msg.as_string())
            log_info(f"[📧]: Enviado a {email_to} con CC a {', '.join(cc_list) or '(sin CC)'}")

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
# HTML BUILDER
# ==========================================

def format_date(d):
    if d is None:
        return ""
    # d puede ser date o datetime
    try:
        return d.strftime('%Y-%m-%d')
    except Exception:
        return str(d)

def safe(value):
    if value is None or value == "":
        return "---"
    return html.escape(str(value))

def build_html_table(headers, rows, title, max_rows=None):
    """
    Construye un bloque HTML para una tabla.
    headers: lista de cabeceras
    rows: lista de tuplas/iterables con valores
    """
    shown_rows = rows if (max_rows is None) else rows[:max_rows]
    html_block = []

    html_block.append(f"<p>{html.escape(title.upper())}</p>")
    html_block.append("<br>")
    html_block.append('<table border="1" cellpadding="4" cellspacing="0" style="border-collapse: collapse; width:60%;">')

    # generar colgroup proporcional
    num_cols = len(headers)
    html_block.append("<colgroup>")
    for _ in range(num_cols):
        html_block.append(f'<col style="width: {100/num_cols}%;">')
    html_block.append("</colgroup>")

    # header
    html_block.append("<thead><tr style='background-color:#f2f2f2;'>")
    for h in headers:
        html_block.append(f"<th>{html.escape(h)}</th>")
    html_block.append("</tr></thead>")

    html_block.append("<tbody>")
    for row in shown_rows:
        html_block.append("<tr>")
        for c in row:
            # if it's a date object, format
            if isinstance(c, (datetime, date)):
                cell = format_date(c) or "---"
            else:
                cell = safe(c)
            html_block.append(f"<td>{cell}</td>")
        html_block.append("</tr>")
    html_block.append("</tbody></table>")

    # Note if truncated
    if (max_rows is not None) and (len(rows) > max_rows):
        html_block.append(f"<p><em>Se muestran las primeras {max_rows} filas de {len(rows)} encontradas.</em></p>")

    return "\n".join(html_block)

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

