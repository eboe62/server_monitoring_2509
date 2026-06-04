# DevSecOps Principles

## Architecture Principles

* Infrastructure as Code first: The declarative Compose ecosystem is the single source of truth.
* Docker Compose standalone: No cluster-level orchestration dependencies or provider-specific locks.
* Single-node architecture: All design decisions must optimize local uptime, process lifecycle, and resource constraints.
* Progressive evolution: Architectural changes must be introduced incrementally via versioned ADRs.
* Operational simplicity: Maximize maintainability; eliminate unnecessary abstraction layers.

---

## Security Principles

* Least privilege: Containers must run with the minimum capabilities required for their specific typology.
* Defense in depth: Multiple layers of isolation (Network segmentation, non-root runtimes, volume constraints).
* Progressive hardening: Security adjustments must be rolling and verified against active service baselines.
* Runtime validation: Security postures must be audited programmatically from the host plane.
* Explicit trust boundaries: Absolute separation between Host Control-Plane (Plano 3) and container workloads.

---

## Container Principles & Typology Boundaries

Default Expectations:
* cap_drop: ALL (Dropping all kernel capabilities by default; additions require explicit ADR justification).
* no-new-privileges: true (Enforced universally to prevent runtime process escalation).
* non-root execution: Mandatory across SERVICE, SUPERVISOR, and TOOLBOX runtimes unless upstream compatibility prevents it.
* healthchecks enabled: Mandatory for SERVICE_RUNTIME; strictly forbidden on supervisor or toolbox runtimes to prevent false evictions.

Read-Only Filesystem Policy:
* read_only: true requires runtime evidence, explicit write-path mapping, and an active observability baseline before enforcement.

Resource Constraints Policy:
* Every service block must declare explicit CPU and memory limits (cpus, mem_limit) to prevent localized DoS or unmanaged OOM events from destabilizing the host.

---

## Operations Principles

* Stability over optimization: Never break runtime predictability or upstream software behavior for minor performance wins.
* Monitoring before enforcement: No security restriction shall be applied without active telemetry confirmation.
* Alerting before automation: Ensure visibility triggers high-signal alerts before configuring automated scripts.
* Evidence before action: Operational decisions must stem from live diagnostics, logs, or metrics.

---

## Observability Principles

All core services must provide:
* Structured logs routed exclusively to stdout/stderr.
* Runtime metrics accessible via isolated internal networks.
* Deterministic health status indicators.

Observability is a binding prerequisite for hardening. If a service cannot be monitored, its security posture cannot be modified.

---

## Governance Principles

Changes must respect:
* Approved ADRs (Historical and active architectural records).
* Project scope and single-node deployment boundaries.
* Strict prohibition of docker.sock exposure or any direct container-to-host execution paths.

---

## Change Management Principles

Every significant repository modification must define:
* Objective & Target Container Typology.
* Risk Level & Blast Radius.
* Automated Validation Methods (Makefile triggers).
* Reversible Rollback Execution Path.

---

## Documentation Principles

* Documentation is part of the deliverable: No feature or infrastructure modification is complete without updating its corresponding declarative files or ADRs.
* Undocumented behaviour must be considered temporary, non-compliant, and subject to automatic remediation or deletion during audits.
