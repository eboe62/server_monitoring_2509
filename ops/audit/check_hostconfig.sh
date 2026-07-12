#!/usr/bin/env bash
set -euo pipefail

# ------------------------------------------------------------
# Propósito:
#     Verificar de forma directa las configuraciones HostConfig de contenedores Docker en ejecución.
#
# Rol dentro de la arquitectura:
#     Es el validador runtime que aplica políticas de seguridad en tiempo de ejecución por contenedor.
#
# Entradas principales:
#     Contenedores en ejecución listados por ops/runtime_containers.sh y salida de docker inspect.
#
# Salidas principales:
#     Mensajes de consola con FAIL/WARN/INFO y código de salida 0/1.
#
# Relación con otros componentes:
#     Se invoca desde Makefile y puede integrarse en pipelines de seguridad runtime.
#
# Relación con la gobernanza:
#     Soporta ADR-0030 y ADR-0031 mediante validaciones de Privileged, SecurityOpt, Capabilities, ReadonlyRootfs y montajes.
#
# Observaciones:
#     No es un analizador de Compose estático; valida el estado real del host en contenedores en ejecución.
# ------------------------------------------------------------

# ==========================================
# HostConfig Runtime Audit
# FAIL = violaciones estructurales
# WARN = excepciones aprobadas o hardening incompleto
# ==========================================

EXIT_CODE=0
info() {
  echo "[INFO] $*"
}
warn() {
  echo "[WARN] $*"
}
fail() {
  echo "[FAIL] $*"
  EXIT_CODE=1
}
require_binary() {
  local bin="$1"

  if ! command -v "$bin" >/dev/null 2>&1; then
    echo "[FAIL] Required binary not found: $bin"
    exit 1
  fi
}

require_binary docker
require_binary jq

# ==========================================
# Allowed readonly host mounts (approved exceptions)
# ==========================================

ALLOWED_READONLY=(
  "/var/log"
  "/var/lib/docker/containers"
)

# ==========================================
# Runtime container inventory
# ==========================================

list=$(bash ops/runtime_containers.sh list)

infra_trusted=$(
  bash ops/runtime_containers.sh by-type INFRA_TRUSTED \
    | tr '\n' ' '
)

# ==========================================
# Main audit loop
# ==========================================

for c in $list; do
  if ! docker ps --format '{{.Names}}' | grep -q "^${c}$"; then
    info "${c} not running; skipping"
    continue
  fi
  info "Checking container ${c}"

  inspect_json=$(docker inspect "${c}" 2>/dev/null)

  # =======================================================
  # Privileged mode
  # =======================================================

  privileged=$(
    echo "${inspect_json}" \
      | jq -r '.[0].HostConfig.Privileged'
  )
  if [ "${privileged}" = "true" ]; then
    fail "${c} has HostConfig.Privileged=true"
  fi

  # =======================================================
  # Network mode
  # =======================================================

  network_mode=$(
    echo "${inspect_json}" \
      | jq -r '.[0].HostConfig.NetworkMode'
  )
  if [ "${network_mode}" = "host" ]; then
    fail "${c} uses network_mode=host"
  fi

  # =======================================================
  # Readonly rootfs
  # =======================================================

  readonly_rootfs=$(
    echo "${inspect_json}" \
      | jq -r '.[0].HostConfig.ReadonlyRootfs'
  )
  if [ "${readonly_rootfs}" != "true" ]; then
    warn "${c} has ReadonlyRootfs=false"
  fi

  # =======================================================
  # SecurityOpt
  # =======================================================

  security_opt=$(
    echo "${inspect_json}" \
      | jq -r '.[0].HostConfig.SecurityOpt // [] | join(",")'
  )

  # no-new-privileges
  if ! echo "${security_opt}" | grep -q "no-new-privileges"; then
    warn "${c} missing no-new-privileges"
  fi

  # seccomp validation
  # Docker aplica seccomp default implícitamente cuando SecurityOpt es null/vacío.
  # Solo advertimos si seccomp está explícitamente deshabilitado.
  if echo "${security_opt}" | grep -q "seccomp=unconfined"; then
    warn "${c} has seccomp explicitly disabled"
  fi

  # =======================================================
  # Capabilities
  # =======================================================

  cap_add=$(
    echo "${inspect_json}" \
      | jq -r '.[0].HostConfig.CapAdd // [] | join(",")'
  )
  if echo "${cap_add}" | grep -Eq 'SYS_ADMIN|NET_ADMIN'; then
    fail "${c} adds dangerous capabilities: ${cap_add}"
  fi
  cap_drop=$(
    echo "${inspect_json}" \
      | jq -r '.[0].HostConfig.CapDrop // [] | join(",")'
  )
  if [ -z "${cap_drop}" ]; then
    warn "${c} does not define CapDrop"
  fi

  # =======================================================
  # Mount inspection
  # =======================================================

  echo "${inspect_json}" \
    | jq -c '.[0].Mounts[]?' \
    | while read -r mount; do
        src=$(echo "${mount}" | jq -r '.Source // ""')
        dest=$(echo "${mount}" | jq -r '.Destination // ""')
        rw=$(echo "${mount}" | jq -r '.RW // false')
        type=$(echo "${mount}" | jq -r '.Type // ""')

        # ---------------------------------------------------
        # docker.sock forbidden
        # ---------------------------------------------------

        if echo "${src}" | grep -q "docker.sock"; then
          fail "${c} mounts docker.sock from host (${src})"
        fi

        # ---------------------------------------------------
        # Host bind mounts
        # ---------------------------------------------------

        if [ "${type}" = "bind" ]; then
          allowed=0
          for a in "${ALLOWED_READONLY[@]}"; do
            if [ "${src}" = "${a}" ]; then
              allowed=1
              break
            fi
          done

          # -------------------------------------------------
          # Approved readonly exceptions
          # -------------------------------------------------

          if [ "${allowed}" -eq 1 ]; then
            if [ "${rw}" = "true" ]; then
              fail "${c} mounts approved path ${src} as rw"
            else
              info "${c} approved readonly bind mount: ${src}"
            fi
            continue
          fi

          # -------------------------------------------------
          # Runtime source-code mounts
          # -------------------------------------------------

          if echo "${src}" | grep -Eq '/opt/monitoring|/home/|/mnt/'; then
            if [ "${rw}" = "true" ]; then
              fail "${c} has dangerous rw bind mount: ${src}"
            else
              warn "${c} mounts host path readonly: ${src}"
            fi
          else
            warn "${c} uses non-approved bind mount: ${src}"
          fi
        fi
      done

  # =======================================================
  # Runtime user
  # =======================================================

  runtime_user=$(
    echo "${inspect_json}" \
      | jq -r '.[0].Config.User // ""'
  )
  if [ -z "${runtime_user}" ]; then
    if echo " ${infra_trusted} " | grep -q " ${c} "; then
      info "${c} is infra_trusted and may run as root"
    else
      warn "${c} has no explicit runtime user"
    fi
  else
    info "${c} configured user=${runtime_user}"
  fi
done

# ==========================================
# Final result
# ==========================================

exit ${EXIT_CODE}
