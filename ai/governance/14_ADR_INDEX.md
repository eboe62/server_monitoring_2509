# ADR Index

## Purpose

This document is the authoritative index of all ADRs in this repository.

The objective is to:

* identify active ADRs
* identify superseded ADRs
* identify deprecated ADRs
* identify ADR relationships
* improve governance consistency
* improve AI reasoning reliability

All ADR reviews should consult this index before evaluating architectural decisions.

---

## Fundamental Principles

Architecture is governed by approved ADRs.

Not all ADRs have equal status.

An ADR may be:

* Proposed
* Accepted
* Superseded
* Deprecated

Only active accepted ADRs are considered authoritative.

---

## ADR Lifecycle

### PROPOSED

Status: PROPOSED

Meaning: Draft ADR. Not authoritative. May be discussed. May not govern implementation.

### APPROVED

Status: APPROVED

Meaning: Approved ADR. Authoritative. May govern architecture.

### SUPERSEDED

Status: SUPERSEDED

Meaning: Replaced by another ADR. Historical reference only. Not authoritative.

### DEPRECATED

Status: DEPRECATED

Meaning: No longer recommended. Historical reference only. Not authoritative.

---

## ADR Registry — Complete Index

### server_monitoring_2509 (Platform: Docker Compose, Python, IaC)

| ADR | Título | Status | Scope | Fecha | Relacionados | Notas |
|-----|--------|--------|-------|-------|--------------|-------|
| ADR-0000 | Trabajo paralelo fuera de Git durante refactor | APPROVED | System | 2026-01-24 | - | Metodología migración |
| ADR-0001 | Verificación de imports en migración Python | APPROVED | Runtime | 2025-12-09 | ADR-0002 | Policy imports |
| ADR-0002 | Scripts como wrappers operativos | APPROVED | Runtime | 2026-01-25 | ADR-0003, ADR-0011 | Separación src/scripts |
| ADR-0003 | Desacoplamiento config y ejecución runtime | APPROVED | Runtime | 2026-01-25 | ADR-0005, ADR-0011, ADR-0025 | init_config() obligatorio |
| ADR-0004 | Eliminación version docker-compose v2 | APPROVED | Infrastructure | 2026-01-27 | - | Docker Compose v2 |
| ADR-0005 | Desacoplamiento runtime + lazy imports | APPROVED | Runtime | 2026-01-27 | ADR-0003, ADR-0025 | Base SMTP (ADR-0025) |
| ADR-0006 | Gobernanza imagen base monitoring-base | DEPRECATED | Infrastructure | 2026-05-04 | - | Rechazado: imagen compartida |
| ADR-0007 | Política entorno VS Code + WSL | APPROVED | System | 2026-02-16 | - | Stack dev oficial |
| ADR-0008 | Clasificación servicios: Micro-stack vs Infra | APPROVED | Infrastructure | 2026-02-17 | ADR-0009, ADR-0010, ADR-0020 | Taxonomía servicios |
| ADR-0009 | Estrategia backups PostgreSQL | APPROVED | Database | 2026-03-05 | ADR-0008, ADR-0010 | Backups contenerizado |
| ADR-0010 | Arquitectura runtime cron | APPROVED | Runtime | 2026-03-05 | ADR-0008, ADR-0011, ADR-0012 | monitoring-cron oficial |
| ADR-0011 | Python Runtime Execution Model | APPROVED | Runtime | 2026-03-05 | ADR-0002, ADR-0003, ADR-0012 | Determinismo Python |
| ADR-0012 | Separation host cron vs monitoring cron | APPROVED | Runtime | 2026-03-12 | ADR-0010, ADR-0011 | Cron reproducible |
| ADR-0013 | Credential Management Policy | APPROVED | Infrastructure | 2026-03-14 | ADR-0032 | .env + .env.template |
| ADR-0014 | Docker Port Exposure Policy | APPROVED | Infrastructure | 2026-03-14 | ADR-0015 | Loopback only |
| ADR-0015 | Docker Network Exposure Model | APPROVED | Infrastructure | 2026-03-14 | ADR-0014, ADR-0021 | 3 niveles exposición |
| ADR-0016 | Política aislamiento redes Docker | APPROVED | Infrastructure | 2026-05-06 | ADR-0015, ADR-0021 | Redes por dominio |
| ADR-0017 | Resilience model single-node Docker | APPROVED | Runtime | 2026-04-01 | ADR-0018, ADR-0019 | Límites Docker Compose |
| ADR-0018 | Modelo seguridad runtime + resiliencia | APPROVED | Runtime | 2026-04-05 | ADR-0017, ADR-0020, ADR-0024 | Normativo seguridad; `make test-security-runtime |
| ADR-0019 | Resilience Testing Strategy | APPROVED | Runtime | 2026-04-25 | ADR-0017 | Tests multinivel |
| ADR-0020 | Container Execution Model & Privilege | APPROVED | Runtime | 2026-05-04 | ADR-0018, ADR-0024 | Privilegios contextuales |
| ADR-0021 | Network Segmentation Strategy | APPROVED | Infrastructure | 2026-05-04 | ADR-0015, ADR-0016, ADR-0022 | backend/observability/restricted; `make audit-runtime |
| ADR-0022 | Promtail Privilege Approval | APPROVED | Runtime | 2026-05-08 | ADR-0018, ADR-0020, ADR-0021 | Excepción auditada |
| ADR-0023 | Egress Control restricted-net | APPROVED | Infrastructure | 2026-05-08 | ADR-0021 | Futuro: proxy egress |
| ADR-0024 | Container Privilege Exception Policy | APPROVED | Runtime | 2026-05-09 | ADR-0020, ADR-0018 | Mínimo privilegio contextual |
| ADR-0025 | Modelo SMTP explícito + endurecimiento | APPROVED | Runtime | 2026-05-13 | ADR-0005, ADR-0003, ADR-0026 | SMTP_MODE: relay\|auth; `make test-smtp-all |
| ADR-0026 | Estrategia testing modelo SMTP | APPROVED | Runtime | 2026-05-13 | ADR-0025 | Testing multinivel SMTP |
| ADR-0027 | Tipología contenedores + healthchecks | APPROVED | Runtime | 2026-05-17 | ADR-0008, ADR-0020 | Clasificación oficial; `make test-python-health |
| ADR-0028 | Política reproducibilidad Docker | APPROVED | Infrastructure | 2026-05-18 | ADR-0004 | Digest SHA256 obligatorio; `make validate-dockerfiles |
| ADR-0029 | Structured Compose Policy Audit | APPROVED | Infrastructure | 2026-05-20 | ADR-0027 | ops/audit/compose_policy_checks.py; `make test-policy-structured |
| ADR-0030 | Auditoría Runtime HostConfig | APPROVED | Runtime | 2026-05-23 | ADR-0020, ADR-0029 | docker inspect host-side; `make audit-runtime |
| ADR-0031 | Gobernanza Runtime + Dependencias Host | APPROVED | Runtime | 2026-05-26 | ADR-0030, ADR-0018, ADR-0029, ADR-0020, ADR-0024 | Auditoría federada evidencia; `make audit-runtime-ci |
| ADR-0032 | Endurecimiento secretos PostgreSQL | APPROVED | Database | 2026-05-31 | ADR-0013 | POSTGRES_PASSWORD_FILE; `make verify-security |
| ADR-0033 | Taxonomia_ADRs | APPROVED | System | 2026-06-17 | - | - |

### Backend — Java/Maven Multi-Module

| ADR | Título | Status | Scope | Fecha | Relacionados | Notas |
|-----|--------|--------|-------|-------|--------------|-------|
| ADR-0600 | Estrategia despliegue microservicios | APPROVED | System | 2026-06-11 | ADR-0601, ADR-0602, ADR-0603 | Arquitectura Maven independientes |
| ADR-0601 | Desacoplamiento capas patrón Commons | APPROVED | System | 2026-06-11 | ADR-0600, ADR-0602 | DTOs/Interfaces en Commons |
| ADR-0602 | Comunicación inter-servicio REST | APPROVED | System | 2026-06-11 | ADR-0600, ADR-0801 | OpenAPI + versionado |
| ADR-0603 | Gestión BBDD microservicios | APPROVED | Database | 2026-06-11 | ADR-0600 | DB por servicio |

### Deployment & Frontend Strategy

| ADR | Título | Status | Scope | Fecha | Relacionados | Notas |
|-----|--------|--------|-------|-------|--------------|-------|
| ADR-0801 | Empaquetado despliegue Docker | APPROVED | Infrastructure | 2026-06-11 | ADR-0602, ADR-0802 | Multi-stage + Kubernetes |
| ADR-0802 | Integración frontend-backend | APPROVED | System | 2026-06-11 | ADR-0602, ADR-0801 | API Gateway |
| ADR-0803 | Seguridad + secretos microservicios | APPROVED | Infrastructure | 2026-06-11 | ADR-0600, ADR-0801 | Vault + JWT |

---

## Active ADRs — Summary by Category

### ✅ Infrastructure & DevSecOps (APPROVED)
ADR-0004, ADR-0013, ADR-0014, ADR-0015, ADR-0016, ADR-0021, ADR-0028, ADR-0029

### ✅ Runtime & Container Security (APPROVED)
ADR-0017, ADR-0018, ADR-0019, ADR-0020, ADR-0022, ADR-0024, ADR-0027, ADR-0030, ADR-0031

### ✅ Database & Persistence (APPROVED)
ADR-0009, ADR-0032

### ✅ Architecture & System Design (APPROVED)
ADR-0000, ADR-0001, ADR-0002, ADR-0003, ADR-0005, ADR-0007, ADR-0008, ADR-0010, ADR-0011, ADR-0012, ADR-0025, ADR-0600, ADR-0601

---

## Deprecated ADRs

| ADR | Razón |
|-----|-------|
| ADR-0006 | Rechazado: Decisión arquitectónica contra imagen base compartida. NO aplicable. |

---

## Proposed ADRs (No Authoritative)

| ADR | Título | Scope |
|-----|--------|-------|
| ADR-0023 | Egress Control restricted-net | Infrastructure |
| ADR-0026 | Estrategia testing SMTP | Runtime |
| ADR-0602 | Comunicación inter-servicio REST | System |
| ADR-0603 | Gestión BBDD microservicios | Database |
| ADR-0801 | Empaquetado despliegue Docker | Infrastructure |
| ADR-0802 | Integración frontend-backend | System |
| ADR-0803 | Seguridad + secretos microservicios | Infrastructure |

---

## ADR Conflict Resolution

If two ADRs appear to conflict:

1. Check ADR_INDEX.md for status
2. Verify supersession chain
3. Only APPROVED ADRs are authoritative
4. PROPOSED ADRs cannot override APPROVED ADRs
5. Activate Governance Arbiter if required

Do not assume newer ADRs automatically override older ADRs.

---

## ADR Authority Rules

Only ADRs with Status: APPROVED are authoritative.

- PROPOSED ADRs: Not authoritative
- SUPERSEDED ADRs: Not authoritative
- DEPRECATED ADRs: Not authoritative

---

## AI Governance Rule

AI assistants must consult ADR_INDEX.md before:

* ADR reviews
* architecture reviews
* hardening reviews
* implementation recommendations

Failure to verify ADR status may produce invalid conclusions.

---

## Maintenance Rules

Every ADR creation must update: ADR_INDEX.md
Every ADR status change must update: ADR_INDEX.md
Every ADR supersession must update: ADR_INDEX.md

ADR changes are incomplete until ADR_INDEX.md is updated.

---

## Final Principle

The ADR repository contains architectural history.

ADR_INDEX.md identifies architectural authority.
