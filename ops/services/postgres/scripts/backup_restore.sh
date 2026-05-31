#!/bin/bash
# Ejecuta el script de restauración dentro del contenedor monitoring-python
# y deja registro en el log del host.
# usa en el host el comando: bash /opt/monitoring/scripts/backup_restore.sh
# comprueba con el comando: cat /var/log/backup_restore.log

LOG_FILE="/var/log/backup_restore.log"

echo "$(date '+%Y-%m-%d %H:%M:%S') [INFO] Iniciando restauración dentro de monitoring-python..." >> "$LOG_FILE"

/usr/bin/docker exec -i monitoring-python \
  python3 /opt/monitoring/ops/services/postgres/scripts/backup_restore.py

if [ $? -eq 0 ]; then
  echo "$(date '+%Y-%m-%d %H:%M:%S') [OK] Restauración completada correctamente." >> "$LOG_FILE"
else
  echo "$(date '+%Y-%m-%d %H:%M:%S') [ERROR] Error durante la restauración. Revisa el log anterior." >> "$LOG_FILE"
fi
