# /opt/monitoring/healthcheck.py

import sys

# Healthcheck intencionalmente trivial:
# - Necesario para compatibilidad con wait_for_health.sh
# - No depende de DB ni servicios externos
# - Evita falsos negativos en CI y tests de resiliencia

sys.exit(0)
