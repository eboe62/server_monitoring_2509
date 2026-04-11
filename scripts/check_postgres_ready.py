import os
import sys
import time
import psycopg2

MAX_RETRIES = int(os.getenv("POSTGRES_READY_RETRIES", 10))
SLEEP_SECONDS = int(os.getenv("POSTGRES_READY_SLEEP", 3))

def check():
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            dbname=os.getenv("POSTGRES_NAME"),
        )
        conn.close()
        return True
    except Exception as e:
        print(f"[WAIT] PostgreSQL no disponible: {e}")
        return False

def main():
    for attempt in range(1, MAX_RETRIES + 1):
        if check():
            print("[OK] PostgreSQL listo")
            sys.exit(0)

        print(f"[RETRY] intento {attempt}/{MAX_RETRIES}")
        time.sleep(SLEEP_SECONDS)

    print("[ERROR] PostgreSQL no disponible tras múltiples intentos")
    sys.exit(1)

if __name__ == "__main__":
    main()
