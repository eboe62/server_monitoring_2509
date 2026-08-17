#!/usr/bin/env python3
"""
------------------------------------------------------------
Propósito:
    Formatear la salida JSON de compose_policy_checks.py para uso en scripts shell.

Rol dentro de la arquitectura:
    Es el convertidor auxiliar que extrae valores específicos de auditoría Compose.

Entradas principales:
    Archivo JSON generado por compose_policy_checks.py y la clave solicitada.

Salidas principales:
    Listado formateado en consola y códigos de salida adaptados.

Relación con otros componentes:
    Lo invoca audit_repo_host.sh cuando jq no está disponible para parsear resultados JSON.

Relación con la gobernanza:
    Soporta ADR-0029 al permitir que scripts host-side consuman salidas estructuradas.

Observaciones:
    No realiza comprobaciones de seguridad; solo formatea resultados ya generados.
------------------------------------------------------------

Helper to parse compose checker JSON output from file.

Usage: parse_compose_json.py <json_file> <key>

Keys supported: ports, docker_sock

Exit codes:
 0 -> printed entries
 2 -> no entries found
 3 -> parse error

This small helper avoids embedding Python inline in shell scripts.
"""
import json
import sys


def main(argv):
    if len(argv) < 3:
        print("Usage: parse_compose_json.py <json_file> <key>", file=sys.stderr)
        return 3
    path = argv[1]
    key = argv[2]
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            j = json.load(fh)
    except Exception as e:
        print(f"[ERR] failed to read/parse JSON: {e}", file=sys.stderr)
        return 3

    items = j.get(key)
    if not items:
        return 2

    try:
        for it in items:
            if isinstance(it, list) and len(it) >= 2:
                print(f"  - {it[0]}: {it[1]}")
            else:
                print(f"  - {it}")
    except Exception as e:
        print(f"[ERR] failed formatting items: {e}", file=sys.stderr)
        return 3

    return 0


if __name__ == '__main__':
    rc = main(sys.argv)
    sys.exit(rc)
