#!/bin/bash

# Función para registrar mensajes con timestamp
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') $1"
}

# Porcentaje de recursos a asignar
MEMORY_PERCENT=20
CPU_PERCENT=10

# Obtener memoria y CPU disponibles
TOTAL_MEM=$(free -m | awk '/^Mem:/{print $2}') # Memoria total en MiB
TOTAL_CPU=$(nproc)                             # Número total de CPUs

# Calcular memoria y CPU en base al porcentaje
LIMIT_MEM="$(echo "$TOTAL_MEM * $MEMORY_PERCENT / 100" | bc)M"
LIMIT_CPU=$(echo "scale=1; $TOTAL_CPU * $CPU_PERCENT / 100" | bc)

# Esperar a que Docker esté en ejecución
log_message "[🚀]: Esperando a que Docker se inicie..."
until docker info >/dev/null 2>&1; do
    sleep 30
done
log_message "[✅]: Docker está en ejecución."

# Aplicar los límites a los contenedores en ejecución
for container_id in $(docker ps -q); do
    log_message "[🔍]: Verificando el contenedor $container_id..."
    INSPECT=$(docker inspect "$container_id")

    CURRENT_MEMORY=$(echo "$INSPECT" | grep -i '"Memory":' | awk '{print $2}' | tr -d ',')
    CURRENT_CPUS=$(echo "$INSPECT" | grep -i '"NanoCpus":' | awk '{print $2}' | tr -d ',')

    if [[ "$CURRENT_MEMORY" -eq 0 || "$CURRENT_CPUS" -eq 0 ]]; then
        log_message "[⚙️]: Aplicando límites al contenedor $container_id..."
        if docker update --memory "$LIMIT_MEM" --memory-swap "$(( ${LIMIT_MEM%M} * 2 ))M" --cpus="$LIMIT_CPU" "$container_id"; then
            log_message "[✅]: Límites aplicados correctamente a $container_id."
        else
            log_message "[❌]: Error al actualizar el contenedor $container_id."
        fi
    else
        log_message "[ℹ️]: El contenedor $container_id ya tiene límites configurados."
    fi
done

log_message "[🎯]: Proceso de configuración de límites completado."
