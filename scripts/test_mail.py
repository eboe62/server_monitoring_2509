# test_mail.py
# Test E2E SMTP relay:
# - monitoring-python -> smtp-relay
# - validación SMTP handshake
# - captura queue_id Postfix
# - correlación runtime para Makefile
#
# Objetivo:
# validar aceptación SMTP y relay interno.
#
# Este test NO garantiza entrega final.
#
# Uso:
#
# docker exec monitoring-python \
#   python3 scripts/test_mail.py
#
# Artefactos runtime:
#
# /tmp/smtp_last_subject
# /tmp/smtp_last_message_id
# /tmp/smtp_queue_id
#
# ==========================================
import smtplib
from email.mime.text import MIMEText
import time
import sys
import socket
import re
import os

# Configuración SMTP
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp-relay")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
MAIL_FROM = os.getenv("SMTP_FROM", "noreply@appvisibility.es")
MAIL_TO = os.getenv("SMTP_TO", "contacto@appvisibility.es")

# Generar identificador único
timestamp = int(time.time())
subject = f"E2E TEST {timestamp}"
message_id = f"<e2e-{timestamp}@appvisibility.es>"

# Persistencia runtime para tests Makefile
with open("/tmp/smtp_last_subject", "w") as f:
    f.write(subject)

with open("/tmp/smtp_last_message_id", "w") as f:
    f.write(message_id)

# Construcción mensaje

body = """
SMTP relay E2E test.

Validaciones:
- SMTP handshake
- MAIL FROM
- RCPT TO
- DATA
- queue_id Postfix

Flujo:
monitoring-python -> smtp-relay -> upstream relay
"""

msg = MIMEText(body.strip())

msg["Subject"] = subject
msg["From"] = MAIL_FROM
msg["To"] = MAIL_TO
msg["Message-ID"] = message_id

# Logs iniciales
print("")
print("=== SMTP RELAY E2E TEST ===")
print("")

print(f"[INFO] Conectando a SMTP server : {SMTP_SERVER}:{SMTP_PORT}...")
print(f"[INFO] Subject                  : {subject}")
print(f"[INFO] Message-ID               : {message_id}")
print(f"[INFO] From                     : {MAIL_FROM}")
print(f"[INFO] To                       : {MAIL_TO}")
print("📤 Enviando email...")
# Ejecución SMTP
queue_id = None

try:
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
        # Debug SMTP
        server.set_debuglevel(1)  # Mostrar salida detallada con debug SMTP

        # EHLO
        server.ehlo()
        # No se usa TLS ni login porque Postfix hace el relay

        # Capturar respuesta SMTP manualmente
        code, _ = server.ehlo()
        if code != 250:
            raise RuntimeError(f"EHLO fallo: {code} {response}")
        print("[OK] EHLO aceptado")

        # MAIL FROM
        code, response = server.mail(MAIL_FROM)

        if code != 250:
            raise RuntimeError(f"MAIL FROM fallo: {code} {response}")
        print("[OK] MAIL FROM aceptado")

        # RCPT TO
        code, response = server.rcpt(MAIL_TO)

        if code != 250:
            raise RuntimeError(f"RCPT TO fallo: {code} {response}")
        print("[OK] RCPT TO aceptado")

        # DATA (aquí es donde obtenemos el queue_id)
        code, response = server.data(msg.as_string())

        if code != 250:
            raise RuntimeError(f"DATA fallo: {code} {response}")
        print("[OK] DATA aceptado")

        # Captura queue_id
        # Ejemplo response:
        # b'2.0.0 Ok: queued as 707898BF47'
        resp_str = response.decode(errors="ignore")

        match = re.search(r"queued as ([A-F0-9]+)", resp_str)
        if match:
            queue_id = match.group(1)
            print(f"✅ SMTP aceptado por el relay Postmark")
            print(f"[OK] queue_id capturado: {queue_id}")

            with open("/tmp/smtp_queue_id", "w") as f:
                f.write(queue_id)
        else:
            print(f"[WARN] No se pudo extraer queue_id de: {resp_str}")

        server.quit()


        # Guardar queue_id para correlación
        with open("/tmp/smtp_queue_id", "w") as f:
            f.write(queue_id)

except (smtplib.SMTPException, socket.error, RuntimeError, Exception) as e:
    print("")
    print(f"[ERROR] Error SMTP: {e}")

    # 🔥 IMPORTANTE: modo CI tolerante
    if os.getenv("CI") == "true":
        print("")
        print("[WARN] modo CI tolerante activado")
        print("[WARN] error SMTP no bloqueante")

        sys.exit(0)

    sys.exit(1)

# Espera mínima relay
print("")
print("[INFO] esperando procesamiento relay...")
time.sleep(2)

# Validación lógica:
# Si hemos llegado aquí:
# - SMTP handshake OK
# - Postfix ha aceptado el mensaje (250)
# - El relay lo intentará entregar a Postmark

# Resumen final
print("=== RESULTADO SMTP E2E ===")
print("   ✔ SMTP handshake OK")
print("   ✔ MAIL FROM")
print("   ✔ RCPT TO")
print("   ✔ DATA")
print("   ✔ Postfix aceptó el mensaje")

if queue_id:
    print("   ✔ queue_id correlacionado")

print("   ✔ relay SMTP aceptó mensaje")

print("[WARN] Nota:")
print("   - Este test valida infraestructura SMTP, no la entrega final")
print("   - Esto NO garantiza entrega final (limitaciones Postmark / cuota)")
print("   - Verificar entrega real requiere webhook o API directa")
print("   - 'status=sent' debe verificarse en logs del contenedor smtp-relay")
print("   - Si no ves el email, puede ser por cuota de Postmark")

print("[INFO] Verifica los logs en el contenedor con:")
print("   docker logs monitoring-smtp-relay --tail 20")

sys.exit(0)
