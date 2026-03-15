#!/usr/bin/env bash

# ==========================================================
# server_monitoring_2509
# Auditoría FASE 4
# Repositorio + Host
# ==========================================================

set -euo pipefail

echo "=========================================="
echo "AUDITORÍA FASE 4 – server_monitoring_2509"
echo "Fecha: $(date)"
echo "Host:  $(hostname)"
echo "=========================================="
echo ""

# ------------------------------------------
# helpers
# ------------------------------------------

ok()   { echo "[OK]   $1"; }
warn() { echo "[WARN] $1"; }
fail() { echo "[FAIL] $1"; }
info() { echo "[INFO] $1"; }

echo ""
echo "=========================================="
echo "A.- AUDITORÍA REPOSITORIO"
echo "=========================================="

# ------------------------------------------
# A1 Git
# ------------------------------------------

info "Verificando repositorio Git"

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    ok "Repositorio Git válido"
else
    fail "No es un repositorio Git"
fi

BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "[INFO] Rama actual: $BRANCH"

COMMIT=$(git rev-parse HEAD)
echo "[INFO] Commit actual: $COMMIT"

if [ -z "$(git status --porcelain)" ]; then
    ok "Repositorio limpio"
else
    warn "Repositorio con cambios locales"
fi

# ------------------------------------------
# A2 estructura
# ------------------------------------------

info "Verificando estructura del proyecto"

dirs=(
    "src"
    "ops/docker"
    "ops/services"
    "scripts"
    "docs/decisiones"
)

for d in "${dirs[@]}"; do
    if [ -d "$d" ]; then
        ok "Directorio presente: $d"
    else
        fail "Directorio faltante: $d"
    fi
done

# ------------------------------------------
# A3 docker compose
# ------------------------------------------

info "Buscando docker-compose"

COMPOSE_FILES=$(find ops -name "compose*.yml" -o -name "compose*.yml")

if [ -z "$COMPOSE_FILES" ]; then
    warn "No se encontraron docker-compose"
else
    ok "docker-compose detectados"
fi

for f in $COMPOSE_FILES; do
    echo "[INFO] Validando $f"
    if docker compose -f "$f" config >/dev/null 2>&1; then
        ok "$f válido"
    else
        warn "$f no pudo validarse"
    fi
done

# ------------------------------------------
# A4 puertos declarados
# ------------------------------------------

info "Buscando puertos publicados en compose"

PORTS=$(grep -R "ports:" -n ops || true)

if [ -z "$PORTS" ]; then
    ok "No hay puertos publicados en compose"
else
    warn "Servicios con puertos publicados:"
    echo "$PORTS"
fi

# ------------------------------------------
# A5 cronfile
# ------------------------------------------

if [ -f "ops/cron/monitoring.cron" ]; then
    ok "Cronfile presente"
else
    warn "Cronfile no encontrado"
fi

if [ -f "ops/stacks/cron/compose.yml" ]; then
    ok "Stack cron declarado"
else
    warn "docker-compose cron no encontrado"
fi

# ------------------------------------------
# A6 ejecución python
# ------------------------------------------

info "Buscando ejecuciones Python"

BAD=$(grep -R "python3 src/" -n . \
      --exclude=README.md \
      --exclude-dir=docs \
      --exclude-dir=ai \
      || true)

if [ -z "$BAD" ]; then
    ok "No se detectó ejecución python por ruta absoluta"
else
    warn "Posible ejecución python incorrecta:"
    echo "$BAD"
fi

GOOD=$(grep -R "python3 -m" -n . || true)

if [ -z "$GOOD" ]; then
    warn "No se detectó uso de python3 -m"
else
    ok "Uso de python3 -m detectado"
fi

# ------------------------------------------
# A7 docker socket
# ------------------------------------------

info "Buscando uso de docker.sock"

SOCK=$(grep -R "docker.sock" -n . || true)

if [ -z "$SOCK" ]; then
    ok "docker.sock no usado"
else
    warn "docker.sock montado en contenedor:"
    echo "$SOCK"
fi

# ------------------------------------------
# A8 secrets
# ------------------------------------------

info "Buscando directorios secrets"

SECRETS=$(find ops/services -type d -name secrets || true)

if [ -z "$SECRETS" ]; then
    warn "No se encontraron directorios secrets"
else
    ok "Directorios secrets detectados:"
    echo "$SECRETS"
fi

# ------------------------------------------
# A9 secrets versionados
# ------------------------------------------

info "Verificando secrets versionados"

TRACKED_SECRETS=$(git ls-files | grep secrets || true)

if [ -z "$TRACKED_SECRETS" ]; then
    ok "No hay secretos versionados"
else
    fail "Secrets versionados en Git:"
    echo "$TRACKED_SECRETS"
fi

echo ""
echo "=========================================="
echo "B.- AUDITORÍA HOST"
echo "=========================================="

# ------------------------------------------
# B1 sistema
# ------------------------------------------

info "Sistema"

uname -a
echo ""

# ------------------------------------------
# B2 ufw
# ------------------------------------------

info "Estado UFW"

if command -v ufw >/dev/null 2>&1; then
    sudo ufw status verbose
else
    warn "UFW no instalado"
fi

# ------------------------------------------
# B3 fail2ban
# ------------------------------------------

info "Estado fail2ban"

if systemctl is-active --quiet fail2ban; then
    ok "fail2ban activo"
else
    warn "fail2ban no activo"
fi

# ------------------------------------------
# B4 cron host
# ------------------------------------------

info "Cron del usuario"

crontab -l 2>/dev/null || echo "Sin crontab"

info "Cron root"

sudo crontab -l 2>/dev/null || echo "Sin crontab root"

# ------------------------------------------
# B5 docker
# ------------------------------------------

info "Docker runtime"

if command -v docker >/dev/null 2>&1; then
    docker version --format '{{.Server.Version}}' || warn "Docker no responde"
    ok "Docker instalado"
else
    fail "Docker no instalado"
fi

# ------------------------------------------
# B6 contenedores
# ------------------------------------------

info "Contenedores activos"

CONTAINERS=$(docker ps -q)

if [ -z "$CONTAINERS" ]; then
    info "No hay contenedores desplegados"
else
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
fi

# ------------------------------------------
# B7 puertos host
# ------------------------------------------

info "Puertos abiertos en host"

ss -tulpn

# ------------------------------------------
# B8 redes docker
# ------------------------------------------

info "Redes Docker"

docker network ls

if docker network inspect monitoring-net >/dev/null 2>&1; then
    ok "monitoring-net existe"
else
    warn "monitoring-net no encontrada"
fi

# ------------------------------------------
# B9 volúmenes
# ------------------------------------------

info "Volúmenes Docker"

docker volume ls

echo ""
echo "=========================================="
echo "C.- CUMPLIMIENTO ADR"
echo "=========================================="

# ------------------------------------------
# C1 ADR-0014 / ADR-0015
# Puertos docker expuestos
# ------------------------------------------

info "Verificando exposición de puertos Docker (ADR-0014 / ADR-0015)"

BAD_PORTS=$(grep -R 'ports:' -n ops 2>/dev/null | grep -v "127.0.0.1" || true)

if [ -z "$BAD_PORTS" ]; then
    ok "No se detectaron puertos expuestos globalmente"
else
    warn "Puertos potencialmente expuestos:"
    echo "$BAD_PORTS"
fi

# ------------------------------------------
# C2 uso de :latest
# ------------------------------------------

info "Verificando uso de tags :latest (recomendación seguridad)"

LATEST=$(grep -R "image: .*:latest" -n ops 2>/dev/null || true)

if [ -z "$LATEST" ]; then
    ok "No se detectaron imágenes :latest"
else
    warn "Imágenes usando :latest:"
    echo "$LATEST"
fi

# ------------------------------------------
# C3 docker.sock
# ------------------------------------------

info "Verificando montaje docker.sock (superficie de ataque)"

SOCK=$(grep -R "docker.sock" -n ops 2>/dev/null || true)

if [ -z "$SOCK" ]; then
    ok "docker.sock no montado en contenedores"
else
    warn "docker.sock detectado:"
    echo "$SOCK"
fi

# ------------------------------------------
# C4 servicios fuera de monitoring-net
# ------------------------------------------

info "Verificando uso de red monitoring-net"

NO_NET=$(grep -R "services:" -n ops/docker 2>/dev/null || true)

if docker network inspect monitoring-net >/dev/null 2>&1; then
    ok "Red monitoring-net disponible"
else
    warn "monitoring-net no existe"
fi

# ------------------------------------------
# C5 cron del host para lógica de aplicación
# ADR-0016
# ------------------------------------------

info "Buscando ejecución de scripts del proyecto en cron del host"

HOST_CRON=$(sudo crontab -l 2>/dev/null | grep "/opt/monitoring" || true)

if [ -z "$HOST_CRON" ]; then
    ok "Cron del host no ejecuta lógica del proyecto"
else
    warn "Cron host ejecuta scripts del proyecto:"
    echo "$HOST_CRON"
fi

# ------------------------------------------
# C6 ejecución python fuera de contenedor
# ------------------------------------------

info "Buscando ejecución directa de Python del proyecto"

HOST_PY=$(ps aux | grep python | grep "/opt/monitoring" | grep -v grep || true)

if [ -z "$HOST_PY" ]; then
    ok "No se detectó Python del proyecto ejecutándose en host"
else
    warn "Python del proyecto ejecutándose en host:"
    echo "$HOST_PY"
fi

# ------------------------------------------
# C7 permisos scripts host hardening
# ADR-0016
# ------------------------------------------

info "Verificando scripts de hardening del host"

HARDEN_SCRIPTS=(
"/usr/local/bin/configure_docker_limits.sh"
"/opt/monitoring/scripts/apply_ssh_ratelimit.sh"
)

for s in "${HARDEN_SCRIPTS[@]}"; do
    if [ -f "$s" ]; then
        ok "Script presente: $s"
    else
        warn "Script no encontrado: $s"
    fi
done

echo ""
echo "=========================================="
echo "FIN AUDITORÍA FASE 4"
echo "=========================================="
