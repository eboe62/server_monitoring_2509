# Execution Protocol

## Objective

Define how approved changes should be executed.

---

## Preconditions

Before implementation:

* analysis completed
* risks identified
* constraints understood
* approval received

---

## Scope Control

Implement only the approved scope.

Do not:

* refactor unrelated code
* redesign architecture
* introduce additional features

unless explicitly authorized.

---

## Implementation Rules

Prefer:

* minimal changes
* reversible changes
* documented changes

Maintain:

* ADR compliance
* IaC compliance
* operational stability

---

## Validation Requirements

Every change must include:

* verification method
* rollback method
* expected outcome

---

## Documentation Requirements

Update documentation when:

* behaviour changes
* architecture changes
* governance changes
* operational procedures change

---

## Security Changes

Security controls must:

* be evidence-based
* be validated
* be reversible

Never deploy unvalidated hardening controls.

---

## Completion Criteria

A change is complete only when:

* implementation finished
* validation passed
* documentation updated
* rollback documented

## Evidence Requirements

Execution proposals must identify:

* evidence supporting the change
* highest evidence level
* validation gaps

Execution based solely on E0 hypotheses is prohibited.

Execution based solely on E1 or E2 requires explicit justification.

E3 or higher is preferred whenever available.

## Confidence Requirements

Execution recommendations must include:

* evidence level
* confidence level
* validation gaps

Execution should normally require:

Confidence:
HIGH

or greater.

Execution proposals with:

Confidence:
LOW

or

INSUFFICIENT

are prohibited unless explicitly authorized by the user.

Validation should be preferred over implementation whenever confidence is insufficient.

## Governance Conflict Validation

Before execution:

Verify that:

* ADRs
* governance documents
* correction plans
* implementation requirements

do not conflict.

If conflicts exist:

Activate:

governance_arbiter

Execution must be suspended until the conflict is resolved.

## Authority Validation

Before execution:

Verify authority hierarchy compliance.

Authority conflicts must be resolved before implementation begins.

Use:

docs/governance/AUTHORITY_HIERARCHY.md

## ADR Authority Validation

Before implementing ADR-driven changes:

Verify:

docs/architecture/ADR_INDEX.md

Implementation based on superseded ADRs is prohibited.

## Skill Authority Validation

Execution workflows may only rely on:

ACTIVE

skills registered in:

docs/governance/SKILL_REGISTRY.md
