# /opt/monitoring/healthcheck.py
import os
import psycopg2
import sys

try:
    psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        dbname=os.getenv("POSTGRES_NAME")
    )
    sys.exit(0)
except Exception as e:
    print(f"[HEALTHCHECK FAIL] {e}")
    sys.exit(1)
