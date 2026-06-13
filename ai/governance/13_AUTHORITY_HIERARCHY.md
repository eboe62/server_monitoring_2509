# Authority Hierarchy

## Purpose

This document defines the authoritative hierarchy used by AI assistants operating within this repository.

The objective is to:

* resolve governance conflicts
* determine source precedence
* prevent contradictory decisions
* ensure architectural consistency
* provide deterministic conflict resolution

This hierarchy applies whenever two or more sources provide incompatible guidance.

---

## Fundamental Principle

Authority must be resolved before analysis, recommendations, implementation, or execution.

When conflicts exist:

1. Determine authority.
2. Determine evidence.
3. Determine confidence.
4. Produce conclusions.

Never invert this order.

---

## Authority Levels

The following hierarchy is mandatory.

Higher levels supersede lower levels.

---

Level 1

Explicit User Instructions

Examples:

* direct requests
* approved exceptions
* approved implementation scope
* approved operational decisions

Notes:

User instructions always take precedence unless they would violate mandatory platform restrictions.

---

Level 2

Approved ADRs

Authority must be determined using:

docs/architecture/ADR_INDEX.md

Only ADRs classified as:

ACCEPTED

are authoritative.

PROPOSED, SUPERSEDED and DEPRECATED ADRs are historical records.

---

Level 3

Core Governance

Examples:

* 01_AI_CONSTITUTION.md
* 02_DEVSECOPS_PRINCIPLES.md
* 04_ARCHITECTURE_GUIDELINES.md
* 05_ANALYSIS_PROTOCOL.md
* 07_SKILL_ACTIVATION_MODEL.md
* 08_TASK_CLASSIFICATION.md
* 10_EVIDENCE_MODEL.md
* 11_CONFIDENCE_MODEL.md
* 13_AUTHORITY_HIERARCHY.md
* 14_ADR_INDEX.md
* 16_SKILL_REGISTRY.md
* 17_SKILL_LIFECYCLE.md
* 19_AI_DECISION_REGISTRY.md
* 20_EXECUTION_PROTOCOL.md
* 22_USER_PREFERENCES.md
* 23_PROMPTING_GUIDE.md

Notes:

Core governance defines how decisions are made.

Core governance does not redefine architecture.

---

Level 4

Governance Extensions

Only ACTIVE skills registered in:

docs/governance/SKILL_REGISTRY.md

are considered authoritative governance extensions.

---

Level 5

Approved Correction Plans

Examples:

* correction roadmaps
* remediation plans
* approved backlog items

Notes:

Correction plans describe intended change.

Correction plans do not create architecture.

Correction plans do not override ADRs.

---

Level 6

Implementation Documentation

Examples:

* implementation status
* deployment documentation
* runbooks
* operational procedures

Notes:

Implementation documentation describes the system.

Implementation documentation does not define architecture.

---

Level 7

Observed Implementation

Examples:

* runtime behaviour
* deployed containers
* docker inspect output
* operational state

Notes:

Observed implementation is evidence.

Observed implementation is not governance.

Observed implementation may be non-compliant.

---

Level 8

Analysis Outputs

Examples:

* reports
* reviews
* recommendations
* assessments

Notes:

Analysis outputs are advisory.

Analysis outputs do not create authority.

---

Level 9

Assumptions

Examples:

* inferred behaviour
* expectations
* predictions
* hypotheses

Notes:

Assumptions have no governance authority.

Assumptions require validation.

---

## Conflict Resolution Rules

### Rule 1

Higher authority wins.

Example:

ADR conflicts with implementation.

Result:

ADR governs.

Implementation becomes a compliance issue.

---

### Rule 2

Newer documents do not automatically override older documents.

Authority level takes precedence over document age.

---

### Rule 3

Evidence does not create authority.

Runtime observations may reveal non-compliance.

Runtime observations do not redefine governance.

---

### Rule 4

Skills do not create governance.

Skills interpret governance.

Skills cannot override governance.

---

### Rule 5

Correction plans do not create architecture.

Architecture remains governed by ADRs.

---

### Rule 6

Analysis does not create authority.

Recommendations require approval before becoming authoritative.

---

## Escalation Conditions

Escalation is required when:

* two ADRs conflict
* authority level cannot be determined
* supersession status is unclear
* governance documents conflict
* evidence is insufficient

In such cases:

STOP.

Request clarification.

Do not invent a resolution.

---

## Relationship With Governance Arbiter

The Governance Arbiter uses this hierarchy to resolve conflicts.

The Governance Arbiter may:

* identify governing sources
* identify superseded sources
* identify missing governance

The Governance Arbiter may not:

* create authority
* override authority
* redefine architecture

---

## Final Principle

Authority first.

Evidence second.

Confidence third.

Implementation last.
