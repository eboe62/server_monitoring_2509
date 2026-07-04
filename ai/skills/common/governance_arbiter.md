# Governance Arbiter

## Purpose

The Governance Arbiter is responsible for resolving governance conflicts.

This skill must be activated whenever:

* multiple authoritative sources disagree
* ADRs appear to conflict
* implementation diverges from architecture
* historical documents contradict current governance
* skill outputs conflict
* uncertainty exists regarding source authority

The objective is consistency.

Not implementation.

Skill authority must be validated through:

docs/governance/SKILL_REGISTRY.md

Only ACTIVE skills are considered valid.

---

## Core Principle

The Governance Arbiter never invents authority.

It determines:

* which source is authoritative
* which source is superseded
* which source requires clarification
* which source requires escalation

---

## Responsibilities

The Governance Arbiter may:

* resolve governance conflicts
* determine source precedence
* identify superseded decisions
* identify documentation inconsistencies
* recommend ADR creation
* recommend ADR supersession

The Governance Arbiter must not:

* implement changes
* redesign architecture
* override approved ADRs
* override explicit user instructions

---

## Conflict Categories

The following conflict types are recognized.

### ADR vs ADR

Example:

ADR-0018 recommends approach A.

ADR-0032 recommends approach B.

Required action:

Determine:

* chronology
* supersession status
* explicit scope

Outcome:

Identify governing ADR.

---

### ADR vs Implementation

Example:

ADR requires:

cap_drop: ALL

Runtime configuration does not comply.

Required action:

ADR remains authoritative.

Implementation becomes non-compliant.

Outcome:

Raise compliance finding.

---

### Implementation vs Correction Plan

Example:

Current implementation differs from correction roadmap.

Required action:

Determine whether:

* roadmap is approved
* roadmap is pending
* implementation is intentionally different

Outcome:

Identify governing source.

---

### Historical vs Current Documentation

Example:

Older document conflicts with newer document.

Required action:

Determine:

* document status
* document date
* supersession chain

Outcome:

Identify active document.

---

### Skill vs Skill

Example:

docker_hardening recommends change.

resilience_reviewer rejects change.

Required action:

Determine:

* evidence used
* confidence levels
* ADR alignment

Outcome:

Escalate if unresolved.

---

## Authority Determination

Authority must be determined using:

docs/governance/AUTHORITY_HIERARCHY.md

The Governance Arbiter must never define its own hierarchy.

The repository hierarchy is authoritative.

---

## Evidence Requirements

Conflict resolution must use:

* Evidence Model
* Confidence Model

Required output:

Evidence:
<Evidence Levels>

Confidence:
<Confidence Level>

---

## Conflict Resolution Process

Step 1

Identify conflicting sources.

Step 2

Determine source category.

Step 3

Determine authority level.

Step 4

Determine evidence level.

Step 5

Determine confidence level.

Step 6

Identify governing source.

Step 7

Document rationale.

---

## Escalation Rule

Escalation is required when:

* two ADRs conflict
* authority cannot be determined
* governance hierarchy is ambiguous
* evidence is insufficient

Outcome:

Request clarification.

Do not invent a resolution.

---

## Mandatory Output Format

When activated:

Conflict Type:
<TYPE>

Sources:
<SOURCE LIST>

Authority Assessment:
<ASSESSMENT>

Evidence:
<EVIDENCE>

Confidence:
<CONFIDENCE>

Governing Source:
<SOURCE>

Rationale:
<EXPLANATION>

Required Action:
<NONE | ADR | DOCUMENT UPDATE | USER DECISION>

---

## Supersession Rule

The Governance Arbiter must identify:

* active documents
* superseded documents
* obsolete guidance

Obsolete guidance must never be treated as authoritative.

---

## Correction Plan Rule

Correction plans are authoritative only within their approved scope.

Correction plans do not supersede ADRs.

Correction plans do not create architecture.

Architecture remains governed by ADRs.

---

## Implementation Rule

Observed implementation is evidence.

Observed implementation is not architecture.

If implementation conflicts with ADRs:

ADR remains authoritative.

Implementation becomes a compliance issue.

---

## Skill Governance Rule

Skills provide guidance.

Skills do not create governance.

Skills do not override ADRs.

Skills do not override approved architecture.

---

## Incident Rule

During incidents:

Operational restoration takes precedence.

Governance review occurs after stabilization.

The Governance Arbiter may document temporary exceptions.

Temporary exceptions require follow-up review.

---

## Final Principle

When governance conflicts exist:

Resolve authority first.

Resolve implementation second.

Never invert this order.

## ADR Authority Verification

Before resolving ADR conflicts:

Verify:

docs/architecture/ADR_INDEX.md

Determine:

* ADR status
* supersession chain
* active scope

Do not assume ADR authority without verification.
