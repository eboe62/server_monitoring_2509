# 🧩 Proyecto MONITORING STACK — DigitalOcean (v250928)

![Python](https://img.shields.io/badge/Python-3.12-blue.svg)
![Docker](https://img.shields.io/badge/Docker-enabled-0db7ed.svg)
![Status](https://img.shields.io/badge/Status-Operational-success.svg)
![License](https://img.shields.io/badge/Environment-DigitalOcean_2509-orange.svg)

---

## 📖 Descripción general

**Monitoring Stack 2509** es una plataforma de **monitorización y observabilidad 100% contenerizada (IaC)** desplegada en un servidor **DigitalOcean**.  
El sistema integra **ingesta y análisis de logs**, **alertas por correo**, **monitorización de recursos Docker** y un **honeypot Postgres** para detección temprana de ataques.  

Inicialmente, la BBDD se gestionaba mediante **CapRover**, pero tras un incidente de redirección no autorizada (“cashmachine.ie”), se migró a un contenedor propio.  
La antigua BBDD se mantiene ahora como **honeypot**, permitiendo detectar intentos de acceso o manipulación externos.

---

## 🏗️ Infraestructura en servidor

Servidor actual:  
`eob-250501a` (DigitalOcean)

Ruta de instalación:  
`/opt/monitoring`

Repositorio:  
[https://github.com/eboe62/server_monitoring_2509.git](https://github.com/eboe62/server_monitoring_2509.git)  
Rama: `develop`

---

## ⚙️ Requisitos previos

- Docker y Docker Compose instalados  
- Python ≥ 3.12  
- Acceso root al servidor  
- Git configurado con credenciales válidas  

---

## 📂 Estructura del proyecto

```
/monitoring
├── cron/                # Definiciones de cronjobs y tareas programadas
├── log_ingestor/        # Scripts Python para ingesta y procesado de logs
├── observability/       # Configuración de Loki, Promtail y Grafana
├── postgres/            # Contenedor PostgreSQL (BBDD real)
├── resource_monitor/    # Monitorización de recursos Docker
├── scripts/             # Wrappers bash para tareas periódicas
├── smtp_relay/          # Servicio Postfix SMTP relay para alertas
├── Dockerfile.base      # Imagen base común
├── Makefile             # Tareas de build/despliegue
└── requirements.txt     # Dependencias Python
```

## ⚙️ Configuración técnica

⏱️ **Cron / Supercronic Jobs** 

Tareas programadas en `cron/monitoring.cron`:

| Frecuencia | Script | Descripción |
|-------------|---------|-------------|
| Diario | `auditoria_binarios.sh` | Verificación de integridad de binarios |
| Cada 10 min | `docker_resources.sh` | Control de recursos Docker |
| Cada 10 min | `log_ingest_batch.sh` | Ingesta de logs del sistema |
| 10:00 / 22:00 | `alert_risk.sh` | Envío de alertas de riesgo |
| @reboot | `configure_docker_limits.sh` | Aplicación de límites de CPU/memoria |

🐳 **Dockerfile base** 

```dockerfile
FROM python:3.12-slim AS monitoring-base

WORKDIR /opt/monitoring
RUN apt-get update && apt-get install -y --no-install-recommends docker-cli bash && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
```

📦 **Dependencias (requirements.txt)**

```
psycopg2-binary>=2.9
python-dotenv>=1.0.0
requests>=2.32
pandas>=2.2
numpy>=1.26
```

⚙️ **Variables de entorno (ejemplo .env — SMTP Relay)**

```env
SMTP_RELAY_CONTAINER_NAME=smtp-relay

# Configuración SMTP común
SMTP_SERVER = smtp.postmarkapp.com
SMTP_PORT = 9999

# Postmark SMTP credentials
EMAIL_FROM = noreply@tudominio.com
EMAIL_DOMAIN = tudominio.com
EMAIL_TO = contacto@tudominio.com

# Redes permitidas para relay
MYNETWORKS = 127.0.0.0/8 172.16.0.0/12 [::1]/128

# Configuración de la base de datos
DB_HOST = postgres
DB_NAME = monitoring_db
DB_USER = user
DB_PASSWORD = 999999999
DB_PORT = 9999
```

---

## 🧠 Componentes principales

### 🧩 `log_ingestor`
Procesa logs del sistema (auth.log, kern.log, Fail2Ban).  
Detecta patrones sospechosos y guarda los eventos en PostgreSQL.  
Scripts destacados:
- `log_ingest_batch.py` — Ingesta principal
- `log_ip_geolocation.py` — Añade localización geográfica
- `alert_risk.py` — Evalúa riesgo y dispara alertas por correo

### 🧩 `resource_monitor`
Controla recursos de contenedores Docker en tiempo real:
- CPU, memoria, swap
- Límites definidos en `docker-compose.yml`
Scripts:
- `docker_resources.py` / `.sh`  
- `configure_docker_limits.sh` — Reajuste de límites

### 🧩 `observability`
Stack **Promtail + Loki + Grafana** para centralizar logs.  
- `promtail-config.yaml` define etiquetas y filtrado.  
- `loki-config.yaml` gestiona almacenamiento local y retención (72h).  
- `grafana` se integra con SMTP relay para alertas.  

### 🧩 `smtp_relay`
Contenedor Postfix que actúa como **relay seguro** hacia `smtp.postmarkapp.com`.  
Permite envío de alertas desde cualquier componente del sistema.

---

## 🚀 Instalación

```bash
Clonar el repositorio:

cd /opt/monitoring
git clone https://github.com/eboe62/server_monitoring_2509.git
Configurar variables de entorno y credenciales según cada servicio (ejemplo para SMTP Relay):

cd /opt/monitoring
nano smtp_relay/.env

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

# Añadir el siguiente código al crontab del servidor
[root]$ crontab -e
# Configurar permisos y ejecutar configure_docker_limits.sh al reiniciar
@reboot chmod +x /usr/local/bin/configure_docker_limits.sh && sleep 60 && /bin/bash /usr/local/bin/configure_docker_limits.sh > /var/log/configure_docker_limits.log 2>&1

# Ejecutar configure_docker_limits.sh cada 10 minutos
*/10 * * * * /usr/local/bin/configure_docker_limits.sh > /var/log/configure_docker_limits.log 2>&1

# Configuramos la prevención de saturación por ataques masivos
@reboot /opt/monitoring/scripts/apply_ssh_ratelimit.sh > /var/log/apply_ssh_ratelimit.log 2>&1

```
## 🚀 Uso

El proyecto incorpora un **Makefile global** que permite construir, desplegar y gestionar los contenedores principales sin necesidad de recordar comandos largos de Docker.  
Basta con anteponer la palabra `make` al comando correspondiente.

```
▶️ Levantar el servicio de email para el envío de alertas
cd /opt/monitoring/smtp_relay
make up

Inicia el contenedor SMTP Relay encargado del envío de alertas y notificaciones por correo.
```
```
▶️ Despliegue completo de todo el stack (SMTP, Python, Cron)
cd /opt/monitoring
make deploy

Ejecuta la reconstrucción completa, levanta los servicios SMTP, Python y Cron, y muestra los últimos logs al finalizar.
Tras el despliegue, verificar los contenedores activos:
docker ps
```
```
▶️ Verificar logs:
make logs

Muestra los logs más recientes del sistema. 
```
```
▶️ Arrancar contenedores Python y Cron
make deploy-python

Levanta el contenedor Python (backup_resotre, etc.)
```
```
▶️ Desplegar solo Cron
cd /opt/monitoring
make deploy-cron

Levanta el contenedor Cron (supercronic con jobs definidos)

Ambos comandos reconstruyen automáticamente la imagen base si es necesario y arrancan los servicios correspondientes dentro de sus rutas (/opt/monitoring/python o /opt/monitoring/cron).
```
```
▶️ Restauración de Backups de PostgreSQL
make restore-backup


Internamente ejecuta el script:
bash /opt/monitoring/scripts/backup_restore.sh

Los resultados y el estado del proceso se registran en:
cat /var/log/backup_restore.log

💡 Este proceso realiza la restauración dentro del contenedor monitoring-python, comunicándose con el contenedor monitoring-postgres para reconstruir la base de datos a partir del último backup disponible en /opt/monitoring/backups/.
```
```
▶️ Despliegue centralizado de Observability (Grafana, Loki, Promtail)
cd /opt/monitoring
make deploy-observability


Reinicia completamente el stack de observabilidad
Este comando permite reconstruir desde cero y relanzar Grafana, Loki y Promtail, asegurando un entorno limpio de logs y métricas.
```
```
▶️ Reconstruir imágenes desde cero (sin cache)
make rebuild
Reconstruye todas las imágenes (base, python y cron) sin usar cache.
```
```
▶️ Otras funcionalidades no definidas en Makefile
cd /opt/monitoring/

Ejecución manual de auditorías y limpieza:
./scripts/docker_resources.sh
./scripts/cleanup_docker.sh 

⚠️ ATENCION: Antes de ejecutar limpieza, crea un snapshot previo — existe riesgo de pérdida no deseada de binarios.
```

---

## 🧩 Honeypot PostgreSQL (CapRover)

La antigua base de datos `srv-captain--security250226app` se mantiene activa como **honeypot controlado**:
- Red aislada `captain-overlay-network`  
- Sin credenciales válidas  
- Permisos mínimos y sin volúmenes compartidos  
- Monitorización de tráfico HTTP/HTTPS a través de `nginx + Promtail`

Esto permite detectar intentos de reconexión, redirecciones fraudulentas o modificaciones no autorizadas.

---

## 🔒 Acciones preventivas clave

1. **Endurecimiento honeypot**: permisos mínimos, red y volúmenes aislados.  
2. **Supervisión temprana**: etiquetado `honeypot=true` en Promtail.  
3. **Integridad/auditoría**: checksum de nginx y revisión binarios.  
4. **Control de exposición**: filtrar IPs y fijar versión de nginx.  
5. **Persistencia evidencias**: logs ≥7 días + exportación periódica.  
6. **Seguridad general**: PostgreSQL fuera de CapRover + rate-limiting global.  

---

## 💡 Recomendaciones

- No usar `:latest` en imágenes críticas (nginx, grafana, postgres).  
- Revisar `logs_summary.txt` y `logs_summary_aaaammdd.txt` tras cada snapshot.  
- Hacer snapshot previo antes de ejecutar `cleanup_docker.sh`.  
- Validar alertas enviadas desde `alert_risk.py` dos veces al día.

---

## 🧾 Licencia y autoría

Proyecto interno de prácticas **DigitalOcean Monitoring Stack (IaC)**  
Desarrollado por: **@eboe62**  
📅 **Última actualización:** 2025-10-10  
