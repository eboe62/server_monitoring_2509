# Source of truth: runtime containers classification

This folder provides the single source of truth for container typology and healthcheck policy used by Makefile, CI and audit scripts.

- `runtime_containers.yml`: mapping of containers to `type`, `healthcheck_policy` and `enforcement_level`.
- `runtime_containers.sh`: lightweight parser (no external deps) to query the YAML.

Usage examples:

List containers:

```sh
ops/runtime_containers.sh list
```

Show metadata for a container:

```sh
ops/runtime_containers.sh get monitoring-python
```

List containers by type:

```sh
ops/runtime_containers.sh by-type SERVICE_RUNTIME
```

Policies:
- `enforcement_level`: `fail` (CI/fail), `warn` (CI warn), controls how validators should treat missing/inadequate healthchecks.
