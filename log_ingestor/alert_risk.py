# alert_risk.py
import os
import psycopg2
from datetime import datetime
from dotenv import load_dotenv
from common.utils import log_info, send_email

# Cargar variables desde .env
load_dotenv("/opt/monitoring/smtp_relay/.env")

with open("/opt/monitoring/smtp_relay/secrets/smtp_user") as f:
    SMTP_USER = f.read().strip()        # Clave API

with open("/opt/monitoring/smtp_relay/secrets/smtp_pass") as f:
    SMTP_PASS = f.read().strip()        # Clave API

# Configuración de la base de datos
# Cargar variables desde .env
load_dotenv("/opt/monitoring/smtp_relay/.env")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Función principal
def main():
    # 1. Conectar a la base de datos
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            connect_timeout=5
        )
        log_info("[✅]: Conexión a la base de datos exitosa.")
    except Exception as e:
        log_info(f"[❌]: Error conectando a la base de datos: {e}")
        return

    cursor = conn.cursor()
    try:
        # Consulta SQL para obtener amenazas de alto riesgo
        query = """
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
                        WHEN BOOL_OR(alp.log_type = '06_login_accepted' OR alp.log_type = '05_connection_in') THEN 10
                        ELSE LEAST(COUNT(DISTINCT alp.log_type), 108)
                    END AS log_type_category
                FROM attacks_last_period alp
                GROUP BY alp.attacking_octets
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

        if rows:
            log_info(f"[✅]: Se detectaron {len(rows)} amenazas con riesgo > 6.")

            # Genera informe HTML
            html_table = """
            <html>
            <body>
            <p><strong>Se han detectado las siguientes amenazas de alto riesgo:</strong></p>
            <table border="1" cellpadding="4" cellspacing="0" style="border-collapse: collapse;">
                <thead>
                    <tr style="background-color: #f2f2f2;">
                        <th>Fecha</th>
                        <th>Referencia</th>
                        <th>Tipo</th>
                        <th># Ataques</th>
                        <th>IP</th>
                        <th>Usuario</th>
                        <th>Puerto</th>
                        <th>País</th>
                        <th>Ciudad</th>
                        <th>Riesgo</th>
                    </tr>
                </thead>
                <tbody>
            """

            for row in rows:
                fecha, referencia, tipo, ataques, ip, user, port, pais, ciudad, riesgo = \
                    row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]
                html_table += f"""
                    <tr>
                        <td>{fecha.strftime('%Y-%m-%d %H:%M:%S')}</td>
                        <td>{referencia}</td>
                        <td>{tipo}</td>
                        <td>{ataques}</td>
                        <td>{ip}</td>
                        <td>{user}</td>
                        <td>{port}</td>
                        <td>{pais}</td>
                        <td>{ciudad}</td>
                        <td><strong>{riesgo}</strong></td>
                    </tr>
                """

            html_table += """
                </tbody>
                </table>
                </body>
                </html>
            """

            # 4. Enviar correo usando el contenedor smtp-relay que gestiona Postfix
            send_email("🚨 Alerta: Ataques de alto riesgo", html_table)
        else:
            log_info("[ℹ️]: No se ha completado el reporte de amenazas con riesgo > 7")

    except Exception as e:
        log_info(f"[❌]: Error en la consulta o procesamiento del mail de alerta: {e}")
    finally:
        try:
            cursor.close()
            conn.close()
            log_info("[✅]: Conexión a la base de datos cerrada.")
        except:
            pass

# Ejecutar script
if __name__ == "__main__":
    main()
