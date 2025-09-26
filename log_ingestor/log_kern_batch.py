#!/usr/bin/env python3
# log_kern_batch.py
import re
import subprocess
import os
from datetime import datetime
from common.config import log_info, connect_db, close_db

# Configuración de la base de datos
# Cargar variables desde .env
load_dotenv("/opt/monitoring/smtp_relay/.env")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
LOG_FILE = "/var/log/kern.log"

# Expresiones regulares para detectar eventos de red (posibles ataques)
regex_patterns = [
    # 10_trafic_blocked: Detección de tráfico bloqueado por el firewall (INPUT DROP en iptables o nftables).
    # Indica intentos de conexión denegados, escaneos de puertos, tráfico malicioso o no permitido.
    r'INPUT DROP: IN=(?P<iface>\S+) OUT=\S* MAC=(?P<mac>(?:[\da-f]{2}:){5}[\da-f]{2}(?::[\da-f]{2})*) SRC=(?P<src_ip>\d{1,3}(?:\.\d{1,3}){3}) DST=(?P<dst_ip>\d{1,3}(?:\.\d{1,3}){3})[^I]*ID=(?P<log_ref>\d+) PROTO=(?P<proto>\w+) SPT=(?P<src_port>\d+) DPT=(?P<dst_port>\d+)',

    # 11_interface_multicast_promiscuous: Una interfaz virtual (veth) entra en modo especial como "promiscuous mode" (captura de todos los paquetes) o "allmulticast mode".
    # Ocurre comúnmente al iniciar contenedores en redes Docker; puede estar asociado a sniffers, IDS o bridges.
    r"(?P<iface>veth\w+): entered (promiscuous|allmulticast) mode",

    # 12_docker_interface_state_change: Cambios de estado (creación, conexión, etc.) de interfaces virtuales conectadas a bridges (docker0, docker_gwbridge, brX) de Docker.
    # P.e. cuando entra en blocking, forwarding o disabled state. Indican actividad de red de contenedores Docker.
    r"(?P<bridge>docker\d*|docker_gwbridge|br\d*): port \d+\((?P<iface>veth\w+)\) entered (?P<state>\w+) state",

    # 13_interface_rename: Una interfaz veth es renombrada a una interfaz de red interna del contenedor (eth0, eth1, etc.).
    # Suele ocurrir al iniciar el contenedor, útil para trazabilidad de interfaces y contenedores.
    r"(?P<to_iface>eth\d+): renamed from (?P<from_iface>veth\w+)",

    # 14_interface_unregister: Desregistro de interfaces veth cuando es eliminada p.e. al detener un contenedor.
    # La interfaz sale de modo promiscuo/multicast y se desvincula del bridge.
    r"(?P<iface>veth\w+) \(unregistering\): left (promiscuous|allmulticast) mode",

    # 15_port_scan: Captura intentos de escaneo de puertos en tráfico de entrada.
    # Muestra paquetes con puertos de destino múltiples (DPT), típico de reconocimiento activo en un ataque de escaneo de puertos
    r"\[(?P<log_ref>\d+)\] SRC= (?P<reason>(DPT=\d+)) ?MAC=(?P<user>\S*?) ?SRC=(?P<ip>[0-9.]+) ?SPT=(?P<port>[0-9]+)",
]

pattern_names = [
    "10_trafic_blocked",
    "11_interface_multicast_promiscuous",
    "12_docker_interface_state_change",
    "13_interface_rename",
    "14_interface_unregister",
    "15_port_scan"
]

# Función para actualizar el número de ataques por IP
def update_attacking_no():
    conn, cursor = None, None
    try:
        conn = connect_db()
        if not conn:
            log_info("[❌]:  No se pudo establecer conexión a la base de datos.")
            return

        cursor = conn.cursor()
        cursor.execute("SELECT update_attacking_no();")
        conn.commit()
        log_info(f"[✅]: attacking_no actualizado correctamente.")
    except Exception as e:
        log_info(f"[❌]: Error actualizando attacking_no: {e}")
    finally:
        close_db(cursor, conn)
            
# Obtener el último timestamp registrado en la base de datos
def get_last_timestamp():
    conn, cursor = None, None
    try:
        conn = connect_db()
        if not conn:
            log_info("[❌]:  No se pudo establecer conexión a la base de datos.")
            return

        cursor = conn.cursor()
        cursor.execute("SELECT MAX(timestamp) FROM kern_logs")
        result = cursor.fetchone()

        return result[0] if result and result[0] else None
    except Exception as e:
        log_info(f"[❌]: Error obteniendo el último timestamp: {e}")
        return None
    finally:
        close_db(cursor, conn)

# Función para convertir el timestamp del log a formato datetime
def parse_timestamp(log_line):
    try:
        match = re.match(r"^([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]+[+-][0-9]{2}:[0-9]{2})", log_line)
        if match:

            return datetime.fromisoformat(match.group(1))  # Convierte la fecha ISO 8601 directamente
    except ValueError as e:
        log_info(f"[⚠️]: Error al parsear timestamp: {e}")
    return None

# Función para obtener logs desde el último timestamp
def get_log_lines():
    if not os.path.exists(LOG_FILE):
        log_info(f"[❌]: El archivo de log {LOG_FILE} no existe.")
        return []

    last_timestamp = get_last_timestamp()
    pattern = r'^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]+[+-][0-9]{2}:[0-9]{2} .*'
    command = ["awk", f'/{pattern}/', LOG_FILE]

    try:
        result = subprocess.run(
            command, shell=False, text=True, capture_output=True, check=False
        )
        if result.returncode not in [0, 1]:  # 0 = encontrado, 1 = no encontrado
            log_info(f"[❌]: Error inesperado al ejecutar awk, código: {result.returncode}")
            return []

        log_lines = result.stdout.strip().split("\n") if result.stdout else []
        log_info(f"[📜]: Líneas obtenidas del log: {len(log_lines)}")

        if last_timestamp:
            filtered_lines = [
                line for line in log_lines if parse_timestamp(line) and parse_timestamp(line) > last_timestamp
            ]
            log_info(f"[⚡]: Líneas después del filtrado: {len(filtered_lines)}")
            return filtered_lines

        return log_lines
    except subprocess.CalledProcessError as e:
        log_info(f"[❌]: Error al ejecutar el comando awk: {e}")
        return []

# Función para insertar registros en la base de datos
def insert_into_db(entries):
    conn, cursor = None, None
    try:
        conn = connect_db()
        if not conn:
            log_info("[❌]:  No se pudo establecer conexión a la base de datos.")
            return

        cursor = conn.cursor()
        query = """
        INSERT INTO kern_logs (
            timestamp, log_type, log_ref, attacking_octets, attacking_ip, attacking_user, attacking_port, attacking_protocol, attacking_interface)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.executemany(query, entries)
        conn.commit()
        log_info(f"[✅]: {len(entries)} registros insertados en la base de datos.")
        update_attacking_no()

    except Exception as e:
        log_info(f"[❌]: Error al insertar en la base de datos: {e}")
    finally:
        close_db(cursor, conn)

# Función para procesar los logs y extraer información
def process_logs():
    log_info("[🚀]: Iniciando procesamiento de logs...")
    log_lines = get_log_lines()
    log_info(f"[📜]: Total de líneas obtenidas del log: {len(log_lines)}")
    if not log_lines:
        log_info("[🔍]: No hay nuevas líneas en el log.")
        return

    batch_data = []

    for log_line in log_lines:
        timestamp = parse_timestamp(log_line)
        if not timestamp:
            continue  # Si no tiene timestamp válido, ignorar

        for i, regex in enumerate(regex_patterns):
            match = re.search(regex, log_line)
            if match:
                data = match.groupdict()
                log_ref = int(data.get("log_ref", 0)) if "log_ref" in data else None
                ip = data.get("src_ip") or data.get("ip") or "N/A"
                mac = data.get("mac") or data.get("user") or "N/A"
                port = int(data.get("dst_port") or data.get("port", 0)) if "dst_port" in data or "port" in data else None
                proto = data.get("proto") or "N/A"
                iface = data.get("iface") or "N/A"
                ip_group = ".".join(ip.split('.')[:3]) if ip != "N/A" else "N/A"

                batch_data.append((
                    timestamp,
                    pattern_names[i],
                    log_ref,
                    ip_group,
                    ip,
                    mac,
                    port,
                    proto,
                    iface
                ))
                break  # Sólo el primer match relevante por línea

    if batch_data:
        insert_into_db(batch_data)

if __name__ == "__main__":
    process_logs()

