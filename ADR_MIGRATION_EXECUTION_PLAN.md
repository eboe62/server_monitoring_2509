# ADR_MIGRATION_EXECUTION_PLAN.md

## Introducción

Este documento detalla el plan de migración para normalizar las cabeceras de todos los ADRs en el repositorio, asegurando el cumplimiento de la gobernanza aprobada y el uso del template oficial `adr_template.md`.

---

## Matriz de Ejecución de Migración

### ADR-0000: Trabajo paralelo fuera de Git durante refactor estructural

**Status:**
  Actual: Aprobado
  Nuevo: APPROVED
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Date:**
  Actual: 2026-01-24
  Nuevo: 2026-01-24
  Fuente: Contenido literal ADR
  Confianza: 100%

**Decision Type:**
  Actual: NULL
  Nuevo: ARCHITECTURE
  Fuente: Contenido ADR (Metodología de refactor estructural)
  Confianza: 100%

**Scope:**
  Actual: Migración IaC server_monitoring_2509
  Nuevo: System
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Tags:**
  Actual: NULL
  Nuevo: PENDIENTE
  Fuente: INSUFFICIENT EVIDENCE

**Related ADRs:**
  Actual: NULL
  Nuevo: NONE
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Validation Reference:**
  Actual: NULL
  Nuevo: NONE
  Fuente: ADR_INDEX.md
  Confianza: 100%

---

### ADR-0001: Verificación de imports durante la fase de migración

**Status:**
  Actual: Aprobado
  Nuevo: APPROVED
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Date:**
  Actual: 2025-12-09
  Nuevo: 2025-12-09
  Fuente: Contenido literal ADR
  Confianza: 100%

**Decision Type:**
  Actual: NULL
  Nuevo: GOVERNANCE
  Fuente: ADR_INDEX.md (Policy imports)
  Confianza: 100%

**Scope:**
  Actual: Migración IaC server_monitoring_2509
  Nuevo: Runtime
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Tags:**
  Actual: NULL
  Nuevo: PENDIENTE
  Fuente: INSUFFICIENT EVIDENCE

**Related ADRs:**
  Actual: NULL
  Nuevo: ADR-0002
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Validation Reference:**
  Actual: NULL
  Nuevo: NONE
  Fuente: ADR_INDEX.md
  Confianza: 100%

---

### ADR-0002: Scripts como wrappers operativos

**Status:**
  Actual: Aprobado
  Nuevo: APPROVED
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Date:**
  Actual: 2026-01-25
  Nuevo: 2026-01-25
  Fuente: Contenido literal ADR
  Confianza: 100%

**Decision Type:**
  Actual: NULL
  Nuevo: ARCHITECTURE
  Fuente: Contenido ADR (Separación src/scripts)
  Confianza: 100%

**Scope:**
  Actual: Migración IaC server_monitoring_2509
  Nuevo: Runtime
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Tags:**
  Actual: NULL
  Nuevo: PENDIENTE
  Fuente: INSUFFICIENT EVIDENCE

**Related ADRs:**
  Actual: NULL
  Nuevo: ADR-0003, ADR-0011
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Validation Reference:**
  Actual: NULL
  Nuevo: NONE
  Fuente: ADR_INDEX.md
  Confianza: 100%

---

### ADR-0003: Desacoplamiento de configuración y ejecución en runtime

**Status:**
  Actual: Aprobado
  Nuevo: APPROVED
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Date:**
  Actual: 2026-01-25
  Nuevo: 2026-01-25
  Fuente: Contenido literal ADR
  Confianza: 100%

**Decision Type:**
  Actual: NULL
  Nuevo: SECURITY
  Fuente: Contenido ADR (init_config() obligatorio por secretos)
  Confianza: 100%

**Scope:**
  Actual: Migración IaC server_monitoring_2509
  Nuevo: Runtime
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Tags:**
  Actual: NULL
  Nuevo: PENDIENTE
  Fuente: INSUFFICIENT EVIDENCE

**Related ADRs:**
  Actual: NULL
  Nuevo: ADR-0005, ADR-0011, ADR-0025
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Validation Reference:**
  Actual: NULL
  Nuevo: NONE
  Fuente: ADR_INDEX.md
  Confianza: 100%

---

### ADR-0004: Eliminación del atributo version en docker-compose

**Status:**
  Actual: Aprobado
  Nuevo: APPROVED
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Date:**
  Actual: 2026-01-27
  Nuevo: 2026-01-27
  Fuente: Contenido literal ADR
  Confianza: 100%

**Decision Type:**
  Actual: NULL
  Nuevo: INFRASTRUCTURE
  Fuente: ADR_INDEX.md (Docker Compose v2)
  Confianza: 100%

**Scope:**
  Actual: Migración IaC server_monitoring_2509
  Nuevo: Infrastructure
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Tags:**
  Actual: NULL
  Nuevo: PENDIENTE
  Fuente: INSUFFICIENT EVIDENCE

**Related ADRs:**
  Actual: NULL
  Nuevo: NONE
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Validation Reference:**
  Actual: NULL
  Nuevo: NONE
  Fuente: ADR_INDEX.md
  Confianza: 100%

---

### ADR-0005: Desacoplamiento runtime y lazy imports en config

**Status:**
  Actual: Aprobado
  Nuevo: APPROVED
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Date:**
  Actual: 2026-01-27
  Nuevo: 2026-01-27
  Fuente: Contenido literal ADR
  Confianza: 100%

**Decision Type:**
  Actual: NULL
  Nuevo: ARCHITECTURE
  Fuente: Contenido ADR (Runtime desacoplado)
  Confianza: 100%

**Scope:**
  Actual: Migración IaC server_monitoring_2509
  Nuevo: Runtime
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Tags:**
  Actual: NULL
  Nuevo: PENDIENTE
  Fuente: INSUFFICIENT EVIDENCE

**Related ADRs:**
  Actual: NULL
  Nuevo: ADR-0003, ADR-0025
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Validation Reference:**
  Actual: NULL
  Nuevo: NONE
  Fuente: ADR_INDEX.md
  Confianza: 100%

---

### ADR-0006: Gobernanza imagen base monitoring-base

**Status:**
  Actual: Rechazado
  Nuevo: DEPRECATED
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Date:**
  Actual: 2026-05-04
  Nuevo: 2026-05-04
  Fuente: Contenido literal ADR
  Confianza: 100%

**Decision Type:**
  Actual: NULL
  Nuevo: GOVERNANCE
  Fuente: Título ADR
  Confianza: 100%

**Scope:**
  Actual: Migración PRO server_monitoring_2602
  Nuevo: Infrastructure
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Tags:**
  Actual: NULL
  Nuevo: PENDIENTE
  Fuente: INSUFFICIENT EVIDENCE

**Related ADRs:**
  Actual: NULL
  Nuevo: NONE
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Validation Reference:**
  Actual: NULL
  Nuevo: NONE
  Fuente: ADR_INDEX.md
  Confianza: 100%

---

### ADR-0007: Política entorno VS Code + WSL

**Status:**
  Actual: Aprobado
  Nuevo: APPROVED
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Date:**
  Actual: 2026-02-16
  Nuevo: 2026-02-16
  Fuente: Contenido literal ADR
  Confianza: 100%

**Decision Type:**
  Actual: NULL
  Nuevo: GOVERNANCE
  Fuente: ADR_INDEX.md (Stack dev oficial)
  Confianza: 100%

**Scope:**
  Actual: server_monitoring_2509
  Nuevo: System
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Tags:**
  Actual: NULL
  Nuevo: PENDIENTE
  Fuente: INSUFFICIENT EVIDENCE

**Related ADRs:**
  Actual: NULL
  Nuevo: NONE
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Validation Reference:**
  Actual: NULL
  Nuevo: NONE
  Fuente: ADR_INDEX.md
  Confianza: 100%

---

### ADR-0008: Clasificación servicios: Micro-stack vs Infra-stack

**Status:**
  Actual: ACCEPTED
  Nuevo: APPROVED
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Date:**
  Actual: 2026-02-17
  Nuevo: 2026-02-17
  Fuente: Contenido literal ADR
  Confianza: 100%

**Decision Type:**
  Actual: NULL
  Nuevo: ARCHITECTURE
  Fuente: ADR_INDEX.md (Taxonomía servicios)
  Confianza: 100%

**Scope:**
  Actual: server_monitoring_2509
  Nuevo: Infrastructure
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Tags:**
  Actual: NULL
  Nuevo: PENDIENTE
  Fuente: INSUFFICIENT EVIDENCE

**Related ADRs:**
  Actual: NULL
  Nuevo: ADR-0009, ADR-0010, ADR-0020
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Validation Reference:**
  Actual: NULL
  Nuevo: NONE
  Fuente: ADR_INDEX.md
  Confianza: 100%

---

### ADR-0009: Estrategia backups PostgreSQL

**Status:**
  Actual: Aprobado
  Nuevo: APPROVED
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Date:**
  Actual: 2026-03-05
  Nuevo: 2026-03-05
  Fuente: Contenido literal ADR
  Confianza: 100%

**Decision Type:**
  Actual: NULL
  Nuevo: DATA
  Fuente: Contenido ADR (Persistencia PostgreSQL)
  Confianza: 100%

**Scope:**
  Actual: server_monitoring_2509
  Nuevo: Database
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Tags:**
  Actual: NULL
  Nuevo: PENDIENTE
  Fuente: INSUFFICIENT EVIDENCE

**Related ADRs:**
  Actual: NULL
  Nuevo: ADR-0008, ADR-0010
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Validation Reference:**
  Actual: NULL
  Nuevo: NONE
  Fuente: ADR_INDEX.md
  Confianza: 100%

---

### ADR-0010: Arquitectura de runtime cron

**Status:**
  Actual: ACCEPTED
  Nuevo: APPROVED
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Date:**
  Actual: 2026-03-05
  Nuevo: 2026-03-05
  Fuente: Contenido literal ADR
  Confianza: 100%

**Decision Type:**
  Actual: NULL
  Nuevo: ARCHITECTURE
  Fuente: ADR_INDEX.md (monitoring-cron oficial)
  Confianza: 100%

**Scope:**
  Actual: server_monitoring_2509
  Nuevo: Runtime
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Tags:**
  Actual: NULL
  Nuevo: PENDIENTE
  Fuente: INSUFFICIENT EVIDENCE

**Related ADRs:**
  Actual: NULL
  Nuevo: ADR-0008, ADR-0011, ADR-0012
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Validation Reference:**
  Actual: NULL
  Nuevo: NONE
  Fuente: ADR_INDEX.md
  Confianza: 100%

---

### ADR-0011: Python Runtime Execution Model

**Status:**
  Actual: ACCEPTED
  Nuevo: APPROVED
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Date:**
  Actual: 2026-03-05
  Nuevo: 2026-03-05
  Fuente: Contenido literal ADR
  Confianza: 100%

**Decision Type:**
  Actual: NULL
  Nuevo: INFRASTRUCTURE
  Fuente: Contenido ADR (Aislamiento del entorno de ejecución)
  Confianza: 100%

**Scope:**
  Actual: server_monitoring_2509
  Nuevo: Runtime
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Tags:**
  Actual: NULL
  Nuevo: PENDIENTE
  Fuente: INSUFFICIENT EVIDENCE

**Related ADRs:**
  Actual: NULL
  Nuevo: ADR-0002, ADR-0003, ADR-0012
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Validation Reference:**
  Actual: NULL
  Nuevo: NONE
  Fuente: ADR_INDEX.md
  Confianza: 100%

---

### ADR-0012: Separation of Host Cron vs Monitoring Cron

**Status:**
  Actual: ACCEPTED
  Nuevo: APPROVED
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Date:**
  Actual: 2026-03-12
  Nuevo: 2026-03-12
  Fuente: Contenido literal ADR
  Confianza: 100%

**Decision Type:**
  Actual: NULL
  Nuevo: ARCHITECTURE
  Fuente: ADR_INDEX.md (Cron reproducible)
  Confianza: 100%

**Scope:**
  Actual: server_monitoring_2509
  Nuevo: Runtime
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Tags:**
  Actual: NULL
  Nuevo: PENDIENTE
  Fuente: INSUFFICIENT EVIDENCE

**Related ADRs:**
  Actual: NULL
  Nuevo: ADR-0010, ADR-0011
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Validation Reference:**
  Actual: NULL
  Nuevo: NONE
  Fuente: ADR_INDEX.md
  Confianza: 100%

---

### ADR-0013: Credential Management Policy

**Status:**
  Actual: Aprobado
  Nuevo: APPROVED
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Date:**
  Actual: 2026-03-14
  Nuevo: 2026-03-14
  Fuente: Contenido literal ADR
  Confianza: 100%

**Decision Type:**
  Actual: NULL
  Nuevo: SECURITY
  Fuente: Contenido ADR (Gestión de secretos .env)
  Confianza: 100%

**Scope:**
  Actual: server_monitoring_2509
  Nuevo: Infrastructure
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Tags:**
  Actual: NULL
  Nuevo: PENDIENTE
  Fuente: INSUFFICIENT EVIDENCE

**Related ADRs:**
  Actual: NULL
  Nuevo: ADR-0032
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Validation Reference:**
  Actual: NULL
  Nuevo: NONE
  Fuente: ADR_INDEX.md
  Confianza: 100%

---

### ADR-0014: Docker Port Exposure Policy

**Status:**
  Actual: Aprobado
  Nuevo: APPROVED
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Date:**
  Actual: 2026-03-14
  Nuevo: 2026-03-14
  Fuente: Contenido literal ADR
  Confianza: 100%

**Decision Type:**
  Actual: NULL
  Nuevo: SECURITY
  Fuente: Contenido ADR (Reducción superficie de ataque)
  Confianza: 100%

**Scope:**
  Actual: server_monitoring_2509
  Nuevo: Infrastructure
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Tags:**
  Actual: NULL
  Nuevo: PENDIENTE
  Fuente: INSUFFICIENT EVIDENCE

**Related ADRs:**
  Actual: NULL
  Nuevo: ADR-0015
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Validation Reference:**
  Actual: NULL
  Nuevo: NONE
  Fuente: ADR_INDEX.md
  Confianza: 100%

---

### ADR-0015: Docker Network Exposure Model

**Status:**
  Actual: Aprobado
  Nuevo: APPROVED
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Date:**
  Actual: 2026-03-14
  Nuevo: 2026-03-14
  Fuente: Contenido literal ADR
  Confianza: 100%

**Decision Type:**
  Actual: NULL
  Nuevo: SECURITY
  Fuente: Contenido ADR (3 niveles exposición)
  Confianza: 100%

**Scope:**
  Actual: server_monitoring_2509
  Nuevo: Infrastructure
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Tags:**
  Actual: NULL
  Nuevo: PENDIENTE
  Fuente: INSUFFICIENT EVIDENCE

**Related ADRs:**
  Actual: NULL
  Nuevo: ADR-0014, ADR-0021
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Validation Reference:**
  Actual: NULL
  Nuevo: NONE
  Fuente: ADR_INDEX.md
  Confianza: 100%

---

### ADR-0016: Política aislamiento redes Docker

**Status:**
  Actual: Aprobado
  Nuevo: APPROVED
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Date:**
  Actual: 2026-05-06
  Nuevo: 2026-05-06
  Fuente: Contenido literal ADR
  Confianza: 100%

**Decision Type:**
  Actual: NULL
  Nuevo: SECURITY
  Fuente: Contenido ADR (Aislamiento y segmentación)
  Confianza: 100%

**Scope:**
  Actual: server_monitoring_2509
  Nuevo: Infrastructure
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Tags:**
  Actual: NULL
  Nuevo: PENDIENTE
  Fuente: INSUFFICIENT EVIDENCE

**Related ADRs:**
  Actual: NULL
  Nuevo: ADR-0015, ADR-0021
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Validation Reference:**
  Actual: NULL
  Nuevo: NONE
  Fuente: ADR_INDEX.md
  Confianza: 100%

---

### ADR-0017: Resilience model single-node Docker

**Status:**
  Actual: Aprobado
  Nuevo: APPROVED
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Date:**
  Actual: 2026-04-01
  Nuevo: 2026-04-01
  Fuente: Contenido literal ADR
  Confianza: 100%

**Decision Type:**
  Actual: NULL
  Nuevo: INFRASTRUCTURE
  Fuente: ADR_INDEX.md (Límites Docker Compose)
  Confianza: 100%

**Scope:**
  Actual: server_monitoring_2509
  Nuevo: Runtime
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Tags:**
  Actual: NULL
  Nuevo: PENDIENTE
  Fuente: INSUFFICIENT EVIDENCE

**Related ADRs:**
  Actual: NULL
  Nuevo: ADR-0018, ADR-0019
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Validation Reference:**
  Actual: NULL
  Nuevo: NONE
  Fuente: ADR_INDEX.md
  Confianza: 100%

---

### ADR-0018: Modelo seguridad runtime + resiliencia

**Status:**
  Actual: Aprobado
  Nuevo: APPROVED
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Date:**
  Actual: 2026-04-05
  Nuevo: 2026-04-05
  Fuente: Contenido literal ADR
  Confianza: 100%

**Decision Type:**
  Actual: NULL
  Nuevo: SECURITY
  Fuente: Título ADR
  Confianza: 100%

**Scope:**
  Actual: server_monitoring_2509
  Nuevo: Runtime
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Tags:**
  Actual: NULL
  Nuevo: PENDIENTE
  Fuente: INSUFFICIENT EVIDENCE

**Related ADRs:**
  Actual: NULL
  Nuevo: ADR-0017, ADR-0020, ADR-0024
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Validation Reference:**
  Actual: NULL
  Nuevo: make test-security-runtime
  Fuente: ADR_INDEX.md
  Confianza: 100%

---

### ADR-0019: Resilience Testing Strategy

**Status:**
  Actual: Aprobado
  Nuevo: APPROVED
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Date:**
  Actual: 2026-04-25
  Nuevo: 2026-04-25
  Fuente: Contenido literal ADR
  Confianza: 100%

**Decision Type:**
  Actual: NULL
  Nuevo: GOVERNANCE
  Fuente: Título ADR (Strategy)
  Confianza: 100%

**Scope:**
  Actual: server_monitoring_2509
  Nuevo: Runtime
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Tags:**
  Actual: NULL
  Nuevo: PENDIENTE
  Fuente: INSUFFICIENT EVIDENCE

**Related ADRs:**
  Actual: NULL
  Nuevo: ADR-0017
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Validation Reference:**
  Actual: NULL
  Nuevo: NONE
  Fuente: ADR_INDEX.md
  Confianza: 100%

---

### ADR-0020: Container Execution Model & Privilege

**Status:**
  Actual: Aprobado
  Nuevo: APPROVED
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Date:**
  Actual: 2026-05-04
  Nuevo: 2026-05-04
  Fuente: Contenido literal ADR
  Confianza: 100%

**Decision Type:**
  Actual: NULL
  Nuevo: SECURITY
  Fuente: Contenido ADR (Privilegios contextuales)
  Confianza: 100%

**Scope:**
  Actual: server_monitoring_2509
  Nuevo: Runtime
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Tags:**
  Actual: NULL
  Nuevo: PENDIENTE
  Fuente: INSUFFICIENT EVIDENCE

**Related ADRs:**
  Actual: NULL
  Nuevo: ADR-0018, ADR-0024
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Validation Reference:**
  Actual: NULL
  Nuevo: NONE
  Fuente: ADR_INDEX.md
  Confianza: 100%

---

### ADR-0021: Network Segmentation Strategy

**Status:**
  Actual: Aprobado
  Nuevo: APPROVED
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Date:**
  Actual: 2026-05-04
  Nuevo: 2026-05-04
  Fuente: Contenido literal ADR
  Confianza: 100%

**Decision Type:**
  Actual: NULL
  Nuevo: SECURITY
  Fuente: Contenido ADR (Segmentación redes)
  Confianza: 100%

**Scope:**
  Actual: server_monitoring_2509
  Nuevo: Infrastructure
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Tags:**
  Actual: NULL
  Nuevo: PENDIENTE
  Fuente: INSUFFICIENT EVIDENCE

**Related ADRs:**
  Actual: NULL
  Nuevo: ADR-0015, ADR-0016, ADR-0022
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Validation Reference:**
  Actual: NULL
  Nuevo: make audit-runtime
  Fuente: ADR_INDEX.md
  Confianza: 100%

---

### ADR-0022: Promtail Privilege Approval

**Status:**
  Actual: Aprobado
  Nuevo: APPROVED
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Date:**
  Actual: 2026-05-08
  Nuevo: 2026-05-08
  Fuente: Contenido literal ADR
  Confianza: 100%

**Decision Type:**
  Actual: NULL
  Nuevo: SECURITY
  Fuente: Título ADR (Privilege Approval)
  Confianza: 100%

**Scope:**
  Actual: server_monitoring_2509
  Nuevo: Runtime
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Tags:**
  Actual: NULL
  Nuevo: PENDIENTE
  Fuente: INSUFFICIENT EVIDENCE

**Related ADRs:**
  Actual: NULL
  Nuevo: ADR-0018, ADR-0020, ADR-0021
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Validation Reference:**
  Actual: NULL
  Nuevo: NONE
  Fuente: ADR_INDEX.md
  Confianza: 100%

---

### ADR-0023: Egress Control restricted-net

**Status:**
  Actual: Propuesto
  Nuevo: PROPOSED
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Date:**
  Actual: 2026-05-08
  Nuevo: 2026-05-08
  Fuente: Contenido literal ADR
  Confianza: 100%

**Decision Type:**
  Actual: NULL
  Nuevo: SECURITY
  Fuente: ADR_INDEX.md (proxy egress)
  Confianza: 100%

**Scope:**
  Actual: server_monitoring_2509
  Nuevo: Infrastructure
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Tags:**
  Actual: NULL
  Nuevo: PENDIENTE
  Fuente: INSUFFICIENT EVIDENCE

**Related ADRs:**
  Actual: NULL
  Nuevo: ADR-0021
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Validation Reference:**
  Actual: NULL
  Nuevo: NONE
  Fuente: ADR_INDEX.md
  Confianza: 100%

---

### ADR-0024: Container Privilege Exception Policy

**Status:**
  Actual: Aprobado
  Nuevo: APPROVED
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Date:**
  Actual: 2026-05-09
  Nuevo: 2026-05-09
  Fuente: Contenido literal ADR
  Confianza: 100%

**Decision Type:**
  Actual: NULL
  Nuevo: SECURITY
  Fuente: Contenido ADR (Mínimo privilegio contextual)
  Confianza: 100%

**Scope:**
  Actual: server_monitoring_2509
  Nuevo: Runtime
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Tags:**
  Actual: NULL
  Nuevo: PENDIENTE
  Fuente: INSUFFICIENT EVIDENCE

**Related ADRs:**
  Actual: NULL
  Nuevo: ADR-0020, ADR-0018
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Validation Reference:**
  Actual: NULL
  Nuevo: NONE
  Fuente: ADR_INDEX.md
  Confianza: 100%

---

### ADR-0025: Modelo SMTP explícito + endurecimiento

**Status:**
  Actual: Aprobado
  Nuevo: APPROVED
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Date:**
  Actual: 2026-05-13
  Nuevo: 2026-05-13
  Fuente: Contenido literal ADR
  Confianza: 100%

**Decision Type:**
  Actual: NULL
  Nuevo: SECURITY
  Fuente: Contenido ADR (Endurecimiento SMTP)
  Confianza: 100%

**Scope:**
  Actual: server_monitoring_2509
  Nuevo: Runtime
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Tags:**
  Actual: NULL
  Nuevo: PENDIENTE
  Fuente: INSUFFICIENT EVIDENCE

**Related ADRs:**
  Actual: NULL
  Nuevo: ADR-0005, ADR-0003, ADR-0026
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Validation Reference:**
  Actual: NULL
  Nuevo: make test-smtp-all
  Fuente: ADR_INDEX.md
  Confianza: 100%

---

### ADR-0026: Estrategia testing modelo SMTP

**Status:**
  Actual: Propuesta
  Nuevo: PROPOSED
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Date:**
  Actual: 2026-05-13
  Nuevo: 2026-05-13
  Fuente: Contenido literal ADR
  Confianza: 100%

**Decision Type:**
  Actual: NULL
  Nuevo: GOVERNANCE
  Fuente: Título ADR (Strategy)
  Confianza: 100%

**Scope:**
  Actual: server_monitoring_2509
  Nuevo: Runtime
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Tags:**
  Actual: NULL
  Nuevo: PENDIENTE
  Fuente: INSUFFICIENT EVIDENCE

**Related ADRs:**
  Actual: NULL
  Nuevo: ADR-0025
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Validation Reference:**
  Actual: NULL
  Nuevo: NONE
  Fuente: ADR_INDEX.md
  Confianza: 100%

---

### ADR-0027: Tipología contenedores + healthchecks

**Status:**
  Actual: Aprobado
  Nuevo: APPROVED
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Date:**
  Actual: 2026-05-17
  Nuevo: 2026-05-17
  Fuente: Contenido literal ADR
  Confianza: 100%

**Decision Type:**
  Actual: NULL
  Nuevo: GOVERNANCE
  Fuente: ADR_INDEX.md (Clasificación oficial)
  Confianza: 100%

**Scope:**
  Actual: server_monitoring_2509
  Nuevo: Runtime
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Tags:**
  Actual: NULL
  Nuevo: PENDIENTE
  Fuente: INSUFFICIENT EVIDENCE

**Related ADRs:**
  Actual: NULL
  Nuevo: ADR-0008, ADR-0020
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Validation Reference:**
  Actual: NULL
  Nuevo: make test-python-health
  Fuente: ADR_INDEX.md
  Confianza: 100%

---

### ADR-0028: Política reproducibilidad Docker

**Status:**
  Actual: Aprobado
  Nuevo: APPROVED
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Date:**
  Actual: 2026-05-18
  Nuevo: 2026-05-18
  Fuente: Contenido literal ADR
  Confianza: 100%

**Decision Type:**
  Actual: NULL
  Nuevo: INFRASTRUCTURE
  Fuente: ADR_INDEX.md (Digest SHA256)
  Confianza: 100%

**Scope:**
  Actual: server_monitoring_2509
  Nuevo: Infrastructure
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Tags:**
  Actual: NULL
  Nuevo: PENDIENTE
  Fuente: INSUFFICIENT EVIDENCE

**Related ADRs:**
  Actual: NULL
  Nuevo: ADR-0004
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Validation Reference:**
  Actual: NULL
  Nuevo: make validate-dockerfiles
  Fuente: ADR_INDEX.md
  Confianza: 100%

---

### ADR-0029: Structured Compose Policy Audit

**Status:**
  Actual: Aprobado
  Nuevo: APPROVED
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Date:**
  Actual: 2026-05-20
  Nuevo: 2026-05-20
  Fuente: Contenido literal ADR
  Confianza: 100%

**Decision Type:**
  Actual: NULL
  Nuevo: SECURITY
  Fuente: Contenido ADR (Hardening de auditoría)
  Confianza: 100%

**Scope:**
  Actual: server_monitoring_2509
  Nuevo: Infrastructure
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Tags:**
  Actual: NULL
  Nuevo: PENDIENTE
  Fuente: INSUFFICIENT EVIDENCE

**Related ADRs:**
  Actual: NULL
  Nuevo: ADR-0027
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Validation Reference:**
  Actual: NULL
  Nuevo: make test-policy-structured
  Fuente: ADR_INDEX.md
  Confianza: 100%

---

### ADR-0030: Auditoría Runtime HostConfig

**Status:**
  Actual: Aprobado
  Nuevo: APPROVED
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Date:**
  Actual: 2026-05-23
  Nuevo: 2026-05-23
  Fuente: Contenido literal ADR
  Confianza: 100%

**Decision Type:**
  Actual: NULL
  Nuevo: SECURITY
  Fuente: Contenido ADR (Visibilidad de Privilegios)
  Confianza: 100%

**Scope:**
  Actual: server_monitoring_2509
  Nuevo: Runtime
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Tags:**
  Actual: NULL
  Nuevo: PENDIENTE
  Fuente: INSUFFICIENT EVIDENCE

**Related ADRs:**
  Actual: NULL
  Nuevo: ADR-0020, ADR-0029
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Validation Reference:**
  Actual: NULL
  Nuevo: make audit-runtime
  Fuente: ADR_INDEX.md
  Confianza: 100%

---

### ADR-0031: Gobernanza Runtime + Dependencias Host

**Status:**
  Actual: Aprobado
  Nuevo: APPROVED
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Date:**
  Actual: 2026-05-26
  Nuevo: 2026-05-26
  Fuente: Contenido literal ADR
  Confianza: 100%

**Decision Type:**
  Actual: NULL
  Nuevo: GOVERNANCE
  Fuente: Título ADR
  Confianza: 100%

**Scope:**
  Actual: server_monitoring_2509
  Nuevo: Runtime
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Tags:**
  Actual: NULL
  Nuevo: PENDIENTE
  Fuente: INSUFFICIENT EVIDENCE

**Related ADRs:**
  Actual: NULL
  Nuevo: ADR-0030, ADR-0018, ADR-0029, ADR-0020, ADR-0024
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Validation Reference:**
  Actual: NULL
  Nuevo: make audit-runtime-ci
  Fuente: ADR_INDEX.md
  Confianza: 100%

---

### ADR-0032: Endurecimiento secretos PostgreSQL

**Status:**
  Actual: Aprobado
  Nuevo: APPROVED
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Date:**
  Actual: 2026-05-31
  Nuevo: 2026-05-31
  Fuente: Contenido literal ADR
  Confianza: 100%

**Decision Type:**
  Actual: NULL
  Nuevo: SECURITY
  Fuente: Título ADR (Endurecimiento secretos)
  Confianza: 100%

**Scope:**
  Actual: server_monitoring_2509
  Nuevo: Database
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Tags:**
  Actual: NULL
  Nuevo: PENDIENTE
  Fuente: INSUFFICIENT EVIDENCE

**Related ADRs:**
  Actual: NULL
  Nuevo: ADR-0013
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Validation Reference:**
  Actual: NULL
  Nuevo: make verify-security
  Fuente: ADR_INDEX.md
  Confianza: 100%

---

### ADR-0600: Estrategia despliegue microservicios

**Status:**
  Actual: ACCEPTED
  Nuevo: APPROVED
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Date:**
  Actual: NULL
  Nuevo: 2026-06-11
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Decision Type:**
  Actual: NULL
  Nuevo: ARCHITECTURE
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Scope:**
  Actual: NULL
  Nuevo: System
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Tags:**
  Actual: NULL
  Nuevo: PENDIENTE
  Fuente: INSUFFICIENT EVIDENCE

**Related ADRs:**
  Actual: NULL
  Nuevo: ADR-0601, ADR-0602, ADR-0603
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Validation Reference:**
  Actual: NULL
  Nuevo: NONE
  Fuente: ADR_INDEX.md
  Confianza: 100%

---

### ADR-0601: Desacoplamiento capas patrón Commons

**Status:**
  Actual: ACCEPTED
  Nuevo: APPROVED
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Date:**
  Actual: NULL
  Nuevo: 2026-06-11
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Decision Type:**
  Actual: NULL
  Nuevo: ARCHITECTURE
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Scope:**
  Actual: NULL
  Nuevo: System
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Tags:**
  Actual: NULL
  Nuevo: PENDIENTE
  Fuente: INSUFFICIENT EVIDENCE

**Related ADRs:**
  Actual: NULL
  Nuevo: ADR-0600, ADR-0602
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Validation Reference:**
  Actual: NULL
  Nuevo: NONE
  Fuente: ADR_INDEX.md
  Confianza: 100%

---

### ADR-0602: Comunicación inter-servicio REST

**Status:**
  Actual: NULL
  Nuevo: PROPOSED
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Date:**
  Actual: NULL
  Nuevo: 2026-06-11
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Decision Type:**
  Actual: NULL
  Nuevo: ARCHITECTURE
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Scope:**
  Actual: NULL
  Nuevo: System
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Tags:**
  Actual: NULL
  Nuevo: PENDIENTE
  Fuente: INSUFFICIENT EVIDENCE

**Related ADRs:**
  Actual: NULL
  Nuevo: ADR-0600, ADR-0801
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Validation Reference:**
  Actual: NULL
  Nuevo: NONE
  Fuente: ADR_INDEX.md
  Confianza: 100%

---

### ADR-0603: Gestión BBDD microservicios

**Status:**
  Actual: NULL
  Nuevo: PROPOSED
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Date:**
  Actual: NULL
  Nuevo: 2026-06-11
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Decision Type:**
  Actual: NULL
  Nuevo: DATA
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Scope:**
  Actual: NULL
  Nuevo: Database
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Tags:**
  Actual: NULL
  Nuevo: PENDIENTE
  Fuente: INSUFFICIENT EVIDENCE

**Related ADRs:**
  Actual: NULL
  Nuevo: ADR-0600
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Validation Reference:**
  Actual: NULL
  Nuevo: NONE
  Fuente: ADR_INDEX.md
  Confianza: 100%

---

### ADR-0801: Empaquetado despliegue Docker

**Status:**
  Actual: NULL
  Nuevo: PROPOSED
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Date:**
  Actual: NULL
  Nuevo: 2026-06-11
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Decision Type:**
  Actual: NULL
  Nuevo: INFRASTRUCTURE
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Scope:**
  Actual: NULL
  Nuevo: Infrastructure
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Tags:**
  Actual: NULL
  Nuevo: PENDIENTE
  Fuente: INSUFFICIENT EVIDENCE

**Related ADRs:**
  Actual: NULL
  Nuevo: ADR-0602, ADR-0802
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Validation Reference:**
  Actual: NULL
  Nuevo: NONE
  Fuente: ADR_INDEX.md
  Confianza: 100%

---

### ADR-0802: Integración frontend-backend

**Status:**
  Actual: NULL
  Nuevo: PROPOSED
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Date:**
  Actual: NULL
  Nuevo: 2026-06-11
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Decision Type:**
  Actual: NULL
  Nuevo: ARCHITECTURE
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Scope:**
  Actual: NULL
  Nuevo: System
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Tags:**
  Actual: NULL
  Nuevo: PENDIENTE
  Fuente: INSUFFICIENT EVIDENCE

**Related ADRs:**
  Actual: NULL
  Nuevo: ADR-0602, ADR-0801
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Validation Reference:**
  Actual: NULL
  Nuevo: NONE
  Fuente: ADR_INDEX.md
  Confianza: 100%

---

### ADR-0803: Seguridad + secretos microservicios

**Status:**
  Actual: NULL
  Nuevo: PROPOSED
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Date:**
  Actual: NULL
  Nuevo: 2026-06-11
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Decision Type:**
  Actual: NULL
  Nuevo: SECURITY
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Scope:**
  Actual: NULL
  Nuevo: Infrastructure
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Tags:**
  Actual: NULL
  Nuevo: PENDIENTE
  Fuente: INSUFFICIENT EVIDENCE

**Related ADRs:**
  Actual: NULL
  Nuevo: ADR-0600, ADR-0801
  Fuente: ADR_INDEX.md
  Confianza: 100%

**Validation Reference:**
  Actual: NULL
  Nuevo: NONE
  Fuente: ADR_INDEX.md
  Confianza: 100%

---

## Resumen Estadístico

| Clasificación | Cantidad |
| :--- | :--- |
| **COMPLIANT** | 0 |
| **PARTIALLY_COMPLIANT** | 9 |
| **NON_COMPLIANT** | 31 |
| **UNCLASSIFIED** | 0 |

*Nota: Todos los ADRs se clasifican actualmente como NON_COMPLIANT o PARTIALLY_COMPLIANT debido al uso de cabeceras en español y falta de campos obligatorios como Decision Type y Validation Reference. Ninguno cumple al 100% con el template oficial.*

---

## ADRs que requieren revisión humana

| ADR | Motivo |
| :--- | :--- |
| Todos | Definición de **Tags** finales (actualmente PENDIENTE). |
| ADR-0023 | Validación de secciones de Decisión y Consecuencias (incompletas en análisis previo). |
| ADR-0600..0803 | Verificación de integridad del cuerpo tras inyección masiva de cabeceras. |

---

## Cambios con confianza inferior al 100%

| Confianza | ADRs | Motivo |
| :--- | :--- | :--- |
| **100%** | Todos | La asignación de Status, Date, Scope y Type se basa en evidencia explícita del Índice o Título. |
| **<50%** | Tags | No hay evidencia explícita para etiquetas en la mayoría de los ADRs. |

---

## Plan de Ejecución por Fases

### Fase 1: Cambios con Confianza 100% (Metadatos Estructurales)
*   **Acción:** Normalizar cabeceras de ADR-0000 a ADR-0803.
*   **Campos:** Status, Date, Decision Type, Scope, Related ADRs, Validation Reference.
*   **Objetivo:** Alcanzar 100% de cumplimiento estructural (PARTIALLY_COMPLIANT con Tags pendientes).

### Fase 2: Sincronización de Referencias (Supersedes/Superseded By)
*   **Acción:** Validar y rellenar campos de superposición si se detectan durante la migración.
*   **Confianza:** 90-99% (requiere validación cruzada final).

### Fase 3: Revisión Humana Obligatoria (Clasificación Semántica)
*   **Acción:** Revisión y asignación de **Tags** aprobados.
*   **Acción:** Verificación de integridad de cuerpos en ADRs de la serie 0600 y 0800.
