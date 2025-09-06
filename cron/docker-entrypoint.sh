#!/bin/sh
set -e

echo "[INFO] Arrancando supercronic con cronfile: /opt/monitoring/cronjobs/monitoring.cron"
exec /usr/local/bin/supercronic /opt/monitoring/cronjobs/monitoring.cron

