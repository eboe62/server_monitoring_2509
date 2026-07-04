# DevSecOps Principles

## Architecture Principles

* Infrastructure as Code first
* Docker Compose standalone
* Single-node architecture
* Progressive evolution
* Operational simplicity

---

## Security Principles

* Least privilege
* Defense in depth
* Progressive hardening
* Runtime validation
* Explicit trust boundaries

---

## Container Principles

Default expectations:

* cap_drop: ALL
* no-new-privileges
* non-root when viable
* healthchecks enabled

read_only requires evidence.

---

## Operations Principles

* Stability over optimization
* Monitoring before enforcement
* Alerting before automation
* Evidence before action

---

## Observability Principles

All critical services should provide:

* logs
* metrics
* healthchecks

Observability is a prerequisite for enforcement.

---

## Governance Principles

Changes must respect:

* approved ADRs
* project scope
* operational constraints

---

## Change Management Principles

Every significant change should define:

* objective
* risk
* validation
* rollback

---

## Documentation Principles

Documentation is part of the deliverable.

Undocumented behaviour should be considered temporary.
