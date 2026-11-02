#!/usr/bin/env bash
set -euo pipefail

# ------------------------------------------------------------
# Propósito:
#     Verificar que el host cumple la política de host hardening antes de dar por bueno un despliegue.
#
# Rol dentro de la arquitectura:
#     Es el control final de make deploy: un host sin endurecer hace fallar los tests del Makefile en cascada.
#
# Entradas principales:
#     Crontabs del host, contenedores listados por ops/runtime_containers.sh (docker inspect) y estado de fail2ban y UFW.
#
# Salidas principales:
#     Mensajes de consola con FAIL/WARN/INFO/OK y código de salida 0/1.
#
# Relación con otros componentes:
#     Se invoca desde Makefile (audit-host-hardening, último paso de deploy).
#
# Relación con la gobernanza:
#     Valida ADR-0016 (P1 portabilidad: nada del proyecto en el cron del host; P2 límites de recursos,
#     fail2ban y UFW) y ADR-0012.
#
# Observaciones:
#     Solo lectura. No necesita root: el crontab de root se lee con sudo -n si está permitido; si no, WARN.
# ------------------------------------------------------------

# ==========================================
# Host Hardening Audit (ADR-0016)
# FAIL = el host no cumple la política
# WARN = comprobación no concluyente
# ==========================================

EXIT_CODE=0
REPO_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

info() {
  echo "[INFO] $*"
}
ok() {
  echo "[OK] $*"
}
warn() {
  echo "[WARN] $*"
}
fail() {
  echo "[FAIL] $*"
  EXIT_CODE=1
}

# Entradas del proyecto: rutas del repo, docker compose, make o módulos Python del proyecto
PROJECT_PATTERN="${REPO_DIR}|monitoring|docker compose|docker-compose|make |python3 -m "

check_cron_source() {
  local label="$1"
  local content="$2"
  local hits

  hits=$(echo "$content" | grep -vE '^[[:space:]]*(#|$)' | grep -E "$PROJECT_PATTERN" || true)
  if [ -n "$hits" ]; then
    fail "${label} contiene tareas del proyecto (ADR-0016 P1):"
    echo "$hits" | sed 's/^/       /'
  else
    ok "${label} sin tareas del proyecto"
  fi
}

# ==========================================
# [1] Cron del host (P1)
# ==========================================

echo "[1] Cron del host"

check_cron_source "crontab de $(id -un)" "$(crontab -l 2>/dev/null || true)"

if [ "$(id -u)" -eq 0 ]; then
  : # ya comprobado arriba
elif root_cron=$(sudo -n crontab -l -u root 2>/dev/null); then
  check_cron_source "crontab de root" "$root_cron"
elif sudo -n true 2>/dev/null; then
  ok "crontab de root vacío"
else
  warn "crontab de root no comprobado (requiere sudo sin contraseña)"
fi

for f in /etc/crontab /etc/cron.d/*; do
  [ -f "$f" ] || continue
  check_cron_source "$f" "$(cat "$f" 2>/dev/null || true)"
done

# ==========================================
# [2] Límites de recursos de los contenedores del proyecto (P2)
# ==========================================

echo "[2] Límites de CPU y memoria"

if ! running=$(docker ps --format '{{.Names}}' 2>/dev/null); then
  fail "docker no disponible: no se pueden comprobar los límites"
  running=""
fi

for c in $(bash "${REPO_DIR}/ops/runtime_containers.sh" list); do
  if ! echo "$running" | grep -q "^${c}$"; then
    info "${c} no está en ejecución; se omite"
    continue
  fi

  mem=$(docker inspect --format '{{.HostConfig.Memory}}' "$c")
  cpus=$(docker inspect --format '{{.HostConfig.NanoCpus}}' "$c")

  if [ "$mem" -eq 0 ] || [ "$cpus" -eq 0 ]; then
    fail "${c} sin límites (Memory=${mem}, NanoCpus=${cpus}); declararlos en deploy.resources.limits"
  else
    ok "${c} con límites (Memory=$((mem / 1024 / 1024))M, CPUs=$(awk "BEGIN { printf \"%.2f\", ${cpus} / 1000000000 }"))"
  fi
done

# ==========================================
# [3] fail2ban y UFW (P2)
# ==========================================

echo "[3] fail2ban y UFW"

if systemctl is-active --quiet fail2ban 2>/dev/null; then
  ok "fail2ban activo"
else
  fail "fail2ban no activo"
fi

if grep -qE '^ENABLED=yes' /etc/ufw/ufw.conf 2>/dev/null && systemctl is-active --quiet ufw 2>/dev/null; then
  ok "UFW activo"
else
  fail "UFW no activo (/etc/ufw/ufw.conf ENABLED=yes y servicio ufw)"
fi

if [ "$EXIT_CODE" -eq 0 ]; then
  echo "[OK] host hardening conforme (ADR-0016)"
else
  echo "[FAIL] host hardening no conforme (ADR-0016)"
fi

exit "$EXIT_CODE"
