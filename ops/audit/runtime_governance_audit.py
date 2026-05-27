#!/usr/bin/env python3
"""
Runtime Governance Audit

Discover compose files under ops/stacks and ops/services, inspect running
containers via `docker inspect` and correlate both inventories.

Outputs machine-readable JSON and a short Markdown summary.

Designed to run host-side (requires Docker CLI and access to docker inspect).
"""
import argparse
import glob
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml


ALLOWLIST = {
    # service_name: exceptions
    "monitoring-smtp-relay": {
        "allow_root": True,
        # Docker returns capabilities in uppercase names
        "allowed_caps": ["NET_BIND_SERVICE", "NET_RAW", "SETUID", "SETGID"],
    },
    "monitoring-postgres": {
        "allow_readonly_false": True,
    },
    "promtail": {
        # promtail may mount host log dirs RO
        "allowed_ro_mounts": ["/var/log", "/var/lib/docker/containers"],
    },
}

# Services expected to meet a stronger baseline hardening
BASELINE_HARDENING_EXPECTED = {
    # service: describes baseline expectations; strict_enforcement must be explicit
    "grafana": {"cap_drop_all": True, "strict_enforcement": False},
    "loki": {"cap_drop_all": True, "strict_enforcement": False},
    "promtail": {"cap_drop_all": True, "strict_enforcement": False},
    "monitoring-cron": {"cap_drop_all": True, "strict_enforcement": False},
    "monitoring-python": {"cap_drop_all": True, "strict_enforcement": False},
}


def run(cmd: str) -> Tuple[int, str, str]:
    p = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return p.returncode, p.stdout, p.stderr


def discover_compose_files() -> List[str]:
    patterns = [
        "ops/stacks/**/compose.yml",
        "ops/stacks/**/compose.yaml",
        "ops/services/**/compose.yml",
        "ops/services/**/compose.yaml",
    ]
    files = []
    for p in patterns:
        files.extend(glob.glob(p, recursive=True))
    files = sorted(set(files))
    return files


def load_compose_inventory(files: List[str]) -> Dict[str, Any]:
    inventory: Dict[str, Any] = {}
    for f in files:
        try:
            with open(f, "r") as fh:
                doc = yaml.safe_load(fh) or {}
        except Exception as e:
            print(f"[WARN] Failed to parse {f}: {e}")
            continue
        services = doc.get("services") or {}
        for name, cfg in services.items():
            key = name
            inventory[key] = inventory.get(key, {})
            inventory[key].setdefault("declared_in", []).append(f)
            inventory[key]["compose_decl"] = cfg
    return inventory


def list_containers() -> List[str]:
    rc, out, err = run("docker ps -q")
    if rc != 0:
        print("[ERROR] docker ps failed:", err, file=sys.stderr)
        return []
    ids = [l.strip() for l in out.splitlines() if l.strip()]
    return ids


def inspect_container(cid: str) -> Optional[Dict[str, Any]]:
    rc, out, err = run(f"docker inspect {cid}")
    if rc != 0:
        return None
    try:
        data = json.loads(out)[0]
        return data
    except Exception:
        return None


def correlate(inspect_obj: Dict[str, Any], compose_inventory: Dict[str, Any]) -> Optional[str]:
    """Correlate container to compose service.

    Priority:
    1) Use `com.docker.compose.service` label when present and known in compose inventory.
    2) Otherwise treat as unmanaged (do NOT use substring heuristics).
    """
    labels = inspect_obj.get("Config", {}).get("Labels") or {}
    svc = labels.get("com.docker.compose.service")
    if svc and svc in compose_inventory:
        return svc
    return None


def analyze_container(inspect_obj: Dict[str, Any], compose_inventory: Dict[str, Any]) -> Dict[str, Any]:
    findings: List[Dict[str, Any]] = []
    hostcfg = inspect_obj.get("HostConfig", {})
    cfg = inspect_obj.get("Config", {})
    mounts = inspect_obj.get("Mounts", [])
    state = inspect_obj.get("State", {})
    name = inspect_obj.get("Name", "").lstrip("/")
    service = correlate(inspect_obj, compose_inventory)

    allow = ALLOWLIST.get(service, {}) if service else {}

    def add_finding(check: str, status: str, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        entry: Dict[str, Any] = {"check": check, "status": status, "message": message}
        if details:
            entry["details"] = details
        findings.append(entry)

    # privileged
    if hostcfg.get("Privileged"):
        if allow.get("allow_privileged"):
            add_finding("privileged", "approved_exception", "Privileged but allowed by exception")
        else:
            add_finding("privileged", "forbidden", "Container runs privileged=True")

    # network_mode host
    if hostcfg.get("NetworkMode") == "host":
        add_finding("network_mode_host", "forbidden", "Container uses host network")

    # docker.sock mounts
    for m in mounts:
        src = m.get("Source") or ""
        if "docker.sock" in src:
            add_finding("docker_sock", "forbidden", f"Mounts docker.sock: {src}", {"mount_type": "socket", "source": src, "destination": m.get("Destination")})

    # correlate: if no compose service label, mark unmanaged (informational)
    if not service:
        add_finding("compose_correlation", "info", "Container not managed by compose labels (advisory)")

    # mounts classification: bind, volume, tmpfs, anonymous
    for m in mounts:
        mtype = m.get("Type") or ""
        src = m.get("Source") or ""
        # normalize source path to reduce path-comparison false negatives
        try:
            src_norm = os.path.normpath(src) if src else ""
        except Exception:
            src_norm = src
        dst = m.get("Destination") or m.get("Target") or ""
        # prefer explicit RW flag; default to False when missing to avoid false forbidden
        rw = m.get("RW") if ("RW" in m) else False
        # include detailed mount info in findings
        if mtype == "bind":
            # classify path risk
            HIGH_RISK_PREFIXES = ["/var/run", "/run", "/proc", "/sys", "/root", "/etc/ssh", "/var/lib/docker", "/var/lib/kubelet"]
            LOW_RISK_EXACT = ["/etc/localtime", "/etc/timezone"]
            LOW_RISK_PREFIXES = ["/etc/ssl", "/etc/pki", "/usr/share/zoneinfo"]
            is_high = any(src_norm == p or src_norm.startswith(p + "/") for p in HIGH_RISK_PREFIXES)
            is_low = src_norm in LOW_RISK_EXACT or any(src_norm == p or src_norm.startswith(p + "/") for p in LOW_RISK_PREFIXES)
            # RW bind mounts: forbidden only for high-risk paths or docker.sock; otherwise warning
            if rw:
                if is_high or "docker.sock" in src_norm:
                    add_finding("bind_rw", "forbidden", "Bind mount RW to high-risk host path", {"mount_type": "bind", "source": src_norm, "destination": dst, "readonly": False})
                else:
                    add_finding("bind_rw", "warning", "Bind mount RW to host path (review)", {"mount_type": "bind", "source": src_norm, "destination": dst, "readonly": False})
            else:
                # RO bind mounts: approved if low-risk or allowed by service exceptions, otherwise advisory
                allowed_ro = allow.get("allowed_ro_mounts", [])
                if any(src_norm == a or src_norm.startswith(a) for a in allowed_ro) or is_low:
                    add_finding("bind_ro", "approved_exception", "Bind mount RO allowed by exception/low-risk path", {"mount_type": "bind", "source": src_norm, "destination": dst, "readonly": True})
                else:
                    add_finding("bind_ro", "info", "Bind mount RO present (needs review)", {"mount_type": "bind", "source": src_norm, "destination": dst, "readonly": True})
        elif mtype == "volume":
            # named or anonymous volumes appear as type 'volume' in inspect
            vol_name = m.get("Name")
            if vol_name:
                add_finding("named_volume", "compliant", f"named_volume:{vol_name}", {"mount_type": "volume", "name": vol_name, "destination": dst, "readonly": (not rw)})
            else:
                add_finding("anonymous_volume", "compliant", f"anonymous_volume", {"mount_type": "anonymous", "destination": dst, "readonly": (not rw)})
        elif mtype == "tmpfs":
            add_finding("tmpfs", "compliant", f"tmpfs", {"mount_type": "tmpfs", "destination": dst})
        else:
            add_finding("mount_unknown", "warning", f"unknown_mount_type:{mtype}", {"mount_type": mtype, "source": src_norm, "destination": dst, "readonly": (not rw)})

    # user
    user = cfg.get("User") or ""
    if not user:
        # empty => root
        if allow.get("allow_root"):
            add_finding("user_root", "approved_exception", "Container runs as root but allowed by exception")
        else:
            add_finding("user_root", "warning", "Container runs as root user (review)")

    # capabilities
    # NOTE/TODO:
    # - Docker's HostConfig.CapAdd/CapDrop reflect declared configuration but not
    #   necessarily the process-effective capability set inside the container.
    # - Determining effective capabilities requires runtime inspection inside
    #   the container (e.g., /proc, capsh) which is out-of-scope for host-side
    #   tooling in this phase. Future iterations should add an optional runtime
    #   capability probe that executes inside the container when permitted.
    # - For now we report CapAdd/CapDrop/SecurityOpt as evidence and apply
    #   policy based on declared HostConfig only.
    cap_add = hostcfg.get("CapAdd") or []
    # Report CapDrop and SecurityOpt explicitly
    cap_drop = hostcfg.get("CapDrop") or []
    if cap_drop:
        add_finding("cap_drop", "info", f"CapDrop declared: {cap_drop}", {"cap_drop": cap_drop})
    secopts = hostcfg.get("SecurityOpt") or []
    if secopts:
        add_finding("security_opt", "info", f"SecurityOpt declared: {secopts}", {"security_opt": secopts})

    # cap_drop missing -> WARNING by default; escalate only when strict_enforcement true
    severity = "warning"
    if service and service in BASELINE_HARDENING_EXPECTED and BASELINE_HARDENING_EXPECTED[service].get("strict_enforcement"):
        severity = "forbidden"
    if "ALL" not in (cap_drop or []):
        add_finding("cap_drop_missing_all", severity, "CapDrop does not include ALL (recommended)")

    if cap_add:
        allowed = allow.get("allowed_caps", [])
        for c in cap_add:
            if c not in allowed:
                # report as warning (declared capability) — do not assert effective capability
                add_finding("cap_add", "warning", f"Capability declared in HostConfig: {c}", {"capability": c})
            else:
                add_finding("cap_add", "approved_exception", f"Capability allowed by exception: {c}", {"capability": c})

    # no-new-privileges
    secopts = hostcfg.get("SecurityOpt") or []
    if not any("no-new-privileges" in s for s in secopts):
        add_finding("no_new_privileges", "warning", "no-new-privileges not present in SecurityOpt")

    # readonly rootfs
    if hostcfg.get("ReadonlyRootfs"):
        add_finding("readonly_rootfs", "compliant", "ReadonlyRootfs enabled")
    else:
        add_finding("readonly_rootfs", "info", "ReadonlyRootfs not enabled (operational)")

    # healthcheck
    if cfg.get("Healthcheck") or state.get("Health"):
        add_finding("healthcheck", "compliant", "Healthcheck present or state contains health info")
    else:
        add_finding("healthcheck", "warning", "No healthcheck defined or reported")

    # restart policy
    rp = hostcfg.get("RestartPolicy", {}).get("Name")
    if not rp or rp == "no":
        add_finding("restart_policy", "warning", f"Restart policy missing or none: {rp}")
    else:
        add_finding("restart_policy", "compliant", f"Restart policy: {rp}")

    # exposed ports (runtime vs compose)
    # ports in Networks/Ports can be checked by State/HostConfig -- but we surface published ports in NetworkSettings
    ports = inspect_obj.get("NetworkSettings", {}).get("Ports") or {}
    published = []
    for k, v in ports.items():
        if v:
            for entry in v:
                published.append(entry.get("HostPort"))
    if published:
        add_finding("published_ports", "info", f"Published host ports: {published}", {"published_ports": published})

    return {
        "name": name,
        "service": service,
        "id": inspect_obj.get("Id"),
        "image": inspect_obj.get("Config", {}).get("Image"),
        "findings": findings,
    }


def generate_report(compose_inv: Dict[str, Any], runtime_items: List[Dict[str, Any]], out_json: str, out_md: str, ci_mode: bool = False) -> int:
    # enrich findings with stable IDs and collect summary
    findings_list = []
    counts = {"forbidden": 0, "warning": 0, "approved_exception": 0, "compliant": 0, "info": 0}
    for r in runtime_items:
        svc = r.get("service") or r.get("name")
        container_name = r.get("name")
        container_id = (r.get("id") or "")[:12]
        for idx, f in enumerate(r.get("findings", [])):
            # include container id/name in finding_id to avoid collisions when multiple containers share service name
            fid = f"{svc}:{container_name}:{container_id}:{f.get('check')}:{idx}"
            entry = {
                "finding_id": fid,
                "service": svc,
                "container": container_name,
                "container_id": container_id,
                "check": f.get("check"),
                "severity": f.get("status"),
                "message": f.get("message"),
                "details": f.get("details", {}),
            }
            findings_list.append(entry)
            sev = f.get("status")
            if sev in counts:
                counts[sev] += 1
            else:
                counts[sev] = counts.get(sev, 0) + 1


    data = {
        "compose_inventory": compose_inv,
        "runtime_inventory": runtime_items,
        "findings": findings_list,
        "summary": {
            "counts": counts,
            "total_containers": len(runtime_items),
        },
    }

    # sort findings for deterministic output between runs
    findings_list = sorted(findings_list, key=lambda x: x.get("finding_id"))
    data["findings"] = findings_list

    os.makedirs(os.path.dirname(out_json), exist_ok=True)
    with open(out_json, "w") as fh:
        json.dump(data, fh, indent=2, sort_keys=False)

    # markdown summary
    lines = ["# Runtime Governance Audit", ""]
    lines.append("")
    lines.append("## Summary by severity")
    for k, v in counts.items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("## Findings (high level)")
    for f in findings_list:
        lines.append(f"- [{f['severity'].upper()}] {f['finding_id']} — {f['service']} — {f['check']} — {f['message']}")

    with open(out_md, "w") as fh:
        fh.write("\n".join(lines))

    # CI behavior
    if ci_mode and counts.get("forbidden", 0) > 0:
        print(f"[CI] Forbidden findings detected: {counts.get('forbidden',0)}")
        return 2
    if counts.get("forbidden", 0) > 0:
        print(f"Forbidden findings: {counts.get('forbidden',0)}")
    else:
        print("No forbidden findings detected (summary written)")
    return 0


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output-json", default="artifacts/runtime_audit.json")
    p.add_argument("--output-md", default="artifacts/runtime_audit.md")
    p.add_argument("--ci", action="store_true", help="Exit non-zero on forbidden findings")
    args = p.parse_args()

    files = discover_compose_files()
    compose_inv = load_compose_inventory(files)

    cids = list_containers()
    runtime_items = []
    for cid in cids:
        obj = inspect_container(cid)
        if not obj:
            continue
        item = analyze_container(obj, compose_inv)
        runtime_items.append(item)

    rc = generate_report(compose_inv, runtime_items, args.output_json, args.output_md, ci_mode=args.ci)
    sys.exit(rc)


if __name__ == "__main__":
    main()
