```bash
==========================================
MONITORING STACK 2509
==========================================

Este repositorio contiene la pila de monitorización y utilidades desplegadas en el servidor DigitalOcean.  
Incluye componentes para observabilidad, ingesta de logs, monitorización de recursos y un servicio de **SMTP Relay**.

==========================================
ESTRUCTURA DEL PROYECTO
==========================================
monitoring/
├── cron/ 		# Definiciones de cronjobs y contenedor para tareas programadas
├── log_ingestor/ 	# Módulos Python para ingesta y procesado de logs
├── observability/ 	# Configuración de Loki, Promtail, Grafana, etc.
├── resource_monitor/ 	# Scripts de control de recursos Docker
├── scripts/ 		# Wrappers en bash para ejecución periódica
├── smtp_relay/ 	# Servicio de relay SMTP en contenedor Postfix
├── Dockerfile.base 	# Imagen base común
├── Makefile 		# Tareas comunes de build y despliegue
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

git clone <repo>
cd monitoring

Configurar variables de entorno y credenciales según cada servicio (ejemplo para SMTP Relay):

nano smtp_relay/.env
nano smtp_relay/secrets/smtp_user
nano smtp_relay/secrets/smtp_pass

Dar permisos a los scripts:

chmod +x ./scripts/*.sh

==========================================
USO
==========================================
Levantar los servicios principales:
make up

Verificar estado y logs:
make status
make logs

Ejecutar auditorías y monitores manualmente:
./scripts/docker_resources.sh
./scripts/alert_risk.sh

==========================================
TAREAS PROGRAMADAS
==========================================
Los cronjobs definidos en cron/monitoring.cron incluyen:
- Auditoría diaria de binarios
- Monitorización de recursos Docker cada 10 min
- Ingesta de logs (fail2ban, kernel, IP geolocation) cada 10 min
- Alertas de riesgo a las 10:00 y 22:00

==========================================
PENDIENTE
==========================================
- Documentación detallada de cada módulo (log_ingestor, observability, etc.)
- Diagramas de arquitectura
- Guía de despliegue en DigitalOcean con CapRover

