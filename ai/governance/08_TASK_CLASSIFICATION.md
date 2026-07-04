# Task Classification Model

## Purpose

This document defines the mandatory task classification model used by AI assistants operating within this repository.

The objective is to:

* reduce ambiguity
* improve reviewer selection
* improve governance consistency
* improve execution safety
* improve traceability

Task classification is mandatory.

No analysis, recommendation, implementation proposal, or execution planning should begin before determining the applicable task type.

---

## Relationship with Governance Hierarchy

This document does not override:

* Explicit User Instructions
* Approved ADRs
* AI Constitution
* DevSecOps Principles

Task classification is a governance mechanism used to determine:

* applicable workflows
* required evidence
* reviewer activation
* execution constraints

---

## Mandatory Classification Rule

Every request must be classified into one primary task type.

Allowed classifications:

* ANALYSIS
* AUDIT
* EXECUTION
* ADR
* HARDENING
* INCIDENT
* DOCUMENTATION

If classification is ambiguous:

STOP.

Request clarification before continuing.

AI assistants must never silently switch between task types.

---

## ANALYSIS

### Objective

Understand a problem, proposal, requirement, correction, architecture, or operational situation.

### Outputs

May produce:

* findings
* observations
* risks
* alternatives
* recommendations
* validation proposals

Must not:

* modify files
* generate implementation without explicit request
* assume execution approval

### Typical Examples

* Review Priority 8
* Evaluate architecture
* Compare alternatives
* Analyze incident causes
* Assess operational impact

### Skill Activation

Evidence-based.

Common examples:

* architecture_reviewer
* devsecops_architect
* governance_reviewer

---

## AUDIT

### Objective

Verify compliance against existing requirements.

### Outputs

May produce:

* compliance findings
* non-conformities
* gaps
* validation results

Must not:

* redesign architecture
* execute changes

### Typical Examples

* ADR compliance review
* Security validation
* Runtime audit
* Governance review
* Infrastructure compliance verification

### Skill Activation

Evidence-based.

Common examples:

* governance_reviewer
* runtime_auditor
* docker_hardening

---

## EXECUTION

### Objective

Implement approved changes.

### Preconditions

Must have:

* explicit execution authorization
* approved scope
* identified files
* rollback strategy

### Outputs

May produce:

* file modifications
* infrastructure modifications
* implementation plans

Must not:

* expand scope
* introduce opportunistic improvements
* redesign architecture

### Typical Examples

* Implement approved correction
* Apply approved ADR
* Modify compose configuration

### Mandatory Governance

Execution Protocol applies.

---

## ADR

### Objective

Create, modify, review, supersede, or evaluate architectural decisions.

### Outputs

May produce:

* ADR proposals
* ADR reviews
* ADR impact analysis
* ADR conflict analysis

### Typical Examples

* Create ADR
* Review ADR
* Supersede ADR
* Architectural trade-off analysis

### Skill Activation

Usually:

* adr_author
* adr_reviewer
* architecture_reviewer

---

## HARDENING

### Objective

Improve security posture while preserving operational stability.

### Outputs

May produce:

* hardening proposals
* validation plans
* staged implementation plans

### Mandatory Principles

* Stability over hardening
* Evidence before action
* Validation before enforcement
* Progressive enforcement

### Typical Examples

* read_only evaluation
* capability reduction
* network restriction
* secret hardening

### Required Reviewers

Normally:

* devsecops_architect
* docker_hardening

Additional reviewers based on scope.

---

## INCIDENT

### Objective

Investigate, contain, mitigate, recover, and document operational incidents.

### Outputs

May produce:

* containment plans
* root cause analysis
* recovery procedures
* corrective actions

### Priority Model

1. Containment
2. Service restoration
3. Root cause analysis
4. Permanent correction

### Typical Examples

* Service outage
* CI failure
* Container startup failure
* Security incident

### Skill Activation

Evidence-based.

Common examples:

* runtime_auditor
* resilience_and_rollback_reviewer
* observability_reviewer

---

## DOCUMENTATION

### Objective

Create, update, review, or reorganize documentation.

### Outputs

May produce:

* documentation updates
* structure improvements
* consistency reviews

Must not:

* introduce implementation changes
* introduce architectural changes

### Typical Examples

* README updates
* Runbooks
* Procedures
* Governance documents

### Skill Activation

Only relevant reviewers.

Apply proportional governance.

---

## Classification Resolution Rules

If multiple classifications appear possible:

Select the dominant objective.

Examples:

Reviewing a hardening proposal
→ HARDENING

Reviewing compliance of a hardening implementation
→ AUDIT

Implementing an approved hardening change
→ EXECUTION

Evaluating a new architecture
→ ANALYSIS

Writing an ADR
→ ADR

Investigating a production failure
→ INCIDENT

Updating a README
→ DOCUMENTATION

---

## Mandatory Response Header

Before beginning substantive analysis, AI assistants should identify:

TASK TYPE:
<CLASSIFICATION>

PRIMARY OBJECTIVE:
<OBJECTIVE>

EXECUTION AUTHORIZATION:
YES / NO

If EXECUTION AUTHORIZATION is NO:

Execution is prohibited.

Analysis only.
