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

Default Expectations apply according to the 4 system runtimes defined in devsecops_architect.md:
* cap_drop: ALL (Dropping all kernel capabilities by default; additions require explicit ADR justification).
* no-new-privileges: true (Enforced universally to prevent runtime process escalation).
* Application of non-root execution and healthchecks must strictly follow the constraints mapped out under the Container Typology Enforcement policy.

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

All core services must provide structured logs (stdout/stderr), isolated runtime metrics, and deterministic health indicators.

These outputs serve to establish the mandatory operational baselines required by the Visibility Precedes Hardening rule in AI_CONSTITUTION.md.

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
