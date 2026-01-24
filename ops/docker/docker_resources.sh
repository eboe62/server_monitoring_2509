#!/bin/bash

# --- NUEVO: Logger uniforme estilo cloud-init ---
log_info() {
  echo "dr-info: $1"
}

log_info "===== $(date '+%Y-%m-%d %H:%M:%S') ====="

# Colores para el terminal
RED='\033[0;31m'
NC='\033[0m' # Sin color

# Obtener lista de contenedores activos
containers=$(docker ps -q)

if [ -z "$containers" ]; then
  log_info "No hay contenedores en ejecución."
  exit 0
fi

# Encabezado del informe
log_info "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++Docker Resources+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
log_info "+--------------+----------------------------------+----------------------------------+-------------------------------+--------------------------------------------------------------+"

printf "dr-info: | %-12s | %-32s | %-32s | %-29s | %-65s\n" \
  "CONTAINER ID" \
  "MEM USAGE/LIMIT" \
  "SWAP USAGE/LIMIT" \
  "CPU USAGE/LIMIT" \
  "NAME"

log_info "+--------------+----------------------------------+----------------------------------+-------------------------------+--------------------------------------------------------------+"

# Procesar cada contenedor
for container in $containers; do
  # Obtener nombre e ID del contenedor
  name=$(docker inspect --format '{{.Name}}' "$container" | sed 's/\///')
  container_id=$(docker inspect --format '{{.Id}}' "$container" | cut -c 1-12) # ID corto

  # Obtener límites de memoria, swap y CPU del contenedor
  mem_limit=$(docker inspect --format '{{.HostConfig.Memory}}' "$container")
  swap_limit=$(docker inspect --format '{{.HostConfig.MemorySwap}}' "$container")
  cpu_limit=$(docker inspect --format '{{.HostConfig.NanoCpus}}' "$container")

  # Manejo de límites no configurados
  mem_limit_str=$([ "$mem_limit" -eq 0 ] && echo "No definido" || echo "$((mem_limit / 1024 / 1024)) MiB")
  swap_limit_str=$([ "$swap_limit" -le "$mem_limit" ] && echo "No definido" || echo "$((swap_limit / 1024 / 1024)) MiB")
  cpu_limit_str=$([ "$cpu_limit" -eq 0 ] && echo "No definido" || echo "$(awk 'BEGIN {print '"$cpu_limit"'/1000000}') MiliCores")

  # Obtener uso de memoria y CPU usando docker stats
  stats=$(docker stats --no-stream --format "{{.MemUsage}} {{.CPUPerc}}" "$container")
  mem_usage=$(echo "$stats" | awk '{print $1}')
  cpu_usage_raw=$(echo "$stats" | awk '{print $2}' | sed 's/ %//')

  # Validar si cpu_usage_raw está vacío o contiene caracteres inesperados
  if [[ -z "$cpu_usage_raw" || ! "$cpu_usage_raw" =~ ^[0-9]+([.][0-9]+)?$ ]]; then
    cpu_usage="N/A"
  else
    cpu_usage=$cpu_usage_raw
  fi

  # Calcular porcentaje de uso de memoria
  mem_usage_mb=$(echo "$mem_usage" | awk '{print int($1+0.5)}')
  mem_usage_percent=$([ "$mem_limit" -eq 0 ] && echo "N/A" || awk 'BEGIN {if ('"$mem_limit"'>0) printf "%.1f", ('"$mem_usage_mb"' / ('"$mem_limit"'/1024/1024)) * 100; else print "N/A"}')

  # Calcular porcentaje de uso de Swap
  swap_usage_percent=$([ "$swap_limit" -le "$mem_limit" ] && echo "N/A" || awk 'BEGIN {if ('"$swap_limit"' > '"$mem_limit"') printf "%.1f", ('"$mem_usage_mb"' / ('"$swap_limit"'/1024/1024)) * 100; else print "N/A"}')

  # Colorear el porcentaje de uso de memoria y Swap si es superior al 80%
  if [[ "$mem_usage_percent" != "N/A" && $(echo "$mem_usage_percent > 80" | bc -l) -eq 1 ]]; then
    mem_usage_percent="${RED}${mem_usage_percent} %${NC}"
  else
    mem_usage_percent="${mem_usage_percent} %"
  fi

  if [[ "$swap_usage_percent" != "N/A" && $(echo "$swap_usage_percent > 80" | bc -l) -eq 1 ]]; then
    swap_usage_percent="${RED}${swap_usage_percent} %${NC}"
  else
    swap_usage_percent="${swap_usage_percent} %"
  fi

  # Colorear el porcentaje de uso de CPU si es superior al 80%
  if [[ "$cpu_usage" != "N/A" && "$cpu_usage" != "" && $(echo "$cpu_usage > 80" | bc -l) -eq 1 ]]; then
    cpu_usage="${RED}${cpu_usage} %${NC}"
  else
    cpu_usage="${cpu_usage} %"
  fi

  printf "dr-info: | %-12s | %-32s | %-32s | %-29s | %-65s\n" \
    "$container_id" \
    "$mem_usage / $mem_limit_str ($mem_usage_percent)" \
    "$mem_usage / $swap_limit_str ($swap_usage_percent)" \
    "$cpu_usage / $cpu_limit_str" \
    "$name"
done

log_info "+--------------+----------------------------------+----------------------------------+-------------------------------+--------------------------------------------------------------+"

