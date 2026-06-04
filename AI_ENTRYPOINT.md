# AI_ENTRYPOINT.md

## Purpose

This document is the primary, mandatory entry point for all AI assistants operating within this repository.

Before performing any analysis, review, recommendation, or implementation task, the AI assistant must read and index the authoritative governance documents and specialized skills listed below to guarantee alignment with the project's single-node DevSecOps operational reality.

---

## Governance Documents

Read and enforce in the following strict order of priority:

1. ai/governance/AI_CONSTITUTION.md
2. ai/governance/DEVSECOPS_PRINCIPLES.md
3. ai/governance/ANALYSIS_PROTOCOL.md
4. ai/governance/EXECUTION_PROTOCOL.md
5. ai/governance/USER_PREFERENCES.md
6. ai/governance/PROMPTING_GUIDE.md

---

## Specialist Skills

Load and apply the relevant contextual skills according to the nature of the task:

* ai/skills/devsecops_architect.md
* ai/skills/runtime_auditor.md
* ai/skills/docker_hardening.md
* ai/skills/adr_reviewer.md
* ai/skills/observability_reviewer.md
* ai/skills/resilience_and_rollback_reviewer.md

---

## Templates

Utilize these standardized formats when producing repository assets or responses:

* ai/templates/repo_commit_message.md
* ai/templates/repo_pull_request.md
* ai/templates/request_adr_review.md
* ai/templates/request_analysis.md
* ai/templates/request_audit.md
* ai/templates/request_execution.md
* ai/templates/request_incident_review.md
* ai/templates/request_priority_analysis.md

---

## Authoritative Project Documentation

The following local files represent the absolute source of truth regarding the infrastructure and requirements:

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
* [Project specific tooling manifest file, e.g., tooling_*.txt]

### Infrastructure & Hardware Context
* [Project specific hardware configuration file, e.g., Configuracion_Equipo_*.txt]

---

## Operational Requirements

Mandatory rules for AI execution:

* Classify the target container under one of the 4 official typologies (SERVICE, SUPERVISOR, TOOLBOX, INFRA_TRUSTED) before emitting reviews.
* Separate analysis from execution. Never output deployment code or config modifications during analysis.
* Require explicit user approval before performing any implementation steps.
* Protect Host Plane (Plano 3) sovereignty. Never suggest exposing docker.sock or cross-plane container inspections.
* Respect approved ADRs, network boundaries, and the declared scope.
* Prefer live runtime evidence and active telemetry over design assumptions or inferences.

---

## Conflict Resolution

Priority hierarchy (Higher levels strictly override lower levels):

1. Explicit user instructions in the current prompt context
2. Approved ADRs (Architecture Decision Records)
3. AI Constitution (AI_CONSTITUTION.md)
4. Container Typology Rules
5. DevSecOps & SRE Principles (DEVSECOPS_PRINCIPLES.md)
6. Execution Protocol (EXECUTION_PROTOCOL.md)
7. User Preferences (USER_PREFERENCES.md)
8. Task-specific instructions

---

## Objective

Provide deterministic, auditable, highly structured, and evidence-based technical assistance aligned with the project's single-node DevSecOps governance model.
