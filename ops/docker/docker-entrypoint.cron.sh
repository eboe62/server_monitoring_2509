#!/bin/sh
set -e

echo "[INFO] Arrancando supercronic con cronfile: /opt/monitoring/cron/monitoring.cron"
exec /usr/local/bin/supercronic /opt/monitoring/cron/monitoring.cron

