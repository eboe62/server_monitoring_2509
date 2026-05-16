#!/usr/bin/env bash
# Simple YAML parser for `ops/runtime_containers.yml`
# Usage: ops/runtime_containers.sh list
#        ops/runtime_containers.sh get <container>
#        ops/runtime_containers.sh by-type <TYPE>

set -euo pipefail
YAML_FILE="$(dirname "$0")/runtime_containers.yml"

if [ ! -f "$YAML_FILE" ]; then
  echo "ERROR: $YAML_FILE not found" >&2
  exit 2
fi

cmd="$1" || cmd=""

parse_all() {
  # Robust YAML parse for our simple structure (no external deps)
  awk '
    BEGIN{in_cont=0; name=""; type=""; policy=""; enforce=""}
    /^[[:space:]]*containers:\s*$/ { in_cont=1; next }
    in_cont && /^[[:space:]]{2}[a-zA-Z0-9_\-]+:\s*$/ {
        if(name!="") { print name "|" type "|" policy "|" enforce }
        name=$1; sub(":","",name); type=""; policy=""; enforce=""; next
    }
    in_cont && /^[[:space:]]{4}type:\s*/ { $1=""; sub(/^[[:space:]]+/,"",$0); type=$0; sub(/^[[:space:]]+/,"",type); next }
    in_cont && /^[[:space:]]{4}healthcheck_policy:\s*/ { $1=""; sub(/^[[:space:]]+/,"",$0); policy=$0; sub(/^[[:space:]]+/,"",policy); next }
    in_cont && /^[[:space:]]{4}enforcement_level:\s*/ { $1=""; sub(/^[[:space:]]+/,"",$0); enforce=$0; sub(/^[[:space:]]+/,"",enforce); next }
    END{ if(name!="") print name "|" type "|" policy "|" enforce }
  ' "$YAML_FILE"
}

# find compose files under ops
find_compose_files() {
  find ops -type f \( -name "compose*.yml" -o -name "compose*.yaml" \) 2>/dev/null || true
}

# Given a compose file, produce a canonical config via `docker compose config` into a temp file
render_compose_config() {
  local file="$1"
  local out="$2"
  if docker compose -f "$file" config >"$out" 2>/dev/null; then
    return 0
  else
    return 1
  fi
}

# Extract service block for a given service name from a rendered compose config
extract_service_block() {
  local cfg="$1"; local svc="$2"
  awk -v svc="$svc" '
    BEGIN{in_services=0; in_svc=0; indent=0}
    /^[[:space:]]*services:\s*$/ { in_services=1; next }
    in_services && /^[[:space:]]{2}[^[:space:]]+:\s*$/ {
        cur = $1; sub(":","",cur);
        gsub(/^[ ]+|[ ]+$/,"",cur);
        if(cur==svc) { in_svc=1; indent=2; print; next } else { in_svc=0 }
    }
    in_svc { print }
  ' "$cfg"
}

# Check healthcheck presence for a given container name by scanning rendered compose files
check_health_for_container() {
  local cname="$1"
  local cf
  local tmp
  for cf in $(find_compose_files); do
    tmp=$(mktemp)
    if ! render_compose_config "$cf" "$tmp"; then
      rm -f "$tmp"
      # skip files that cannot be rendered (missing envs etc.)
      continue
    fi

    # First, try to find a service with the same name
    svc_found=""
    if awk -v n="$cname" 'BEGIN{FS=":"} /^[[:space:]]{2}[a-zA-Z0-9_\-]+:\s*$/ { s=$1; gsub(/^[[:space:]]+|[[:space:]]+$/,"",s); if(s==n){print s; exit 0}}' "$tmp" >/dev/null 2>&1; then
      svc_found="$cname"
    fi

    # If not found by service name, search for a container_name match inside service blocks
    if [ -z "$svc_found" ]; then
      # iterate services
      awk '/^[[:space:]]{2}[a-zA-Z0-9_\-]+:\s*$/ {svc=$1; sub(":","",svc); gsub(/^[ ]+|[ ]+$/,"",svc); in_svc=1; next} in_svc{ if($1~/container_name:/){ print svc ":" substr($0,index($0,$2)) ; exit 0 } }' "$tmp" | while IFS= read -r line; do
        # line like: svc: monitoring-postgres
        svcname=${line%%:*}
        val=${line#*:}
        val=$(echo "$val" | sed 's/^[[:space:]]*//')
        # compare val to cname
        if [ "$val" = "$cname" ]; then
          svc_found="$svcname"
        fi
      done
    fi

    if [ -n "$svc_found" ]; then
      # extract service block and check healthcheck presence
      block=$(extract_service_block "$tmp" "$svc_found")
      if echo "$block" | awk '/^[[:space:]]*healthcheck:\s*$/ {found=1} END{if(found) exit 0; else exit 1}'; then
        echo "$cname|FOUND|$cf|$svc_found|healthcheck_present"
        rm -f "$tmp"
        return 0
      else
        echo "$cname|FOUND|$cf|$svc_found|healthcheck_absent"
        rm -f "$tmp"
        return 1
      fi
    fi
    rm -f "$tmp"
  done
  echo "$cname|NOT_FOUND|||"
  return 2
}

case "$cmd" in
  list)
    parse_all | cut -d'|' -f1
    ;;
  check-health)
    if [ $# -lt 2 ]; then echo "Usage: $0 check-health <container>" >&2; exit 2; fi
    cname="$2"
    check_health_for_container "$cname"
    exit $?
    ;;
  get)
    if [ $# -lt 2 ]; then echo "Usage: $0 get <container>" >&2; exit 2; fi
    name="$2"
    parse_all | awk -F'|' -v n="$name" '$1==n{print; exit 0} END{exit 1}'
    ;;
  by-type)
    if [ $# -lt 2 ]; then echo "Usage: $0 by-type <TYPE>" >&2; exit 2; fi
    t="$2"
    parse_all | awk -F'|' -v t="$t" '$2==t{print $1}'
    ;;
  all)
    parse_all
    ;;
  *)
    echo "Runtime containers helper" >&2
    echo "Usage: $0 list|all|get <container>|by-type <TYPE>" >&2
    exit 2
    ;;
esac
