#!/usr/bin/env python3
# log_ip_geolocation.py
import time
from monitoring.common.config import log_info, connect_db, close_db, get_ip_info, init_config

def extract_ips_from_bbdd():
    """Lee BBDD y extrae IPs sin datos de geolocalización."""
    log_info(f"[✅] Extrayendo IPs de tabla attacking_logs ...")
    conn, cursor = None, None
    ips = []
    try:
        conn = connect_db()
        if not conn:
            log_info(f"[❌]: No se pudo establecer conexión a la base de datos.")
            return ips

        cursor = conn.cursor()

        # Extraer de BBDD las IPs sin datos de geolocalización
        cursor.execute("""
            SELECT DISTINCT attacking_ip
            FROM attacking_logs
            WHERE attacking_country IS NULL OR attacking_country = '';
        """)
        ips = [row[0] for row in cursor.fetchall()]
        log_info(f"[ℹ️]: Se encontraron {len(ips)} IPs sin geolocalización.")

        cursor.close()
        log_info(f"[✅]: ... finalizada extracción de IPs de BBDD")
    except Exception as e:
        log_info(f"[❌] Error al extraer IPs: {e}")
    finally:
        close_db(cursor, conn)
    return ips

# Función para actualizar la base de datos
def update_database():
    """Actualiza IPs de attacking_logs con información geográfica."""
    log_info(f"[✅]: Iniciando geolocalización de IPs...")
    ips = extract_ips_from_bbdd()
    if not ips:
        log_info("[ℹ️]: No hay IPs pendientes de geolocalizar.")
        return

    conn, cursor = None, None
    try:
        conn = connect_db()
        if not conn:
            log_info(f"[❌]: No se pudo establecer conexión a la base de datos.")
            return

        cursor = conn.cursor()

        for ip in ips:
#            log_info(f"[🌍]: Obteniendo datos para {ip}...")
            ip_info = get_ip_info(ip)
            if not ip_info:
                continue
            cursor.execute("""
                UPDATE attacking_logs
                SET attacking_country = %s,
                    attacking_town = %s,
                    attacking_long = %s,
                    attacking_lat = %s
                WHERE attacking_ip = %s;
            """, (ip_info["country"], ip_info["city"], ip_info["long"], ip_info["lat"], ip))
            conn.commit()
#            log_info(f"[✅]: {ip} actualizado correctamente.")
            time.sleep(1)  # evita rate-limiting

        cursor.close()
    except Exception as e:
        log_info(f"[❌]: Error durante la geolocalización: {e}")
    finally:
        close_db(cursor, conn)
        log_info(f"[✅]: ... finalizada geolocalización")

if __name__ == "__main__":
    # Inicializar configuración sensible en tiempo de ejecución (carga .env y secrets)
    init_config()
    update_database()
