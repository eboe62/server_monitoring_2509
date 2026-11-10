#!/usr/bin/env python3
# alert_risk.py
"""
Alerta de la Línea A (cron diario 21:10 UTC).

Se revisa cada día. Lo urgente (🚨 y ⚠️) se envía el mismo día; el correo tranquilo (✅,
prueba de vida) solo cada ALERT_ROUTINE_EVERY_DAYS días (por defecto 3, cuota de correo).
Asuntos:
  🚨 asunto de alerta  -> hay IPs de riesgo > 6 que NO son de administración
  ✅ asunto tranquilo  -> solo accesos de administración (o ninguno)
  ⚠️ asunto de aviso   -> no se ha ingerido ninguna fila en 24 h (la cadena está parada)
  ⚠️ asunto de recursos -> el kernel ha matado (OOM) o reiniciado un contenedor (B5b)

Al final va la sección "Recursos" (memoria, pico, OOM, CPU frenada) leída del kernel:
resource_monitor/cgroup_resources.py. Si el montaje /host/cgroup no existe, se indica y sigue.

Las IPs de administración se declaran en ADMIN_IPS (.env del cron), nunca en el código.
No se ocultan: aparecen en su propio bloque, separadas de las amenazas.
"""
import datetime
import html
import ipaddress
import os
import sys

from monitoring.common.config import (
    log_info,
    send_email,
    init_config,
    connect_db,
    close_db,
    build_html_table,
)
from resource_monitor import cgroup_resources

# Las credenciales SMTP se gestionan exclusivamente desde
# monitoring.common.config.init_config() en tiempo de ejecución.
# Este módulo no debe definir ni leer credenciales en import-time.

# Máximo de filas a mostrar por tabla (None = sin límite)
MAX_ROWS_PER_TABLE = None

# Posición de attacking_ip en las filas que devuelve RISK_QUERY
IP_COLUMN = 4

HEADERS = ["Fecha", "Referencia", "Tipo", "Ataques", "IP", "Usuario", "Puerto", "País", "Ciudad", "Riesgo"]

# Riesgo = 40 % volumen de ataques (decil) + 60 % diversidad de tipos de log.
# Un login aceptado o una conexión entrante valen 10 en diversidad: riesgo >= 6,4.
RISK_QUERY = """
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
        SELECT
            attacking_octets,
            attack_count,
            NTILE(10) OVER (ORDER BY attack_count) AS attack_count_category
        FROM attack_counts
    ),
    log_type_diversity AS (
        SELECT
            alp.attacking_octets,
            CASE
                WHEN BOOL_OR(
                    alp.log_type = '06_login_accepted'
                    OR alp.log_type = '05_connection_in'
                )
                THEN 10
                ELSE LEAST(COUNT(DISTINCT alp.log_type), 108)
            END AS log_type_category
        FROM attacks_last_period alp
        GROUP BY alp.attacking_octets
    ),
    top_attacks AS (
        SELECT DISTINCT ON (alp.attacking_octets)
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

# Salud de la ingesta: si en 24 h no entra nada, la cadena está parada (fallo silencioso)
HEALTH_QUERY = """
    SELECT
        COUNT(*) FILTER (WHERE timestamp >= NOW() - INTERVAL '1 day'),
        MAX(timestamp)
    FROM public.attacking_logs;
"""


# ==========================================
# Clasificación (funciones puras: se prueban sin BBDD)
# ==========================================

def parse_admin_ips(value):
    """
    'a.b.c.d, 83.45., 10.0.0.0/8' -> lista de reglas.
    Tres formas admitidas:
      - IP exacta       (203.0.113.7)
      - prefijo de texto (203.0.113.)  para IPs domésticas que cambian
      - red CIDR        (203.0.113.0/24)
    """
    return [t.strip() for t in (value or "").split(",") if t.strip()]


def is_admin_ip(ip, rules):
    """True si la IP cumple alguna regla de ADMIN_IPS."""
    if not ip:
        return False
    ip = str(ip).strip()
    for rule in rules:
        if "/" in rule:
            try:
                if ipaddress.ip_address(ip) in ipaddress.ip_network(rule, strict=False):
                    return True
            except ValueError:
                continue
        elif rule.endswith((".", ":")):
            if ip.startswith(rule):
                return True
        elif ip == rule:
            return True
    return False


def classify_rows(rows, rules):
    """Separa las filas en (amenazas, administración) según ADMIN_IPS."""
    threats, admins = [], []
    for row in rows:
        (admins if is_admin_ip(row[IP_COLUMN], rules) else threats).append(row)
    return threats, admins


def routine_every_days():
    """Cada cuántos días sale el correo tranquilo (ALERT_ROUTINE_EVERY_DAYS, por defecto 3)."""
    try:
        return max(1, int(os.environ.get("ALERT_ROUTINE_EVERY_DAYS", "3")))
    except ValueError:
        return 3


def is_routine_day(day, every):
    """Día de correo tranquilo: cuenta días seguidos (sin saltos a fin de mes)."""
    return day.toordinal() % every == 0


def is_urgent(n_threats, rows_last_24h, n_oom):
    """Amenazas, cadena parada u OOM: el correo sale cualquier día."""
    return n_threats > 0 or rows_last_24h == 0 or n_oom > 0


def build_subject(n_threats, rows_last_24h, n_oom=0):
    """Asunto según el caso: se distingue sin abrir el correo."""
    oom_txt = f"el kernel ha matado o reiniciado {n_oom} contenedor{'es' if n_oom != 1 else ''}"
    if rows_last_24h == 0:
        return "⚠️ Monitorización: sin datos en 24 h"
    if n_threats > 0:
        subject = f"🚨 Alerta: {n_threats} amenazas de alto riesgo"
        return f"{subject} · ⚠️ {oom_txt}" if n_oom else subject
    if n_oom:
        return f"⚠️ Recursos: {oom_txt}"
    return "✅ Monitorización activa: sin amenazas"


# ==========================================
# Construcción del correo
# ==========================================

def build_html_body(threats, admins, rows_last_24h, last_ingest, resources_html=""):
    parts = ["<html><body>"]

    # Línea de salud: la prueba de que la cadena está viva
    last_txt = last_ingest.strftime("%Y-%m-%d %H:%M UTC") if last_ingest else "nunca"
    parts.append(
        "<p style='color:#555;'>Salud de la ingesta: "
        f"<strong>{rows_last_24h}</strong> filas en las últimas 24 h · última: {html.escape(last_txt)}</p>"
    )
    if rows_last_24h == 0:
        parts.append(
            "<p style='color:#b36b00;'><strong>⚠️ No ha entrado ningún registro en 24 h.</strong> "
            "Revisar los jobs de ingesta del cron (docker logs monitoring-cron).</p>"
        )

    # Bloque 1: amenazas
    parts.append("<h3 style='color:#c0392b;'>🚨 Amenazas de alto riesgo (riesgo &gt; 6)</h3>")
    if threats:
        parts.append(
            build_html_table(
                headers=HEADERS,
                rows=threats,
                title="IPs ajenas a la administración que superan el umbral",
                max_rows=MAX_ROWS_PER_TABLE,
            )
        )
    else:
        parts.append("<p>Sin amenazas en las últimas 24 h.</p>")

    # Bloque 2: prueba de vida (administración)
    parts.append("<h3 style='color:#7f8c8d;'>✅ Prueba de vida: accesos de administración</h3>")
    if admins:
        parts.append("<div style='color:#7f8c8d;'>")
        parts.append(
            build_html_table(
                headers=HEADERS,
                rows=admins,
                title="IPs declaradas en ADMIN_IPS",
                max_rows=MAX_ROWS_PER_TABLE,
            )
        )
        parts.append("</div>")
    else:
        parts.append("<p style='color:#7f8c8d;'>Sin accesos de administración en las últimas 24 h.</p>")

    # Bloque 3: recursos de los contenedores (B5b)
    if resources_html:
        parts.append(resources_html)

    parts.append(
        "<br><p>Un saludo<br>"
        "AppVisibility<br>"
        "http://www.appvisibility.es/"
        "</p>"
    )
    parts.append("</body></html>")
    return "\n".join(parts)


# ==========================================
# Proceso
# ==========================================

def process_alert():
    """
    Consulta riesgo y salud, clasifica y envía un único correo.
    Devuelve True si el correo se ha enviado.
    """
    log_info("[📌]: INICIO alert_risk")
    rules = parse_admin_ips(os.environ.get("ADMIN_IPS"))
    if not rules:
        log_info("[WARN] ADMIN_IPS vacío: todos los accesos se tratarán como amenazas")

    conn, cursor = None, None
    try:
        conn = connect_db()
        if not conn:
            log_info("[ERROR] No se pudo establecer conexión a la base de datos.")
            return False

        cursor = conn.cursor()
        cursor.execute(RISK_QUERY)
        rows = cursor.fetchall()
        cursor.execute(HEALTH_QUERY)
        rows_last_24h, last_ingest = cursor.fetchone()
    except Exception as e:
        log_info(f"[ERROR] Error en la consulta de riesgo: {e}")
        return False
    finally:
        close_db(cursor, conn)

    threats, admins = classify_rows(rows, rules)
    log_info(
        f"[INFO] Riesgo > 6: {len(threats)} amenazas, {len(admins)} de administración; "
        f"filas en 24 h: {rows_last_24h}"
    )

    # Recursos (B5b): un fallo aquí no debe impedir el correo de seguridad
    try:
        res_rows, map_time = cgroup_resources.collect()
        resources_html = cgroup_resources.build_html(res_rows, map_time)
        n_oom = cgroup_resources.count_oom(res_rows)
        log_info(f"[INFO] Recursos: {len(res_rows or [])} contenedores leídos; OOM/reinicios: {n_oom}")
    except Exception as e:
        log_info(f"[WARN] Recursos no disponibles: {e}")
        resources_html, n_oom = "", 0

    # Cuota de correo: el correo tranquilo solo cada N días; lo urgente sale siempre
    every = routine_every_days()
    today = datetime.date.today()
    if not is_urgent(len(threats), rows_last_24h, n_oom) and not is_routine_day(today, every):
        next_day = today + datetime.timedelta(days=(-today.toordinal()) % every)
        log_info(f"[INFO] Sin correo hoy: nada urgente; el correo tranquilo sale cada {every} días (próximo: {next_day})")
        return True

    subject = build_subject(len(threats), rows_last_24h, n_oom)
    html_body = build_html_body(threats, admins, rows_last_24h, last_ingest, resources_html)

    # Un solo envío (cuota de correo limitada): destinatario y copias desde EMAIL_TO / CC_LIST
    if send_email(html_content=html_body, subject=subject):
        log_info(f"[📧]: Correo enviado: {subject}")
        return True

    log_info("[ERROR] El envío del correo ha fallado (ver el log de send_email)")
    return False


# ==========================================
# MAIN
# ==========================================
if __name__ == "__main__":
    # Inicializar configuración sensible en tiempo de ejecución
    # - carga .env
    # - modo relay: no requiere credenciales SMTP
    init_config()
    # Código de salida != 0 si no se envía: supercronic lo registra como fallo, no como "ok"
    sys.exit(0 if process_alert() else 1)
