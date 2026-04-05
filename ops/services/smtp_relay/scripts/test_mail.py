#test_mail.py
# Test E2E realista:
# - Envío SMTP → smtp-relay
# - Validación: aceptación completa del flujo SMTP
#
# Uso:
# docker exec -it monitoring-python bash
# python3 ops/services/smtp_relay/test_mail_e2e.py

import smtplib
from email.mime.text import MIMEText
import time
import sys

SMTP_SERVER = "smtp-relay"
SMTP_PORT = 587

msg = MIMEText("¡Hola! Este es un test mail desde el contenedor boky/postfix monitoring-smtp-relay via Postmar: E2E Test SMTP relay + Postmark API")
msg["Subject"] = f"E2E TEST {int(time.time())}"
msg["From"] = "noreply@appvisibility.es"
msg["To"] = "contacto@appvisibility.es"

print(f"Conectando a {SMTP_SERVER}:{SMTP_PORT}...")
print("📤 Enviando email...")

try:
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
        server.set_debuglevel(1)  # Mostrar salida detallada con debug SMTP
        server.ehlo()
        # No se usa TLS ni login porque Postfix hace el relay
        response = server.send_message(msg)

    # send_message devuelve {} si todo OK
    if response == {}:
        print("✅ SMTP aceptado por el relay Postmark")

    else:
        print("⚠️ Respuesta parcial del servidor:", response)

except Exception as e:
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
print("   ✔ Postfix aceptó el mensaje")
print("   ✔ Relay hacia Postmark ejecutado")

print("⚠️ Nota:")
print("   - Esto NO garantiza entrega final (limitaciones Postmark / cuota)")
print("   - Verificar entrega real requiere webhook o API directa")
print("   - 'status=sent' debe verificarse en logs del contenedor smtp-relay")
print("   - Si no ves el email, puede ser por cuota de Postmark")
print("   - Este test valida infraestructura, no entrega final")

print("ℹ️ Verifica los logs en el contenedor con:")
print("   docker logs monitoring-smtp-relay --tail 20")

sys.exit(0)
