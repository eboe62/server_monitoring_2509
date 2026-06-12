# AI Entrypoint

## Purpose

This document is the primary entry point for AI assistants operating within this repository.

Before performing any analysis, review, recommendation, or implementation task, read the authoritative governance documents listed below.

---

## Context Resolution & Path Constraints

* **Strict Relative Resolution:** AI assistants MUST NOT expect or attempt to access absolute OS filesystem paths (e.g., `C:\WorkSpace\...`). All internal governance references, skills, templates, and codebase analysis MUST be executed using relative workspace paths (`./`) or files explicitly attached to the active session via chat references (`#` or `@`).
* **Path Alignment:** Any absolute path mentioned in prompts or configurations must be automatically translated by the AI to its equivalent relative position within the active VS Code workspace root.

---

## Governance Documents

Read in the following order:

1. ai/governance/AI_CONSTITUTION.md
2. ai/governance/DEVSECOPS_PRINCIPLES.md
3. ai/governance/ANALYSIS_PROTOCOL.md
4. ai/governance/EXECUTION_PROTOCOL.md
5. ai/governance/USER_PREFERENCES.md
6. ai/governance/PROMPTING_GUIDE.md

---

## Specialist Skills

Load relevant skills according to the task:

* ai/skills/common/adr_author.md
* ai/skills/common/adr_reviewer.md
* ai/skills/common/architecture_reviewer.md
* ai/skills/common/dependency_governance_reviewer.md
* ai/skills/common/governance_reviewer.md
* ai/skills/common/quality_attribute_reviewer.md
* ai/skills/common/threat_model_reviewer.md
* ai/skills/infraestructure/devsecops_architect.md
* ai/skills/infraestructure/docker_hardening.md
* ai/skills/infraestructure/observability_reviewer.md
* ai/skills/infraestructure/resilience_and_rollback_reviewer.md
* ai/skills/infraestructure/runtime_auditor.md
* ai/skills/backend/api_gateway_reviewer.md
* ai/skills/backend/backend_security_reviewer.md
* ai/skills/backend/backend_testing_reviewer.md
* ai/skills/backend/jpa_reviewer.md
* ai/skills/backend/microservice_architect.md
* ai/skills/backend/spring_architect.md
* ai/skills/frontend/accessibility_reviewer.md
* ai/skills/frontend/api_client_reviewer.md
* ai/skills/frontend/composables_reviewer.md
* ai/skills/frontend/frontend_architect.md
* ai/skills/frontend/frontend_security_reviewer.md
* ai/skills/frontend/frontend_testing_reviewer.md
* ai/skills/frontend/quasar_architect.md
* ai/skills/frontend/state_management_reviewer.md
* ai/skills/frontend/vue_architect.md

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
- Configuracion_Equipo_2601.txt
- Servidor_DigitalOcean_Definicion_Proyecto.txt
- Servidor_DigitalOcean_Implementacion.txt
- Servidor_DigitalOcean_Correccion.txt

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
