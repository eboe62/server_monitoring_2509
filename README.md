# Proyecto Monitoring Stack 2511
# DigitalOcean (v251120)

![Python](https://img.shields.io/badge/Python-3.12-blue.svg)
![Docker](https://img.shields.io/badge/Docker-enabled-0db7ed.svg)
![Status](https://img.shields.io/badge/Status-Operational-success.svg)
![License](https://img.shields.io/badge/Environment-DigitalOcean_2509-orange.svg)

---

## 📖 Descripción general

**Monitoring Stack 2511** es una plataforma modular de **monitorización y observabilidad 100% contenerizada (IaC = Infrastructure as Code)** para servidores Linux desplegada en un servidor **DigitalOcean**.

Incluye:
- Observabilidad (Grafana + Loki + Promtail)
- Ingesta y análisis de logs
- Monitorización de recursos
- Alertas por correo
- Honeypot PostgreSQL para detección de ataques

---

## 📖 Modelo de ejecución

### Principio fundamental (IaC)

1. El host **no ejecuta lógica de aplicación**
2. El host **solo gestiona Docker**
3. El estado se define por:
   - repositorio
   - imágenes Docker
   - volúmenes declarados
4. Toda ejecución de código ocurre dentro de:
    - monitoring-python
    - monitoring-cron
5. No existen dependencias implícitas del sistema operativo.
6. No se permiten ejecuciones manuales fuera del modelo declarativo.

### Regla arquitectónica

✔ Correcto:
- Ningún archivo Python se ejecuta por ruta absoluta.
- Siempre se ejecuta mediante: python3 -m paquete.modulo

Comando válido:
docker exec -it monitoring-python python3 -m log_ingestor.alert_risk

❌ Prohibido:
python3 src/log_ingestor/alert_risk.py
/usr/bin/python3 ...

---

## 🧩 Componentes principales

Aplicación (Micro-Stacks Autónomos)
- postgres → base de datos
- smtp-relay → envío de alertas

Runtime Interno (Infra-Stacks)
- monitoring-python → ejecución lógica
- monitoring-cron → scheduling (Supercronic)
- observability → Grafana + Loki + Promtail

------------------------------------------------------------------------

## 🏗️ Infraestructura
- Denominación:         `eob-250501a`
- Proveedor:            DigitalOcean
- Tipo de servidor:     Droplet virtualizado (KVM) – "DO-Regular"
- Arquitectura:         x86_64
- Sistema operativo:    Ubuntu 24.04.1 LTS (Noble Numbat)
- CPU:                  1 vCPU (Intel • KVM • modelo DO-Regular)
- RAM:                  2 GB
- Almacenamiento:       48 GB SSD (ext4) → /dev/vda1
- ip pública:           165.22.87.56
- Disk: 48GB SSD
- Ruta: /opt/monitoring

Repositorio:
[https://github.com/eboe62/server_monitoring_2509.git](https://github.com/eboe62/server_monitoring_2509.git)
Rama: `develop`

---

## ⚙️ Requisitos previos

- Docker
- Docker Compose v2
- Git
- Python ≥ 3.12
- Acceso root al servidor

---

## 📂 Estructura del proyecto

```
    server_monitoring/
    ├ Makefile                  # Tareas de build/despliegue
    ├ requirements.txt          # Dependencias Python
    ├ ai/                       # Prompts / requisitos generados con IA
    ├ config/                   # Configuración (Loki, Promtail…)
    ├ docs/                     # Documentación técnica y ADRs
    ├ ops/                      # Infraestructura como código / DevOps
    │ ├ deployment/             # setup_symlinks
    │ ├ images/
    │ │ └ base                  # Imagen base común
    │ ├ stacks/                 # Gestión de contenedores
    │ │ ├ python                # Servicio python específico del stack
    │ │ │ └ compose.yml
    │ │ ├ cron                  # Definicion de cronjob y tareas independiente del core
    │ │ │ └ compose.yml
    │ │ └ observability         # Configuración de Loki, Promtail y Grafana
    │ │   └ compose.yml
    │ └ services/
    │   ├ postgres/             # Micro-stack autónomo Servicio BBDD PostgreSQL
    │   │ ├ .env.template
    │   │ └ compose.yml
    │   └ smtp_relay/           # Micro-stack autónomo Servicio Postfix SMTP-relay para alertas
    │     ├ .env.template
    │     └ compose.yml
    ├ resources/                # Artefactos generados (logs_summary, etc.)
    ├ scripts/                  # Wrappers bash para tareas periódicas
    ├ src/                      # Código fuente Python ejecutable como módulos (-m)
    │ ├ log_ingestor/           # Scripts Python para ingesta y procesado de logs
    │ ├ common/                 # Utilidades comunes
    │ └ resource_monitor/       # Monitorización de recursos Docker
    └ tests/                    # Pruebas de funcionalidad
```
---

## 📂 Política de persistencia

El entorno utiliza exclusivamente volúmenes Docker locales para la persistencia de datos.
PostgreSQL se define como micro-stack autónomo, con sus propios volúmenes declarados en ops/services/postgres/compose.yml.

La persistencia de la base de datos queda desacoplada del resto de servicios y puede ser transferida de forma independiente mediante:
- dump lógico (pg_dump)
- restauración en nuevo servidor
- recreación declarativa del micro-stack

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


Modelo de programación de tareas
- No se utiliza cron del host.
- Todas las tareas programadas se ejecutan dentro del contenedor monitoring-cron.
- Supercronic es el scheduler oficial del proyecto.
- El host no contiene entradas crontab relacionadas con la aplicación.

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
POSTGRES_HOST = postgres
POSTGRES_NAME = monitoring_db
POSTGRES_USER = user
POSTGRES_PASSWORD = 999999999
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
- `promtail-config.yml` define etiquetas y filtrado.
- `loki-config.yml` gestiona almacenamiento local y retención (72h).
- `grafana` se integra con SMTP relay para alertas.

### 🧩 `smtp_relay`
Contenedor Postfix que actúa como **relay seguro** hacia `smtp.postmarkapp.com`.
Permite envío de alertas desde cualquier componente del sistema.

---

## ▶️ Configuración del host
El proyecto sigue el principio de Infraestructura como Código y no utiliza cron del host para ejecutar lógica de aplicación.

Todas las tareas programadas relacionadas con la aplicación se ejecutan dentro del contenedor monitoring-cron mediante Supercronic.

Sin embargo, algunas tareas de configuración del sistema se aplican directamente en el host durante el arranque o mediante automatización del sistema.

Ejemplos:
- configuración de límites Docker
- aplicación de rate-limiting SSH
- endurecimiento del sistema

Estas tareas pueden ejecutarse manualmente o integrarse en el sistema de inicialización del servidor.

Ejemplo de ejecución manual:
    # Añadir el siguiente código al crontab del servidor
    [root]$ crontab -e
    # Configurar permisos y ejecutar configure_docker_limits.sh al reiniciar
    @reboot chmod +x /usr/local/bin/configure_docker_limits.sh && sleep 60 && /bin/bash /usr/local/bin/configure_docker_limits.sh > /var/log/configure_docker_limits.log 2>&1

    # Ejecutar configure_docker_limits.sh cada 10 minutos
    */10 * * * * /usr/local/bin/configure_docker_limits.sh > /var/log/configure_docker_limits.log 2>&1

    # Configuramos la prevención de saturación por ataques masivos
    @reboot /opt/monitoring/scripts/apply_ssh_ratelimit.sh > /var/log/apply_ssh_ratelimit.log 2>&1

---

## ▶️ Clonar el repositorio:

```bash
cd /opt/monitoring
git clone https://github.com/eboe62/server_monitoring_2509.git
Configurar variables de entorno y credenciales según cada servicio (ejemplos .env.template):

cd /opt/monitoring
nano ops/services/smtp_relay/.env

Dar permisos a los scripts:
chmod +x ./scripts/*.sh


## 🚀 Despliegue completo por stacks

```bash
cd /opt/monitoring/
make phase4-init
make stack-up STACK=postgres
make stack-up STACK=smtp_relay
make stack-up STACK=python
make stack-up STACK=cron
make stack-up STACK=observability

Ejecuta la reconstrucción completa, levanta los servicios SMTP, Python, Cron.
Tras el despliegue, verificar los contenedores activos:
docker ps

---

## ▶️ Parar un stack

make stack-down STACK=xxx

---
## ▶️ Reiniciar

make stack-restart STACK=xxx

---

# 📊 VALORACIÓN DE ESTADO

## ▶️ Estado global

make doctor

Incluye:
- Docker instalado
- contenedores activos
- red
- disco
- volúmenes

---

## ▶️ Salud de contenedores

make health

Verifica:
- containers unhealthy
- restarting

---

## ▶️ Estado de un stack

make stack-status STACK=xxx

---

## 🚀 Uso

El proyecto incorpora un **Makefile global** que permite construir, desplegar y gestionar los contenedores principales sin necesidad de recordar comandos largos de Docker.
Basta con anteponer la palabra `make` al comando correspondiente.

```

## ▶️ Logs globales

make logs

---

Muestra los logs más recientes del sistema.

```
▶️ Restauración de Backups de PostgreSQL
make restore-backup

Internamente ejecuta el script:
bash /opt/monitoring/scripts/backup_restore.sh

Los resultados y el estado del proceso se registran en:
cat /var/log/backup_restore.log | tail -n 30

💡 Este proceso realiza la restauración dentro del contenedor monitoring-python, comunicándose con el contenedor monitoring-postgres para reconstruir la base de datos a partir del último backup disponible en /ops/backups/.
```
```
# 🔍 AUDITORÍA

## ▶️ Auditoría completa

make audit

Valida:
- estructura del repo
- docker-compose
- exposición de puertos
- uso de docker.sock
- cumplimiento ADR
./scripts/cleanup_docker.sh

---

# 🧪 DEBUGGING / OPERABILIDAD

## ▶️ Shell en contenedor

make debug-shell STACK=xxx

⚠️ Nota:
- Las imágenes son minimalistas → puede no haber bash, ps, ping

---


## 🔒 Modelo de Seguridad

- PostgreSQL no se expone públicamente.
- Comunicación interna exclusivamente por red Docker.
- Exposición mínima de puertos.
- Secrets nunca versionados.
- Firewall UFW activo con política deny por defecto.

---

## 🧩 Honeypot PostgreSQL (CapRover)

La antigua base de datos `srv-captain--security250226app` se mantiene activa como **honeypot controlado**:
- Red aislada `captain-overlay-network`
- Sin credenciales válidas
- Permisos mínimos y sin volúmenes compartidos
- Monitorización de tráfico HTTP/HTTPS a través de `nginx + Promtail`

Esto permite detectar intentos de reconexión, redirecciones fraudulentas o modificaciones no autorizadas.


---

## 📜 Documentación adicional

La documentación técnica completa se encuentra en:
    docs/decisiones/
Incluye:
-   Definición del proyecto\
-   Implementación inicial\
-   Documento de migración\
-   Decisiones arquitectónicas (ADR)

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
3.  Envía un Product Release claro y bien documentado

------------------------------------------------------------------------

## 🛡 Licencia

Proyecto privado **DigitalOcean Monitoring Stack (IaC)**
Desarrollado por: **@eboe62**
📅 **Última actualización de este documento:** 2026-03-28
