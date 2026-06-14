# AI Entrypoint

## Purpose

This document is the primary entry point for AI assistants operating within this repository.

Before performing any analysis, review, recommendation, or implementation task, read the authoritative governance documents listed below.

---

## Context Resolution & Path Constraints

* **Strict Relative Resolution:** AI assistants MUST NOT expect or attempt to access absolute OS filesystem paths (e.g., `C:\WorkSpace\...`). All internal governance references, skills, templates, and codebase analysis MUST be executed using relative workspace paths (`./`) or files explicitly attached to the active session via chat references (`#` or `@`).
* **Path Alignment:** Any absolute path provided by the user must be interpreted relative to the active repository root.

---

# LAYER 1 — MANDATORY CORE GOVERNANCE

These documents MUST always be loaded.

Read in the following order:

1. ai/governance/01_AI_CONSTITUTION.md
2. ai/governance/02_DEVSECOPS_PRINCIPLES.md
3. ai/governance/08_TASK_CLASSIFICATION.md
4. ai/governance/10_EVIDENCE_MODEL.md
5. ai/governance/11_CONFIDENCE_MODEL.md
6. ai/governance/13_AUTHORITY_HIERARCHY.md
7. ai/governance/14_ADR_INDEX.md
8. ai/governance/22_USER_PREFERENCES.md

These documents define:

* authority
* task type
* evidence
* confidence
* ADR authority
* response behaviour

No task may bypass Layer 1.

---

# LAYER 2 — TASK-SPECIFIC GOVERNANCE

After task classification, load only the governance required for that task.

---

## ANALYSIS

Load:

* ai/governance/04_ARCHITECTURE_GUIDELINES.md
* ai/governance/05_ANALYSIS_PROTOCOL.md
* ai/governance/07_SKILL_ACTIVATION_MODEL.md

---

## AUDIT

Load:

* ai/governance/05_ANALYSIS_PROTOCOL.md
* ai/governance/07_SKILL_ACTIVATION_MODEL.md
* ai/governance/16_SKILL_REGISTRY.md

---

## EXECUTION

Load:

* ai/governance/05_ANALYSIS_PROTOCOL.md
* ai/governance/07_SKILL_ACTIVATION_MODEL.md
* ai/governance/20_EXECUTION_PROTOCOL.md
* ai/governance/16_SKILL_REGISTRY.md

---

## ADR

Load:

* ai/governance/04_ARCHITECTURE_GUIDELINES.md
* ai/governance/05_ANALYSIS_PROTOCOL.md
* ai/governance/16_SKILL_REGISTRY.md
* ai/governance/17_SKILL_LIFECYCLE.md

---

## HARDENING

Load:

* ai/governance/05_ANALYSIS_PROTOCOL.md
* ai/governance/07_SKILL_ACTIVATION_MODEL.md
* ai/governance/16_SKILL_REGISTRY.md

Mandatory principles:

* Stability over hardening
* Evidence before action
* Validation before enforcement

---

## INCIDENT

Load:

* ai/governance/05_ANALYSIS_PROTOCOL.md
* ai/governance/07_SKILL_ACTIVATION_MODEL.md

Follow TASK_CLASSIFICATION incident workflow.

No dedicated incident governance layer is required.

---

## DOCUMENTATION

Load:

* ai/governance/05_ANALYSIS_PROTOCOL.md

Only load additional governance if required by scope.

---

# LAYER 3 — GOVERNANCE EXTENSIONS

Load only when required.

---

## Governance Extensions

Potential governance extensions:

* ai/governance/17_SKILL_LIFECYCLE.md
* ai/governance/19_AI_DECISION_REGISTRY.md

Load only when the task explicitly affects:

* skill creation
* skill modification
* skill retirement
* governance lifecycle
* AI decision traceability

Do not load by default.

---

# LAYER 4 — SPECIALIST SKILLS

Load only the skills required by:

* task type
* repository scope
* affected components

Never load all skills.

Skills must be activated proportionally.

---

## Common Skills

Potentially relevant:

* ai/skills/common/adr_author.md
* ai/skills/common/adr_reviewer.md
* ai/skills/common/architecture_reviewer.md
* ai/skills/common/dependency_governance_reviewer.md
* ai/skills/common/governance_arbiter.md
* ai/skills/common/governance_reviewer.md
* ai/skills/common/quality_attribute_reviewer.md
* ai/skills/common/threat_model_reviewer.md

---

## Infrastructure Skills

Potentially relevant:

* ai/skills/infraestructure/devsecops_architect.md
* ai/skills/infraestructure/docker_hardening.md
* ai/skills/infraestructure/observability_reviewer.md
* ai/skills/infraestructure/resilience_and_rollback_reviewer.md
* ai/skills/infraestructure/runtime_auditor.md

---

## Backend Skills

Potentially relevant:

* ai/skills/backend/api_gateway_reviewer.md
* ai/skills/backend/backend_security_reviewer.md
* ai/skills/backend/backend_testing_reviewer.md
* ai/skills/backend/jpa_reviewer.md
* ai/skills/backend/microservice_architect.md
* ai/skills/backend/spring_architect.md

---

## Frontend Skills

Potentially relevant:

* ai/skills/frontend/accessibility_reviewer.md
* ai/skills/frontend/api_client_reviewer.md
* ai/skills/frontend/frontend_security_reviewer.md
* ai/skills/frontend/quasar_reviewer.md
* ai/skills/frontend/state_management_reviewer.md

Load only the minimum set required.

---

# Authoritative Project Documentation

Authoritative project sources include:

* docs/Project_Definition/
* docs/Project_Implementation/
* docs/Project_Corrections/
* docs/Project_ADRs/
* docs/decisiones/

Approved ADRs remain normative and binding.

ADR status must be validated through:

ai/governance/14_ADR_INDEX.md

before architectural conclusions are produced.

---

# Response Generation Requirements

Before generating a final response verify:

1. Task classification determined.
2. Authority hierarchy applied.
3. ADR status validated.
4. Evidence model applied.
5. Confidence model applied.
6. Relevant skills activated.
7. Analysis and execution separated.
8. User preferences respected.

---

# Conflict Resolution

Priority order:

1. Explicit User Instructions
2. Approved ADRs
3. AI Constitution
4. Core Governance
5. Active Specialist Skills
6. Execution Protocol
7. User Preferences
8. Task-Specific Instructions

When conflicts exist:

* determine authority first
* determine evidence second
* determine confidence third

Do not invert this order.

---

# Objective

Provide deterministic, auditable, evidence-based assistance aligned with the repository DevSecOps governance model while minimizing unnecessary context consumption.

---

## Skill Activation Model

Skills are independent review filters.

The activation of one skill does not imply the activation of any other skill.

Skills must only be activated when they are directly relevant to:

* repository evidence
* architectural scope
* requested task

AI assistants must not assume a mandatory review chain unless explicitly defined by the user.

Example:

A frontend styling change does not require backend, infrastructure, threat modeling, or quality attribute reviews unless repository evidence demonstrates relevance.

Skill activation must always be evidence-based and scope-driven.

---

## Skill Selection Principle

Skills are not mandatory by default.

The existence of a skill does not imply that the skill must participate in every analysis.

AI assistants must justify skill activation based on:

* evidence
* risk profile
* affected architectural boundaries
* task objectives

Unnecessary reviewer activation should be avoided.

---

## Proportionality Principle

Governance must be applied proportionally to the scope, risk, and impact of the task.

AI assistants must avoid activating unnecessary governance processes, specialist skills, review workflows, or architectural analysis when repository evidence demonstrates that the change is local, isolated, or low-risk.

Examples:

Low-impact changes:

* UI styling adjustments
* text corrections
* documentation updates
* comments
* formatting changes

These changes normally require only directly relevant skills.

Medium-impact changes:

* service configuration changes
* API contract modifications
* dependency updates

These require activation of affected domain reviewers.

High-impact changes:

* architectural boundary changes
* security model modifications
* infrastructure redesign
* ADR proposals

These require broader governance review.

The existence of a governance skill does not imply mandatory activation.

Apply the minimum review set necessary to achieve reliable analysis.

Prefer proportional governance over maximum governance.

---

## Templates

Use templates when appropriate:

* ai/templates/repo_commit_message.md
* ai/templates/repo_pull_request.md
* ai/templates/request_adr_review.md
* ai/templates/request_analysis.md
* ai/templates/request_audit.md
* ai/templates/request_execution.md
* ai/templates/request_incident_review.md
* ai/templates/request_priority_analysis.md

---

## Alineación de Infraestructura

### Protocolo Obligatorio para Cambios de Infraestructura

Toda modificación que afecte:

* Configuración Docker Compose
* Modelo de ejecución de contenedores (privilegios, usuarios, capacidades)
* Segmentación o exposición de redes
* Requisitos de seguridad en runtime
* Gestión de secretos

**Debe cumplir obligatoriamente** con las decisiones arquitectónicas aprobadas listadas a continuación.

---

### ADRs Aprobados — Seguridad Infraestructura

1. **ADR-0014 — Docker Port Exposure Policy**
   - `docs/decisiones/ADR-0014-docker_port_exposure_policy.md`
   - **Regla:** Puerto restringido a loopback (`127.0.0.1:port`) o red interna Docker
   - **Prohibido:** Publicación global (`port:port` sin restricción de interfaz)
   - **Justificación:** Reducción de superficie de ataque, coherencia IaC

2. **ADR-0018 — Docker Security Runtime & Resilience Requirements**
   - `docs/decisiones/ADR-0018-docker_security_runtime_and_resilience_requirements.md`
   - **Regla:** `cap_drop: ALL` por defecto
   - **Regla:** Usuario no-root en runtime-stacks
   - **Prohibido:** `docker.sock` sin justificación ADR explícita
   - **Validación:** `make test-security-runtime`

3. **ADR-0020 — Container Execution Model & Privilege Strategy**
   - `docs/decisiones/ADR-0020-Container_Execution_Model_Privilege_Strategy.md`
   - **Clasificación:** runtime-stacks, service-stacks, operational-stacks
   - **Regla:** Separación clara por propósito funcional
   - **Regla:** Sin bind mounts de código en producción
   - **Validación:** `make test-reproducibilidad`

4. **ADR-0021 — Network Segmentation Strategy**
   - `docs/decisiones/ADR-0021-Network_Segmentation_Strategy.md`
   - **Redes aprobadas:** `backend-net`, `observability-net`, `restricted-net`, `edge-net` (opcional)
   - **Prohibido:** Red global única (`monitoring-net`)
   - **Regla:** Principio de mínimo acceso por red
   - **Justificación:** Aislamiento de dominios funcionales, reducción de movimiento lateral

5. **ADR-0027 — Container Typology & Healthchecks Policy**
   - `docs/decisiones/ADR-0027-tipologia_contenedores_politica_healthchecks.md`
   - **Tipología:** SERVICE_RUNTIME, SUPERVISOR_RUNTIME, TOOLBOX_RUNTIME, INFRA_TRUSTED
   - **Regla:** Clasificación explícita en `ops/runtime_containers.yml`
   - **Regla:** Healthchecks semánticamente coherentes con propósito del contenedor
   - **Fuente única de verdad:** `ops/runtime_containers.yml`

6. **ADR-0032 — PostgreSQL Secrets Hardening & CI Validation**
   - `docs/decisiones/ADR-0032-endurecimiento_secretos_PostgreSQL_y_validaciones_CI.md`
   - **Regla:** `POSTGRES_PASSWORD_FILE=/run/secrets/postgres_password`
   - **Prohibido:** Secretos hardcodeados en `.env` o archivos versionados
   - **Validación:** `ops/services/postgres/scripts/check_postgres_secret.sh`
   - **Validación CI:** `make verify-security`

---

### Principios Rectores — DevSecOps Infrastructure

Referencia: `ai/governance/DEVSECOPS_PRINCIPLES.md`

**Container Principles:**
* `cap_drop: ALL` por defecto
* `no-new-privileges` habilitado
* Usuario no-root cuando sea viable
* Healthchecks habilitados

**Security Principles:**
* Principio de mínimo privilegio
* Defensa en profundidad
* Hardening progresivo
* Validación en runtime

**Operations Principles:**
* Estabilidad sobre optimización
* Monitoreo antes de enforcement
* Evidencia antes de acción
* Reproducibilidad verificable

---

### Modelo de Activación de Skills — Tareas Infraestructurales

Los cambios infraestructurales requieren activación proporcional de skills especialistas:

**Cuando la tarea implique:**

* Modelo de ejecución, privilegios o usuarios de contenedores → Activar: **devsecops_architect**
* Seguridad Docker, hardening o validación de runtime → Activar: **docker_hardening**
* Exposición de puertos o cambios de red → Activar: **devsecops_architect**
* Secretos, credenciales o cumplimiento regulatorio → Activar: **backend_security_reviewer** + **devsecops_architect**
* Integración de observabilidad (logs, métricas, healthchecks) → Activar: **observability_reviewer**
* Resiliencia, retry logic o escenarios de fallo → Activar: **resilience_and_rollback_reviewer**

**Activación interdependiente de skills:**

Si ADR-0014 (exposición de puertos) es afectado → También activar validación ADR-0021 (segmentación de red).

Si ADR-0020 (modelo de privilegios) es afectado → También validar cumplimiento ADR-0018 (seguridad runtime).

---

### Gates de Validación — Cambios Infraestructurales

Antes de proponer modificaciones infraestructurales, verificar obligatoriamente:

**Validación Estructural:**

* ✓ Todos los servicios docker-compose tienen asignación explícita de red
* ✓ Sin uso de red por defecto (`monitoring-net` eliminada)
* ✓ Declaraciones de puerto siguen regla de vinculación a loopback (si es necesario)
* ✓ Usuario/UID declarado explícitamente en runtime-stacks
* ✓ Capacidades explícitamente droppadas (`cap_drop: ALL`)

**Validación de Cumplimiento:**

* ✓ Cambios respetan todos los ADRs referenciados (estado = Aprobado)
* ✓ Clasificación de contenedor en `ops/runtime_containers.yml` es explícita
* ✓ Semántica de healthcheck coincide con tipología de contenedor
* ✓ Gestión de secretos sigue estándar ADR-0032

**Validación de Seguridad Runtime (Makefile):**

```
make test-security-runtime       # Verifica usuario, exposición, docker.sock
make verify-security             # Validación de secretos PostgreSQL
make test-reproducibilidad       # Validación de independencia del host
```

**Gate CI/CD:**

Todo cambio infraestructural requiere:

* Validación exitosa: `make test-security-runtime`
* Validación exitosa: `make verify-security`
* Validación exitosa: `make test-reproducibilidad`
* Actualización documentación en ADR relevante o README

---

### Language & Documentation

Toda documentación de gobernanza infraestructural:

* Sigue política de idioma español (coherente con `DEVSECOPS_PRINCIPLES.md`, ADRs)
* Utiliza terminología consistente de ADRs aprobados
* Debe ser auditable y referenceable
* Referencias a rutas deben ser relativas (`./` o `docs/decisiones/`)

---

## Current Authoritative Ledgers

The user may designate specific authoritative versions.

Unless explicitly superseded, do not automatically replace an authoritative ledger with a newer version.

Historical ledgers remain authoritative records of project state, implementation history, corrections, and operational context.

Approved ADRs may supersede architectural decisions, but they do not invalidate historical ledgers.

When inconsistencies exist between ADRs and historical ledgers:

* ADRs define current architectural authority.
* Ledgers preserve historical project traceability.
* AI assistants must explicitly identify the divergence.

Examples:
.docs/Project_Implementation/Servidor_DigitalOcean_Implementacion.txt
.docs/Project_Definition/Servidor_DigitalOcean_Definicion_Proyecto.txt
.docs/Project_Corrections/Servidor_DigitalOcean_Correccion.txt

## Authoritative Project Documentation

The following documents are the authoritative project sources.
AI must not assume that the most recent file is authoritative.
When multiple versions exist, the user must explicitly identify the authoritative version, or the AI must request clarification before proceeding.

### Architecture Decisions

* docs/decisiones/
* docs/Project_ADRs/

### Project Definition

* docs/Project_Definition/

### Project Implementation

* docs/Project_Implementation/

### Project Corrections

* docs/Project_Corrections/

### Tooling

* Active tooling inventory documentation (e.g., `tooling_*.txt` or equivalent project tooling registry)

### Infrastructure

* Active infrastructure inventory documentation (e.g., `Configuracion_Equipo_*.txt` or equivalent infrastructure registry)

---

## Response Generation Requirements

Before generating the final response, AI assistants must verify that:

1. Repository language policy has been applied.
2. USER_PREFERENCES.md response formatting requirements have been applied.
3. Governance hierarchy has been applied.
4. Relevant skills have been selected according to the Skill Activation Model.
5. Evidence requirements have been respected.
6. Assumptions are explicitly identified.
7. Analysis and execution phases remain separated.

Mandatory response requirements defined in USER_PREFERENCES.md must be applied unless explicitly overridden by the user.

Examples:

* If USER_PREFERENCES.md requires responses to begin with a timestamp, the timestamp must be included.
* If USER_PREFERENCES.md defines a preferred language, responses must use that language unless the user explicitly requests another.
* If USER_PREFERENCES.md defines uncertainty handling requirements, they must be applied consistently.

Response generation requirements apply to:

* analysis
* recommendations
* plans
* reviews
* ADR discussions
* implementation proposals
* governance explanations

## Operational Requirements

Mandatory rules:

* **Architectural Precision:** Every proposed ADR must document a real, non-trivial structural design decision, boundary restriction, or topological pattern specific to the project. Generic framework setup, language versioning bump, linting rules, or standard library updates MUST NOT be generated as ADRs.
* Separate analysis from execution.
* Analysis of proposals that conflict with current governance remains permitted.
* Implementation of such proposals requires the governance changes defined by approved ADRs.
* Never execute modifications during analysis.
* Require explicit approval before implementation.
* Respect approved ADRs.
* Respect repository boundaries.
* Respect declared scope.
* Prefer evidence over assumptions.
* Prefer validation over inference.
* Response formatting requirements defined in USER_PREFERENCES.md are mandatory unless explicitly overridden by the user.

---

## Conflict Resolution

Priority order (Strict Downward Enforcement):

1. Explicit user instructions
2. Approved ADRs
3. AI Constitution & DevSecOps Principles
4. Specialist Skills Constraints (Technical and security restrictions from loaded skills act as non-negotiable filters over lower levels)
5. Execution Protocol
6. User Preferences
7. Task-specific instructions

Lower-priority documents must never contradict or bypass higher-priority documents or Specialist Skills restrictions.

---

## Objective

Provide deterministic, auditable, evidence-based assistance aligned with the project's DevSecOps governance model.
