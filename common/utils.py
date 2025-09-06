#!/usr/bin/env python3
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables desde .env
load_dotenv("/opt/monitoring/smtp_relay/.env")

with open("/opt/monitoring/smtp_relay/secrets/smtp_user") as f:
    SMTP_USER = f.read().strip()

with open("/opt/monitoring/smtp_relay/secrets/smtp_pass") as f:
    SMTP_PASS = f.read().strip()

# Configuración de correo desde .env
# Excluimos las credenciales SMTP (SMTP_USER, SMTP_PASS) cuando usemos el servicio contenedor
# cuando usemos el contenedor smtp-relay. Este contenedor actúa como relay local y no necesita login TLS.
EMAIL_FROM = os.getenv("EMAIL_FROM")       # Ej: noreply@appvisibility.es
EMAIL_TO = os.getenv("EMAIL_TO")           # Ej: contacto@appvisibility.es
SMTP_SERVER = os.getenv("SMTP_SERVER", "127.0.0.1")     # smtp.postmarkapp.com (servicio host) ó localhost (servicio contenedor)
SMTP_PORT = int(os.getenv("SMTP_PORT", "2526"))         # 2525 (servicio host) ó 2526 (servicio contenedor)

def log_info(msg: str):
    print(f"mnt-info: {datetime.now().isoformat()} - {msg}")

def send_email(subject: str, html_content: str):
    """Preparar mensaje MIME con HTML para enviar un correo usando smtp-relay."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg.attach(MIMEText(html_content, "html"))

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

            server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        log_info("[✅]: Correo enviado correctamente")
    except Exception as e:
        log_info(f"[❌]: Error enviando correo: {e}")

