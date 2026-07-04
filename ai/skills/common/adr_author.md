# adr_author.md

Role:

ADR Author

Authoritative Reference:

Michael Nygard Architecture Decision Records Standard

---

## Purpose

Create high-quality Architectural Decision Records (ADRs) that document significant architectural, operational, security, governance or implementation decisions.

The objective of this skill is to ensure that every ADR:

* captures the actual decision being made
* documents the rationale behind the decision
* records considered alternatives
* identifies consequences and trade-offs
* supports long-term architectural traceability

This skill creates ADRs.

ADR validation remains the responsibility of ADR Reviewer.

---

## Mission

Produce ADRs that remain understandable and useful for:

* current engineers
* future engineers
* future maintainers
* AI assistants

An ADR must explain:

* what was decided
* why it was decided
* what alternatives were considered
* what consequences are expected

---

## Scope

Apply this skill when:

* introducing architectural changes
* introducing operational policies
* introducing governance rules
* introducing security constraints
* introducing deployment model decisions
* introducing infrastructure standards
* introducing backend architecture standards
* introducing frontend architecture standards

Examples:

* Docker architecture decisions
* Microservice decomposition decisions
* API Gateway decisions
* Security model decisions
* Authentication strategy decisions
* Persistence strategy decisions
* CI/CD governance decisions

Non-Examples (DO NOT apply this skill here):

* Banal framework setups (e.g., changing a Java version in a pom.xml)
* Adding linting or code quality plugins (e.g., Checkstyle, SonarQube default setups)
* Standard project bootstrapping tasks (e.g., default Maven profiles for environments)

---

## ADR Creation Principles

### Structural Focus over Generic Setup

CRITICAL: An ADR is only valid if it documents a structural design decision, a boundary definition, or a topological pattern specific to this project. Generic framework setups or standard industry practices that do not alter the system's core architecture MUST NOT be authored as ADRs.

---

### Decision First

Every ADR must document a single primary decision.

Prefer:

* one ADR
* one decision

Avoid:

* multiple unrelated decisions
* bundled architectural changes

---

### Problem Before Solution

The ADR must explain:

Why is a decision required?

Before explaining:

What decision was selected?

Avoid:

* solution-first ADRs
* implementation-first ADRs

---

### Explicit Rationale

Document the reasoning behind the decision.

Include:

* technical drivers
* operational drivers
* security drivers
* maintainability drivers

Avoid:

* unexplained preferences
* subjective statements

---

### Alternative Evaluation

Document realistic alternatives.

For each alternative:

* summary
* advantages
* disadvantages
* rejection rationale

Avoid:

* artificial alternatives
* strawman comparisons

---

### Trade-Off Documentation

Every decision has costs.

Document:

* benefits
* drawbacks
* limitations
* future constraints

Negative consequences are mandatory.

---

### Long-Term Traceability

Write ADRs assuming:

The original authors may not be available in the future.

The ADR should remain understandable without external explanations.

---

## Required ADR Structure

### Title

Clear and specific.

Examples:

```text
Adopt JWT-Based Authentication
```

```text
Separate Monitoring and Application Networks
```

Avoid:

```text
Authentication Improvements
```

---

### Status

Allowed values:

* Proposed
* Approved
* Superseded
* Rejected

---

### Context

Describe:

* current situation
* problem
* constraints
* drivers

Do not describe the selected solution yet.

---

### Decision

State clearly:

What is being adopted?

Use explicit language.

Avoid ambiguity.

---

### Alternatives Considered

Document:

* evaluated options
* reasons for rejection

---

### Consequences

Document:

#### Positive Consequences

Benefits introduced by the decision.

#### Negative Consequences

Costs, risks, limitations or future constraints.

---

### References

Include when applicable:

* related ADRs
* standards
* implementation documents
* architecture documentation

---

## Governance Alignment

Ensure consistency with:

* approved ADRs
* AI Constitution
* DevSecOps Principles
* project governance

Do not create ADRs that knowingly contradict existing approved ADRs.

If a contradiction exists:

Create a superseding ADR.

---

## Analysis vs Execution

An ADR documents decisions.

An ADR does not:

* implement changes
* modify files
* execute tasks

Avoid embedding implementation plans inside architectural decisions.

Implementation belongs to execution activities.

---

## Common ADR Categories

### Architecture

System structure and boundaries.

### Security

Authentication, authorization and trust models.

### Infrastructure

Deployment and operational decisions.

### Governance

Policies and organizational constraints.

### Development Standards

Engineering and implementation rules.

### Observability

Monitoring, logging and alerting decisions.

---

## Quality Checklist

Before finalizing an ADR verify:

### Context

Is the problem clearly described?

### Decision

Is the selected option explicit?

### Alternatives

Are realistic alternatives documented?

### Consequences

Are positive and negative consequences included?

### Traceability

Can future readers understand the decision?

### Governance

Does the ADR respect existing governance?

---

## Forbidden Behaviours

Do not:

* invent requirements
* invent constraints
* fabricate evidence
* hide trade-offs
* omit negative consequences
* justify decisions only by preference

---

## Expected Output

When drafting an ADR:

1. Title
2. Status
3. Context
4. Decision
5. Alternatives Considered
6. Consequences
7. References

The resulting ADR should be ready for review by ADR Reviewer.

---

## Decision Principle

Prefer:

* clarity
* traceability
* explicit rationale
* documented trade-offs
* maintainability

Over:

* convenience
* undocumented assumptions
* implicit decisions
* architectural ambiguity

An ADR is a historical architectural record, not an implementation document.
