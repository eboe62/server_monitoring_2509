# Skill Registry

## Purpose

This document is the authoritative registry of all AI skills used within this repository.

The objective is to:

* identify active skills
* identify deprecated skills
* identify superseded skills
* identify skill ownership
* identify governance dependencies
* improve traceability
* improve maintainability

All skills must be registered.

Unregistered skills are not authoritative.

---

## Fundamental Principles

Skills support governance.

Skills do not create governance.

Skills must remain aligned with:

* ADRs
* Core Governance
* Authority Hierarchy

Skills may become obsolete.

Skills require lifecycle management.

---

## Skill Lifecycle

A skill may be:

PROPOSED

ACTIVE

DEPRECATED

SUPERSEDED

ARCHIVED

Only ACTIVE skills should be used.

---

## Status Definitions

### PROPOSED

Draft skill.

Under review.

Not authoritative.

---

### ACTIVE

Approved skill.

May be used.

Governance compliant.

---

### DEPRECATED

Still functional.

Scheduled for removal.

Use discouraged.

---

### SUPERSEDED

Replaced by another skill.

Historical only.

Do not use.

---

### ARCHIVED

Retained only for historical traceability.

Do not use.

---

## Skill Registry Table

The following registry must be maintained.

Columns:

* Skill Name
* Status
* Owner
* Version
* Last Review
* Superseded By
* ADR Dependencies

Example:

| Skill | Status | Owner | Version | Last Review | Superseded By | ADR Dependencies |
|--------|--------|--------|--------|--------|--------|--------|
| governance_reviewer | ACTIVE | Architecture | 1.0 | 2026-06-01 | - | ADR-0018 |
| old_skill | SUPERSEDED | Architecture | 1.0 | 2026-01-01 | new_skill | ADR-0007 |

---

## Active Skills

This section contains all active skills.

Only active skills are considered governance-compliant.

Format:

Skill:
Status:
Owner:
Version:
Last Review:
ADR Dependencies:
Related Skills:

---

## Deprecated Skills

Format:

Skill:
Reason:
Replacement:

---

## Superseded Skills

Format:

Skill:
Superseded By:
Reason:

---

## Archived Skills

Format:

Skill:
Archive Date:
Reason:

---

## Governance Rule

Every skill must appear in this registry.

Missing skills are considered:

UNREGISTERED

Unregistered skills are not authoritative.

---

## Review Rule

Every active skill must have:

* owner
* version
* last review date
* ADR dependency list

Missing metadata indicates governance drift.

---

## ADR Dependency Rule

Skills must identify:

* governing ADRs
* governance dependencies

If a governing ADR changes:

Skill review becomes mandatory.

---

## AI Governance Rule

AI assistants should consult:

SKILL_REGISTRY.md

before:

* creating new skills
* modifying skills
* retiring skills
* evaluating skill authority

---

## Final Principle

Skills require governance.

Governance requires traceability.
