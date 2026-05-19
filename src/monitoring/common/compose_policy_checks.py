#!/usr/bin/env python3
"""Checks for Docker Compose policies using structured parsing.

Designed to be imported or executed as a module:
  python3 -m monitoring.common.compose_policy_checks

It tries to use `docker compose config` when available, falling back to
reading compose files under `ops/`.
"""
from __future__ import annotations

import os
import sys
import subprocess
import yaml
from typing import Dict, Any, List, Tuple


def ok(msg: str):
    print(f"[ OK ] {msg}")


def warn(msg: str):
    print(f"[WARN] {msg}")


def fail(msg: str):
    print(f"[FAIL] {msg}")


def load_compose_via_docker() -> Dict[str, Any] | None:
    try:
        out = subprocess.check_output(["docker", "compose", "config"], stderr=subprocess.DEVNULL)
        return yaml.safe_load(out)
    except Exception:
        return None


def find_compose_files() -> List[str]:
    files = []
    for root, _, filenames in os.walk("ops"):
        for fn in filenames:
            if fn.startswith("compose") and fn.endswith(('.yml', '.yaml')):
                files.append(os.path.join(root, fn))
    return files


def load_compose_from_files(files: List[str]) -> Dict[str, Any] | None:
    merged: Dict[str, Any] = {"services": {}}
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
    # Prefer runtime-resolved compose
    d = load_compose_via_docker()
    if d:
        return d

    files = find_compose_files()
    if files:
        loaded = load_compose_from_files(files)
        if loaded:
            return loaded

    return {"services": {}}


def _service_ports(svc: Dict[str, Any]) -> List[str]:
    ports = svc.get("ports") or []
    # ports can be dicts in long syntax
    out = []
    for p in ports:
        if isinstance(p, str):
            out.append(p)
        elif isinstance(p, dict):
            target = p.get("target")
            published = p.get("published")
            mode = p.get("mode")
            out.append(f"{published}:{target}" if published and target else str(p))
    return out


def detect_published_ports(compose: Dict[str, Any]) -> List[Tuple[str, str]]:
    findings = []
    for name, svc in (compose.get("services") or {}).items():
        for p in _service_ports(svc):
            findings.append((name, p))
    return findings


def detect_docker_sock(compose: Dict[str, Any]) -> List[Tuple[str, str]]:
    findings = []
    for name, svc in (compose.get("services") or {}).items():
        vols = svc.get("volumes") or []
        for v in vols:
            # v can be string 'host:container:ro' or dict
            if isinstance(v, str) and "docker.sock" in v:
                findings.append((name, v))
            elif isinstance(v, dict):
                src = v.get("source") or v.get("type")
                if isinstance(src, str) and "docker.sock" in src:
                    findings.append((name, str(v)))
    return findings


def detect_images_latest_and_no_digest(compose: Dict[str, Any]) -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]]]:
    latest = []
    no_digest = []
    for name, svc in (compose.get("services") or {}).items():
        image = svc.get("image")
        if not image:
            continue
        if "@sha256:" not in image:
            no_digest.append((name, image))
        # explicit :latest
        if image.endswith(":latest") or image.endswith(":latest\n"):
            latest.append((name, image))
    return latest, no_digest


def detect_privileged(compose: Dict[str, Any]) -> List[Tuple[str, Any]]:
    findings = []
    for name, svc in (compose.get("services") or {}).items():
        if svc.get("privileged") is True:
            findings.append((name, True))
    return findings


def detect_mounts_rw_sensitive(compose: Dict[str, Any]) -> List[Tuple[str, str]]:
    findings = []
    sensitive_paths = ("/etc/passwd", "/etc/shadow", "/var/run/docker.sock", "/root", "/var/lib/docker")
    for name, svc in (compose.get("services") or {}).items():
        vols = svc.get("volumes") or []
        for v in vols:
            if isinstance(v, str):
                # host:container(:ro)?
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
                            findings.append((name, str(v)))
    return findings


def detect_cap_add(compose: Dict[str, Any]) -> List[Tuple[str, Any]]:
    findings = []
    for name, svc in (compose.get("services") or {}).items():
        caps = svc.get("cap_add") or svc.get("capabilities")
        if caps:
            findings.append((name, caps))
    return findings


def detect_read_only_false(compose: Dict[str, Any]) -> List[str]:
    findings = []
    for name, svc in (compose.get("services") or {}).items():
        if svc.get("read_only") is False:
            findings.append(name)
    return findings


def run_all_checks() -> int:
    compose = get_compose_dict()

    had_fail = False

    # Ports
    ports = detect_published_ports(compose)
    if not ports:
        ok("No hay puertos publicados en compose (estructura detectada)")
    else:
        warn("Servicios con puertos publicados (structured):")
        for svc, p in ports:
            print(f"  - {svc}: {p}")

    # docker.sock
    ds = detect_docker_sock(compose)
    if not ds:
        ok("docker.sock no usado (estructura detectada)")
    else:
        warn("docker.sock montado en contenedor (structured):")
        for svc, v in ds:
            print(f"  - {svc}: {v}")

    # images
    latest, no_digest = detect_images_latest_and_no_digest(compose)
    if latest:
        warn("Imágenes con tag :latest detectadas:")
        for svc, img in latest:
            print(f"  - {svc}: {img}")
    else:
        ok("No se detectaron imágenes con tag :latest (estructura detectada)")

    if no_digest:
        warn("Imágenes sin digest (recomendado fijar digest):")
        for svc, img in no_digest:
            print(f"  - {svc}: {img}")
    else:
        ok("Todas las imágenes contienen digest o no se detectaron imágenes")

    # privileged
    priv = detect_privileged(compose)
    if priv:
        fail("Servicios con privileged=true detectados:")
        had_fail = True
        for svc, _ in priv:
            print(f"  - {svc}")
    else:
        ok("No se detectó privileged=true en servicios")

    # mounts rw sensitive
    sensitive = detect_mounts_rw_sensitive(compose)
    if sensitive:
        warn("Mounts sensibles en modo RW detectados:")
        for svc, v in sensitive:
            print(f"  - {svc}: {v}")
    else:
        ok("No se detectaron mounts sensibles en modo RW")

    # cap_add
    caps = detect_cap_add(compose)
    if caps:
        warn("Servicios con cap_add/capabilities:")
        for svc, c in caps:
            print(f"  - {svc}: {c}")
    else:
        ok("No se detectaron cap_add/capabilities")

    # read_only false
    ro_false = detect_read_only_false(compose)
    if ro_false:
        warn("Servicios con read_only=false detectados:")
        for svc in ro_false:
            print(f"  - {svc}")
    else:
        ok("No se detectaron servicios con read_only=false")

    return 1 if had_fail else 0


if __name__ == "__main__":
    rc = run_all_checks()
    sys.exit(rc)
