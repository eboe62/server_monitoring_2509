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
