#!/usr/bin/env python3
# config.py
import os
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from email.mime.multipart import MIMEMultipart
import datetime
import re
import socket
import html

# ==========================================
# 🔧 RUTAS DE CONFIGURACIÓN (sobrescribibles por entorno)
# ==========================================
# Nota: la carga del .env y la lectura de secrets se realizan en tiempo de
# ejecución mediante init_config(). De este modo se evitan errores en la fase de importación (import-time) si
# /opt/monitoring/smtp_relay/.env o los secrets no existen. Esto permite que el módulo puede importarse de
# forma segura en cualquier entorno (local, CI/CD, contenedor, producción).

DEFAULT_ENV_PATH = os.getenv("SMTP_RELAY_ENV_PATH", "ops/services/smtp_relay/.env")
DEFAULT_SECRETS_DIR = os.getenv("SMTP_RELAY_SECRETS_DIR", "ops/services/smtp_relay/secrets")

# NOTE: Do not cache SMTP_MODE at import-time. Use get_smtp_mode() to
# determine mode dynamically at runtime to avoid import-time side-effects.

# ==========================================
# SMTP MODE
# ==========================================

VALID_SMTP_MODES = ("relay", "auth")

def get_smtp_mode() -> str:
    """Devuelve el modo SMTP válido: 'relay' o 'auth'.
    Lee la variable de entorno `SMTP_MODE` en tiempo de ejecución, valida valores permitidos y su comportamiento debe ser fail-fast ante valores inválidos.
    """
    mode = os.getenv("SMTP_MODE", "relay")
    if mode is None:
        mode = "relay"
    mode = mode.strip().lower()
    if mode not in ("relay", "auth"):
        log_info(f"[❌]: SMTP_MODE inválido: {mode}. Valores permitidos: {VALID_SMTP_MODES}")
        raise RuntimeError(f"Invalid SMTP_MODE: {mode}")
    return mode

# ==========================================
# CONFIGURACIÓN SMTP / EMAIL (valores iniciales desde el entorno)
# ==========================================
# Configuración SMTP (valores leídos inicialmente desde el entorno; pueden
# actualizarse llamando a init_config() que cargará el .env si existe y
# leerá archivos de secrets en runtime)

SMTP_SERVER = os.getenv("SMTP_SERVER", "localhost")   # Ej: smtp.postmarkapp.com (servicio host) o localhost (servicio contenedor)
SMTP_PORT   = int(os.getenv("SMTP_PORT", "2526"))     # Ej: 2525 (servicio host) o 2526 (servicio contenedor)

SMTP_USER   = os.getenv("SMTP_USER")
SMTP_PASS   = os.getenv("SMTP_PASS")

# Configuración de correo desde el entorno (se actualizará si init_config carga .env)
EMAIL_FROM  = os.getenv("EMAIL_FROM")       # Ej: noreply@appvisibility.es
EMAIL_TO    = os.getenv("EMAIL_TO")         # Ej: contacto@appvisibility.es
CC_LIST     = os.getenv("CC_LIST", "").split(",") if os.getenv("CC_LIST") else []
SUBJECT     = os.getenv("SUBJECT", "📊 Informe")

# ==========================================
# CONFIG BBDD (valores iniciales desde entorno; init_config() puede hacer re-lectura)
# ==========================================
DB = {
    "host": os.getenv("POSTGRES_HOST"),
    "port": int(os.getenv("POSTGRES_PORT", 5432)),
    "name": os.getenv("POSTGRES_NAME"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
}
# INIT CONFIG (runtime explícito)
def init_config(env_path: str = None, secrets_dir: str = None):
    """
    Inicializa la configuración en tiempo de ejecución.

    SMTP_MODE define COMPLETAMENTE el comportamiento:

    relay:
      - NO requiere secrets
      - NO requiere auth
      - ignora secrets ausentes

    auth:
      - requiere credenciales SMTP
      - Carga las variables desde .env si existen.
      - Lee secrets SMTP desde filesystem si están disponibles.
      - Re-lee variables dependientes del entorno.
      - NO lanza excepción en ausencia de ficheros.
      - fail-fast si faltan

    Esta función debe invocarse desde los entrypoints (wrappers/sh/containers)
    antes de ejecutar operaciones que dependan de estas credenciales.

    La función gestiona FileNotFoundError de forma controlada y registra
    mensajes mediante log_info() para diagnóstico.
    """
    global SMTP_USER, SMTP_PASS, EMAIL_FROM, EMAIL_TO, CC_LIST, SUBJECT, DB, IPINFO_TOKEN

    env_path = env_path or DEFAULT_ENV_PATH
    secrets_dir = secrets_dir or DEFAULT_SECRETS_DIR

    mode = get_smtp_mode()

    # Cargar .env si existe
    if os.path.exists(env_path):
        try:
            load_dotenv(env_path)
            log_info(f"[ℹ️]: Se ha cargado .env desde {env_path}")
        except Exception as e:
            log_info(f"[⚠️]: Error cargando .env ({env_path}): {e}")
    else:
        log_info(f"[⚠️]: .env no encontrado en {env_path}; usando variables de entorno actuales")

    # Re-lectura de variables que podrían haber cambiado al cargar .env
    EMAIL_FROM = os.getenv("EMAIL_FROM")
    EMAIL_TO   = os.getenv("EMAIL_TO")
    CC_LIST    = os.getenv("CC_LIST", "").split(",") if os.getenv("CC_LIST") else []
    SUBJECT    = os.getenv("📊 Informe")

    # Actualizar DB desde entorno (posible cambio tras cargar .env)
    DB = {
        "host": os.getenv("POSTGRES_HOST"),
        "port": int(os.getenv("POSTGRES_PORT", 5432)),
        "name": os.getenv("POSTGRES_NAME"),
        "user": os.getenv("POSTGRES_USER"),
        "password": os.getenv("POSTGRES_PASSWORD"),
    }

    # Leer secrets SMTP del filesystem si están disponibles; fallback a variables de entorno
    user_path = os.path.join(secrets_dir, "smtp_user")
    pass_path = os.path.join(secrets_dir, "smtp_pass")

    SMTP_USER = None
    SMTP_PASS = None

    # RELAY MODE
    # Relay-only mode: no se esperan credenciales. Solo usar variables de entorno si existen.
    if mode == "relay":
        SMTP_USER = os.getenv("SMTP_USER")
        SMTP_PASS = os.getenv("SMTP_PASS")
        log_info(f"[ℹ️]: SMTP_MODE={mode} sin autenticación SMTP")

    # AUTH MODE
    elif mode == "auth":
        # Auth-required: intentar cargar desde filesystem y fallar explícitamente si no existen
        user_val = None
        pass_val = None

```python
if os.path.exists(user_path):
    try:
        with open(user_path) as f:
            user_val = f.read().strip()

        log_info("[✅]: SMTP_USER cargado desde secrets")

    except Exception as e:
        log_info(f"[❌]: Error leyendo SMTP_USER desde {user_path}: {e}")

else:
    log_info(f"[⚠️]: SMTP_USER no encontrado en secrets ({user_path})")


if os.path.exists(pass_path):
    try:
        with open(pass_path) as f:
            pass_val = f.read().strip()

        log_info("[✅]: SMTP_PASS cargado desde secrets")

    except Exception as e:
        log_info(f"[❌]: Error leyendo SMTP_PASS desde {pass_path}: {e}")

else:
    log_info(f"[⚠️]: SMTP_PASS no encontrado en secrets ({pass_path})")


SMTP_USER = user_val or os.getenv("SMTP_USER")
SMTP_PASS = pass_val or os.getenv("SMTP_PASS")
```


        # Hard-fail si el modo exige auth pero faltan credenciales
        if not SMTP_USER or not SMTP_PASS:
            log_info(f"[❌]: SMTP_MODE=auth pero faltan credenciales al intentar enviar correo (se requieren smtp_user/smtp_pass)")
            raise RuntimeError("Auth mode requiere credenciales SMTP")

    return {
        "SMTP_SERVER": SMTP_SERVER,
        "SMTP_PORT": SMTP_PORT,
        "SMTP_USER": SMTP_USER,
        "SMTP_PASS": SMTP_PASS,
        "EMAIL_FROM": EMAIL_FROM,
        "EMAIL_TO": EMAIL_TO,
        "CC_LIST": CC_LIST,
        "DB": DB,
    }

# ==========================================
# CONEXION A PostgreSQL (lazy import)
# ==========================================
def connect_db():
    """Establece conexión PostgreSQL. Requiere init_config previo."""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=DB["host"],
            port=DB["port"],
            dbname=DB["name"],
            user=DB["user"],
            password=DB["password"],
            connect_timeout=5,
            keepalives=1,
        )
        log_info(f"[✅]: Conexión a la base de datos establecida.")
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
def send_email(html_content: str = None, subject: str = None, email_to: str = None, cc_list: list = None):
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

    if not email_to:
        raise ValueError("No se ha definido destinatario de correo (email_to)")

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
            if server.has_extn("STARTTLS"):
                log_info(f"[ℹ️ ]: Usando servidor SMTP externo, activando conexión segura, iniciando TLS...")
                server.starttls()
                server.ehlo()

                log_info(f"[ℹ️ ]: Conexión TLS iniciada: Autenticando...")

            # En modo 'auth' las credenciales son obligatorias
            mode = get_smtp_mode()
            if mode == "auth":
                if not SMTP_USER or not SMTP_PASS:
                    log_info(f"[❌]: SMTP_MODE=auth pero faltan credenciales al intentar enviar correo (se requieren smtp_user/smtp_pass)")
                    raise RuntimeError("Se requieren credenciales SMTP")
                server.login(SMTP_USER, SMTP_PASS)
                log_info(f"[ℹ️ ]: Autenticación SMTP exitosa.")
            else:
                # relay-only: si hay credenciales las usa y si no, continúa sin autenticar
                if SMTP_USER and SMTP_PASS:
                    server.login(SMTP_USER, SMTP_PASS)
                    log_info(f"[ℹ️ ]: Autenticación SMTP exitosa (creds desde env/secrets).")

            # Enviar mensaje
            recipients = [email_to] + cc_list
            server.sendmail(EMAIL_FROM, recipients, msg.as_string())

        log_info(f"[📧]: Enviado a {email_to} con CC a {', '.join(cc_list) or '(sin CC)'}")
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
# GESTION DEL TIEMPO
# ==========================================

def get_month_gap(month_gap):
    """
    Devuelve:
      - hoy (date)
      - primer_dia_mes_actual (date)
      - primer_dia_mes_inicio (date)
      - fecha_anterior_str (string normalizada)
    """
    hoy = datetime.date.today()

    primer_dia_mes_actual = hoy.replace(day=1)

    # primer día del mes de hace n meses
    mes_objetivo = primer_dia_mes_actual.month - month_gap
    anno_objetivo = primer_dia_mes_actual.year

    if mes_objetivo <= 0:
        mes_objetivo += 12
        anno_objetivo -= 1

    primer_dia_mes_inicio = datetime.date(anno_objetivo, mes_objetivo, 1)

    fecha_anterior_str = normalize_date(primer_dia_mes_inicio.strftime("%Y-%m-%d"))

    return hoy, primer_dia_mes_actual, primer_dia_mes_inicio, fecha_anterior_str

# ==========================================
# CONFIG LOGS
# ==========================================
def log_info(msg: str):
    """Logger simple con fecha ISO y prefijo GDA."""
    print(f"gda-info: {datetime.datetime.now().isoformat()} - {msg}")

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
    html_block.append('<table border="1" cellpadding="4" cellspacing="0" style="border-collapse: collapse; width:80%;">')

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
            if isinstance(c, (datetime.datetime, datetime.date)):
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
# Consulta IPInfo.io y devuelve país, ciudad, latitud y longitud.
def get_ip_info(ip):
    if not IPINFO_TOKEN:
        log_info(f"[⚠️]: IPINFO_TOKEN no definido")
        return None

    try:
        import requests
        url = f"https://ipinfo.io/{ip}/json?token={IPINFO_TOKEN}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Lanza error si la solicitud falla
        data = response.json()
        return {
            "country": data.get("country", "Unknown"),
            "city": data.get("city", "Unknown"),
            "lat": data.get("loc", "0,0").split(",")[0],
            "long": data.get("loc", "0,0").split(",")[1]
        }
    except Exception as e:
        log_info(f"[❌]: Error obteniendo datos desde IPInfo para {ip}: {e}")
        return None

