#!/bin/bash
set -e

echo "[INIT] esperando PostgreSQL..."
python3 scripts/check_postgres_ready.py

echo "[INIT] arrancando servicio python..."
exec python3 -m monitoring.main
