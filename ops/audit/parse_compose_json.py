#!/usr/bin/env python3
"""Helper to parse compose checker JSON output from file.

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
