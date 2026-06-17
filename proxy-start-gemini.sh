#!/bin/bash
# ==========================================
# INFRASTRUCTURE SIDE-CAR - CLAUDE PROXY LIFECYCLE
# Protocolo de Seguridad EOB-v2606
# ==========================================
set -euo pipefail

PROXY_NAME="ia_opencode_proxy"
IMAGE_NAME="ia-opencode:latest"

echo "🔄 Comprobando estado del proxy corporativo..."

# 1. Validar requerimiento crítico de Gobernanza: API Keys presentes
if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
    echo "❌ Error: La variable ANTHROPIC_API_KEY no está exportada en esta terminal."
    echo "👉 Ejecuta primero: export ANTHROPIC_API_KEY=\"tu_clave_sk_aquí\""
    exit 1
fi

if [ -z "${GEMINI_API_KEY:-}" ]; then
    echo "❌ Error: La variable GEMINI_API_KEY no está exportada en esta terminal."
    echo "👉 Ejecuta primero: export GEMINI_API_KEY=\"tu_clave_gemini_aquí\""
    echo "💡 Puedes conseguir una clave gratuita registrándote en https://aistudio.google.com"
    exit 1
fi

# 2. Limpieza de contenedores huérfanos o activos previos
if [ "$(docker ps -a -q -f name=^/${PROXY_NAME}$)" ]; then
    echo "🧹 Limpiando contenedor sidecar activo previo..."
    docker stop "$PROXY_NAME" >/dev/null 2>&1 || true
    docker rm "$PROXY_NAME" >/dev/null 2>&1 || true
fi

echo "🚀 Levantando Proxy Sidecar con Hardening de Máximo Aislamiento..."

# ==========================================
# NOTAS DE HARDENING APLICADAS EN EL RUNTIME:
# - Capdrop=ALL: Elimina capacidades del kernel reduciendo drásticamente la superficie de ataque.
# - No-new-privileges: Impide elevación de privilegios en caliente.
# - Encapsulamiento con uv: Las dependencias quedan aisladas e inmutables en /app/.venv/.
# - Filtro Loopback Local-Only: Mapeado estricto al puerto 8082 únicamente en 127.0.0.1.
# profundo pero con limite de cuota por minuto mayor entradas por dia
#  -e MODEL="gemini/gemini-1.5-pro" \
#  -e MODEL_SONNET="gemini/gemini-1.5-pro" \
# básico no usar
#  -e MODEL="gemini/gemini-3.1-flash-lite" \
#  -e MODEL_SONNET="gemini/gemini-3.1-flash-lite" \
# mayor cuota por minuto pero menos profundo más perspectiva de contexto
#  -e MODEL="gemini/gemini-2.5-flash" \
#  -e MODEL_SONNET="gemini/gemini-2.5-flash" \
# mayor entradas por dia
#  -e MODEL="gemini/gemini-2.5-pro" \
#  -e MODEL_SONNET="gemini/gemini-2.5-pro" \
# ==========================================

# 3. Lanzamiento automatizado con Hardening Estricto y Enrutamiento hacia GEMINI
docker run -d \
  --name "$PROXY_NAME" \
  --network ia-net \
  --restart unless-stopped \
  --cap-drop=ALL \
  --security-opt no-new-privileges:true \
  -p 127.0.0.1:8082:8000 \
  -e ANTHROPIC_API_KEY \
  -e GEMINI_API_KEY \
  -e MODEL="gemini/gemini-2.5-pro" \
  -e MODEL_SONNET="gemini/gemini-2.5-pro" \
  "$IMAGE_NAME"

echo "------------------------------------------"
echo "✅ Proxy iniciado con éxito y escuchando de forma aislada."
echo "🔒 Solo accesible localmente en el puerto 8082 (127.0.0.1)."
echo "📡 Ejecuta './box-opencode.sh' en tus proyectos para llamar a la IA."
echo "------------------------------------------"
