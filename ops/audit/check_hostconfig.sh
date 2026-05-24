#!/usr/bin/env bash
set -euo pipefail
# Simple HostConfig checks: FAIL = structural violations, WARN = exceptions

EXIT_CODE=0

info(){ echo "[INFO] $@"; }
warn(){ echo "[WARN] $@"; }
fail(){ echo "[FAIL] $@"; EXIT_CODE=1; }

# Allowed readonly host mounts (exceptions)
ALLOWED_READONLY=("/var/log" "/var/lib/docker/containers")

list=$$(bash ops/runtime_containers.sh list)

infra_trusted=$$(bash ops/runtime_containers.sh by-type INFRA_TRUSTED | tr '\n' ' ')

for c in $$list; do
  if ! docker ps --format '{{.Names}}' | grep -q "^$$c$$"; then
    info "$$c not running; skipping"; continue
  fi

  info "Checking container $$c"
  # privileged
  PRIV=$$(docker inspect --format '{{.HostConfig.Privileged}}' $$c 2>/dev/null || echo "false")
  if [ "$$PRIV" = "true" ]; then
    fail "$$c has HostConfig.Privileged=true"
  fi

  # network_mode
  NMODE=$$(docker inspect --format '{{.HostConfig.NetworkMode}}' $$c 2>/dev/null || echo "")
  if [ "$$NMODE" = "host" ]; then
    fail "$$c uses network_mode=host"
  fi

  # mounts
  docker inspect --format '{{range .Mounts}}{{.Source}}:::{{.Destination}}:::{{.RW}}\n{{end}}' $$c 2>/dev/null | while IFS= read -r m; do
    src=$$(echo "$$m" | cut -d':' -f1)
    dest=$$(echo "$$m" | cut -d':' -f3)
    rwflag=$$(echo "$$m" | cut -d':' -f5)
    # detect docker.sock
    if echo "$$src" | grep -q "docker.sock"; then
      fail "$$c mounts docker.sock from host (source=$$src)"
    fi
    # detect bind mounts to repo code (heuristic: presence of /opt/monitoring or relative paths)
    if echo "$$src" | grep -q "/opt/monitoring\|/home/\|/mnt/"; then
      # allow readonly exceptions for specific allowed paths
      allowed=0
      for a in "${ALLOWED_READONLY[@]}"; do
        if [ "$$src" = "$$a" ]; then allowed=1; break; fi
      done
      if [ $$allowed -eq 0 ]; then
        # if rw then FAIL, else WARN
        if [ "$$rwflag" = "true" ]; then
          fail "$$c has potentially dangerous bind mount $$src (rw)"
        else
          warn "$$c mounts host path $$src (ro) — review if sensitive"
        fi
      fi
    fi
  done

  # capabilities
  caps=$$(docker inspect --format '{{json .HostConfig.CapAdd}}' $$c 2>/dev/null || echo "[]")
  echo "$$caps" | grep -q "SYS_ADMIN\|NET_ADMIN" && fail "$$c adds dangerous capabilities: $$caps" || true

  # user check: if running as root and not infra_trusted -> WARN
  USERVAL=$$(docker inspect --format '{{.Config.User}}' $$c 2>/dev/null || echo "")
  if [ -z "$$USERVAL" ]; then
    # no user specified -> default image user (often root)
    if echo " $$infra_trusted " | grep -q " $$c "; then
      info "$$c is infra_trusted and may run as root"
    else
      warn "$$c has no explicit user (may run as root)"
    fi
  else
    info "$$c configured user=$$USERVAL"
  fi
done

exit $$EXIT_CODE
