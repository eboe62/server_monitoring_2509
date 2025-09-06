#!/bin/bash
set -e

POSTFIX_CF="/etc/postfix/main.cf"
USER=$(cat /run/secrets/smtp_user)
PASS=$(cat /run/secrets/smtp_pass)

# Espera a que Postfix esté listo con main.cf
while [ ! -f "$POSTFIX_CF" ]; do
  echo "Esperando a que se genere $POSTFIX_CF..."
  sleep 1
done

# Generamos sasl_passwd y mapa SASL
echo "[${SMTP_SERVER}]:${SMTP_PORT} ${USER}:${PASS}" > /etc/postfix/sasl_passwd
chmod 600 /etc/postfix/sasl_passwd
postmap /etc/postfix/sasl_passwd

# Configuración Postfix y autenticación SASL
postconf -e "smtp_sasl_auth_enable = yes"
postconf -e "smtp_sasl_password_maps = hash:/etc/postfix/sasl_passwd"
postconf -e "smtp_sasl_security_options = noanonymous"
postconf -e "smtp_sasl_mechanism_filter = plain, login"

# TLS con STARTTLS (no wrappermode específico para puerto 465)
postconf -e "smtp_use_tls = yes"
postconf -e "smtp_tls_security_level = encrypt"
postconf -e "smtp_tls_CAfile = /etc/ssl/certs/ca-certificates.crt"

# Configuración de identidad del servidor y redes
# Usamos un hostname ficticio para evitar "mail loops"
postconf -e "myhostname = smtp-relay.local"
postconf -e "myorigin = ${EMAIL_DOMAIN}"
postconf -e "mydestination = localhost.localdomain, localhost"

# Permitir localhost y Docker network
postconf -e "mynetworks = ${MYNETWORKS}"

# Relay Postmark
postconf -e "relayhost = [${SMTP_SERVER}]:${SMTP_PORT}"

# Forzar reescritura de tablas si es necesario
postmap /etc/postfix/sasl_passwd || true

# Lanza postfix
echo "[INFO] Configuración aplicada. Lanzando Postfix..."
exec /scripts/run.sh "$@"
