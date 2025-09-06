# SMTP Relay con Docker y Postfix (IaC)

Infraestructura para envío seguro de correos mediante Postmark o cualquier SMTP externo, usando Docker y Postfix.  
Permite realizar relay SMTP local con autenticación y TLS, gestionado con Docker Compose.

---

## ✅ Pasos de instalación (Docker Compose)

```bash
git clone <repo>
cd smtp_relay

# Edita las variables de entorno y las credenciales SMTP
nano .env
nano ./secrets/smtp_user
nano ./secrets/smtp_pass

# Da permisos a los scripts
chmod +x ./scripts/*.sh

# Levanta el servicio
make up

# Verifica el estado y logs
make status
make logs

