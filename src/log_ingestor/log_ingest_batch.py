#!/usr/bin/env python3
# log_ingest_batch.py
import re
import subprocess
import os
from datetime import datetime
from monitoring.common.config import log_info, connect_db, close_db, init_config

LOG_FILE = "/var/log/auth.log"

# Expresiones regulares para detectar ataques
regex_patterns = [
    # Para casos como: "Disconnected from invalid user X Y port Z"
    r"\[(?P<log_ref>\d+)\]: (?P<reason>(Invalid user|invalid user|Connection closed by invalid user|Disconnected from invalid user)) ?(?P<user>\S*?) ?from (?P<ip>[0-9.]+) port (?P<port>[0-9]+)",
    # Para casos de desconexión como "Disconnected from <IP> port <port> [preauth]"
    r"\[(?P<log_ref>\d+)\]: (?P<reason>(Connection closed by|Connection reset by|Disconnected from authenticating user|Received disconnect from|Disconnected from)) (?:(?P<authenticating>authenticating user) )?(?:(?P<user>\S+) )?(?P<ip>[0-9.]+) port (?P<port>[0-9]+)",
    # Para casos como: "Unable to negotiate with Y port Z"
    r"\[(?P<log_ref>\d+)\]: (?P<reason>(Unable to negotiate)) (?:with )?(?:from )?(?P<ip>[0-9.]+) port (?P<port>[0-9]+)",
    r"\[(?P<log_ref>\d+)\]: (?P<reason>(error: maximum authentication attempts exceeded|Disconnecting authenticating user)) (?:for )?(?P<user>\S+) (?:with )?(?:from )?(?P<ip>[0-9.]+) port (?P<port>[0-9]+)",
    # Para casos como: "Accepted publickey for user X from Y port Z"
    r"\[(?P<log_ref>\d+)\]: (?P<reason>(Accepted publickey)) (?:for )?(?P<user>\S+) (?:with )?(?:from )?(?P<ip>[0-9.]+) port (?P<port>[0-9]+) ssh2: .+",
]
# Nombres descriptivos para cada tipo de log
pattern_names = [
    "03_invalid_user",
    "08_connection_out",
    "02_no_negotiate",
    "04_attempts_exceeded",
    "06_login_accepted",
]

# Función para actualizar el número de ataques por IP
def update_attacking_no():
    conn, cursor = None, None
    try:
        conn = connect_db()
        if not conn:
            log_info("[ERROR] No se pudo establecer conexión a la base de datos.")
            return

        cursor = conn.cursor()
        cursor.execute("SELECT update_attacking_no();")
        conn.commit()
        log_info(f"[OK] attacking_no actualizado correctamente.")
    except Exception as e:
        log_info(f"[ERROR] Error actualizando attacking_no: {e}")
    finally:
        close_db(cursor, conn)

# Obtener el último timestamp registrado en la base de datos
def get_last_timestamp():
    conn, cursor = None, None
    try:
        conn = connect_db()
        if not conn:
            log_info("[ERROR] No se pudo establecer conexión a la base de datos.")
            return

        cursor = conn.cursor()
        cursor.execute("SELECT MAX(timestamp) FROM attacking_logs")
        result = cursor.fetchone()

        return result[0] if result and result[0] else None
    except Exception as e:
        log_info(f"[ERROR] Error obteniendo el último timestamp: {e}")
        return None
    finally:
        close_db(cursor, conn)

# Función para convertir el timestamp del log a formato datetime
def parse_timestamp(log_line):
    try:
        match = re.match(r"^([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]+[+-][0-9]{2}:[0-9]{2})", log_line)
        if match:

            return datetime.fromisoformat(match.group(1))  # Convierte la fecha ISO directamente
    except ValueError as e:
        log_info(f"[WARN] Error al parsear timestamp: {e}")
    return None

# Función para obtener logs desde el último timestamp
def get_log_lines():
    # La ingestion de logs en el host está desactivada por defecto, para forzar el registro mediante contenedores.
    if os.environ.get("ALLOW_HOST_LOGS", "false").lower() != "true":
        log_info("[WARN] Ingestión desactivada en el host. Establece ALLOW_HOST_LOGS=true para activarla (no recomendado).")
        return []

    if not os.path.exists(LOG_FILE):
        log_info(f"[ERROR] El archivo de log {LOG_FILE} no existe.")
        return []

    last_timestamp = get_last_timestamp()

    pattern = r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]+[+-][0-9]{2}:[0-9]{2} .*"
    command = ["grep", "-E", pattern, LOG_FILE]

    try:
        result = subprocess.run(
            command, shell=False, text=True, capture_output=True, check=False
        )
        if result.returncode not in [0, 1]:  # 0 = encontrado, 1 = no encontrado
            log_info(f"[ERROR] Error inesperado al ejecutar grep, código: {result.returncode}")
            return []

        log_lines = result.stdout.strip().split("\n") if result.stdout else []
        log_info(f"[INFO] Líneas obtenidas del log: {len(log_lines)}")

        if last_timestamp:
            filtered_lines = [
                line for line in log_lines if parse_timestamp(line) and parse_timestamp(line) > last_timestamp
            ]
            log_info(f"[INFO] Líneas después del filtrado: {len(filtered_lines)}")
            return filtered_lines

        return log_lines
    except subprocess.CalledProcessError as e:
        log_info(f"[ERROR] Error al ejecutar el comando grep: {e}")
        return []

# Función para insertar registros en la base de datos
def insert_into_db(entries):
    conn, cursor = None, None
    try:
        conn = connect_db()
        if not conn:
            log_info("[ERROR] No se pudo establecer conexión a la base de datos.")
            return

        cursor = conn.cursor()
        query = """
        INSERT INTO attacking_logs (
            timestamp, log_type, log_ref, attacking_octets, attacking_ip, attacking_user, attacking_port)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.executemany(query, entries)
        conn.commit()
        log_info(f"[OK] {len(entries)} registros insertados en la base de datos.")
        update_attacking_no()

    except Exception as e:
        log_info(f"[ERROR] Error al insertar en la base de datos: {e}")
    finally:
        close_db(cursor, conn)

# Función para procesar los logs y extraer información
def process_logs():
    log_info("[INFO] Iniciando procesamiento de logs...")
    log_lines = get_log_lines()
    log_info(f"[INFO] Total de líneas obtenidas del log: {len(log_lines)}")
    if not log_lines:
        log_info("[INFO] No hay nuevas líneas en el log.")
        return

    batch_data = []

    for log_line in log_lines:
        timestamp = parse_timestamp(log_line)
        if not timestamp:
            continue  # Si no tiene timestamp válido, ignorar

        for i, regex in enumerate(regex_patterns):
            match = re.search(regex, log_line)
            if match:
                log_ref = int(match.group('log_ref')) if 'log_ref' in match.groupdict() else None
#                reason = match.group('reason') if 'reason' in match.groupdict() else "N/A"
                user = match.group('user') if 'user' in match.groupdict() else "N/A"
                ip = match.group('ip') if 'ip' in match.groupdict() else "N/A"
                port = match.group('port') if 'port' in match.groupdict() else None
                ip_group = ".".join(ip.split('.')[:3]) if ip != "N/A" else "N/A"

                batch_data.append((
                    timestamp,
                    pattern_names[i],
                    log_ref,
                    ip_group,
                    ip,
                    user,
                    int(port) if port else None
                ))
                break

    if batch_data:
        insert_into_db(batch_data)

if __name__ == "__main__":
    # Inicializar configuración sensible en tiempo de ejecución (carga .env y secrets)
    # Relay-only: este entrypoint no requiere credenciales SMTP
    init_config()
    process_logs()
