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

Status:

PROPOSED

Meaning:

Draft ADR.

Not authoritative.

May be discussed.

May not govern implementation.

---

### ACCEPTED

Status:

ACCEPTED

Meaning:

Approved ADR.

Authoritative.

May govern architecture.

---

### SUPERSEDED

Status:

SUPERSEDED

Meaning:

Replaced by another ADR.

Historical reference only.

Not authoritative.

Must not be used as governing architecture.

---

### DEPRECATED

Status:

DEPRECATED

Meaning:

No longer recommended.

Historical reference only.

Not authoritative.

---

## ADR Registry

The following table must be maintained.

Columns:

* ADR ID
* Title
* Status
* Superseded By
* Scope
* Notes

Example:

| ADR | Title | Status | Superseded By | Scope | Notes |
|------|--------|--------|---------------|--------|--------|
| ADR-0001 | Example | ACCEPTED | - | Global | Active |
| ADR-0002 | Example | SUPERSEDED | ADR-0005 | Docker | Historical |

---

## Active ADRs

This section should contain all active ADRs.

Only ADRs listed here are considered authoritative.

Format:

ADR-XXXX
Title:
Status: ACCEPTED
Scope:
Dependencies:
Related ADRs:

---

## Superseded ADRs

This section should contain all superseded ADRs.

Format:

ADR-XXXX
Superseded By:
Reason:

---

## Deprecated ADRs

This section should contain all deprecated ADRs.

Format:

ADR-XXXX
Reason:

---

## ADR Dependencies

When ADRs depend on other ADRs, relationships should be recorded.

Example:

ADR-0032

Depends On:

ADR-0018

Related:

ADR-0020

---

## ADR Conflict Resolution

If two ADRs appear to conflict:

1. Check ADR_INDEX.md
2. Verify status
3. Verify supersession chain
4. Activate Governance Arbiter if required

Do not assume newer ADRs automatically override older ADRs.

---

## ADR Authority Rules

Only ADRs with:

Status: ACCEPTED

are authoritative.

PROPOSED ADRs:

Not authoritative.

SUPERSEDED ADRs:

Not authoritative.

DEPRECATED ADRs:

Not authoritative.

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

Every ADR creation must update:

ADR_INDEX.md

Every ADR supersession must update:

ADR_INDEX.md

Every ADR deprecation must update:

ADR_INDEX.md

ADR changes are incomplete until ADR_INDEX.md is updated.

---

## Final Principle

The ADR repository contains architectural history.

ADR_INDEX.md identifies architectural authority.
