#!/bin/bash

# Función para registrar mensajes con timestamp
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') $1"
}

# Porcentaje de recursos a asignar
MEMORY_PERCENT=20
CPU_PERCENT=10
LABEL_FILTER="monitoring.managed=true"

# Validaciones previas
command -v docker >/dev/null 2>&1 || { echo "[ERROR] docker no está instalado"; exit 1; }
command -v bc >/dev/null 2>&1 || { echo "[ERROR] bc no está instalado"; exit 1; }

# Obtener recursos disponibles: memoria y CPU
TOTAL_MEM=$(free -m | awk '/^Mem:/{print $2}') # Memoria total en MiB
TOTAL_CPU=$(nproc)                             # Número total de CPUs

# Calcular memoria y CPU en base al porcentaje
LIMIT_MEM="$(echo "$TOTAL_MEM * $MEMORY_PERCENT / 100" | bc)M"
LIMIT_CPU=$(echo "scale=1; $TOTAL_CPU * $CPU_PERCENT / 100" | bc)

log_message "[INFO] Memoria total: ${TOTAL_MEM}MB → límite por contenedor: ${LIMIT_MEM}"
log_message "[INFO] CPUs totales: ${TOTAL_CPU} → límite por contenedor: ${LIMIT_CPU}"

# Esperar a que Docker esté en ejecución
log_message "[INFO]: Esperando a que Docker se inicie..."
until docker info >/dev/null 2>&1; do
    sleep 30
done
log_message "[OK] Docker está en ejecución."

# Obtener contenedores gestionados
CONTAINERS=$(docker ps --filter "label=$LABEL_FILTER" -q)

if [ -z "$CONTAINERS" ]; then
    log_message "[WARN] No hay contenedores con label '$LABEL_FILTER'"
    exit 0
fi

# Aplicar los límites a los contenedores monitoring
for container_id in $CONTAINERS; do

    NAME=$(docker inspect --format='{{.Name}}' "$container_id" | sed 's/\///')

    log_message "[INFO] Revisando $NAME ($container_id)"

    CURRENT_MEMORY=$(docker inspect --format='{{.HostConfig.Memory}}' "$container_id")
    CURRENT_CPUS=$(docker inspect --format='{{.HostConfig.NanoCpus}}' "$container_id")

    if [[ "$CURRENT_MEMORY" -eq 0 || "$CURRENT_CPUS" -eq 0 ]]; then

        log_message "[⚙️] Aplicando límites a $NAME"

        if docker update \
            --memory "$LIMIT_MEM" \
            --memory-swap "$(( ${LIMIT_MEM%M} * 2 ))M" \
            --cpus="$LIMIT_CPU" \
            "$container_id" >/dev/null; then

            log_message "[OK] Límites aplicados a $NAME"

        else
            log_message "[ERROR] Error aplicando límites a $NAME"
        fi

    else
        log_message "[ℹ️] $NAME ya tiene límites definidos"
    fi

done

log_message "[🎯] Configuración de límites completada"
