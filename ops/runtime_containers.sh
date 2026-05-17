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

# ==========================================
# Deterministic compose resolution using `docker compose config`
# ==========================================

find_compose_files() {
  # Only consider explicit compose locations
  files=""
  for f in ops/stacks/*/compose.yml; do
    [ -f "$f" ] && files="$files $f"
  done
  for f in ops/services/*/compose.yml; do
    [ -f "$f" ] && files="$files $f"
  done
  echo "$files"
}

render_compose_config() {
  local file="$1"
  local out="$2"
  # Render compose into canonical YAML; caller handles return code
  docker compose -f "$file" config >"$out" 2>/dev/null
}

parse_rendered_compose() {
  # Output: service_name|container_name|has_healthcheck
  local cfg="$1"
  awk '
    BEGIN{in_services=0; svc=""; c_name=""; hc=0}
    /^[[:space:]]*services:\s*$/ { in_services=1; next }
    in_services && /^[[:space:]]{2}[^[:space:]]+:\s*$/ {
        if(svc!="") { print svc "|" c_name "|" (hc?"yes":"no") }
        svc=$1; sub(":","",svc); gsub(/^[[:space:]]+|[[:space:]]+$/,"",svc);
        c_name=""; hc=0; next
    }
    in_services && /^[[:space:]]{4}container_name:\s*/ { $1=""; sub(/^[[:space:]]+/,"",$0); c_name=$0; next }
    in_services && /^[[:space:]]{4}healthcheck:\s*/ { hc=1; next }
    END{ if(svc!="") print svc "|" c_name "|" (hc?"yes":"no") }
  ' "$cfg"
}

check_health_for_container() {
  local cname="$1"
  local file tmp
  local first_invalid=""
  for file in $(find_compose_files); do
    tmp=$(mktemp)
    if ! render_compose_config "$file" "$tmp"; then
      # record first invalid compose
      if [ -z "$first_invalid" ]; then
        first_invalid="$file"
      fi
      rm -f "$tmp"
      continue
    fi

    while IFS='|' read -r svc c_name has_hc; do
      svc_trim=$(echo "$svc" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
      c_trim=$(echo "$c_name" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
      if [ "$svc_trim" = "$cname" ]; then
        echo "$cname|FOUND|$file|$svc_trim|${has_hc}"
        rm -f "$tmp"
        return 0
      fi
      if [ -n "$c_trim" ] && [ "$c_trim" = "$cname" ]; then
        echo "$cname|FOUND|$file|$svc_trim|${has_hc}"
        rm -f "$tmp"
        return 0
      fi
    done < <(parse_rendered_compose "$tmp")

    rm -f "$tmp"
  done

  if [ -n "$first_invalid" ]; then
    echo "$cname|COMPOSE_INVALID|$first_invalid|||"
    return 3
  fi

  echo "$cname|NOT_FOUND|||"
  return 2
}

debug_check_health() {
  local cname="$1"
  local file tmp
  echo "DEBUG: checking container '$cname'"
  for file in $(find_compose_files); do
    echo "- evaluating compose: $file"
    tmp=$(mktemp)
    if ! render_compose_config "$file" "$tmp"; then
      echo "  -> compose render FAILED (missing .env or invalid)"
      rm -f "$tmp"
      continue
    fi
    echo "  -> services found:"
    parse_rendered_compose "$tmp" | while IFS='|' read -r svc c_name has_hc; do
      svc_trim=$(echo "$svc" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
      c_trim=$(echo "$c_name" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
      echo "     * service='$svc_trim' container_name='$c_trim' healthcheck=$has_hc"
      if [ "$svc_trim" = "$cname" ]; then
        echo "       => MATCH by service name"
      elif [ -n "$c_trim" ] && [ "$c_trim" = "$cname" ]; then
        echo "       => MATCH by container_name"
      else
        echo "       => no match"
      fi
    done
    rm -f "$tmp"
  done
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
  debug)
    if [ $# -lt 2 ]; then echo "Usage: $0 debug <container>" >&2; exit 2; fi
    cname="$2"
    debug_check_health "$cname"
    exit 0
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
