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

import yaml


ALLOWLIST = {
    # service_name: exceptions
    "monitoring-smtp-relay": {
        "allow_root": True,
        "allowed_caps": [],
    },
    "monitoring-postgres": {
        "allow_readonly_false": True,
    },
    "promtail": {
        "allowed_ro_mounts": ["/var/log", "/var/lib/docker/containers"],
    },
}


def run(cmd):
    p = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return p.returncode, p.stdout, p.stderr


def discover_compose_files():
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


def load_compose_inventory(files):
    inventory = {}
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


def list_containers():
    rc, out, err = run("docker ps -q")
    if rc != 0:
        print("[ERROR] docker ps failed:", err, file=sys.stderr)
        return []
    ids = [l.strip() for l in out.splitlines() if l.strip()]
    return ids


def inspect_container(cid):
    rc, out, err = run(f"docker inspect {cid}")
    if rc != 0:
        return None
    try:
        data = json.loads(out)[0]
        return data
    except Exception:
        return None


def correlate(inspect_obj, compose_inventory):
    labels = inspect_obj.get("Config", {}).get("Labels") or {}
    svc = labels.get("com.docker.compose.service")
    if svc and svc in compose_inventory:
        return svc
    name = inspect_obj.get("Name", "").lstrip("/")
    # best-effort: find service whose name appears in container name
    for s in compose_inventory:
        if s in name:
            return s
    return None


def analyze_container(inspect_obj, compose_inventory):
    findings = []
    hostcfg = inspect_obj.get("HostConfig", {})
    cfg = inspect_obj.get("Config", {})
    mounts = inspect_obj.get("Mounts", [])
    state = inspect_obj.get("State", {})
    name = inspect_obj.get("Name", "").lstrip("/")
    service = correlate(inspect_obj, compose_inventory)

    allow = ALLOWLIST.get(service, {}) if service else {}

    # privileged
    if hostcfg.get("Privileged"):
        if allow.get("allow_privileged"):
            findings.append(("privileged", "approved_exception", "Privileged but allowed by exception"))
        else:
            findings.append(("privileged", "forbidden", "Container runs privileged=True"))

    # network_mode host
    if hostcfg.get("NetworkMode") == "host":
        findings.append(("network_mode_host", "forbidden", "Container uses host network"))

    # docker.sock mounts
    for m in mounts:
        src = m.get("Source") or ""
        if "docker.sock" in src:
            findings.append(("docker_sock", "forbidden", f"Mounts docker.sock: {src}"))

    # RW host mounts
    for m in mounts:
        src = m.get("Source") or ""
        rw = m.get("RW", True)
        if src and src.startswith("/") and rw:
            # check allowlist exceptions for promtail
            allowed_ro = allow.get("allowed_ro_mounts", [])
            if src in allowed_ro:
                findings.append(("host_mount_rw", "approved_exception", f"RW host mount allowed by exception: {src}"))
            else:
                findings.append(("host_mount_rw", "forbidden", f"Host bind mount RW: {src}"))

    # readonly mounts (informational)
    for m in mounts:
        src = m.get("Source") or ""
        rw = m.get("RW", True)
        if src and src.startswith("/") and not rw:
            findings.append(("host_mount_ro", "compliant", f"Host bind mount RO: {src}"))

    # user
    user = cfg.get("User") or ""
    if not user:
        # empty => root
        if allow.get("allow_root"):
            findings.append(("user_root", "approved_exception", "Container runs as root but allowed by exception"))
        else:
            findings.append(("user_root", "forbidden", "Container runs as root user"))

    # capabilities
    cap_add = hostcfg.get("CapAdd") or []
    cap_drop = hostcfg.get("CapDrop") or []
    if "ALL" not in (cap_drop or []):
        findings.append(("cap_drop_missing_all", "warning", "CapDrop does not include ALL (recommended)"))
    if cap_add:
        allowed = allow.get("allowed_caps", [])
        for c in cap_add:
            if c not in allowed:
                findings.append(("cap_add", "forbidden", f"Unexpected capability added: {c}"))
            else:
                findings.append(("cap_add", "approved_exception", f"Capability allowed: {c}"))

    # no-new-privileges
    secopts = hostcfg.get("SecurityOpt") or []
    if not any("no-new-privileges" in s for s in secopts):
        findings.append(("no_new_privileges", "warning", "no-new-privileges not present in SecurityOpt"))

    # readonly rootfs
    if hostcfg.get("ReadonlyRootfs"):
        findings.append(("readonly_rootfs", "compliant", "ReadonlyRootfs enabled"))
    else:
        findings.append(("readonly_rootfs", "warning", "ReadonlyRootfs not enabled"))

    # healthcheck
    if cfg.get("Healthcheck") or state.get("Health"):
        findings.append(("healthcheck", "compliant", "Healthcheck present or state contains health info"))
    else:
        findings.append(("healthcheck", "warning", "No healthcheck defined or reported"))

    # restart policy
    rp = hostcfg.get("RestartPolicy", {}).get("Name")
    if not rp or rp == "no":
        findings.append(("restart_policy", "warning", f"Restart policy missing or none: {rp}"))
    else:
        findings.append(("restart_policy", "compliant", f"Restart policy: {rp}"))

    # exposed ports (runtime vs compose)
    # ports in Networks/Ports can be checked by State/HostConfig -- but we surface published ports in NetworkSettings
    ports = inspect_obj.get("NetworkSettings", {}).get("Ports") or {}
    published = []
    for k, v in ports.items():
        if v:
            for entry in v:
                published.append(entry.get("HostPort"))
    if published:
        findings.append(("published_ports", "warning", f"Published host ports: {published}"))

    return {
        "name": name,
        "service": service,
        "id": inspect_obj.get("Id"),
        "image": inspect_obj.get("Config", {}).get("Image"),
        "findings": [
            {"check": f[0], "status": f[1], "message": f[2]} for f in findings
        ],
    }


def generate_report(compose_inv, runtime_items, out_json, out_md, ci_mode=False):
    data = {
        "compose_inventory": compose_inv,
        "runtime_inventory": runtime_items,
    }
    os.makedirs(os.path.dirname(out_json), exist_ok=True)
    with open(out_json, "w") as fh:
        json.dump(data, fh, indent=2)

    # markdown summary
    lines = ["# Runtime Governance Audit", ""]
    total_forbidden = 0
    for r in runtime_items:
        lines.append(f"## {r['name']} ({r.get('service')})")
        for f in r["findings"]:
            status = f["status"]
            msg = f["message"]
            lines.append(f"- **{status.upper()}**: {f['check']} — {msg}")
            if status == "forbidden":
                total_forbidden += 1
        lines.append("")

    lines.append(f"\n\nSummary: total containers: {len(runtime_items)}, forbidden findings: {total_forbidden}")
    with open(out_md, "w") as fh:
        fh.write("\n".join(lines))

    if ci_mode and total_forbidden > 0:
        print(f"[CI] Forbidden findings detected: {total_forbidden}")
        return 2
    if total_forbidden > 0:
        print(f"Forbidden findings: {total_forbidden}")
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
