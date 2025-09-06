# log_ip_geolocation.py
import os
import requests
import psycopg2
import time
from datetime import datetime
from dotenv import load_dotenv
from common.utils import log_info

# Configuración
IPINFO_TOKEN = "9620b4b5ca0f27"  # Reemplaza con tu token de ipinfo.io

# Configuración de la base de datos
# Cargar variables desde .env
load_dotenv("/opt/monitoring/smtp_relay/.env")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

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

# Función para conectar a PostgreSQL
def connect_db():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            connect_timeout=5,
            keepalives=1
        )
        return conn
    except Exception as e:
        log_info(f"[❌] Error conectando a la base de datos: {e}")
        return None

# Función para actualizar la base de datos
def update_database():
    conn = connect_db()
    if not conn:
        return
    try:
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
        conn.close()
        log_info("[🏁] Proceso de actualización finalizado.")
    except psycopg2.Error as e:
        log_info(f"[❌] Error en la base de datos: {e}")
    except Exception as e:
        log_info(f"[❌] Error inesperado: {e}")

if __name__ == "__main__":
    update_database()
