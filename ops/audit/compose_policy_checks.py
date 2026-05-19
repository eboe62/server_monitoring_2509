#!/usr/bin/env python3
"""Structured Compose policy checks for audit.

Modelo de ejecución (importante):

- Este módulo está diseñado para ejecutarse dentro del contenedor monitoring-python para garantizar la paridad con el tiempo de ejecución (aceso al CLI de docker / docker.sock cuando el contenedor tiene permisos).
- El script de orquestación del host (ops/audit/audit_repo_host.sh) llama a este módulo dentro del contenedor y solo se encarga de coordinar y recoger su salida en formato JSON
- Fallback (Respaldo): cuando el comando docker compose config (que resuelve el estado real en runtime) no está disponible, el módulo hará un intento de parseo de los archivos YAML de compose bajo la carpeta ops/. Este respaldo es explícitamente no determinista comparado con docker compose y emitirá un aviso (WARN) para informar a los operadores.
Prefiere la salida resuelta de docker compose config cuando está disponible y recurre a la fusión de archivos compose encontrados bajo ops/ como último recurso.

Soporta --json para salida procesable por máquinas, --self-test para comprobaciones del entorno de ejecución y --check para ejecutar un subconjunto específico de comprobaciones.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from typing import Any, Dict, List, Tuple

try:
    import yaml
except Exception:
    print("[WARN] PyYAML no disponible dentro del contenedor; algunas comprobaciones pueden fallar", file=sys.stderr)
    yaml = None


def ok(msg: str):
    print(f"[ OK ] {msg}", file=sys.stderr)


def warn(msg: str):
    print(f"[WARN] {msg}", file=sys.stderr)


def fail(msg: str):
    print(f"[FAIL] {msg}", file=sys.stderr)


def load_compose_via_docker() -> Dict[str, Any] | None:
    try:
        out = subprocess.check_output(["docker", "compose", "config"], stderr=subprocess.DEVNULL)
        if not yaml:
            return None
        return yaml.safe_load(out)
    except Exception:
        return None


def check_docker_runtime() -> Dict[str, bool]:
    """Check availability of docker CLI and compose inside the runtime container."""
    status = {"docker_cli": False, "docker_compose": False, "compose_config": False, "docker_sock": False}
    try:
        subprocess.check_output(["docker", "--version"], stderr=subprocess.DEVNULL)
        status["docker_cli"] = True
    except Exception:
        return status

    try:
        subprocess.check_output(["docker", "compose", "version"], stderr=subprocess.DEVNULL)
        status["docker_compose"] = True
    except Exception:
        pass

    try:
        # Try a harmless compose config to validate connectivity
        subprocess.check_output(["docker", "compose", "config"], stderr=subprocess.DEVNULL, timeout=10)
        status["compose_config"] = True
    except Exception:
        pass

    # Check docker.sock accessibility by trying to list containers
    try:
        subprocess.check_output(["docker", "ps", "-q"], stderr=subprocess.DEVNULL, timeout=10)
        status["docker_sock"] = True
    except Exception:
        pass

    return status


def find_compose_files() -> List[str]:
    candidates = []
    names = (
        "docker-compose.yml",
        "docker-compose.yaml",
        "compose.yml",
        "compose.yaml",
        "compose.override.yml",
        "compose.override.yaml",
    )
    for root, _, filenames in os.walk("ops"):
        for fn in filenames:
            if (fn in names) or (fn.startswith("compose") and fn.endswith((".yml", ".yaml"))):
                candidates.append(os.path.join(root, fn))
    return sorted(set(candidates))


def load_compose_from_files(files: List[str]) -> Dict[str, Any] | None:
    merged: Dict[str, Any] = {"services": {}}
    if not yaml:
        return None
    for f in files:
        try:
            with open(f, "rb") as fh:
                data = yaml.safe_load(fh)
                if not data:
                    continue
                services = data.get("services") or {}
                merged["services"].update(services)
        except Exception:
            continue
    return merged if merged["services"] else None


def get_compose_dict() -> Dict[str, Any]:
    d = load_compose_via_docker()
    if d:
        return d

    files = find_compose_files()
    if files:
        loaded = load_compose_from_files(files)
        if loaded:
            warn("Usando parseo estático de archivos Compose (mejor usar runtime `docker compose config`)")
            return loaded

    return {"services": {}}


def _service_ports(svc: Dict[str, Any]) -> List[str]:
    ports = svc.get("ports") or []
    out: List[str] = []
    for p in ports:
        if isinstance(p, str):
            out.append(p)
        elif isinstance(p, dict):
            target = p.get("target")
            published = p.get("published")
            out.append(f"{published}:{target}" if published and target else json.dumps(p))
    return out


def detect_published_ports(compose: Dict[str, Any]) -> List[Tuple[str, str]]:
    findings: List[Tuple[str, str]] = []
    for name, svc in (compose.get("services") or {}).items():
        for p in _service_ports(svc):
            findings.append((name, p))
    return findings


def detect_docker_sock(compose: Dict[str, Any]) -> List[Tuple[str, str]]:
    findings: List[Tuple[str, str]] = []
    for name, svc in (compose.get("services") or {}).items():
        vols = svc.get("volumes") or []
        for v in vols:
            # short syntax: 'host:container:ro'
            if isinstance(v, str):
                parts = v.split(":")
                # check both source and target
                if any("docker.sock" in part for part in parts):
                    findings.append((name, v))
            elif isinstance(v, dict):
                src = v.get("source") or v.get("bind") or v.get("type")
                target = v.get("target") or v.get("destination")
                if isinstance(src, str) and "docker.sock" in src:
                    findings.append((name, json.dumps(v)))
                elif isinstance(target, str) and "docker.sock" in target:
                    findings.append((name, json.dumps(v)))
    return findings


def detect_images_latest_and_no_digest(compose: Dict[str, Any]) -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]]]:
    latest: List[Tuple[str, str]] = []
    no_digest: List[Tuple[str, str]] = []
    for name, svc in (compose.get("services") or {}).items():
        image = svc.get("image")
        if not image:
            continue
        if "@sha256:" not in image:
            no_digest.append((name, str(image)))
        if isinstance(image, str) and image.endswith(":latest"):
            latest.append((name, image))
    return latest, no_digest


def detect_privileged(compose: Dict[str, Any]) -> List[Tuple[str, Any]]:
    findings: List[Tuple[str, Any]] = []
    for name, svc in (compose.get("services") or {}).items():
        if svc.get("privileged") is True:
            findings.append((name, True))
    return findings


def detect_mounts_rw_sensitive(compose: Dict[str, Any]) -> List[Tuple[str, str]]:
    findings: List[Tuple[str, str]] = []
    sensitive_paths = ("/etc/passwd", "/etc/shadow", "/var/run/docker.sock", "/root", "/var/lib/docker")
    for name, svc in (compose.get("services") or {}).items():
        vols = svc.get("volumes") or []
        for v in vols:
            if isinstance(v, str):
                parts = v.split(":")
                if len(parts) >= 2:
                    host = parts[0]
                    mode = parts[-1] if parts[-1] in ("ro", "rw") else None
                    for s in sensitive_paths:
                        if host == s or host.startswith(s + "/"):
                            if mode != "ro":
                                findings.append((name, v))
            elif isinstance(v, dict):
                src = v.get("source")
                read_only = v.get("read_only") or v.get("ro")
                for s in sensitive_paths:
                    if isinstance(src, str) and (src == s or src.startswith(s + "/")):
                        if not read_only:
                            findings.append((name, json.dumps(v)))
    return findings


def detect_cap_add(compose: Dict[str, Any]) -> List[Tuple[str, Any]]:
    findings: List[Tuple[str, Any]] = []
    for name, svc in (compose.get("services") or {}).items():
        caps = svc.get("cap_add") or svc.get("capabilities")
        if caps:
            findings.append((name, caps))
    return findings


def detect_read_only_false(compose: Dict[str, Any]) -> List[str]:
    findings: List[str] = []
    for name, svc in (compose.get("services") or {}).items():
        if svc.get("read_only") is False:
            findings.append(name)
    return findings


POLICY_SEVERITY = {
    "privileged": "FAIL",
    "docker_sock": "WARN",
    "ports": "WARN",
    "sensitive_mounts": "WARN",
    "images_no_digest": "WARN",
    "images_latest": "WARN",
    "cap_add": "WARN",
    "read_only_false": "WARN",
}


def run_all_checks(selected: List[str] | None = None) -> Dict[str, Any]:
    compose = get_compose_dict()
    out: Dict[str, Any] = {}

    # runtime-status
    out["runtime_checks"] = check_docker_runtime()

    if selected is None or "ports" in selected:
        ports = detect_published_ports(compose)
        out["ports"] = ports

    if selected is None or "docker_sock" in selected:
        ds = detect_docker_sock(compose)
        out["docker_sock"] = ds

    if selected is None or "images" in selected:
        latest, no_digest = detect_images_latest_and_no_digest(compose)
        out["images_latest"] = latest
        out["images_no_digest"] = no_digest

    if selected is None or "privileged" in selected:
        out["privileged"] = detect_privileged(compose)

    if selected is None or "sensitive_mounts" in selected:
        out["sensitive_mounts"] = detect_mounts_rw_sensitive(compose)

    if selected is None or "cap_add" in selected:
        out["cap_add"] = detect_cap_add(compose)

    if selected is None or "read_only_false" in selected:
        out["read_only_false"] = detect_read_only_false(compose)

    return out


def pretty_print(results: Dict[str, Any]):
    # Ports
    if not results.get("ports"):
        ok("No hay puertos publicados en compose (estructura detectada)")
    else:
        warn("Servicios con puertos publicados (structured):")
        for svc, p in results.get("ports", []):
            print(f"  - {svc}: {p}")

    # docker.sock
    if not results.get("docker_sock"):
        ok("docker.sock no usado (estructura detectada)")
    else:
        warn("docker.sock montado en contenedor (structured):")
        for svc, v in results.get("docker_sock", []):
            print(f"  - {svc}: {v}")

    # images
    if results.get("images_latest"):
        warn("Imágenes con tag :latest detectadas:")
        for svc, img in results.get("images_latest", []):
            print(f"  - {svc}: {img}")
    else:
        ok("No se detectaron imágenes con tag :latest (estructura detectada)")

    if results.get("images_no_digest"):
        warn("Imágenes sin digest (recomendado fijar digest):")
        for svc, img in results.get("images_no_digest", []):
            print(f"  - {svc}: {img}")
    else:
        ok("Todas las imágenes contienen digest o no se detectaron imágenes")

    # privileged
    if results.get("privileged"):
        fail("Servicios con privileged=true detectados:")
        for svc, _ in results.get("privileged", []):
            print(f"  - {svc}")
    else:
        ok("No se detectó privileged=true en servicios")

    # sensitive mounts
    if results.get("sensitive_mounts"):
        warn("Mounts sensibles en modo RW detectados:")
        for svc, v in results.get("sensitive_mounts", []):
            print(f"  - {svc}: {v}")
    else:
        ok("No se detectaron mounts sensibles en modo RW")

    # cap_add
    if results.get("cap_add"):
        warn("Servicios con cap_add/capabilities:")
        for svc, c in results.get("cap_add", []):
            print(f"  - {svc}: {c}")
    else:
        ok("No se detectaron cap_add/capabilities")

    # read_only false
    if results.get("read_only_false"):
        warn("Servicios con read_only=false detectados:")
        for svc in results.get("read_only_false", []):
            print(f"  - {svc}")
    else:
        ok("No se detectaron servicios con read_only=false")

    # runtime checks
    rt = results.get("runtime_checks") or {}
    if rt:
        print("")
        print("[INFO] Runtime checks:")
        if rt.get("docker_cli"):
            ok("docker CLI disponible")
        else:
            warn("docker CLI no disponible")
        if rt.get("docker_compose"):
            ok("docker compose disponible")
        else:
            warn("docker compose no disponible")
        if rt.get("compose_config"):
            ok("docker compose config operativo")
        else:
            warn("docker compose config no operativo dentro del runtime")
        if rt.get("docker_sock"):
            ok("Acceso a docker.sock operativo")
        else:
            warn("Acceso a docker.sock NO operativo (el contenedor puede no tener acceso al control plane)")


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compose structured policy checks")
    parser.add_argument("--json", dest="json", action="store_true", help="Emitir salida JSON machine-readable")
    parser.add_argument("--check", dest="check", action="append", help="Ejecutar solo comprobaciónes específicas (ports,docker_sock,images,privileged,sensitive_mounts,cap_add,read_only_false)")
    parser.add_argument("--self-test", dest="self_test", action="store_true", help="Ejecutar autotest runtime (docker CLI/compose/compose config/docker.sock)")
    args = parser.parse_args(argv)

    results = run_all_checks(args.check)

    if args.self_test:
        rt = results.get("runtime_checks") or {}
        # Emit JSON if requested
        if args.json:
            print(json.dumps({"runtime_checks": rt}, indent=2, ensure_ascii=False))
            # rc: fail if docker_cli missing
            return 1 if not rt.get("docker_cli") else 0
        # Human readable
        if rt.get("docker_cli"):
            ok("docker CLI disponible")
        else:
            fail("docker CLI no disponible")
        if rt.get("docker_compose"):
            ok("docker compose disponible")
        else:
            warn("docker compose no disponible")
        if rt.get("compose_config"):
            ok("docker compose config operativo")
        else:
            warn("docker compose config no operativo dentro del runtime")
        if rt.get("docker_sock"):
            ok("Acceso a docker.sock operativo")
        else:
            warn("Acceso a docker.sock NO operativo (el contenedor puede no tener acceso al control plane)")
        return 0 if rt.get("docker_cli") else 1

    # Normalize for JSON: tuples -> lists
    serializable = {}
    for k, v in results.items():
        if isinstance(v, list):
            serializable[k] = [list(x) if isinstance(x, tuple) else x for x in v]
        else:
            serializable[k] = v

    # Determine exit code based on policy severity
    rc = 0
    for policy, severity in POLICY_SEVERITY.items():
        items = results.get(policy)
        if items:
            if severity == "FAIL":
                rc = 1

    if args.json:
        print(json.dumps(serializable, indent=2, ensure_ascii=False))
        return rc

    pretty_print(results)
    return rc


if __name__ == "__main__":
    rc = main()
    sys.exit(rc)
