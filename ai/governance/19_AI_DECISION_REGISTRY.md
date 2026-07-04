# AI Decision Registry

## Purpose

This document defines the governance framework for recording significant AI-assisted decisions.

The objective is to:

* improve traceability
* improve auditability
* improve governance transparency
* support incident investigations
* support ADR creation
* support decision reviews

Not every AI interaction requires registration.

Only significant decisions require registration.

---

## Fundamental Principle

AI recommendations do not become authoritative automatically.

Authority remains governed by:

* User Instructions
* ADRs
* Governance Documents

Decision records provide traceability.

They do not create authority.

---

## Registration Criteria

A decision should be registered when it affects:

* architecture
* security
* hardening
* observability
* deployment
* governance
* operational procedures

Minor documentation changes do not require registration.

---

## Registry Location

Decision records must be stored under:

docs/ai_decisions/

One file per decision.

---

## Naming Convention

Format:

YYYYMMDD-DECISION-XXXX.md

Example:

20260613-DECISION-0001.md

---

## Decision Lifecycle

A decision may be:

PROPOSED

APPROVED

IMPLEMENTED

REJECTED

SUPERSEDED

ROLLED_BACK

---

## Decision Record Template

Every decision record should contain:

Decision ID:

Date:

Task Type:

Decision Status:

Author:

AI System:

Repository Version:

---

## Authority Assessment

Authority Sources:

Authority Level:

Governing Source:

---

## Evidence Assessment

Evidence:

Highest Evidence Level:

Missing Evidence:

---

## Confidence Assessment

Confidence:

Confidence Rationale:

---

## Context

Problem:

Scope:

Constraints:

---

## Recommendation

Summary:

Alternatives Considered:

Risks:

Expected Benefits:

---

## Outcome

Approved:

Implemented:

Rejected:

Rollback Required:

---

## Related Artifacts

ADRs:

Skills:

Governance Documents:

Correction Plans:

Implementation Documents:

---

## Lessons Learned

Optional

---

## Final Status

PROPOSED

APPROVED

IMPLEMENTED

REJECTED

SUPERSEDED

ROLLED_BACK

---

## Governance Rule

Significant AI-assisted decisions should be traceable.

Decision records improve governance visibility.

Decision records do not create authority.
