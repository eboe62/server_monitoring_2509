#!/bin/bash
set -euo pipefail

POSTFIX_CF="/etc/postfix/main.cf"
SASL_PASSWD_FILE="/etc/postfix/sasl_passwd"

# --- Validación de entorno mínimo ---
: "${SMTP_SERVER:?SMTP_SERVER no definido}"
: "${SMTP_PORT:?SMTP_PORT no definido}"
: "${EMAIL_DOMAIN:?EMAIL_DOMAIN no definido}"
: "${MYNETWORKS:?MYNETWORKS no definido}"

# --- Leer secrets ---
if [ ! -f /run/secrets/smtp_user ] || [ ! -f /run/secrets/smtp_pass ]; then
  echo "[ERROR] Secrets SMTP no disponibles en /run/secrets"
  exit 1
fi

SMTP_USER=$(cat /run/secrets/smtp_user)
SMTP_PASS=$(cat /run/secrets/smtp_pass)

if [ -z "$SMTP_USER" ] || [ -z "$SMTP_PASS" ]; then
  echo "[ERROR] SMTP_USER o SMTP_PASS vacíos"
  exit 1
fi

# --- Esperar a que Postfix genere main.cf ---
echo "[INFO] Esperando a que $POSTFIX_CF esté listo..."
while [ ! -f "$POSTFIX_CF" ]; do
  sleep 1
done

# --- Generamos sasl_passwd y mapa SASL ---
echo "[INFO] Generando sasl_passwd..."

echo "[${SMTP_SERVER}]:${SMTP_PORT} ${SMTP_USER}:${SMTP_PASS}" > "$SASL_PASSWD_FILE"
chmod 600 "$SASL_PASSWD_FILE"

# Forzar reescritura de tablas si es necesario
postmap "$SASL_PASSWD_FILE"

# --- Configuración Postfix  y autenticación SASL (cliente SMTP → relay) ---
echo "[INFO] Aplicando configuración Postfix..."

# --- Relay Postmark ---
postconf -e "relayhost = [${SMTP_SERVER}]:${SMTP_PORT}"

postconf -e "smtp_sasl_auth_enable = yes"
postconf -e "smtp_sasl_password_maps = hash:${SASL_PASSWD_FILE}"
postconf -e "smtp_sasl_security_options = noanonymous"

# ⚠️ Forzamos mecanismos compatibles y evitamos XOAUTH2
postconf -e "smtp_sasl_mechanism_filter = plain, login"

# Forzamos TLS obligatorio con STARTTLS (no wrappermode específico para puerto 465)
# postconf -e "smtp_use_tls = yes"
postconf -e "smtp_tls_security_level = encrypt"
postconf -e "smtp_tls_CAfile = /etc/ssl/certs/ca-certificates.crt"

# --- Configuración de identidad del servidor y redes ---
# Usamos un hostname ficticio para evitar "mail loops"
postconf -e "myhostname = smtp-relay.local"
postconf -e "myorigin = ${EMAIL_DOMAIN}"
postconf -e "mydestination = localhost.localdomain, localhost"

# --- Red interna confiable, permitir localhost y Docker network ---
postconf -e "mynetworks = ${MYNETWORKS}"

# --- Debug controlado (sin ruido) ---
echo "[DEBUG] Configuración relevante:"
postconf | grep -E "relayhost|smtp_sasl|smtp_tls|myhostname|mynetworks"

# --- Nota sobre XOAUTH2 ---
echo "[INFO] Nota: warnings sasl-xoauth2 pueden aparecer si el plugin existe en la imagen."
echo "[INFO] No afecta a Postmark (usa LOGIN/PLAIN)."

# --- Lanzar Postfix ---
echo "[INFO] Configuración aplicada. Lanzando Postfix..."
exec /scripts/run.sh "$@"
