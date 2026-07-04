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

| ADR | Status | Category | Scope | Date | Title |
|-----|--------|----------|-------|------|-------|
| ADR-0000 | APPROVED | GOVERNANCE | System | 2026-01-24 | Trabajo paralelo fuera de Git durante refactor estructural |
| ADR-0001 | APPROVED | ARCHITECTURE | Runtime | 2025-12-09 | Verificación de imports durante la fase de migración |
| ADR-0002 | APPROVED | ARCHITECTURE | Runtime | 2026-01-25 | Scripts como wrappers operativos |
| ADR-0003 | APPROVED | RUNTIME | Runtime | 2026-01-25 | Desacoplamiento de configuración y ejecución en runtime |
| ADR-0004 | APPROVED | INFRASTRUCTURE | Infrastructure | 2026-01-27 | Eliminación del atributo version en docker-compose (Docker Compose v2) |
| ADR-0005 | APPROVED | RUNTIME | Runtime | 2026-01-27 | Desacoplamiento runtime y lazy imports en config (Runtime desacoplado) |
| ADR-0006 | DEPRECATED | GOVERNANCE | Infrastructure | 2026-05-04 | Gobernanza de imagen base monitoring-base (Rechazado) |
| ADR-0007 | APPROVED | GOVERNANCE | System | 2026-02-16 | Política oficial de entorno VS Code + WSL para proyectos Linux/DevOps |
| ADR-0008 | APPROVED | ARCHITECTURE | Infrastructure | 2026-02-17 | Clasificación de servicios: Micro-stack vs Infraestructura Operativa |
| ADR-0009 | APPROVED | DATABASE | Database | 2026-03-05 | Estrategia de Backups PostgreSQL |
| ADR-0010 | APPROVED | RUNTIME | Runtime | 2026-03-05 | Arquitectura de runtime cron |
| ADR-0011 | APPROVED | RUNTIME | Runtime | 2026-03-05 | Python Runtime Execution Model (Determinismo) |
| ADR-0012 | APPROVED | RUNTIME | Runtime | 2026-03-12 | Separation of Host Cron vs Monitoring Cron (Runtime reproducible) |
| ADR-0013 | APPROVED | SECURITY | Infrastructure | 2026-03-14 | Credential Management Policy |
| ADR-0014 | APPROVED | INFRASTRUCTURE | Infrastructure | 2026-03-14 | Docker Port Exposure Policy |
| ADR-0015 | APPROVED | INFRASTRUCTURE | Infrastructure | 2026-03-14 | Docker Network Exposure Model |
| ADR-0016 | APPROVED | SECURITY | Infrastructure | 2026-05-06 | Política de aislamiento y segmentación de redes Docker |
| ADR-0017 | APPROVED | RUNTIME | Runtime | 2026-04-01 | Resilience model at docker single-node |
| ADR-0018 | APPROVED | SECURITY | Runtime | 2026-04-05 | Modelo de Seguridad Runtime Docker y Requisitos de Resiliencia |
| ADR-0019 | APPROVED | TESTING | Runtime | 2026-04-25 | Resilience Testing Strategy |
| ADR-0020 | APPROVED | SECURITY | Runtime | 2026-05-04 | Container Execution Model & Privilege Strategy |
| ADR-0021 | APPROVED | SECURITY | Infrastructure | 2026-05-04 | Network Segmentation Strategy |
| ADR-0022 | APPROVED | SECURITY | Runtime | 2026-05-08 | Promtail Privilege Approval |
| ADR-0023 | APPROVED | SECURITY | Infrastructure | 2026-05-08 | Egress Control for restricted-net (Propuesto) |
| ADR-0024 | APPROVED | SECURITY | Runtime | 2026-05-09 | Container Privilege Exception Policy (Mínimo privilegio contextual) |
| ADR-0025 | APPROVED | SECURITY | Runtime | 2026-05-13 | Modelo SMTP explícito y endurecimiento de configuración (Endurecimiento SMTP) |
| ADR-0026 | APPROVED | TESTING | Runtime | 2026-05-13 | Estrategia de validación y testing del modelo SMTP (Estrategia de validación multinivel) |
| ADR-0027 | APPROVED | RUNTIME | Runtime | 2026-05-17 | Tipología oficial de contenedores y política de healthchecks |
| ADR-0028 | APPROVED | INFRASTRUCTURE | Infrastructure | 2026-05-18 | Política de reproducibilidad Docker y endurecimiento de validaciones IaC |
| ADR-0029 | APPROVED | GOVERNANCE | Infrastructure | 2026-05-20 | Structured Compose Policy Audit |
| ADR-0030 | APPROVED | GOVERNANCE | Runtime | 2026-05-23 | Auditoría Runtime HostConfig y Visibilidad de Privilegios Docker |
| ADR-0031 | APPROVED | GOVERNANCE | Runtime | 2026-05-26 | Gobernanza Runtime Docker y Clasificación de Dependencias Host |
| ADR-0032 | APPROVED | SECURITY | Database | 2026-05-31 | Endurecimiento de gestión de secretos PostgreSQL y validaciones CI |
| ADR-0033 | APPROVED | GOVERNANCE | System | 2026-06-17 | Taxonomía Oficial de Clasificación y Etiquetado de ADRs |

### Backend — Java/Maven Multi-Module

| ADR | Status | Category | Scope | Date | Title |
|-----|--------|----------|-------|------|-------|
| ADR-0600 | APPROVED | ARCHITECTURE | System | 2026-06-11 | Estrategia de Despliegue: Arquitectura de Microservicios Independientes basados en Maven Multi-Module |
| ADR-0601 | APPROVED | ARCHITECTURE | System | 2026-06-11 | Estructura de Desacoplamiento de Capas mediante el Patrón Módulo-Commons |
| ADR-0602 | APPROVED | ARCHITECTURE | System | 2026-06-11 | Estrategia de Comunicación Inter-Servicio en Arquitectura de Microservicios |
| ADR-0603 | APPROVED | DATABASE | Database | 2026-06-11 | Políticas de Gestión de Bases de Datos en Microservicios |

### Deployment & Frontend Strategy

| ADR | Status | Category | Scope | Date | Title |
|-----|--------|----------|-------|------|-------|
| ADR-0801 | APPROVED | DEPLOYMENT | Infrastructure | 2026-06-11 | Estrategia de Empaquetado y Despliegue con Contenedores Docker |
| ADR-0802 | APPROVED | ARCHITECTURE | System | 2026-06-11 | Lineamientos de Integración Frontend con Microservicios Backend |
| ADR-0803 | APPROVED | SECURITY | Infrastructure | 2026-06-11 | Estrategias de Seguridad y Gestión de Secretos en Microservicios |

---

## Active ADRs — Summary by Category

### ✅ ARCHITECTURE (APPROVED)
ADR-0001, ADR-0002, ADR-0008, ADR-0600, ADR-0601, ADR-0602, ADR-0802

### ✅ RUNTIME (APPROVED)
ADR-0003, ADR-0005, ADR-0010, ADR-0011, ADR-0012, ADR-0017, ADR-0027

### ✅ INFRASTRUCTURE (APPROVED)
ADR-0004, ADR-0014, ADR-0015, ADR-0028

### ✅ SECURITY (APPROVED)
ADR-0013, ADR-0016, ADR-0018, ADR-0020, ADR-0021, ADR-0022, ADR-0023, ADR-0024, ADR-0025, ADR-0032, ADR-0803

### ✅ DATABASE (APPROVED)
ADR-0009, ADR-0603

### ✅ DEPLOYMENT (APPROVED)
ADR-0801

### ✅ TESTING (APPROVED)
ADR-0019, ADR-0026

### ✅ GOVERNANCE (APPROVED)
ADR-0000, ADR-0007, ADR-0029, ADR-0030, ADR-0031, ADR-0033

---

## Deprecated ADRs

| ADR | Status | Category | Scope | Date | Title |
|-----|--------|----------|-------|------|-------|
| ADR-0006 | DEPRECATED | GOVERNANCE | Infrastructure | 2026-05-04 | Gobernanza de imagen base monitoring-base (Rechazado) |

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
