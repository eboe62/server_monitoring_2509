#!/usr/bin/env python3
# log_ip_geolocation.py
import requests
import time
from common.config import log_info, connect_db, close_db

# Configuración
IPINFO_TOKEN = "9620b4b5ca0f27"  # Reemplaza con tu token de ipinfo.io

# Función para obtener datos de geolocalización
def get_ip_info(ip):
    url = f"https://ipinfo.io/{ip}/json?token={IPINFO_TOKEN}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Lanza error si la solicitud falla
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

# Función para actualizar la base de datos
def update_database():
    conn, cursor = None, None
    try:
        conn = connect_db()
        if not conn:
            log_info("[❌]:  No se pudo establecer conexión a la base de datos.")
            return

        cursor = conn.cursor()

        # Seleccionar IPs sin datos de geolocalización
        cursor.execute("""
            SELECT DISTINCT attacking_ip
            FROM attacking_logs
            WHERE attacking_country IS NULL OR attacking_country = ''
        """)
        ips = [row[0] for row in cursor.fetchall()]
        log_info(f"[ℹ️] Se encontraron {len(ips)} IPs para actualizar.")

        for ip in ips:
#            log_info(f"[🌍] Obteniendo datos para {ip}...")
            ip_info = get_ip_info(ip)
            if ip_info:
                cursor.execute("""
                    UPDATE attacking_logs
                    SET attacking_country = %s,
                        attacking_town = %s,
                        attacking_long = %s,
                        attacking_lat = %s
                    WHERE attacking_ip = %s
                """, (ip_info["country"], ip_info["city"], ip_info["long"], ip_info["lat"], ip))
                conn.commit()
#                log_info(f"[✅] {ip} actualizado correctamente.")
                time.sleep(1)  # Evitar rate-limiting

        cursor.close()
    except Exception as e:
        log_info(f"[❌] Error inesperado: {e}")
    finally:
        close_db(cursor, conn)


if __name__ == "__main__":
    update_database()
