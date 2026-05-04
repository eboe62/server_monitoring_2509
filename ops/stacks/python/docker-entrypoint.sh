#!/bin/sh
set -e

# Copiar secrets a ubicación accesible si existen
if [ -d "/run/secrets" ]; then
    echo "[INFO] Copiando secrets..."
    mkdir -p /run/secrets-copy
    cp -r /run/secrets/* /run/secrets-copy/ 2>/dev/null || true
    chmod -R 600 /run/secrets-copy || true
fi

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

# --------------------------------------------------
# Si se pasa comando → ejecutar como appuser
# --------------------------------------------------
if [ "$#" -gt 0 ]; then
    exec "$@"
fi

# --------------------------------------------------
# Modo idle (contenedor vivo para docker exec)
# --------------------------------------------------
echo "[INFO] monitoring-python en modo idle (listo para docker exec)"
exec tail -f /dev/null
