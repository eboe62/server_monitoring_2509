#!/bin/sh
set -e

echo "[INFO] monitoring-python iniciado"
echo "[INFO] modo toolbox (docker exec)"

# Validación mínima runtime
python3 --version || exit 1

# --------------------------------------------------
# CONTEXTO DEL CONTENEDOR
# --------------------------------------------------
# Este contenedor NO es un servicio.
# NO ejecuta procesos de negocio automáticamente.
# NO expone API.
# NO actúa como worker ni scheduler.
#
# Su único propósito es servir como entorno de ejecución
# para scripts Python lanzados manualmente o desde Makefile:
#
# Ejemplos:
#   docker exec monitoring-python python3 script.py
#   docker exec monitoring-python python3 ops/.../test_mail.py
#
# Casos de uso:
#   ✔ tests E2E (SMTP, DB, etc.)
#   ✔ scripts de diagnóstico
#   ✔ utilidades operativas
#   ✔ tareas ad-hoc
#
# --------------------------------------------------
# DECISIONES DE DISEÑO
# --------------------------------------------------
# - No depende de Postgres ni otros servicios en arranque
# - No tiene lógica interna ni bucles de negocio
# - No implementa retry/backoff global
# - Cada script es responsable de su propia resiliencia
#
# Esto evita:
#   ✘ estados inconsistentes (CI vs PROD)
#   ✘ falsos negativos en healthchecks
#   ✘ acoplamiento innecesario a la infraestructura
#
# --------------------------------------------------
# LIFECYCLE
# --------------------------------------------------
# El contenedor se mantiene vivo únicamente para permitir
# la ejecución de comandos vía "docker exec".
#
# No hacer exit automático es clave para:
#   ✔ debugging interactivo
#   ✔ ejecución repetida de scripts
#   ✔ estabilidad en pipelines CI
#
# --------------------------------------------------

# Mantener contenedor vivo de forma determinista
tail -f /dev/null
