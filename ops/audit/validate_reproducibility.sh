#!/usr/bin/env bash
set -euo pipefail

# ------------------------------------------------------------
# Propósito:
#     Verificar la reproducibilidad de los archivos Compose y la trazabilidad de imágenes.
#
# Rol dentro de la arquitectura:
#     Es el validador de coherencia Compose/imágenes que detecta tags latest y falta de digest.
#
# Entradas principales:
#     Archivos Compose bajo ops/ y el estado de Docker Compose en el host.
#
# Salidas principales:
#     Mensajes de consola con FAIL/WARN/OK y código de salida 0/1.
#
# Relación con otros componentes:
#     Se invoca desde audit_repo_host.sh y puede ejecutarse como comprobación independiente.
#
# Relación con la gobernanza:
#     Soporta ADR-0028 y ADR-0029 al validar la reproducibilidad de imágenes y Compose.
#
# Observaciones:
#     No ejecuta builds ni transforma imágenes; solo evalúa la definición declarativa y sus referencias.
# ------------------------------------------------------------

FAILED=0

info(){ echo "[INFO] $1"; }
warn(){ echo "[WARN] $1"; }
fail(){ echo "[FAIL] $1"; FAILED=1; }
ok(){ echo "[OK] $1"; }

COMPOSE_FILES=$(find ops -name "compose*.yml" -o -name "compose.yml" 2>/dev/null | sort -u)

if [ -z "$COMPOSE_FILES" ]; then
  info "No se encontraron compose bajo ops"
else
  for f in $COMPOSE_FILES; do
    info "Validando $f"

    # 1) docker compose config
    if ! docker compose -f "$f" config >/dev/null 2>&1; then
      fail "$f: docker compose config falló"
    else
      ok "$f: compose válido"
    fi

    # 2) Prohibir :latest
    if grep -E "image:.*:latest" -n "$f" >/dev/null 2>&1; then
      LINES=$(grep -nE "image:.*:latest" "$f" || true)
      fail "$f: Uso de :latest detectado:\n$LINES"
    else
      ok "$f: sin :latest"
    fi

    # 3) Detectar imágenes sin digest upstream
    # Para cada línea image:, comprobar si contiene @sha256
    while IFS= read -r line; do
      # Extract line number and content
      num=$(printf "%s" "$line" | cut -d: -f1)
      content=$(printf "%s" "$line" | cut -d: -f2-)

      # Skip if contains @sha256
      if printf "%s" "$content" | grep -q "@sha256:"; then
        continue
      fi

      # Check if this service has a local build (look back 8 lines for 'build:')
      start=$(( num - 8 ))
      if [ "$start" -lt 1 ]; then start=1; fi
      context=$(sed -n "${start},${num}p" "$f" || true)

      if printf "%s" "$context" | grep -q "build:"; then
        # local build image — enforce explicit tag (no latest)
        if printf "%s" "$content" | grep -q ":latest"; then
          fail "$f:$num: imagen local con tag :latest — evitar"
        else
          ok "$f:$num: imagen local con tag explícito"
        fi
      else
        # upstream image without digest — fail reproducibility
        fail "$f:$num: imagen upstream sin digest (@sha256) — $content"
      fi

    done < <(grep -n "image:" "$f" || true)

  done
fi

# ==========================================
# 4) Detectar imágenes dangling en runtime
#
# IMPORTANTE:
# - dangling images pueden aparecer temporalmente
#   durante builds legítimos de Docker/BuildKit
# - no siempre representan problema real
# - generar FAIL aquí introduce falsos positivos
#
# Política:
# - WARN operacional
# - nunca bloquear auditoría por dangling images
# ==========================================

if command -v docker >/dev/null 2>&1; then

  dangling=$(docker images -f "dangling=true" -q || true)

  if [ -n "$dangling" ]; then

    warn "Imágenes dangling detectadas (IDs):\n$dangling"
    warn "Sugerencia: ejecutar 'make clean-dangling' tras despliegues o builds"

  else

    ok "No hay imágenes dangling"

  fi

else

  warn "docker no disponible — omitiendo detección dangling"

fi

if [ "$FAILED" -ne 0 ]; then
  echo ""
  echo "VALIDACIÓN FALLIDA: problemas de reproducibilidad detectados"
  exit 1
else
  echo ""
  echo "VALIDACIÓN OK: reproducibilidad básica verificada"
  exit 0
fi
