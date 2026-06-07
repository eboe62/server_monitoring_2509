# AI Entrypoint

## Purpose

This document is the primary entry point for AI assistants operating within this repository.

Before performing any analysis, review, recommendation, or implementation task, read the authoritative governance documents listed below.

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

* ai/skills/devsecops_architect.md
* ai/skills/runtime_auditor.md
* ai/skills/docker_hardening.md
* ai/skills/adr_reviewer.md
* ai/skills/observability_reviewer.md

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

## Authoritative Project Documentation

The following documents are the authoritative project sources. (Note: AI must dynamically query the repository to use the most recent active version matching these patterns if multiple versions exist).

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

## Operational Requirements

Mandatory rules:

* Separate analysis from execution.
* Never execute modifications during analysis.
* Require explicit approval before implementation.
* Respect approved ADRs.
* Respect repository boundaries.
* Respect declared scope.
* Prefer evidence over assumptions.
* Prefer validation over inference.

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
