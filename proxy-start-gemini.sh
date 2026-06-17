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
    echo "🧹 DeLimpiando contenedor sidecar activo previo..."
    docker stop "$PROXY_NAME" >/dev/null 2>&1 || true
    docker rm "$PROXY_NAME" >/dev/null 2>&1 || true
fi

echo "🚀 LevaLevantando Proxy Sidecar con Hardening de Máximo Aislamiento..."

# 3. Lanzamiento automatizado con Hardening Estricto y restricción Loopback al puerto 8082 y Enrutamiento hacia GEMINI
docker run -d \
  --name "$PROXY_NAME" \
  --network ia-net \
  --restart unless-stopped \
# No incluir curl: Esto reduce la superficie de ataque drásticamente: si un atacante vulnera la aplicación web, ni siquiera tendrá un curl interno para descargar malware o scripts maliciosos
# Encapsulamiento estricto con uv: El autor decidió empaquetar el proyecto usando el gestor moderno uv de Python. Esto crea un entorno inmutable donde todas las librerías necesarias (como loguru para los logs) quedan confinadas en el directorio reservado /app/.venv/. No se instalan de forma global, bloqueando el uso de llamadas genéricas con el binario de Python estándar del sistema.
# Eliminación de capacidades para ejecutar acciones comunes del kernel de Linux incluso entrando como usuario root el contenedor tiene prohibido hacer ciertas llamadas de bajo nivel.
  --cap-drop=ALL \
# Restricción de privilegios: impide que cualquier binario o script (como el CLI del proxy) eleve sus permisos en caliente durante la ejecución. Si se intenta forzar tareas secundarias, el contenedor aborta el proceso.
  --security-opt no-new-privileges:true \
# El programador de la aplicación escribió un middleware (un filtro) en FastAPI que inspecciona la IP de origen de la conexión. Si la IP no es 127.0.0.1, responde con un HTTP de rechazo {"detail":"Admin UI is local-only"}
  -p 127.0.0.1:8082:8082 \
  -e ANTHROPIC_API_KEY \
  -e GEMINI_API_KEY \
# profundo pero con limite de cuota por minuto
#  -e MODEL="gemini/gemini-1.5-pro" \
#  -e MODEL_SONNET="gemini/gemini-1.5-pro" \
# básico no usar
#  -e MODEL="gemini/gemini-3.1-flash-lite" \
#  -e MODEL_SONNET="gemini/gemini-3.1-flash-lite" \
# mayor cuota por minuto pero menos profundo más perspectiva de contexto
  -e MODEL="gemini/gemini-2.5-flash" \
  -e MODEL_SONNET="gemini/gemini-2.5-flash" \
  "$IMAGE_NAME"

echo "------------------------------------------------------------------"
echo "✅ Proxy iniciado con éxito y escuchando de forma aislada."
echo "🔒 Solo accesible localmente en el puerto 8082 (127.0.0.1)."
echo "📡 Ejecuta './box-opencode.sh' en tus proyectos para llamar a la IA."
echo "------------------------------------------------------------------"
