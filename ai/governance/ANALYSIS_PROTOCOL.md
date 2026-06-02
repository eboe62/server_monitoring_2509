# Analysis Protocol

## Objective

Provide a structured methodology for technical analysis before implementation.

---

## Phase 1 - Context Collection

Identify:

* objective
* affected systems
* constraints
* dependencies
* existing ADRs

If information is missing:

Request additional evidence.

Do not guess.

---

## Phase 2 - Current State Assessment

Determine:

* current implementation
* runtime behaviour
* configuration state
* operational dependencies

Prefer:

* runtime inspection
* logs
* metrics
* source code

over assumptions.

---

## Phase 3 - Risk Assessment

Identify:

* operational risks
* security risks
* performance risks
* maintenance risks

Classify:

* Low
* Medium
* High
* Critical

---

## Phase 4 - Impact Assessment

Evaluate impact on:

* services
* deployments
* observability
* backups
* CI/CD
* security controls

---

## Phase 5 - Options

Provide:

* recommended option
* alternative options
* rejected options

Explain rationale.

---

## Phase 6 - Validation Plan

Define:

* required evidence
* tests
* rollback strategy
* acceptance criteria

---

## Analysis Output Format

Every analysis should contain:

1. Context
2. Current State
3. Findings
4. Risks
5. Options
6. Recommendation
7. Validation Plan

Implementation is not part of analysis.
