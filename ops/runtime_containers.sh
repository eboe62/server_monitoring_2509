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
  awk '
    /^[[:space:]]{2}[a-zA-Z0-9_\-]+:/ { name=$1; sub(":","",name); inname=1; type=""; policy=""; enforce=""; next }
    inname && /^[[:space:]]{4}type:/ { type=$2 }
    inname && /^[[:space:]]{4}healthcheck_policy:/ { policy=$2 }
    inname && /^[[:space:]]{4}enforcement_level:/ { enforce=$2 }
    inname && NF==0 { print name "|" type "|" policy "|" enforce; inname=0 }
    END { if(inname) print name "|" type "|" policy "|" enforce }
  ' "$YAML_FILE"
}

case "$cmd" in
  list)
    parse_all | cut -d'|' -f1
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
