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

```bash
monitoring/
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

## 🐳 Dockerfile base

```dockerfile
FROM python:3.12-slim AS monitoring-base

WORKDIR /opt/monitoring
RUN apt-get update && apt-get install -y --no-install-recommends docker-cli bash && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
```

---

## 📦 Dependencias (`requirements.txt`)

```text
psycopg2-binary>=2.9
python-dotenv>=1.0.0
requests>=2.32
pandas>=2.2
numpy>=1.26
```

---

## ⚙️ Variables de entorno (ejemplo .env — SMTP Relay)

```env
SMTP_RELAY_CONTAINER_NAME=smtp-relay
SMTP_SERVER=smtp.postmarkapp.com
SMTP_PORT=9999
EMAIL_FROM=noreply@tudominio.com
EMAIL_DOMAIN=tudominio.com
EMAIL_TO=contacto@tudominio.com
MYNETWORKS=127.0.0.0/8 172.16.0.0/12 [::1]/128

DB_HOST=srv-captain--security999999app
DB_NAME=security9999
DB_USER=user
DB_PASSWORD=999999999
```

---

## 🚀 Instalación

```bash
cd /opt/monitoring
git clone https://github.com/eboe62/server_monitoring_2509.git
cd server_monitoring_2509
chmod +x ./scripts/*.sh
make deploy
```

Verificar logs:
```bash
make logs
```

---

## ⏱️ Cron / Supercronic Jobs

Tareas programadas en `cron/monitoring.cron`:

| Frecuencia | Script | Descripción |
|-------------|---------|-------------|
| Diario | `auditoria_binarios.sh` | Verificación de integridad de binarios |
| Cada 10 min | `docker_resources.sh` | Control de recursos Docker |
| Cada 10 min | `log_ingest_batch.sh` | Ingesta de logs del sistema |
| 10:00 / 22:00 | `alert_risk.sh` | Envío de alertas de riesgo |
| @reboot | `configure_docker_limits.sh` | Aplicación de límites de CPU/memoria |

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
