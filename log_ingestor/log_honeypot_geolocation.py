#!/usr/bin/env python3
# log_honeypot_geolocation.py
import re
from datetime import datetime
from common.config import log_info, connect_db, close_db, get_ip_info
import glob, json

LOG_DIR = "/var/lib/docker/containers"

# Extraer de los logs las IPs
def extract_ips_from_log():
    """Lee los logs JSON de contenedores honeypot (nginx) y devuelve IPs únicas detectadas."""
    log_info(f"[✅]: Extrayendo IPs de {LOG_DIR} ...")
    ips = set()
    try:
        for log_file in glob.glob(f"{LOG_DIR}/*/*-json.log"):
            if "nginx" not in log_file and "caprover" not in log_file:
                continue
            with open(log_file, "r", errors="ignore") as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        if "log" in entry and any(c.isdigit() for c in entry["log"]):
                            match = re.search(r"([0-9]{1,3}(?:\.[0-9]{1,3}){3})", entry["log"])
                            if match:
                                ips.add(match.group(1))
                    except json.JSONDecodeError:
                        continue
        log_info(f"[ℹ️]: Se encontraron {len(ips)} IPs únicas.")
    except Exception as e:
        log_info(f"[❌]: Error leyendo contenedores Docker: {e}")
    return list(ips)

# Función para actualizar la base de datos
def update_database():
    """Inserta o actualiza IPs de honeypot_logs con información geográfica."""
    log_info(f"[✅]: Iniciando geolocalización de IPs...")
    ips = extract_ips_from_log()
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
                INSERT INTO honeypot_logs (attacking_ip, attacking_country, attacking_town, attacking_long, attacking_lat, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (attacking_ip) DO UPDATE
                SET attacking_country = EXCLUDED.attacking_country,
                    attacking_town = EXCLUDED.attacking_town,
                    attacking_long = EXCLUDED.attacking_long,
                    attacking_lat = EXCLUDED.attacking_lat,
                    timestamp = EXCLUDED.timestamp;
            """, (
                ip, ip_info["country"], ip_info["city"],
                ip_info["long"], ip_info["lat"], datetime.utcnow()
            ))
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
    update_database()
