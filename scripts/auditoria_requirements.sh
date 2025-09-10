#!/usr/bin/env bash
set -euo pipefail

CONTAINER=${1:-}
REQ_FILE=${2:-requirements.txt}

if [ -z "$CONTAINER" ]; then
  echo "Uso: $0 <nombre_contenedor> [ruta_a_requirements.txt]"
  exit 1
fi

if [ ! -f "$REQ_FILE" ]; then
  echo "ERROR: no se encuentra $REQ_FILE"
  exit 2
fi

echo "📦 Comprobando dependencias en contenedor: $CONTAINER (archivo: $REQ_FILE)"

while IFS= read -r rawline || [ -n "$rawline" ]; do
  # eliminar CR, comentarios y espacios
  line="${rawline//$'\r'/}"            # quitar CR
  line="${line%%#*}"                   # quitar comentario a partir de '#'
  line="$(echo "$line" | awk '{$1=$1;print}')"  # trim
  [ -z "$line" ] && continue

  # quitar especificadores de versión (>=, ==, ~=, <=, !=, ...)
  pkg="$(echo "$line" | sed -E 's/[><=!~].*$//g' | sed -E 's/\[.*\]//g' | xargs)"

  echo -n "🔍 $pkg ... "

  # Primero intentamos con pip (nombre tal cual)
  if docker exec "$CONTAINER" python3 -m pip show "$pkg" >/dev/null 2>&1; then
    ver=$(docker exec "$CONTAINER" python3 -m pip show "$pkg" | awk '/^Version:/ {print $2}')
    echo "OK (pip $ver)"
    continue
  fi

  # Si pip no lo encuentra intentamos comprobar import map (ej. python-dotenv -> dotenv)
  case "$pkg" in
    python-dotenv) import_name="dotenv";;
    psycopg2-binary) import_name="psycopg2";;
    *) import_name="$pkg";;
  esac

  if docker exec "$CONTAINER" python3 - <<PY 2>/dev/null
import importlib.util, sys
spec = importlib.util.find_spec("$import_name")
print("FOUND" if spec is not None else "NOTFOUND")
PY
  then
    # si el comando devuelve FOUND en stdout, capturamos y lo mostramos
    res=$(docker exec "$CONTAINER" python3 -c "import importlib.util; print('FOUND' if importlib.util.find_spec('$import_name') else 'NOTFOUND')" 2>/dev/null || true)
    if [ "$res" = "FOUND" ]; then
      echo "INSTALADO como módulo '$import_name' (nombre pip distinto)"
      continue
    fi
  fi

  echo "❌ NO INSTALADO"
done < "$REQ_FILE"

