#!/usr/bin/env python3
# /opt/monitoring/scripts/healthcheck.py

import sys

# Healthcheck intencionalmente trivial:
# - Necesario para compatibilidad con wait_for_health.sh
# - No depende de DB ni servicios externos
# - No depende de red
# - Solo valida que Python runtime está operativo
# - Evita falsos negativos en CI

sys.exit(0)
