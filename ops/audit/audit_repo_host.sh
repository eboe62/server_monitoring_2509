#!/usr/bin/env bash

# ==========================================
# AUDITORÍA SERVIDOR
# Repositorio + Host
# Informe técnico = diagnóstico
# ¿Qué está mal y por qué?
# ==========================================

set -euo pipefail

echo "=========================================="
echo "AUDITORÍA SERVIDOR"
echo "Fecha: $(date)"
echo "Host:  $(hostname)"
echo "=========================================="

# helpers
ok()   { echo "[ OK ] $1"; }
warn() { echo "[WARN] $1"; }
fail() { echo "[FAIL] $1"; }
info() { echo "[INFO] $1"; }

echo ""
echo "------------------------------------------"
echo "A.- AUDITORÍA REPOSITORIO"
echo "------------------------------------------"

echo ""
# ==========================================
echo "A1 Git"
# ==========================================
echo ""

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

echo ""
# ==========================================
echo "A2 Estructura"
# ==========================================
echo ""

info "Verificando estructura del proyecto"

dirs=(
    "src"
    "ops/stacks"
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

echo ""
# ==========================================
echo "A3 docker compose"
# ==========================================
echo ""

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

echo ""
# ==========================================
# A3.1 Healthcheck policy enforcement (runtime classification)
# ==========================================

if [ -f "ops/runtime_containers.sh" ]; then
    info "Validando presencia de healthchecks según ops/runtime_containers.yml"
    bash ops/runtime_containers.sh all | while IFS='|' read -r NAME TYPE POLICY ENFORCE; do
        # Use structured check to find the service and healthcheck presence
        RESULT=$(bash ops/runtime_containers.sh check-health "$NAME" 2>/dev/null || true)
        # RESULT format: name|FOUND|compose_file|service_name|yes| or name|NOT_FOUND|||
        IFS='|' read -r RNAME RSTATUS RFILE RSERVICE RHC <<< "$RESULT"
            if [ "$RSTATUS" = "FOUND" ]; then
            if [ "$RHC" = "yes" ]; then
                ok "$NAME: healthcheck present for service $RSERVICE in $RFILE"
            else
                if [ "$ENFORCE" = "fail" ]; then
                    fail "$NAME: healthcheck ABSENT for service $RSERVICE in $RFILE (enforcement=fail)"
                    exit 1
                else
                    warn "$NAME: healthcheck ABSENT for service $RSERVICE in $RFILE (enforcement=$ENFORCE)"
                fi
            fi
        else
            warn "$NAME: service not found in compose files; skipping enforcement (enforcement=$ENFORCE)"
        fi
    done
else
    warn "ops/runtime_containers.sh no encontrado — omitiendo validación de policy runtime"
fi


echo ""
# ==========================================
echo "A4 Puertos declarados"
# ==========================================
echo ""

info "Buscando puertos publicados en compose"

# Ejecutar validaciones estructuradas una sola vez dentro del contenedor monitoring-python
STRUCTURED_FILE=""
if docker compose version >/dev/null 2>&1 && docker ps --format '{{.Names}}' | grep -q '^monitoring-python$'; then
    STRUCTURED_FILE=$(mktemp)
    if docker compose exec -T monitoring-python python -m ops.audit.compose_policy_checks --json > "$STRUCTURED_FILE" 2>/tmp/compose_checks.err; then
        :
    else
        warn "Validación estructurada falló dentro del contenedor (ver /tmp/compose_checks.err)"
    fi
else
    warn "monitoring-python container no disponible: omitiendo validaciones estructuradas"
fi

echo ""
# ==========================================
echo "A5 Cronfile"
# ==========================================
echo ""

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

echo ""
# ==========================================
echo "A6 Ejecución Python"
# ==========================================
echo ""

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

echo ""
# ==========================================
echo "A7 Docker socket"
# ==========================================
echo ""

info "Buscando uso de docker.sock"

SOCK=$(grep -R "docker.sock" -n . || true)

if [ -z "$SOCK" ]; then
    ok "docker.sock no usado"
else
    warn "docker.sock montado en contenedor:"
    echo "$SOCK"
fi

echo ""
# ==========================================
echo "A8 Secrets"
# ==========================================
echo ""

info "Buscando directorios secrets"

SECRETS=$(find ops/services -type d -name secrets || true)

if [ -z "$SECRETS" ]; then
    warn "No se encontraron directorios secrets"
else
    ok "Directorios secrets detectados:"
    echo "$SECRETS"
fi

echo ""
# ==========================================
echo "A9 Secrets versionados"
# ==========================================
echo ""

info "Verificando secrets versionados"

TRACKED_SECRETS=$(git ls-files | grep secrets || true)

if [ -z "$TRACKED_SECRETS" ]; then
    ok "No hay secretos versionados"
else
    fail "Secrets versionados en Git:"
    echo "$TRACKED_SECRETS"
fi

echo ""
echo "------------------------------------------"
echo "B.- AUDITORÍA HOST"
echo "------------------------------------------"

echo ""
# ==========================================
echo "B1 Sistema"
# ==========================================
echo ""

info "Sistema"

uname -a

echo ""
# ==========================================
echo "B2 UFW"
# ==========================================
echo ""

info "Estado UFW"

if command -v ufw >/dev/null 2>&1; then
    if [ "$EUID" -ne 0 ]; then
        warn "UFW instalado — se requiere ejecutar como root para mostrar estado (omitido)"
    else
        ufw status verbose
    fi
else
    warn "UFW no instalado"
fi

echo ""
# ==========================================
echo "B3 fail2ban"
# ==========================================
echo ""

info "Estado fail2ban"

if systemctl is-active --quiet fail2ban; then
    ok "fail2ban activo"
else
    warn "fail2ban no activo"
fi

echo ""
# ==========================================
echo "B4 Cron host"
# ==========================================
echo ""

info "Cron del usuario"

crontab -l 2>/dev/null || echo "Sin crontab"

info "Cron root"

if [ "$EUID" -ne 0 ]; then
    warn "Comprobación de crontab root requiere privilegios de root (omitido)"
else
    crontab -l 2>/dev/null || echo "Sin crontab root"
fi

echo ""
# ==========================================
echo "B5 Docker"
# ==========================================
echo ""

info "Docker runtime"

if command -v docker >/dev/null 2>&1; then
    docker version --format '{{.Server.Version}}' || warn "Docker no responde"
    ok "Docker instalado"
else
    fail "Docker no instalado"
fi

echo ""
# ==========================================
echo "B6 Contenedores"
# ==========================================
echo ""

info "Contenedores activos"

CONTAINERS=$(docker ps -q)

if [ -z "$CONTAINERS" ]; then
    info "No hay contenedores desplegados"
else
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
fi

echo ""
# ==========================================
echo "B7 Puertos host"
# ==========================================
echo ""

info "Puertos abiertos en host"

ss -tulpn

echo ""
# ==========================================
echo "B8 Redes Docker"
# ==========================================
echo ""

info "Redes Docker"

docker network ls

if docker network inspect backend-net >/dev/null 2>&1 || docker network inspect observability-net >/dev/null 2>&1 || docker network inspect restricted-net >/dev/null 2>&1; then
    ok "Redes de monitoring (backend-net/observability-net/restricted-net) detectadas"
else
    warn "No se detectan redes de monitoring (backend-net/observability-net/restricted-net)"
fi

echo ""
# ==========================================
echo "B9 Volúmenes"
# ==========================================
echo ""

info "Volúmenes Docker"

docker volume ls

echo ""
echo "------------------------------------------"
echo "C.- CUMPLIMIENTO ADR"
echo "------------------------------------------"

echo ""
# ==========================================
echo "C1 ADR-0014 / ADR-0015"
# ==========================================
echo ""

info "Verificando exposición de puertos Docker (ADR-0014 / ADR-0015)"

if [ -n "$STRUCTURED_FILE" ] && [ -s "$STRUCTURED_FILE" ]; then
    PORTS_OUTPUT=$(python3 - <<PY
import json,sys
try:
    j=json.load(open('$STRUCTURED_FILE'))
    ports=j.get('ports',[])
    if not ports:
        sys.exit(2)
    for s,p in ports:
        print(f"  - {s}: {p}")
except Exception:
    sys.exit(3)
PY
)
    RC=$?
    if [ $RC -eq 2 ]; then
        ok "No se detectaron puertos expuestos globalmente (estructura detectada)"
    elif [ $RC -eq 3 ]; then
        warn "No se pudo parsear salida JSON de validación estructurada"
    else
        warn "Puertos potencialmente expuestos (structured):"
        echo "$PORTS_OUTPUT"
    fi
else
    warn "No se ejecutaron validaciones estructuradas: no se pudo evaluar exposición de puertos"
fi

echo ""
# ==========================================
echo "C2 Validación reproducibilidad de imágenes"
# ==========================================
echo ""

info "Ejecutando validaciones de reproducibilidad: ops/audit/validate_reproducibility.sh"

if bash ops/audit/validate_reproducibility.sh; then
    ok "Validación reproducibilidad pasada"
else
    fail "Validación reproducibilidad falló — revisar salida anterior"
    exit 1
fi

echo ""
# ==========================================
echo "C3 docker.sock"
# ==========================================
echo ""

info "Verificando montaje docker.sock (superficie de ataque)"

if [ -n "$STRUCTURED_FILE" ] && [ -s "$STRUCTURED_FILE" ]; then
    SOCK_OUTPUT=$(python3 - <<PY
import json,sys
try:
    j=json.load(open('$STRUCTURED_FILE'))
    ds=j.get('docker_sock',[])
    if not ds:
        sys.exit(2)
    for s,v in ds:
        print(f"  - {s}: {v}")
except Exception:
    sys.exit(3)
PY
)
    RC=$?
    if [ $RC -eq 2 ]; then
        ok "docker.sock no montado en contenedores (estructura detectada)"
    elif [ $RC -eq 3 ]; then
        warn "No se pudo parsear salida JSON de validación estructurada"
    else
        warn "docker.sock detectado (structured):"
        echo "$SOCK_OUTPUT"
    fi
else
    SOCK=$(grep -R "docker.sock" -n ops 2>/dev/null || true)
    if [ -z "$SOCK" ]; then
        ok "docker.sock no montado en contenedores"
    else
        warn "docker.sock detectado:"
        echo "$SOCK"
    fi
fi

echo ""
# ==========================================
echo "C4 servicios fuera de backend-net / observability-net / restricted-net"
# ==========================================
echo ""


info "Verificando uso de redes backend-net / observability-net / restricted-net"

NO_NET=$(grep -R "services:" -n ops/stacks 2>/dev/null || true)

if docker network inspect backend-net >/dev/null 2>&1; then
    ok "Red backend-net disponible"
else
    warn "backend-net no existe"
fi

echo ""
# ==========================================
echo "C5 ADR-0016 cron del host para lógica de aplicación"
# ==========================================
echo ""

info "Buscando ejecución de scripts del proyecto en cron del host"

HOST_CRON=$(sudo crontab -l 2>/dev/null | grep "/opt/monitoring" || true)

if [ -z "$HOST_CRON" ]; then
    ok "Cron del host no ejecuta lógica del proyecto"
else
    warn "Cron host ejecuta scripts del proyecto:"
    echo "$HOST_CRON"
fi

echo ""
# ==========================================
echo "C6 ejecución python fuera de contenedor"
# ==========================================
echo ""

info "Buscando ejecución directa de Python del proyecto"

HOST_PY=$(ps aux | grep python | grep "/opt/monitoring" | grep -v grep || true)

if [ -z "$HOST_PY" ]; then
    ok "No se detectó Python del proyecto ejecutándose en host"
else
    warn "Python del proyecto ejecutándose en host:"
    echo "$HOST_PY"
fi

# ADR-0016

echo ""
# ==========================================
echo "C7 permisos scripts host hardening"
# ==========================================
echo ""

info "Verificando scripts de hardening del host"

HARDEN_SCRIPTS=(
"/opt/monitoring/ops/deployment/configure_docker_limits.sh"
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
echo "------------------------------------------"
echo "FIN AUDITORÍA"
echo "------------------------------------------"
