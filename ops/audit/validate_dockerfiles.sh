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

  # 1) FROM implicit tag (no tag) -> implicit latest
  if grep -E -n '^FROM\s+[^:]+(\s|$)' "$df" >/dev/null 2>&1; then
    LINES=$(grep -nE '^FROM\s+[^:]+(\s|$)' "$df" || true)
    fail "$df: Uso de FROM sin tag (implícito :latest):\n$LINES"
  fi

  # 2) FROM explicit :latest
  LATESTS=$(grep -nE '^FROM\s+.*:latest' "$df" || true)
  if [ -n "$LATESTS" ]; then
    fail "$df: Uso de FROM :latest detectado:\n$LATESTS"
  else
    ok "$df: no usa FROM :latest explícito"
  fi

  # 3) Detectar pip requirements referenced and check unpinned entries
  REQ_LINES=$(grep -n "COPY .*requirements.txt" -n "$df" || true)
  if [ -n "$REQ_LINES" ]; then
    # try to locate requirements file path relative to Dockerfile
    REQ_FILE="requirements.txt"
    if [ -f "$(dirname "$df")/../requirements.txt" ]; then
      REQ_FILE="$(dirname "$df")/../requirements.txt"
    elif [ -f "requirements.txt" ]; then
      REQ_FILE="requirements.txt"
    fi

    if [ -f "$REQ_FILE" ]; then
      # lines without '==' or '@' (approximation of unpinned)
      UNPINNED=$(grep -E -v '^(#|\s*$)' "$REQ_FILE" | grep -n -E -v '(==|@|===)' || true)
      if [ -n "$UNPINNED" ]; then
        warn "$df: requisitos no fijados en $REQ_FILE (recomendado fijar versiones):\n$UNPINNED"
      else
        ok "$df: requisitos parecen fijados en $REQ_FILE"
      fi
    else
      warn "$df: no se encontró requirements para analizar ($REQ_FILE)"
    fi
  fi

  # 4) Detectar apt-get install sin versiones (solo advertencia)
  APT_LINES=$(grep -n "apt-get install" "$df" || true)
  if [ -n "$APT_LINES" ]; then
    for l in $(echo "$APT_LINES" | cut -d: -f1); do
      line=$(sed -n "${l}p" "$df")
      if ! echo "$line" | grep -q "="; then
        warn "$df:$l apt-get install sin versiones explícitas: $line"
      fi
    done
  fi

done

if [ "$FAILED" -ne 0 ]; then
  echo "\nVALIDACIÓN DOCKERFILES: problemas detectados"
  exit 1
else
  echo "\nVALIDACIÓN DOCKERFILES: OK"
  exit 0
fi
