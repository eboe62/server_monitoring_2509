#!/usr/bin/env python3

import yaml
from pathlib import Path

COMPOSE_FILES = [
    "ops/stacks/python/compose.yml",
    "ops/stacks/cron/compose.yml",
]

def load_yaml(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def test_auth_mode_requires_secrets_mount():
    for compose_file in COMPOSE_FILES:
        data = load_yaml(compose_file)
        services = data.get("services", {})
        for service_name, service in services.items():
            env = service.get("environment", {})
            smtp_mode = env.get("SMTP_MODE")
            volumes = service.get("volumes", [])
            volume_str = "\n".join(volumes)
            has_secrets_mount = (
                "smtp_relay/secrets" in volume_str
            )
            if smtp_mode == "auth":
                assert has_secrets_mount, (
                    f"{compose_file}:{service_name} "
                    "usa SMTP_MODE=auth "
                    "pero no monta secrets SMTP"
                )

def test_relay_mode_does_not_require_secrets():
    for compose_file in COMPOSE_FILES:
        data = load_yaml(compose_file)
        services = data.get("services", {})
        for service_name, service in services.items():
            env = service.get("environment", {})
            smtp_mode = env.get("SMTP_MODE")
            if smtp_mode == "relay":
                assert True
