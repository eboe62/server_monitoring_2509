# Skill Activation Model

## Purpose

This document defines how AI assistants must select, activate, and coordinate specialist skills during repository analysis and execution activities.

The objective is to ensure:

* consistent governance enforcement
* proportional review depth
* evidence-based reviewer selection
* avoidance of unnecessary review overhead

This document is normative.

---

## Relationship with Governance Hierarchy

This document does not override:

* Explicit User Instructions
* Approved ADRs
* AI Constitution
* DevSecOps Principles

Skill activation decisions must always respect the repository governance hierarchy.

---

## Core Principle

Skills are independent review filters.

A skill exists to provide specialized analysis within a defined domain.

The existence of a skill does not imply that the skill must participate in every task.

Skill activation must always be:

* evidence-based
* scope-driven
* risk-aware
* context-dependent

---

## Independence Rule

Skills do not form a fixed execution pipeline.

The activation of one skill does not imply the activation of any other skill.

Examples:

* A frontend styling change may not require backend review.
* A documentation update may not require security review.
* A Docker runtime modification may not require frontend review.

AI assistants must not invent mandatory reviewer chains unless explicitly defined by repository governance or user instructions.

---

## Skill Selection Criteria

AI assistants should activate skills based on:

### Scope

Which repository areas are affected?

Examples:

* infrastructure
* backend
* frontend
* governance
* architecture
* documentation

### Risk

What is the operational impact?

Examples:

* low-risk documentation change
* security-sensitive modification
* production runtime change
* architectural redesign

### Evidence

What evidence demonstrates skill relevance?

Examples:

* affected files
* runtime findings
* ADR references
* architectural boundaries

User-declared scope is valid evidence for determining review proportionality.

When a user explicitly states that a change is limited to:

- documentation
- comments
- formatting
- typo corrections
- naming cleanup

the AI may classify governance requirements according to that declared scope unless repository evidence demonstrates a broader impact.

The absence of repository inspection does not automatically force an Unknown classification when the requested change scope is explicit and unambiguous.

### Objectives

What is the user attempting to achieve?

Examples:

* implementation
* review
* audit
* hardening
* troubleshooting
* architectural assessment

---

## Minimal Activation Principle

Activate only the skills necessary to perform a complete and reliable review.

Avoid activating reviewers that do not contribute meaningful analysis.

Unnecessary reviewer activation increases complexity and may introduce noise.

---

## Cross-Domain Reviews

Multiple skills may participate when a task spans multiple domains.

Examples:

### Infrastructure + Security

* devsecops_architect
* docker_hardening

### Architecture + Quality

* architecture_reviewer
* quality_attribute_reviewer

### Architecture + Threat Analysis

* architecture_reviewer
* threat_model_reviewer

### Backend + Security

* backend_security_reviewer
* microservice_architect

The AI assistant must justify why multiple skills are relevant.

---

## Skill Conflict Resolution

Skills are advisory governance filters.

Skills do not possess independent authority.

When reviewer conclusions appear to conflict:

1. Verify repository evidence.
2. Verify active ADRs.
3. Apply governance hierarchy.
4. Explicitly identify the conflict.
5. Request clarification if required.

Conflict resolution authority remains with:

* Explicit User Instructions
* Approved ADRs
* Repository Governance

---

## Architectural Reviews

Architectural reviews may require participation from multiple reviewers.

However:

No reviewer has automatic precedence over another reviewer.

Examples:

* architecture_reviewer
* quality_attribute_reviewer
* threat_model_reviewer
* governance_reviewer

must be selected based on relevance, not by default.

---

## Paradigm Change Assessments

When a proposal challenges established repository architecture, additional reviewers may become relevant.

Examples:

* Docker Compose to Kubernetes
* Single-node to multi-node
* Monolith to microservices
* Local execution to managed cloud services

Such situations may require broader architectural review.

However, reviewer activation remains evidence-based and context-dependent.

---

## Analysis Phase Behaviour

During analysis:

* identify relevant skills
* justify activation decisions
* document assumptions
* identify evidence gaps

Do not activate skills merely to increase review volume.

---

## Execution Phase Behaviour

During execution:

* apply only the reviews relevant to the approved scope
* avoid expanding reviewer participation without justification
* preserve scope boundaries

Skill activation must not be used to justify scope expansion.

---

## Validation Requirements

AI assistants should be able to explain:

* why a skill was activated
* why a skill was not activated
* what evidence justified the decision
* how the selected skills relate to the requested task

Reviewer selection must remain transparent and traceable.

---

## Expected Outcome

The repository should benefit from:

* proportional reviews
* consistent governance enforcement
* reduced review noise
* better architectural focus
* evidence-driven decision making

The goal is not maximum reviewer participation.

The goal is appropriate reviewer participation.
