#test_mail.py
import smtplib
from email.mime.text import MIMEText
import time
import socket

SMTP_SERVER = "localhost"
SMTP_PORT = 2526

msg = MIMEText("¡Hola! Este es un test mail desde el contenedor boky/postfix smtp-relay via Postmark")
msg["Subject"] = "Correo desde el SMTP relay local"
msg["From"] = "noreply@appvisibility.es"
msg["To"] = "contacto@appvisibility.es"

print(f"Conectando a {SMTP_SERVER}:{SMTP_PORT}...")

try:
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
        server.set_debuglevel(1)  # Mostrar salida detallada con debug SMTP
        server.ehlo()
        # No se usa TLS ni login porque Postfix hace el relay
        response = server.send_message(msg)
    if response == {}:
        print("✅ Correo enviado correctamente.")
    else:
        print("⚠️ Respuesta parcial del servidor:", response)
except (smtplib.SMTPException, socket.error) as e:
    print(f"❌ Error enviando correo: {e}")

print("ℹ️ Verifica los logs en el contenedor con:")
print("   docker logs smtp-relay --tail 50")

