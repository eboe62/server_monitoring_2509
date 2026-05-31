import os
import sys
import time
import psycopg2
from monitoring.common.secrets import load_secret
from monitoring.common.config import log_info

MAX_RETRIES = int(os.getenv("POSTGRES_READY_RETRIES", 10))
SLEEP_SECONDS = int(os.getenv("POSTGRES_READY_SLEEP", 3))

def check():
    try:
        pg_password = load_secret('POSTGRES_PASSWORD_FILE', 'POSTGRES_PASSWORD')
        if pg_password is None:
            log_info("[WARN] No se encontró contraseña Postgres por fichero o variable; la conexión puede fallar")
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT"),
            user=os.getenv("POSTGRES_USER"),
            password=pg_password,
#            password=os.getenv("POSTGRES_PASSWORD"),
            dbname=os.getenv("POSTGRES_NAME"),
        )
        conn.close()
        return True
    except Exception as e:
        log_info(f"[WARN] PostgreSQL no disponible: {e}")
        return False

def main():
    for attempt in range(1, MAX_RETRIES + 1):
        if check():
            log_info("[OK] PostgreSQL listo")
            sys.exit(0)

        log_info(f"[RETRY] intento {attempt}/{MAX_RETRIES}")
        time.sleep(SLEEP_SECONDS)

    log_info("[ERROR] PostgreSQL no disponible tras múltiples intentos")
    sys.exit(1)

if __name__ == "__main__":
    main()
