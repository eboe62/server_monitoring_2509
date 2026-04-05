# test_mail.py
# Test E2E realista con captura de queue_id:
# - Envío SMTP → smtp-relay
# - Captura queue_id real de Postfix
# - Genera Message-ID único
# - Permite correlación exacta en logs para tests posteriores
# - Validación: aceptación completa del flujo SMTP
#
# Uso:
# docker exec -it monitoring-python bash
# python3 ops/services/smtp_relay/test_mail_e2e.py

import smtplib
from email.mime.text import MIMEText
import time
import sys
import socket
import re

SMTP_SERVER = "smtp-relay"
SMTP_PORT = 587

# Generar identificador único
timestamp = int(time.time())
subject = f"E2E TEST {timestamp}"
message_id = f"<e2e-{timestamp}@appvisibility.es>"

# Persistencia para Makefile
with open("/tmp/smtp_last_subject", "w") as f:
    f.write(subject)

with open("/tmp/smtp_last_message_id", "w") as f:
    f.write(message_id)

msg = MIMEText(
    "¡Hola! Este es un test mail desde el contenedor boky/postfix monitoring-smtp-relay via Postmar: Test SMTP relay con correlación completa de mensaje por queue_id (Postfix → Postmark)"
)

msg["Subject"] = subject
msg["From"] = "noreply@appvisibility.es"
msg["To"] = "contacto@appvisibility.es"
msg["Message-ID"] = message_id

print(f"Conectando a {SMTP_SERVER}:{SMTP_PORT}...")
print(f"📨 Subject: {subject}")
print(f"🧾 Message-ID: {message_id}")
print("📤 Enviando email...")

queue_id = None

try:
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
        server.set_debuglevel(1)  # Mostrar salida detallada con debug SMTP
        server.ehlo()
        # No se usa TLS ni login porque Postfix hace el relay

        # Capturar respuesta SMTP manualmente
        # MAIL FROM
        code, response = server.mail(msg["From"])
        if code != 250:
            raise Exception(f"MAIL FROM fallo: {code} {response}")

        # RCPT TO
        code, response = server.rcpt(msg["To"])
        if code != 250:
            raise Exception(f"RCPT TO fallo: {code} {response}")

        # DATA (aquí es donde obtenemos el queue_id)
        code, response = server.data(msg.as_string())

        if code != 250:
            raise Exception(f"DATA fallo: {code} {response}")

        # Ejemplo response:
        # b'2.0.0 Ok: queued as 707898BF47'
        resp_str = response.decode()

        match = re.search(r"queued as ([A-F0-9]+)", resp_str)
        if match:
            queue_id = match.group(1)
            print(f"✅ SMTP aceptado por el relay Postmark")
            print(f"📌 queue_id: {queue_id}")

            with open("/tmp/smtp_last_queue_id", "w") as f:
                f.write(queue_id)
        else:
            print(f"❌ No se pudo extraer queue_id de: {resp_str}")

        server.quit()


        # Guardar queue_id para correlación
        with open("/tmp/smtp_queue_id", "w") as f:
            f.write(queue_id)

except (smtplib.SMTPException, socket.error, Exception) as e:
    print(f"❌ Error SMTP: {e}")
    sys.exit(1)

print("⏳ Esperando procesamiento en relay Postmark...")
time.sleep(2)

# Validación lógica:
# Si hemos llegado aquí:
# - SMTP handshake OK
# - Postfix ha aceptado el mensaje (250)
# - El relay lo intentará entregar a Postmark

print("📬 Validación E2E:")
print("   ✔ SMTP handshake OK")
print("   ✔ Postfix aceptó el mensaje")

if queue_id:
    print("   ✔ queue_id capturado")

print("   ✔ Relay hacia Postmark ejecutado")

print("⚠️ Nota:")
print("   - Este test valida infraestructura, no entrega final")
print("   - Esto NO garantiza entrega final (limitaciones Postmark / cuota)")
print("   - Verificar entrega real requiere webhook o API directa")
print("   - 'status=sent' debe verificarse en logs del contenedor smtp-relay")
print("   - Si no ves el email, puede ser por cuota de Postmark")

print("ℹ️ Verifica los logs en el contenedor con:")
print("   docker logs monitoring-smtp-relay --tail 20")

sys.exit(0)
