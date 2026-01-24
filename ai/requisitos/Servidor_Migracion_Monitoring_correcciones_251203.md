# 251203 - Documento único: 3 Documentos IaC + Archivos corregidos

Fecha: 2025/12/03

Contenido:
1) Documento A — Estado actual y análisis (Arquitectura IaC actual)
2) Documento B — Arquitectura IaC ideal (diseño objetivo)
3) Documento C — Plan delta: pasos concretos para migración y pruebas

---

# Documento A — Estado actual y análisis (Arquitectura IaC actual)

## Resumen ejecutivo

Actualmente el proyecto `server_monitoring_2509` construye imágenes Docker (`monitoring-base`, `monitoring-python`, `monitoring-cron`, `smtp_relay`, etc.) y copia el código fuente dentro de las imágenes. Los jobs se programan con cron (host o contenedor según el servicio) y existen scripts bash en `scripts/` que pueden ejecutarse tanto desde el host como desde contenedores. El objetivo es que el sistema sea 100% Infrastructure as Code (IaC).

## Elementos clave detectados

- Dockerfile.base usa `FROM python:3.12-slim` y ejecuta `pip install -r requirements.txt`.
- Se copia todo el proyecto dentro de la imagen (`COPY . .`), por lo que la ejecución ideal debe correr dentro de contenedores.
- Existe un `venv/` dentro de `log_ingestor/` (posible uso local) y hay contenedores `monitoring-python` y `monitoring-cron` que deberían ser las runtimes reales.
- Actualmente hay scripts en el host que a veces llaman `python3` del host (error detectado: `ModuleNotFoundError: No module named 'psycopg2'`).

## Problemas encontrados que rompen la pureza IaC

1. Algunos cronjobs o invocaciones directas ejecutan el `python3` del host en lugar del Python de la imagen/contendor.
2. Scripts `*.sh` con rutas absolutas a `/usr/local/bin/python3` suponen un runtime local (host), que no coincide con el runtime containerizado.
3. Faltan controles que forcen la ejecución dentro de contenedor, o wrappers que detecten el entorno.
4. Código Python con bugs menores (ej.: shadowing de `datetime`, firma de `send_email` inconsistente, llamadas a variables no inicializadas) que hemos corregido en los archivos adjuntos.

## Implicaciones

- Ejecutar en host hace que dependencias instaladas en la imagen (psycopg2, requests, dotenv, etc.) no estén disponibles → fallos en producción.
- Pérdida de reproducibilidad: si el host ejecuta cosas, el estado ya no es solo lo que define el repositorio + imagen.

## Recomendaciones inmediatas (corto plazo)

- Forzar que todos los jobs se ejecuten con `docker exec <container> python3 -m ...`.
- Convertir scripts en entrypoints o incluirlos en la imagen para que el host no ejecute lógica Python directamente.
- Añadir detección de entorno en scripts para evitar ejecuciones accidentales con Python del host.

---

# Documento B — Arquitectura IaC ideal (diseño objetivo)

## Principios

1. **Todo el runtime está en imágenes reproducibles**: el estado de ejecución depende únicamente de las imágenes generadas por CI/CD a partir del repo.
2. **No ejecutar Python de host**: los hosts solo gestionan contenedores (scheduler), no ejecutan lógica de aplicación.
3. **Declarativo**: uso de docker-compose / stack + jobs en contenedor (supercronic) para programar tareas.
4. **Configuración gestionada por variables de entorno y secret management**: .env para dev, Vault/DO secrets en prod.

## Componentes

- `monitoring-base`: imagen base con dependencias instaladas (requirements.txt). No contiene cron.
- `monitoring-python`: imagen para ejecutar procesos python (entrypoint: supervisión o ejecución de jobs). Incluye scripts y `supercronic` o `cron` minimal configurado.
- `monitoring-cron`: si se quiere segregar, esta imagen ejecuta `supercronic` con `monitoring.cron` montado y lanza los comandos internamente en lugar de usar `docker exec` desde host.
- `smtp_relay`, `postgres`, `grafana`, `loki`, `promtail` tal como ya están: orquestados por docker-compose / swarm.

## Flujos

1. CI construye imágenes (tag con SHA + semver) y las sube al registry.
2. Infra (IaC) despliega stack con imágenes versionadas.
3. Cronjobs se ejecutan dentro del contenedor `monitoring-cron` (o `monitoring-python` con supercronic). Si se requiere acceder a otros contenedores, usar la red Docker compartida.
4. Logs y alertas se envían desde contenedores; no hay dependencias locales.

## Seguridad y secretos

- No copiar secretos en imágenes (no almacenar credenciales en `COPY`).
- Usar Docker secrets o un secret manager; en Docker Compose v3.8 usar `secrets`.

---

# Documento C — Plan delta: pasos concretos para migración y pruebas

## Objetivo

Pasar del estado actual a un despliegue 100% IaC donde todos los jobs Python se ejecutan en contenedores reproducibles.

## Precondiciones

- Acceso root al host y privilegios Docker.
- CI/CD capaz de construir imágenes o permiso para usar `docker build` localmente.

## Paso 0 — Backups

- Hacer snapshot del droplet (DigitalOcean).
- Exportar .env y secrets a backup seguro.

## Paso 1 — Cambios en repositorio (commit)

1. Mover/duplicar `scripts/*.sh` dentro de `docker/entrypoints/` o `bin/` del repo y marcar ejecutables.
2. Modificar `cron/monitoring.cron` para que los jobs invocen comandos locales **dentro** del contenedor (si vas a usar supercronic en contenedor) o se mantengan y ejecuten `docker exec` desde host.

## Paso 2 — Modificar scripts problemáticos

- Reemplazar en `scripts/alert_risk.sh` la línea que usa `/usr/local/bin/python3` por `docker exec -i monitoring-python python3 -m log_ingestor.alert_risk`.
- Alternativa: mover `monitoring.cron` dentro del contenedor y ejecutar `supercronic` en la imagen `monitoring-cron`.

## Paso 3 — Incluir pruebas unitarias/integ

- Añadir `tests/` para: `common/config.py` funciones: `build_html_table`, `send_email` (mock SMTP), `normalize_date`.
- Ejecutar en CI con la imagen base.

## Paso 4 — Rebuild y deploy en staging

- `docker-compose -f docker-compose.staging.yml build --pull --no-cache`.
- `docker-compose -f docker-compose.staging.yml up -d`.

## Paso 5 — Validación

- Ejecutar manualmente dentro del contenedor:
  `docker exec -it monitoring-python python3 -m log_ingestor.alert_risk`
- Revisar logs en `log_ingestor/alert_risk.log`.
- Verificar envío de correo (usar SMTP simulador / stub en staging).

## Paso 6 — Promoción a producción

- Tag de release y despliegue con `docker stack deploy` o `docker-compose` según tu flujo.

## Rollback

- Si algo falla, usar snapshot o versiones anteriores de imágenes.

---

# Archivos corregidos (lista) — para sustituir en el repo

- common/config.py
- log_ingestor/alert_risk.py
- scripts/alert_risk.sh
- cron/monitoring.cron (sugerencia)
- Makefile (nuevo opcional)


---
# Archivo: common/config.py (CORREGIDO)

#!/usr/bin/env python3
# config.py
import os
import smtplib
from dotenv import load_dotenv
import psycopg2
from email.mime.text import MIMEText
from email.utils import formataddr
from email.mime.multipart import MIMEMultipart
from datetime import datetime, date
import re
import socket
import html
import requests

# Carga .env
load_dotenv("/opt/monitoring/smtp_relay/.env")

SMTP_SERVER = os.getenv("SMTP_SERVER", "127.0.0.1")
SMTP_PORT   = int(os.getenv("SMTP_PORT", "2526"))
with open("/opt/monitoring/smtp_relay/secrets/smtp_user") as f:
    SMTP_USER = f.read().strip()
with open("/opt/monitoring/smtp_relay/secrets/smtp_pass") as f:
    SMTP_PASS = f.read().strip()

EMAIL_FROM  = os.getenv("EMAIL_FROM")
EMAIL_TO    = os.getenv("EMAIL_TO")
CC_LIST     = os.getenv("CC_LIST", "").split(",") if os.getenv("CC_LIST") else []
SUBJECT     = os.getenv("SUBJECT", "📊 Informe del estado de droplet")

DB = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "name": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}


def connect_db():
    try:
        conn = psycopg2.connect(
            host=DB["host"],
            port=DB["port"],
            dbname=DB["name"],
            user=DB["user"],
            password=DB["password"],
            connect_timeout=5,
            keepalives=1,
        )
        log_info(f"[✅]: Conexión a la base de datos exitosa.")
        return conn
    except Exception as e:
        log_info(f"[❌]: Error conectando a la base de datos: {e}")
        return None


def close_db(cursor=None, conn=None):
    if cursor:
        try:
            cursor.close()
        except Exception as e:
            log_info(f"[⚠️]: Error cerrando cursor: {e}")

    if conn:
        try:
            conn.close()
            log_info("[✅]: Conexión a la base de datos cerrada.")
        except Exception as e:
            log_info(f"[⚠️]: Error cerrando conexión: {e}")


def send_email(subject: str, html_content: str, email_to: str = None, cc_list: list = None):
    if cc_list is None:
        cc_list = []

    subject  = subject or SUBJECT
    email_to = email_to or EMAIL_TO
    cc_list  = cc_list or CC_LIST

    is_html = bool(re.search(r"<[^>]+>", html_content))

    if is_html:
        plain_text = re.sub(r"<[^>]+>", "", html_content)
        msg = MIMEMultipart("alternative")
        msg.attach(MIMEText(plain_text, "plain", "utf-8"))
        msg.attach(MIMEText(html_content, "html", "utf-8"))
    else:
        msg = MIMEText(html_content, "plain", "utf-8")

    msg["From"] = formataddr(("AppVisibility Monitoring", EMAIL_FROM))
    msg["To"] = email_to
    msg["Cc"] = ", ".join(cc_list)
    msg["Subject"] = subject

    try:
        smtp_host_ipv4 = socket.getaddrinfo(SMTP_SERVER, SMTP_PORT, socket.AF_INET)[0][4][0]
        with smtplib.SMTP(smtp_host_ipv4, SMTP_PORT, timeout=10) as server:
            log_info(f"[ℹ️ ]: Conectando al servidor SMTP...")
            server.ehlo()

            if SMTP_SERVER not in ("localhost", "127.0.0.1"):
                log_info(f"[ℹ️ ]: Usando servidor SMTP externo, iniciando TLS...")
                server.starttls()
                server.ehlo()
                log_info(f"[ℹ️ ]: TLS iniciado.")

            if SMTP_USER and SMTP_PASS:
                server.login(SMTP_USER, SMTP_PASS)
                log_info(f"[ℹ️ ]: Autenticación SMTP exitosa.")

            recipients = [email_to] + cc_list
            server.sendmail(EMAIL_FROM, recipients, msg.as_string())
            log_info(f"[📧]: Enviado a {email_to} con CC a {', '.join(cc_list) or '(sin CC)'}")

        return True

    except Exception as e:
        log_info(f"[❌]: Error enviando correo: {e}")
        return False


def to_snake_case(name: str) -> str:
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def normalize_date(value):
    if isinstance(value, str):
        try:
            if "/" in value:
                return datetime.strptime(value, "%d/%m/%Y").strftime("%Y-%m-%d")
        except Exception:
            pass
    return value


def log_info(msg: str):
    print(f"gda-info: {datetime.now().isoformat()} - {msg}")


def format_date(d):
    if d is None:
        return ""
    try:
        return d.strftime('%Y-%m-%d')
    except Exception:
        return str(d)


def safe(value):
    if value is None or value == "":
        return "---"
    return html.escape(str(value))


def build_html_table(headers, rows, title, max_rows=None):
    shown_rows = rows if (max_rows is None) else rows[:max_rows]
    html_block = []

    html_block.append(f"<p>{html.escape(title.upper())}</p>")
    html_block.append("<br>")
    html_block.append('<table border="1" cellpadding="4" cellspacing="0" style="border-collapse: collapse; width:80%;">')

    num_cols = len(headers)
    html_block.append("<colgroup>")
    for _ in range(num_cols):
        html_block.append(f'<col style="width: {100/num_cols}%;">')
    html_block.append("</colgroup>")

    html_block.append("<thead><tr style='background-color:#f2f2f2;'>")
    for h in headers:
        html_block.append(f"<th>{html.escape(h)}</th>")
    html_block.append("</tr></thead>")

    html_block.append("<tbody>")
    for row in shown_rows:
        html_block.append("<tr>")
        for c in row:
            if isinstance(c, (datetime, date)):
                cell = format_date(c)
            else:
                cell = safe(c)
            html_block.append(f"<td>{cell}</td>")
        html_block.append("</tr>")
    html_block.append("</tbody></table>")

    if (max_rows is not None) and (len(rows) > max_rows):
        html_block.append(f"<p><em>Se muestran las primeras {max_rows} filas de {len(rows)} encontradas.</em></p>")

    return "\n".join(html_block)


# get_ip_info (usa requests)
IPINFO_TOKEN = os.getenv("IPINFO_TOKEN")

def get_ip_info(ip):
    url = f"https://ipinfo.io/{ip}/json?token={IPINFO_TOKEN}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return {
            "country": data.get("country", "Unknown"),
            "city": data.get("city", "Unknown"),
            "lat": data.get("loc", "0,0").split(",")[0],
            "long": data.get("loc", "0,0").split(",")[1]
        }
    except requests.exceptions.RequestException as e:
        log_info(f"[❌] Error obteniendo datos para {ip}: {e}")
        return None

---

# Archivo: log_ingestor/alert_risk.py (CORREGIDO)

#!/usr/bin/env python3
# alert_risk.py

from common.config import log_info, send_email, connect_db, close_db, build_html_table
import html

MAX_ROWS_PER_TABLE = None


def process_alert():
    conn, cursor = None, None
    html_parts = []

    try:
        conn = connect_db()
        if not conn:
            log_info("[❌]: No se pudo establecer conexión a la base de datos.")
            return

        cursor = conn.cursor()

        query = """
            WITH attacks_last_period AS (
                SELECT *
                FROM public.attacking_logs
                WHERE attacking_octets IS NOT NULL
                AND timestamp >= NOW() - INTERVAL '1 day'
            ),
            attack_counts AS (
                SELECT attacking_octets, COUNT(*) AS attack_count
                FROM attacks_last_period
                GROUP BY attacking_octets
            ),
            attack_counts_ranked AS (
                SELECT attacking_octets,
                    attack_count,
                    NTILE(10) OVER (ORDER BY attack_count) AS attack_count_category
                FROM attack_counts
            ),
            log_type_diversity AS (
                SELECT attacking_octets,
                    CASE WHEN BOOL_OR(log_type IN ('06_login_accepted','05_connection_in'))
                        THEN 10
                        ELSE LEAST(COUNT(DISTINCT log_type),108)
                    END AS log_type_category
                FROM attacks_last_period
                GROUP BY attacking_octets
            ),
            top_attacks AS (
                SELECT DISTINCT ON (alp.attacking_octets)
                    alp.id,
                    alp.timestamp,
                    alp.log_ref,
                    alp.log_type,
                    alp.attacking_no,
                    alp.attacking_ip,
                    alp.attacking_user,
                    alp.attacking_port,
                    alp.attacking_country,
                    alp.attacking_town,
                    ROUND((acr.attack_count_category * 0.4 + ltd.log_type_category * 0.6)::numeric, 2) AS risk_score
                FROM attacks_last_period alp
                JOIN attack_counts_ranked acr ON alp.attacking_octets = acr.attacking_octets
                JOIN log_type_diversity ltd ON alp.attacking_octets = ltd.attacking_octets
                ORDER BY alp.attacking_octets, alp.attacking_no DESC
            )
            SELECT *
            FROM top_attacks
            WHERE risk_score > 6
            ORDER BY risk_score DESC;
        """

        cursor.execute(query)
        rows = cursor.fetchall()

        if not rows:
            log_info("[ℹ️]: No se ha completado el reporte de amenazas con riesgo > 6")
            return

        log_info(f"[✅]: Se detectaron {len(rows)} amenazas con riesgo > 6.")

        html_parts.append("<html><body><br>")
        html_parts.append("<h3>Se han detectado las siguientes amenazas de alto riesgo:</h3><br>")

        headers = ["Fecha","Referencia","Tipo","Ataques","IP","Usuario","Puerto","País","Ciudad","Riesgo"]
        html_parts.append(build_html_table(headers, rows, "Tabla: IP's que han conseguido entrar en el servidor", MAX_ROWS_PER_TABLE))

        html_parts.append("<br><p>Un saludo<br>AppVisibility<br>http://www.appvisibility.es/</p></body></html>")

        html_body = "\n".join(html_parts)

        subject = "🚨 Alerta: Ataques de alto riesgo"

        # Envío principal, usando valores por defecto de config si no se especifica email
        send_email(subject, html_body)

    except Exception as e:
        log_info(f"[❌]: Error en la consulta o procesamiento del mail de alerta: {e}")
    finally:
        close_db(cursor, conn)


if __name__ == "__main__":
    process_alert()

---

# Archivo: scripts/alert_risk.sh (CORREGIDO)

#!/bin/bash
# Ejecutar el job dentro del contenedor monitoring-python (asegúrate de que exista)

CONTAINER_NAME=monitoring-python
LOGFILE=/opt/monitoring/log_ingestor/alert_risk.log

if sudo docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    sudo docker exec -i ${CONTAINER_NAME} python3 -m log_ingestor.alert_risk >> ${LOGFILE} 2>&1
else
    # fallback: intentar con nombre parcial
    CID=$(sudo docker ps --filter ancestor=monitoring-python --format '{{.ID}}' | head -n1)
    if [ -n "$CID" ]; then
        sudo docker exec -i $CID python3 -m log_ingestor.alert_risk >> ${LOGFILE} 2>&1
    else
        echo "[ERROR] Contenedor ${CONTAINER_NAME} no encontrado" >> ${LOGFILE}
    fi
fi

---

# Archivo: cron/monitoring.cron (SUGERENCIA actualizada)

# Usar docker exec para garantizar ejecución en el contenedor
*/10 * * * * /opt/monitoring/scripts/log_ingest_batch.sh
*/10 * * * * /opt/monitoring/scripts/log_fail2ban_batch.sh
*/10 * * * * /opt/monitoring/scripts/log_kern_batch.sh
*/10 * * * * /opt/monitoring/scripts/log_ip_geolocation.sh
*/10 * * * * /opt/monitoring/scripts/log_honeypot_geolocation.sh
0 12,22 * * * /opt/monitoring/scripts/alert_risk.sh

---

# Archivo: Makefile (opcional, nuevo)

.PHONY: alert-risk shell build

alert-risk:
	@echo "Ejecutando alert_risk dentro del contenedor..."
	sudo docker exec -i monitoring-python python3 -m log_ingestor.alert_risk

shell:
	sudo docker exec -it monitoring-python bash

build:
	docker build -t monitoring-base -f Dockerfile.base .
	docker build -t monitoring-python -f python/Dockerfile .

---

# Notas finales y advertencias

- He corregido los puntos más urgentes: import de datetime, firma de send_email, uso correcto de send_email desde alert_risk, y evitado variables no inicializadas.
- He preparado el wrapper `scripts/alert_risk.sh` para forzar `docker exec` (esto es fundamental para IaC puro).
- No modifiqué Dockerfiles ni requirements.txt: asumo que tu pipeline/CI ya instala `psycopg2` y `requests`. Si falla dentro del contenedor, deberás reconstruir la imagen y revisar `requirements.txt`.

---

FIN DEL ARCHIVO

