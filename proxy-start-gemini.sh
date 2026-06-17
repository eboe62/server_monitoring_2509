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
    echo "🧹 Detectado contenedor antiguo o en bucle. Limpiando..."
    docker stop "$PROXY_NAME" >/dev/null 2>&1 || true
    docker rm "$PROXY_NAME" >/dev/null 2>&1 || true
fi

echo "🚀 Levantando Proxy Sidecar en segundo plano de forma segura..."

# 3. Lanzamiento automatizado con Hardening Estricto y restricción Loopback al puerto 8082 y Enrutamiento hacia GEMINI
docker run -d \
  --name "$PROXY_NAME" \
  --network ia-net \
  --restart unless-stopped \
  --cap-drop=ALL \
  --security-opt no-new-privileges:true \
  -p 127.0.0.1:8082:8082 \
  -e ANTHROPIC_API_KEY \
  -e GEMINI_API_KEY \
#  -e MODEL="gemini/models/gemini-1.5-pro" \
#  -e MODEL_SONNET="gemini/models/gemini-1.5-pro" \
  -e MODEL="gemini/models/gemini-3.1-flash-lite" \
  -e MODEL_SONNET="gemini/models/gemini-3.1-flash-lite" \
  "$IMAGE_NAME"

echo "------------------------------------------------------------------"
echo "✅ Proxy iniciado con éxito y escuchando de forma aislada."
echo "🔒 Solo accesible localmente en el puerto 8082 (127.0.0.1)."
echo "📡 Ejecuta './box-opencode.sh' en tus proyectos para llamar a la IA."
echo "------------------------------------------------------------------"
