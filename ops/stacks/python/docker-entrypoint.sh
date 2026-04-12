#!/bin/sh

echo "[INFO] monitoring-python iniciado"

while true; do
  if [ -f /opt/monitoring/tu_script.py ]; then
    python3 /opt/monitoring/tu_script.py || echo "[WARN] fallo script"
  else
    echo "[WARN] script no encontrado, modo idle"
  fi
  sleep 10
done
