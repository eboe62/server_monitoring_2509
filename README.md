# Proyecto Monitoring Stack 2511
# DigitalOcean (v251120)

![Python](https://img.shields.io/badge/Python-3.12-blue.svg)
![Docker](https://img.shields.io/badge/Docker-enabled-0db7ed.svg)
![Status](https://img.shields.io/badge/Status-Operational-success.svg)
![License](https://img.shields.io/badge/Environment-DigitalOcean_2509-orange.svg)

---

## 📖 Descripción general

**Monitoring Stack 2511** es un plataforma modular de **monitorización y observabilidad 100% contenerizada (IaC)** para servidores Linux desplegada en un servidor **DigitalOcean**.


Incluye componentes para análisis de seguridad, ingesta de eventos,
monitorización de recursos y servicios auxiliares listos para
producción.

Inicialmente, la BBDD se gestionaba mediante **CapRover**, pero tras un incidente de redirección no autorizada (“cashmachine.ie”), se migró a un contenedor propio.
La antigua BBDD se mantiene ahora como **honeypot**, permitiendo detectar intentos de acceso o manipulación externos.

---

## 🧩 Características principales

El sistema integra modularmente:
-   **Ingesta y análisis de logs** del sistema (kernel, fail2ban, honeypot, etc.)
-   Procesamiento por lotes y normalización de eventos
-  **Monitorización de recursos Docker** (CPU, RAM, IO, contenedores, etc.)
-   Servicios complementarios:
    -   SMTP Relay independiente
    -   Cronjobs integrados
    -   Despliegue automatizado
    -   Docker Compose modular
    -   **Alertas por correo**
    -   **Honeypot Postgres** para detección temprana de ataques
-   Estructura profesional y escalable orientada a microservicios

------------------------------------------------------------------------

## 🏗️ Infraestructura en servidor
- Denominación:         `eob-250501a`
- Proveedor:            DigitalOcean
- Tipo de servidor:     Droplet virtualizado (KVM) – "DO-Regular"
- Arquitectura:         x86_64
- Sistema operativo:    Ubuntu 24.04.1 LTS (Noble Numbat)
- CPU:                  1 vCPU (Intel • KVM • modelo DO-Regular)
- RAM:                  2 GB
- Almacenamiento:       48 GB SSD (ext4) → /dev/vda1
- ip pública:           165.22.87.56

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
    server_monitoring/
    ├ Makefile                  # Tareas de build/despliegue
    ├ requirements.txt          # Dependencias Python
    ├ ai/                       # Prompts / requisitos generados con IA
    ├ config/                   # Configuración (Loki, Promtail…)
    ├ docs/                     # Documentación técnica y decisiones
    ├ ops/                      # Infraestructura / DevOps
    │ ├ cron/                   # Definicion de cronjob y tareas independiente del core
    │ ├ deployment/             # setup_symlinks
    │ ├ docker/                 # Gestión de contenedores
    │ │ ├ Dockerfile.base       # Imagen base común
    │ │ ├ cron                  # Servicio cron específico del stack
    │ │ ├ observability         # Configuración de Loki, Promtail y Grafana
    │ │ ├ postgres              # Servicio BBDD PostgreSQL específico del stack
    │ │ └ python                # Servicio python específico del stack
    │ └ services/smtp_relay/    # Servicio Postfix SMTP-relay para alertas
    ├ resources/                # Material auxiliar (logs locales, etc.)
    ├ scripts/                  # Wrappers bash para tareas periódicas
    ├ src/                      # Código principal (Python)
    │ ├ common/                 # Utilidades comunes
    │ ├ log_ingestor/           # Scripts Python para ingesta y procesado de logs
    │ └ resource_monitor/       # Monitorización de recursos Docker
    └ tests/                    # Pruebas de funcionalidad
```

---

## 📂 Política de persistencia

El entorno utiliza exclusivamente volúmenes Docker locales para la persistencia de datos (BBDD, logs y artefactos operativos).

No se emplea Block Storage externo ni servicios gestionados de persistencia.

La estrategia de recuperación ante desastre se basa en:
- snapshots del droplet a nivel de proveedor
- recreación declarativa de contenedores
- restauración lógica de datos cuando aplique

Este modelo es intencional y aceptado como parte del alcance PRO.

---

## ⚙️ Configuración técnica

⏱️ **Cron / Supercronic Jobs**

Tareas programadas en `ops/cron/monitoring.cron`:

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
nano ops/services/smtp_relay/.env

cd /opt/monitoring
nano ops/services/smtp_relay/secrets/smtp_user
=====================
99x9xx99-9x99-9x99-99x9-99xx9xxx9xxx (token https://postmarkapp.com)
=====================

cd /opt/monitoring
nano ops/services/smtp_relay/secrets/smtp_pass
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
cd /opt/monitoring/ops/services/smtp_relay
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
cat /var/log/backup_restore.log | tail -n 30

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
./ops/docker/docker_resources.sh
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

## 📜 Documentación adicional

La documentación técnica completa se encuentra en:
    docs/arquitectura/
Incluye:
-   Definición del proyecto\
-   Implementación inicial\
-   Documento de migración\
-   Decisiones arquitectónicas (ADR)

---

## 🤖 Servicios destacados

### SMTP Relay independiente

Se encuentra en:
    ops/services/smtp_relay/
Este servicio está diseñado para ser **replicable** en otros proyectos
sin dependencias del core.

---

## 💡 Recomendaciones

- No usar `:latest` en imágenes críticas (nginx, grafana, postgres).
- Revisar `logs_summary.txt` y `logs_summary_aaaammdd.txt` tras cada snapshot.
- Hacer snapshot previo antes de ejecutar `cleanup_docker.sh`.
- Validar alertas enviadas desde `alert_risk.py` dos veces al día.

---

## 🗺 Roadmap

-   [ ] Integración con Prometheus nativa\
-   [ ] Exportación de métricas personalizadas\
-   [ ] Dashboard Grafana dedicado\
-   [ ] Sistema de alertas extensible\
-   [ ] Test unitarios completos del pipeline de ingesta

---

## 🤝 Contribuir

1.  Haz un fork del repositorio\
2.  Crea una rama (`feature/nueva-funcionalidad`)\
3.  Envía un Product Rerlease claro y bien documentado

------------------------------------------------------------------------

## 🛡 Licencia

Proyecto privado **DigitalOcean Monitoring Stack (IaC)**
Desarrollado por: **@eboe62**
📅 **Última actualización de este documento:** 2025-11-24
