```bash
==========================================
MONITORING STACK 2509
==========================================

Este repositorio contiene la pila de monitorización y utilidades desplegadas en el servidor DigitalOcean.  
Incluye componentes para observabilidad, ingesta de logs, monitorización de recursos y un servicio de SMTP Relay.

==========================================
ESTRUCTURA DEL PROYECTO
==========================================
monitoring/
├── cron/ 		        # Definiciones de cronjobs y contenedor para tareas programadas
├── log_ingestor/ 	    # Módulos Python para ingesta y procesado de logs
├── observability/ 	    # Configuración de Loki, Promtail, Grafana, etc.
├── resource_monitor/ 	# Scripts de control de recursos Docker
├── scripts/ 		    # Wrappers en bash para ejecución periódica
├── smtp_relay/ 	    # Servicio de relay SMTP en contenedor Postfix
├── Dockerfile.base 	# Imagen base común
├── Makefile 		    # Tareas comunes de build y despliegue
└── requirements.txt 	# Dependencias Python

==========================================
REQUISITOS PREVIOS
==========================================
- Docker y Docker Compose instalados
- Python 3.12+ disponible en `/usr/local/bin/python3`
- Acceso a Git y credenciales configuradas

==========================================
INSTALACION
==========================================
Clonar el repositorio:

cd /opt/monitoring
git clone <repo>

Configurar variables de entorno y credenciales según cada servicio (ejemplo para SMTP Relay):

cd /opt/monitoring
nano smtp_relay/.env

=====================
SMTP_RELAY_CONTAINER_NAME=smtp-relay

# Configuración SMTP común
SMTP_SERVER=smtp.postmarkapp.com
SMTP_PORT=9999

# Postmark SMTP credentials
EMAIL_FROM=noreply@tudominio.com
EMAIL_DOMAIN=tudominio.com
EMAIL_TO=contacto@tudominio.com

# Redes permitidas para relay
MYNETWORKS=127.0.0.0/8 172.16.0.0/12 [::1]/128

# Configuración de la base de datos
# DB_HOST = "localhost"  # Si estás ejecutando en el mismo contenedor o servidor
DB_HOST=srv-captain--security999999app # Si estás ejecutando en remoto
DB_NAME=security9999
DB_USER=user
DB_PASSWORD=999999999
=====================

cd /opt/monitoring
nano smtp_relay/secrets/smtp_user
=====================
99x9xx99-9x99-9x99-99x9-99xx9xxx9xxx (token https://postmarkapp.com)
=====================

cd /opt/monitoring
nano smtp_relay/secrets/smtp_pass
=====================
99x9xx99-9x99-9x99-99x9-99xx9xxx9xxx (token https://postmarkapp.com)
=====================

Dar permisos a los scripts:
chmod +x ./scripts/*.sh

==========================================
USO
==========================================
Makefile gestiona las operaciones principales precediendo el comando correspondiente con la palabra "make ..."

Levantar los servicios principales:
cd /opt/monitoring
make deploy

Verificar logs:
make logs

cd /opt/monitoring/

Ejecución manual de auditorías y limpieza:
./scripts/docker_resources.sh
./scripts/cleanup_docker.sh (ATENCION hacer snapshot previo - riesgo de perdida no deseada de binarios)

==========================================
TAREAS PROGRAMADAS
==========================================
Los cronjobs definidos en cron/monitoring.cron incluyen:
- Auditoría diaria de binarios (./scripts/auditoria_binarios.sh)
- Monitorización de recursos Docker cada 10 min (./scripts/docker_resources.sh)
- Ingesta de logs (fail2ban, kernel, IP geolocation) cada 10 min (./scripts/log_ingest_batch.sh, etc)
- Alertas de riesgo a las 10:00 y 22:00 (./scripts/alert_risk.sh)

# Añadir el siguiente código al crontab
[root]$ crontab -e
# Configurar permisos y ejecutar configure_docker_limits.sh al reiniciar
@reboot chmod +x /usr/local/bin/configure_docker_limits.sh && sleep 60 && /bin/bash /usr/local/bin/configure_docker_limits.sh > /var/log/configure_docker_limits.log 2>&1

# Ejecutar configure_docker_limits.sh cada 10 minutos
*/10 * * * * /usr/local/bin/configure_docker_limits.sh > /var/log/configure_docker_limits.log 2>&1

# Configuramos la prevención de saturación por ataques masivos
@reboot /opt/monitoring/scripts/apply_ssh_ratelimit.sh > /var/log/apply_ssh_ratelimit.log 2>&1

==========================================
PENDIENTE
==========================================
- Documentación detallada de cada módulo (log_ingestor, observability, etc.)
- Diagramas de arquitectura
- Guía de despliegue en DigitalOcean con CapRover

