#!/usr/bin/env python3
"""Comprobaciones de políticas estructuradas de Compose para auditoría.

Modelo de ejecución (host-side):

- Este módulo está diseñado para ser ejecutado desde el HOST (por ejemplo:
    `python3 -m ops.audit.compose_policy_checks`). Realiza comprobaciones
    deterministas y legibles por máquina sobre la configuración de Compose y
    (opcionalmente) sobre el conjunto de herramientas de Docker del host cuando está disponible.
- El módulo NO asume que se ejecuta dentro de `monitoring-python` ni que los
    contenedores proporcionan Docker/compose/docker.sock. Cualquier comprobación de
    Docker/compose se interpreta como una comprobación del lado del host.
- Cuando `docker compose config` está disponible en el host, es la fuente
    autorizada preferida. Cuando no está disponible, el módulo recurre a una
    fusión de mejor esfuerzo (best-effort) de los archivos YAML de Compose bajo `ops/`.
    Este modo de respaldo es un comportamiento operativo esperado y emitirá mensajes
    de advertencia (WARN) cuando se utilice.

Soporta `--json` para salida legible por máquina, `--self-test` para validar
la disponibilidad de las herramientas en el host y `--check` para ejecutar un subconjunto de comprobaciones.
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
    print("[WARN] PyYAML no disponible en el host; algunas comprobaciones pueden fallar", file=sys.stderr)
    yaml = None


def ok(msg: str):
    print(f"[OK] {msg}", file=sys.stderr)


def warn(msg: str):
    print(f"[WARN] {msg}", file=sys.stderr)


def fail(msg: str):
    print(f"[FAIL] {msg}", file=sys.stderr)


def load_compose_via_docker() -> Dict[str, Any] | None:
    try:
        # Ejecuta `docker compose config` en el host (cwd/resolved context).
        out = subprocess.check_output(["docker", "compose", "config"], stderr=subprocess.DEVNULL)
        if not yaml:
            return None
        return yaml.safe_load(out)
    except Exception:
        return None


def check_docker_runtime() -> Dict[str, bool]:
    """Verifica la disponibilidad de la CLI de docker y compose en el entorno del host.

    Nota: esta función realiza comprobaciones del lado del host. El módulo ya no
    asume que Docker/compose están disponibles dentro de ningún contenedor.
    """
    status = {
        "docker_cli": False,
        "docker_compose": False,
        "compose_config": False,
        "docker_host_access": False
    }
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
        # Valida la resolución en tiempo de ejecución de compose
        subprocess.check_output(
            ["docker", "compose", "config"],
            stderr=subprocess.DEVNULL,
            timeout=10,
        )
        status["compose_config"] = True
    except Exception:
        pass

    # Verifica la accesibilidad de docker.sock intentando listar los contenedores
    try:
        subprocess.check_output(["docker", "ps", "-q"], stderr=subprocess.DEVNULL, timeout=10)
        status["docker_host_access"] = True
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
    """
    Carga best-effort de archivos Compose desde el host.
    ADR-0029:
    - fallback exclusivamente estructural
    - sin dependencia docker.sock
    - sin dependencia runtime Docker
    """
    merged: Dict[str, Any] = {"services": {}}
    if not yaml:
        warn("PyYAML no disponible; imposible realizar parseo Compose fallback")
        return None
    for f in files:
        try:
            with open(f, "rb") as fh:
                data = yaml.safe_load(fh)
            if not data:
                continue
            services = data.get("services") or {}
            if not isinstance(services, dict):
                warn(f"{f}: bloque services inválido")
                continue
            merged["services"].update(services)
        except Exception as exc:
            warn(f"No se pudo parsear compose file {f}: {exc}")
    if not merged["services"]:
        warn("No se encontraron servicios Compose válidos en fallback estático")
        return None
    return merged

def get_compose_dict() -> Dict[str, Any]:
    """
    Obtiene configuración Compose consolidada.
    Prioridad:
    1. docker compose config (host-side)
    2. parseo estático fallback (ADR-0029)
    El fallback estático:
    - es comportamiento operativo esperado
    - no requiere docker.sock
    - no requiere Docker runtime operativo
    """
    d = load_compose_via_docker()
    if d:
        return d
    warn(
        "docker compose config no disponible; "
        "activando fallback estructural estático ADR-0029"
    )
    files = find_compose_files()
    if not files:
        warn("No se encontraron archivos Compose bajo ops/")
        return {"services": {}}
    loaded = load_compose_from_files(files)
    if loaded:
        warn(
            "Usando parseo estático de archivos Compose "
            "(fallback host-side sin docker.sock)"
        )
        return loaded
    warn("Fallback Compose no produjo servicios válidos")
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
    """
    Detecta imágenes:
    - con tag :latest
    - sin digest reproducible
    ADR-0018 / ADR-0029:
    - las imágenes internas buildadas localmente no requieren digest
    - el enforcement de digest aplica principalmente a imágenes externas
    - se evita ruido operacional sobre imágenes `monitoring-*`
    """
    latest: List[Tuple[str, str]] = []
    no_digest: List[Tuple[str, str]] = []
    for name, svc in (compose.get("services") or {}).items():
        image = svc.get("image")
        if not image:
            continue
        if not isinstance(image, str):
            continue
        # Imágenes internas/locales:
        # - monitoring-*
        # - nombres sin namespace/registry
        # Estas imágenes forman parte del build local controlado
        # y no requieren digest OCI explícito.
        is_internal_image = (
            image.startswith("monitoring-")
            or "/" not in image
        )
        if "@sha256:" not in image and not is_internal_image:
            no_digest.append((name, image))
        if image.endswith(":latest"):
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


def detect_runtime_hostconfig(compose: Dict[str, Any]) -> List[Tuple[str, str, Dict[str, Any]]]:
    """
    When docker CLI and host access are available, inspect running containers
    corresponding to compose services and collect HostConfig/security fields.

    Returns list of tuples: (service_name, container_name, fields_dict)
    fields_dict contains keys: Privileged, CapAdd, CapDrop, SecurityOpt,
    ReadonlyRootfs, AppArmorProfile
    """
    findings: List[Tuple[str, str, Dict[str, Any]]] = []
    # Early exit when docker CLI unavailable
    try:
        subprocess.check_output(["docker", "--version"], stderr=subprocess.DEVNULL)
    except Exception:
        return findings

    for svc_name, svc in (compose.get("services") or {}).items():
        # Prefer explicit container_name when present
        c_name = svc.get("container_name") if isinstance(svc.get("container_name"), str) else None
        candidates = []
        if c_name:
            candidates.append(c_name)
        # also try service name as fallback
        candidates.append(svc_name)

        matched = None
        try:
            ps_out = subprocess.check_output(["docker", "ps", "--format", "{{.Names}}"], text=True)
            running = [x.strip() for x in ps_out.splitlines() if x.strip()]
        except Exception:
            running = []

        for cand in candidates:
            for r in running:
                # match exact or project-prefixed names (project_service)
                if r == cand or r.endswith("_" + cand):
                    matched = r
                    break
            if matched:
                break

        if not matched:
            # not running or not found
            findings.append((svc_name, "NOT_RUNNING", {}))
            continue

        # Inspect the matched container
        try:
            out = subprocess.check_output(["docker", "inspect", matched], text=True)
            data = json.loads(out)[0]
            hostcfg = data.get("HostConfig") or {}
            secopt = hostcfg.get("SecurityOpt") or []
            fields = {
                "Privileged": bool(hostcfg.get("Privileged")),
                "CapAdd": hostcfg.get("CapAdd") or [],
                "CapDrop": hostcfg.get("CapDrop") or [],
                "SecurityOpt": secopt,
                "ReadonlyRootfs": bool(hostcfg.get("ReadonlyRootfs")),
                "Tmpfs": hostcfg.get("Tmpfs") or {},
                "Devices": hostcfg.get("Devices") or [],
                "AppArmorProfile": data.get("AppArmorProfile") or "",
            }
            # Detect no-new-privileges in SecurityOpt entries if present
            nnpr = any(str(s).startswith("no-new-privileges") for s in secopt)
            fields["NoNewPrivileges"] = nnpr
            findings.append((svc_name, matched, fields))
        except Exception:
            findings.append((svc_name, matched, {"error": "inspect_failed"}))

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

    # Estado del entorno de ejecución (runtime-status)
    out["runtime_checks"] = check_docker_runtime()

    # Runtime HostConfig inspections (host-side only)
    try:
        if out["runtime_checks"].get("docker_host_access"):
            out["runtime_hostconfig"] = detect_runtime_hostconfig(compose)
        else:
            out["runtime_hostconfig"] = []
    except Exception:
        out["runtime_hostconfig"] = []

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
    # Puertos
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

    # Imágenes
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

    # Capacidades (cap_add)
    if results.get("cap_add"):
        warn("Servicios con cap_add/capabilities:")
        for svc, c in results.get("cap_add", []):
            print(f"  - {svc}: {c}")
    else:
        ok("No se detectaron cap_add/capabilities")

    # Read_only false
    if results.get("read_only_false"):
        warn("Servicios con read_only=false detectados:")
        for svc in results.get("read_only_false", []):
            print(f"  - {svc}")
    else:
        ok("No se detectaron servicios con read_only=false")

    # Comprobaciones del entorno de ejecución (runtime checks)
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
        if rt.get("docker_host_access"):
            ok("Acceso a docker.sock operativo")
        else:
            warn("Acceso a docker.sock NO operativo (el contenedor puede no tener acceso al control plane)")

        # Runtime HostConfig summary (if available)
        rh = results.get("runtime_hostconfig") or []
        if rh:
            print("")
            print("[INFO] Runtime HostConfig (host-side inspect) — visibility only:")
            for svc, cname, fields in rh:
                print(f"  [INFO] {svc}")
                if not fields:
                    print(f"    container: {cname}")
                    print(f"    data: null or not available")
                    continue
                if isinstance(fields, dict) and fields.get("error"):
                    print(f"    container: {cname}")
                    print(f"    inspect: failed")
                    continue
                # Normalize nulls into user-friendly defaults
                capadd = fields.get("CapAdd") or []
                capdrop = fields.get("CapDrop") or []
                secopt = fields.get("SecurityOpt") or []
                ro = bool(fields.get("ReadonlyRootfs"))
                privileged = bool(fields.get("Privileged"))
                apparmor = fields.get("AppArmorProfile") or ""
                tmpfs = fields.get("Tmpfs") or {}
                devices = fields.get("Devices") or []
                nnpr = bool(fields.get("NoNewPrivileges"))

                print(f"    container: {cname}")
                print(f"    Privileged={str(privileged).lower()}")
                print(f"    CapAdd={capadd}")
                print(f"    CapDrop={capdrop}")
                print(f"    SecurityOpt={secopt}")
                print(f"    NoNewPrivileges={str(nnpr).lower()}")
                print(f"    ReadonlyRootfs={str(ro).lower()}")
                print(f"    AppArmor={apparmor}")
                print(f"    Tmpfs={tmpfs}")
                print(f"    Devices={devices}")


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

    # Normaliza para JSON: tuplas -> listas
    serializable = {}
    for k, v in results.items():
        if isinstance(v, list):
            serializable[k] = [list(x) if isinstance(x, tuple) else x for x in v]
        else:
            serializable[k] = v

    # Determina el código de salida basándose en la severidad de la política
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
