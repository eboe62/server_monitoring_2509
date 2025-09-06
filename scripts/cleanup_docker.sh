#!/bin/bash
# Limpieza segura de Docker no agresiva 
# Conserva servicios críticos, volúmenes y redes de sistema sin borrar imágenes necesarias
# Uso:
#   ./cleanup_docker.sh          # Limpieza real
#   ./cleanup_docker.sh --dry-run # Solo mostrar lo que se eliminaría
set -euo pipefail

# ========= CONFIGURACIÓN =========

# Contenedores que nunca deben borrarse (por nombre)
PROTECTED_CONTAINERS=(
  "captain-captain"
  "captain-certbot"
  "data-container_data-container"
)

# Redes protegidas (incluyendo bridge/host/none)
PROTECTED_NETWORKS=(
  "bridge" "host" "none"
  "docker_gwbridge" "ingress"
  "captain-overlay-network"
  "observability_default"
  "smtp_relay_default"
  "data-container_default"
)

# Volúmenes críticos (bases de datos y datos persistentes)
PROTECTED_VOLUMES=(
  "mysql-data"
  "observability_grafana-data"
  "observability_loki-data"
  "shared-data"
  "captain--security250226app-data"
)

DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

# ========= FUNCIONES =========

log() {
  echo -e "$@"
}

docker_stats() {
  log "Estado actual:"
  docker system df
  echo "----------------------------------------"
}

is_protected() {
  local item=$1; shift
  local -n arr=$1
  for p in "${arr[@]}"; do
    [[ "$item" == "$p" ]] && return 0
  done
  return 1
}

# ========= INICIO =========

log "===== [ Limpieza segura de Docker ] ====="
docker_stats

if $DRY_RUN; then
  log "[MODO PRUEBA] Esto es lo que se eliminaría:\n"
else
  log "[MODO REAL] Ejecutando limpieza...\n"
fi

# --- 1/4 Contenedores parados ---
log "[1/4] Contenedores parados:"
containers=$(docker ps -a --filter "status=exited" --format "{{.Names}} {{.ID}}")
while read -r name id; do
  [[ -z "$name" ]] && continue
  if is_protected "$name" PROTECTED_CONTAINERS; then
    log ">> Saltando contenedor protegido: $name"
    continue
  fi
  if $DRY_RUN; then
    log "Se eliminaría contenedor: $name"
  else
    docker rm "$id" && log "Eliminado contenedor: $name"
  fi
done <<< "$containers"

# --- 2/4 Imágenes huérfanas ---
log "[2/4] Imágenes huérfanas:"
if $DRY_RUN; then
  docker images -f "dangling=true"
else
  docker image prune -f
fi

# --- 3/4 Redes no usadas ---
log "[3/4] Redes no usadas:"
networks=$(docker network ls --filter "dangling=true" --format "{{.Name}} {{.ID}}")
while read -r name id; do
  [[ -z "$name" ]] && continue
  if is_protected "$name" PROTECTED_NETWORKS; then
    log ">> Saltando red protegida: $name"
    continue
  fi
  if $DRY_RUN; then
    log "Se eliminaría red: $name"
  else
    docker network rm "$id" && log "Eliminada red: $name"
  fi
done <<< "$networks"

# --- 4/4 Volúmenes no usados ---
log "[4/4] Volúmenes no usados:"
volumes=$(docker volume ls -qf "dangling=true")
for v in $volumes; do
  if is_protected "$v" PROTECTED_VOLUMES; then
    log ">> Saltando volumen protegido: $v"
    continue
  fi
  if $DRY_RUN; then
    log "Se eliminaría volumen: $v"
  else
    docker volume rm "$v" && log "Eliminado volumen: $v"
  fi
done

docker_stats
log "===== Limpieza completada ====="
exit 0
