#!/usr/bin/env bash
set -euo pipefail

FAILED=0

info(){ echo "[INFO] $1"; }
warn(){ echo "[WARN] $1"; }
fail(){ echo "[FAIL] $1"; FAILED=1; }
ok(){ echo "[ OK ] $1"; }

DOCKERFILES=$(find . -type f -name Dockerfile | sort)

if [ -z "$DOCKERFILES" ]; then
  info "No Dockerfiles encontrados"
  exit 0
fi

for df in $DOCKERFILES; do
  info "Analizando $df"

  # ==========================================
  # 1) Detectar FROM con latest explícito
  # ==========================================

  LATESTS=$(grep -nE '^FROM\s+.*:latest([[:space:]]|$)' "$df" || true)

  if [ -n "$LATESTS" ]; then
    fail "$df: Uso de FROM :latest detectado:\n$LATESTS"
  else
    ok "$df: no usa FROM :latest explícito"
  fi

  # ==========================================
  # 2) Detectar FROM sin tag real
  #
  # Excluir:
  #   FROM ${BASE_IMAGE}
  #   FROM ${BASE_IMAGE:-valor}
  #
  # porque pueden resolverse mediante ARG.
  # ==========================================

  FROM_LINES=$(grep -nE '^FROM\s+' "$df" || true)

  if [ -n "$FROM_LINES" ]; then

    while IFS= read -r entry; do

      lineno=$(echo "$entry" | cut -d: -f1)
      line=$(echo "$entry" | cut -d: -f2-)

      image=$(echo "$line" | awk '{print $2}')

      # Ignorar variables ARG (${...})
      if echo "$image" | grep -qE '^\$\{.+\}$'; then
        warn "$df:$lineno FROM parametrizado mediante ARG: $image"
        continue
      fi

      # Si no contiene ":" ni "@sha256:"
      # asumimos latest implícito
      if ! echo "$image" | grep -q ":" \
         && ! echo "$image" | grep -q "@sha256:"; then

        fail "$df:$lineno FROM sin tag explícito (latest implícito): $image"

      fi

    done <<< "$FROM_LINES"

  fi

  # ==========================================
  # 3) Detectar requirements no fijados
  # (solo WARN)
  # ==========================================

  REQ_LINES=$(grep -n "COPY .*requirements.txt" "$df" || true)

  if [ -n "$REQ_LINES" ]; then

    REQ_FILE="requirements.txt"

    if [ -f "$(dirname "$df")/../requirements.txt" ]; then
      REQ_FILE="$(dirname "$df")/../requirements.txt"

    elif [ -f "requirements.txt" ]; then
      REQ_FILE="requirements.txt"
    fi

    if [ -f "$REQ_FILE" ]; then

      UNPINNED=$(grep -E -v '^(#|\s*$)' "$REQ_FILE" \
        | grep -n -E -v '(==|@|===)' || true)

      if [ -n "$UNPINNED" ]; then
        warn "$df: requisitos no fijados en $REQ_FILE (recomendado fijar versiones):\n$UNPINNED"
      else
        ok "$df: requisitos parecen fijados en $REQ_FILE"
      fi

    else
      warn "$df: no se encontró requirements para analizar ($REQ_FILE)"
    fi
  fi

  # ==========================================
  # 4) apt-get install sin versiones
  # (solo WARN)
  # ==========================================

  APT_LINES=$(grep -n "apt-get install" "$df" || true)

  if [ -n "$APT_LINES" ]; then

    while IFS= read -r entry; do

      lineno=$(echo "$entry" | cut -d: -f1)
      line=$(echo "$entry" | cut -d: -f2-)

      if ! echo "$line" | grep -q "="; then
        warn "$df:$lineno apt-get install sin versiones explícitas: $line"
      fi

    done <<< "$APT_LINES"

  fi

done

if [ "$FAILED" -ne 0 ]; then
  echo ""
  echo "VALIDACIÓN DOCKERFILES: problemas detectados"
  exit 1
else
  echo ""
  echo "VALIDACIÓN DOCKERFILES: OK"
  exit 0
fi
