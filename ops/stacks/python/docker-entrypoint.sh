#!/bin/sh

echo "[INFO] monitoring-python iniciado"

echo "[INFO] esperando disponibilidad de Postgres..."

# Espera activa a Postgres (resiliencia real)
until python3 -c '
import os, psycopg2, sys
try:
    psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        dbname=os.getenv("POSTGRES_NAME")
    )
except Exception as e:
    print(f"[WAIT] postgres no disponible: {e}")
    sys.exit(1)
'; do
  sleep 2
done

echo "[OK] conexión a Postgres disponible"

# Loop principal
while true; do
if [ -f /opt/monitoring/tu_script.py ]; then
  python3 /opt/monitoring/tu_script.py
  STATUS=$?

  if [ "$STATUS" -ne 0 ]; then
    echo "[WARN] fallo script → reintentando con espera de DB..."

    # Espera activa a DB en runtime (NO solo en arranque)
    until python3 -c '
import os, psycopg2, sys
try:
    psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        dbname=os.getenv("POSTGRES_NAME")
    )
except Exception:
    sys.exit(1)
'; do
      sleep 2
    done

    echo "[OK] DB recuperada, siguiente iteración"
  fi
else
  echo "[WARN] script no encontrado, modo idle"
fi
sleep 10
done
