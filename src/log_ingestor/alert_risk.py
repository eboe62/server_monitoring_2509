#!/usr/bin/env python3
# alert_risk.py
import html
from monitoring.common.config import (
    log_info,
    send_email,
    init_config,
    connect_db,
    close_db,
    build_html_table,
    get_month_gap,
)

# Las credenciales SMTP se gestionan exclusivamente desde
# monitoring.common.config.init_config() en tiempo de ejecución.
# Este módulo no debe definir ni leer credenciales en import-time.

# ==========================================
# ALERTA: Atacantes que han conseguido entrar en el servidor
# ==========================================

# Configuramos un máximo de filas a mostrar por tabla (None = sin límite)
MAX_ROWS_PER_TABLE = None
# Configuramos un periodo temporal (meses)
MONTH_GAP = 4

def process_alert():
    """
    Genera alerta de IPs que han conseguido acceder al servidor
    y envía el resultado por correo.
    """

    log_info(f"[📌]: INICIO TEST: Atacantes que han conseguido entrar en el servidor")

    # ==========================================
    # Conectar a la base de datos
    # ==========================================
    conn, cursor = None, None
    html_table = ""  # Inicializamos para evitar NameError
    html_parts = []
    email_to = None

    try:
        conn = connect_db()
        if not conn:
            log_info(f"[ERROR] No se pudo establecer conexión a la base de datos.")
            return

        cursor = conn.cursor()

        # ==========================================
        # Cálculo de fechas (como strings ISO)
        # ==========================================
        hoy, primer_dia_mes_actual, primer_dia_mes_inicio, fecha_anterior_str = get_month_gap(MONTH_GAP)

        log_info(f"[ℹ️ ]: Cálculo fechas: hoy={hoy}, desde={primer_dia_mes_inicio}")
        log_info(f"[ℹ️ ]: Fecha límite usada en query: desde {fecha_anterior_str} hasta {hoy.strftime('%Y-%m-%d')}")

        # ==========================================
        # Consulta SQL para obtener amenazas de alto riesgo
        # ==========================================
        query = f"""
            WITH attacks_last_period AS (
                SELECT *
                FROM public.attacking_logs
                WHERE attacking_octets IS NOT NULL
                AND timestamp >= NOW() - INTERVAL '1 day'
            ),
            attack_counts AS (
                SELECT
                    attacking_octets,
                    COUNT(*) AS attack_count
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
--                    alp.id,
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

        # ==========================================
        # Ejecutar query
        # ==========================================
        cursor.execute(query)
        rows = cursor.fetchall()

        if not rows:
            log_info(f"[INFO] No se ha completado el reporte de amenazas con riesgo > 6")
            return

        log_info(f"[OK] Se detectaron {len(rows)} amenazas con riesgo > 6.")

        # ==========================================
        # Construimos las filas omitiendo los id
        # ==========================================
        for row in rows:
            timestamp, log_ref, log_type, attacking_no, attacking_ip, attacking_user, attacking_port, attacking_country, attacking_town, risk_score = row

        # ==========================================
        # Construcción del HTML
        # ==========================================
        head_text = (
            f"Se han detectado las siguientes amenazas de alto riesgo:"
        )
        intro_text = (
            "La IP's indicadas a continuación han conseguido acceder al servidor vía SSH"
        )
        reasons_text = (
            "Nota: Algunas de las IP's identificadas corresponden a las de los propios administradores del servidor"
        )


        html_parts.append("<html><body>")
        html_parts.append("<br>")
        html_parts.append(f"<h3>{html.escape(head_text)}</h3>")
        html_parts.append("<br>")
        html_parts.append(f"<p>{html.escape(intro_text)}</p>")

        headers = ["Fecha","Referencia","Tipo","Ataques","IP","Usuario","Puerto","País","Ciudad","Riesgo"]

        html_parts.append(
            build_html_table(
                headers=headers,
                rows=rows,
                title="Tabla: IP's que han conseguido entrar en el servidor",
                max_rows=MAX_ROWS_PER_TABLE,
            )
        )

        html_parts.append("<br>")
        html_parts.append(f"<p>{html.escape(reasons_text)}</p>")
        html_parts.append("<br>")
        html_parts.append(
            "<p>Un saludo<br>"
            "AppVisibility<br>"
            "http://www.appvisibility.es/"
            "</p>"
        )
        html_parts.append("</body></html>")

        html_body = "\n".join(html_parts)

            # ==========================================
            # Envio del resultado por correo usando el contenedor smtp-relay que gestiona Postfix
            # ==========================================
        subject = "🚨 Alerta: Ataques de alto riesgo"
        send_email(subject, html_body)
        email_to=""
        try:
            send_email(
                subject,
                html_body,
                email_to,
                cc_list=[""]
            )
            log_info(f"[📧]: Enviado a ...{email_to} con CC a ...")
        except Exception as e:
            log_info(f"[ERROR] El envío ha fallado: {e}")

    except Exception as e:
        log_info(f"[ERROR] Error en la consulta o procesamiento del mail de alerta: {e}")
    finally:
        close_db(cursor, conn)

# ==========================================
# MAIN
# ==========================================
if __name__ == "__main__":
    # Inicializar configuración sensible en tiempo de ejecución
    # - carga .env
    # - carga secrets si SMTP_MODE=auth
    # - modo relay no no requiere credenciales SMTP; usar relay-only explícito
    init_config()
    process_alert()
