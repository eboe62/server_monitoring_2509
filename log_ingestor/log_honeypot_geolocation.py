#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# log_honeypot_geolocation.py
import time
from common.config import log_info, connect_db, close_db, get_ip_info
import re
import requests
from datetime import datetime, timezone

# Configuración
LOKI_URL = "http://loki:3100/loki/api/v1/query_range"
LOKI_QUERY = '{honeypot="true"}'
TIME_RANGE_MINUTES = 30  # rango de búsqueda en minutos hacia atrás

# Extraer de los logs las IPs
def extract_ips_from_loki():
    """Lee logs de Loki (nginx) y extrae IPs únicas del label honeypot=true."""
    log_info(f"[✅]: Extrayendo IPs de Loki ...")

    # Calcula rango de tiempo en nanosegundos
    end = int(datetime.now(timezone.utc).timestamp() * 1e9)
    start = end - (TIME_RANGE_MINUTES * 60 * 1e9)

    params = {
        "query": LOKI_QUERY,
        "start": int(start),
        "end": int(end),
        "limit": 5000
    }

    ips = set()
    try:
        response = requests.get(LOKI_URL, params=params, timeout=30)
        response.raise_for_status()  # Lanza error si la solicitud falla
        data = response.json()

        streams = data.get("data", {}).get("result", [])
        if not streams:
            log_info(f"[ℹ️]: No se encontraron logs con honeypot=true.")
            return []

        log_info(f"[ℹ️]: {len(streams)} streams de logs encontrados.")
        for stream in streams:
            values = stream.get("values", [])
            for _, line in values:
                match = re.search(r'([0-9]{1,3}(?:\.[0-9]{1,3}){3})', line)
                if match:
                    ips.add(match.group(1))

        log_info(f"[ℹ️]: Se encontraron {len(ips)} IPs únicas en Loki.")
    except Exception as e:
        log_info(f"[❌]: Error consultando Loki: {e}")

    return list(ips)

# Función para actualizar la base de datos
def update_database():
    """Inserta o actualiza IPs del honeypot_logs con información geográfica."""
    log_info(f"[✅]: Iniciando geolocalización de IPs...")
    ips = extract_ips_from_loki()

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
                ip, ip_info["country"], ip_info["city"], ip_info["long"], ip_info["lat"], datetime.now(timezone.utc)))
            conn.commit()
#            log_info(f"[✅]: {ip} actualizado correctamente.")
            time.sleep(1)  # evita rate-limiting

        cursor.close()
        log_info(f"[✅]: {len(ips)} IPs procesadas correctamente.")
    except Exception as e:
        log_info(f"[❌]: Error durante la geolocalización: {e}")
    finally:
        close_db(cursor, conn)
        log_info(f"[✅]: ... finalizada geolocalización")

if __name__ == "__main__":
    update_database()
