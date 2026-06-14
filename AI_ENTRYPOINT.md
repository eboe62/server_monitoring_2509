# AI Entrypoint

## Purpose

This document is the primary entry point for AI assistants operating within this repository.

Before performing any analysis, review, recommendation, implementation, audit, ADR activity, hardening assessment, incident investigation, or documentation task, determine the task classification and load governance context proportionally.

The objective is:

* deterministic behaviour
* auditable decisions
* proportional context loading
* reduced governance noise
* scalable multi-agent operation

---

## Context Resolution & Path Constraints

### Strict Relative Resolution

AI assistants MUST NOT expect or attempt to access absolute OS filesystem paths.

Examples:

* `C:\Workspace\...`
* `/home/user/...`

All governance references, skills, templates, repository analysis, and implementation activities MUST use:

* relative repository paths
* workspace-relative references
* explicitly attached chat artifacts

### Path Alignment

Any absolute path provided by the user must be interpreted relative to the active repository root unless explicitly stated otherwise.

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
* task classification
* evidence requirements
* confidence requirements
* ADR authority
* response behaviour

No task may bypass Layer 1.

---

# LAYER 2 — TASK-SPECIFIC GOVERNANCE

After task classification, load only the governance required for the task.

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

Follow the incident workflow defined in:

* ai/governance/08_TASK_CLASSIFICATION.md

No dedicated incident governance layer is required.

---

## DOCUMENTATION

Load:

* ai/governance/05_ANALYSIS_PROTOCOL.md

Load additional governance only when required by scope.

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

Skills must be activated proportionally to the evidence and scope.

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

* ai/skills/infrastructure/devsecops_architect.md
* ai/skills/infrastructure/docker_hardening.md
* ai/skills/infrastructure/observability_reviewer.md
* ai/skills/infrastructure/resilience_and_rollback_reviewer.md
* ai/skills/infrastructure/runtime_auditor.md

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

Load only the minimum skill set required.

---

# Skill Activation Summary

This section summarizes the principles defined in:

* ai/governance/07_SKILL_ACTIVATION_MODEL.md

The existence of a skill does not imply mandatory activation.

Skills must be activated only when justified by:

* repository evidence
* architectural scope
* task objectives
* risk profile

The activation of one skill does not automatically require activation of any other skill.

Prefer evidence-based activation over blanket review chains.

---

# Proportionality Principle

Governance must be applied proportionally to the scope, risk, and impact of the task.

Avoid activating unnecessary:

* governance processes
* specialist skills
* review workflows
* architectural assessments

Low-impact changes typically require only directly relevant reviewers.

Examples:

* UI styling changes
* documentation updates
* formatting corrections
* comments

Medium-impact changes require affected domain reviewers.

Examples:

* dependency updates
* API contract modifications
* service configuration changes

High-impact changes require broader governance review.

Examples:

* architectural boundary changes
* infrastructure redesign
* security model modifications
* ADR proposals

Apply the minimum review set necessary to achieve reliable analysis.

Prefer proportional governance over maximum governance.

---

# Infrastructure Alignment

## Mandatory Protocol for Infrastructure Changes

Any modification affecting:

* Docker Compose configuration
* container execution model
* privileges, users, or capabilities
* network exposure or segmentation
* runtime security controls
* secret management

must comply with approved architectural decisions.

---

## Infrastructure ADR Compliance

Before proposing infrastructure changes:

* Validate applicable ADRs through:

  * ai/governance/14_ADR_INDEX.md
* Review the referenced approved ADRs.
* Verify that proposed changes remain compliant.

Do not duplicate ADR content in implementation proposals.

Use ADR_INDEX as the authoritative navigation source.

---

## DevSecOps Infrastructure Principles

Reference:

* ai/governance/02_DEVSECOPS_PRINCIPLES.md

Container principles:

* cap_drop: ALL by default
* no-new-privileges enabled
* non-root execution when feasible
* healthchecks enabled

Security principles:

* least privilege
* defence in depth
* progressive hardening
* runtime validation

Operational principles:

* stability over optimization
* monitoring before enforcement
* evidence before action
* verifiable reproducibility

---

## Infrastructure Skill Activation

Infrastructure changes may require activation of:

* devsecops_architect
* docker_hardening
* observability_reviewer
* resilience_and_rollback_reviewer
* backend_security_reviewer

Skill selection must remain evidence-based and scope-driven.

---

## Infrastructure Validation Gates

Before proposing infrastructure modifications verify:

Structural validation:

* explicit network assignment
* compliant port exposure
* explicit runtime user configuration
* capability reduction where applicable

Compliance validation:

* approved ADR compliance
* runtime classification compliance
* healthcheck consistency
* secret management compliance

Runtime validation:

* make test-security-runtime
* make verify-security
* make test-reproducibilidad

CI/CD validation:

* successful security validation
* successful reproducibility validation
* successful secret validation
* documentation updates where required

---

# Templates

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

# Current Authoritative Ledgers

The user may designate specific authoritative versions.

Do not automatically replace an authoritative ledger with a newer version unless explicitly instructed.

Historical ledgers remain authoritative records of:

* project state
* implementation history
* correction history
* operational context

Approved ADRs may supersede architectural decisions but do not invalidate historical records.

When inconsistencies exist:

* ADRs define current architectural authority.
* Ledgers preserve historical traceability.
* Divergences must be explicitly identified.

Examples:

* docs/Project_Implementation/Servidor_DigitalOcean_Implementacion.txt
* docs/Project_Definition/Servidor_DigitalOcean_Definicion_Proyecto.txt
* docs/Project_Corrections/Servidor_DigitalOcean_Correccion.txt

---

# Authoritative Project Documentation

The following sources are authoritative.

AI assistants must not assume that the newest file is authoritative.

If multiple versions exist and authority is unclear, request clarification.

## Architecture Decisions

* docs/decisiones/
* docs/Project_ADRs/

## Project Definition

* docs/Project_Definition/

## Project Implementation

* docs/Project_Implementation/

## Project Corrections

* docs/Project_Corrections/

## Tooling

* tooling inventories
* tooling registries

## Infrastructure

* infrastructure inventories
* infrastructure registries

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
9. Assumptions explicitly identified.
10. Repository language policy respected.

Mandatory requirements defined in:

* ai/governance/22_USER_PREFERENCES.md

must be applied unless explicitly overridden by the user.

These requirements apply to:

* analysis
* recommendations
* plans
* audits
* reviews
* ADR discussions
* implementation proposals
* governance explanations

---

# Operational Requirements

Mandatory rules:

* Every ADR must document a meaningful architectural decision.
* Separate analysis from execution.
* Analysis of conflicting proposals is permitted.
* Implementation requires compliance with approved ADRs.
* Never execute modifications during analysis.
* Require explicit approval before implementation.
* Respect approved ADRs.
* Respect repository boundaries.
* Respect declared scope.
* Prefer evidence over assumptions.
* Prefer validation over inference.

---

# Conflict Resolution

Authority and conflict resolution are governed by:

* ai/governance/13_AUTHORITY_HIERARCHY.md

When conflicts exist:

1. Determine authority.
2. Determine evidence.
3. Determine confidence.
4. Apply the governing source.

Do not reverse this sequence.

---

# Objective

Provide deterministic, auditable, evidence-based assistance aligned with the repository DevSecOps governance model while minimizing unnecessary context consumption and preserving governance scalability.
