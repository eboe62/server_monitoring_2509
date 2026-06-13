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

---

## ADR Referencing Rule

AI assistants must not claim that a specific ADR is impacted,
superseded, contradicted, or requires modification unless that ADR
has been explicitly reviewed during the current analysis.

When repository evidence is incomplete, ADR references must be
reported as potential candidates rather than confirmed impacts.

---

## Evidence Sufficiency Gate

Before entering impact analysis,
AI assistants must verify that sufficient
repository evidence has been reviewed.

Impact analysis must not be performed solely from:

- names
- labels
- filenames
- directory structure
- technology references
- user assumptions

If repository evidence is insufficient:

STOP

Report:

- known facts
- assumptions
- unknowns

Request additional evidence.

Impact classification is prohibited until the
Evidence Sufficiency Gate is satisfied.

### User-Supplied Scope Evidence

Explicit information provided by the user about the intended scope of a change constitutes admissible evidence for governance classification.

Examples:

- "Fix typo in README"
- "Rename variable"
- "Update comment"
- "Change button color"

The AI may use the declared change scope to determine proportional governance requirements.

The AI must not assume hidden impacts beyond the declared scope unless repository evidence directly contradicts the user statement.

Repository inspection becomes mandatory only when:

- the requested change itself is ambiguous
- repository evidence contradicts the declared scope
- the requested action could reasonably alter runtime behavior, security boundaries, persistence, networking, authorization, authentication, infrastructure, or architectural constraints

The Evidence Sufficiency Gate prohibits unsupported technical inferences, not the use of explicit user-provided scope information.

## Evidence Assessment

All findings must identify:

* evidence sources
* highest evidence level
* missing evidence

Use the Evidence Classification Model.

Conclusions without identified evidence levels are considered incomplete.

## Confidence Assessment

All findings and recommendations must include:

* confidence level
* confidence justification
* known limitations

Use the Confidence Assessment Model.

Confidence must be treated independently from evidence level.

High evidence does not automatically imply high confidence.

Missing evidence must reduce confidence.

Confidence levels:

* INSUFFICIENT
* LOW
* MEDIUM
* HIGH
* VERY HIGH

## Governance Conflict Detection

If multiple authoritative sources provide incompatible guidance:

Activate:

governance_arbiter

Do not silently choose one source.

Determine:

* authority hierarchy
* evidence levels
* confidence levels

Document the rationale.

If authority cannot be determined:

STOP.

Request clarification.

## Authority Validation

Before evaluating evidence:

Determine authority using:

docs/governance/AUTHORITY_HIERARCHY.md

Authority assessment precedes evidence assessment.

## ADR Validation

When ADRs are referenced:

Verify ADR status using:

docs/architecture/ADR_INDEX.md

Do not assume referenced ADRs remain active.

## Skill Validation

Before activating specialized skills:

Verify:

* skill exists
* skill status is ACTIVE

using:

docs/governance/SKILL_REGISTRY.md
