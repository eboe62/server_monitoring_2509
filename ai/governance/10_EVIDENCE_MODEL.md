# Evidence Classification Model

## Purpose

This document defines the evidence classification framework used by AI assistants operating within this repository.

The objective is to:

* distinguish assumptions from validated facts
* improve decision quality
* reduce hallucinations
* improve architectural consistency
* improve operational safety
* improve traceability

All findings, recommendations, conclusions, implementation proposals, and ADR discussions should be evaluated using this evidence model.

Evidence does not create authority.

Authority must be determined using:

docs/governance/AUTHORITY_HIERARCHY.md

before evidence assessment begins.

---

## Relationship with Governance Hierarchy

This document does not override:

* Explicit User Instructions
* Approved ADRs
* AI Constitution
* DevSecOps Principles
* Task Classification Model

This model defines how confidence and evidence should be assessed.

---

## Fundamental Principle

Not all evidence has the same value.

Operational decisions must prioritize stronger evidence levels whenever possible.

Higher evidence levels supersede lower evidence levels.

Example:

Runtime evidence overrides code assumptions.

Production validation overrides theoretical analysis.

---

## Evidence Levels

The following levels are mandatory.

---

## E0 - Hypothesis

### Definition

Assumptions, expectations, guesses, predictions, or inferred behaviour.

### Examples

* Expected container behaviour
* Assumed Docker image behaviour
* Suspected root cause
* Predicted hardening impact

### Allowed Uses

* Exploration
* Brainstorming
* Investigation planning

### Forbidden Uses

E0 alone must never justify:

* Production changes
* ADR approval
* Security enforcement
* Hardening implementation

### Example

"Promtail probably only writes positions."

Evidence Level:

E0

---

## E1 - Source Code

### Definition

Evidence derived from:

* source code
* Dockerfiles
* shell scripts
* Python scripts
* repository contents

### Examples

* Dockerfile contains USER 1000
* Script creates directory
* Python application writes log files

### Strength

Stronger than assumptions.

Weaker than runtime evidence.

### Limitations

Code may not reflect actual execution.

### Example

Dockerfile creates:

/var/lib/promtail

Evidence Level:

E1

---

## E2 - Configuration

### Definition

Evidence derived from:

* compose files
* configuration files
* environment variables
* CI definitions
* infrastructure definitions

### Examples

* read_only configured
* tmpfs configured
* capability drops configured
* healthcheck configured

### Strength

Represents intended behaviour.

Does not prove actual behaviour.

### Example

compose.yml contains:

read_only: true

Evidence Level:

E2

---

## E3 - Runtime Validation

### Definition

Evidence collected from a running system.

### Examples

* docker inspect
* docker exec
* runtime filesystem inspection
* open file handles
* process inspection
* mounted volumes

### Strength

Represents actual behaviour.

Normally preferred over E1 and E2.

### Example

docker inspect reports:

ReadonlyRootfs=false

Evidence Level:

E3

---

## E4 - Automated Validation

### Definition

Evidence obtained through automated controls.

### Examples

* CI pipelines
* security tests
* runtime tests
* integration tests
* reproducibility tests

### Strength

Repeatable and verifiable.

Provides stronger confidence than isolated runtime observations.

### Example

make test-security-runtime passes.

Evidence Level:

E4

---

## E5 - Production Validation

### Definition

Evidence validated through successful operational use.

### Examples

* Production deployments
* Operational observations
* Monitoring confirmation
* Incident-free operation

### Strength

Highest evidence level.

Preferred for architectural decisions.

### Example

Promtail running 30 days with:

read_only=true

without incidents.

Evidence Level:

E5

---

## Evidence Hierarchy

Highest confidence:

E5 Production Validation

↓

E4 Automated Validation

↓

E3 Runtime Validation

↓

E2 Configuration

↓

E1 Source Code

↓

E0 Hypothesis

Lowest confidence

---

## Mandatory Evidence Reporting

AI assistants should explicitly identify evidence levels whenever making:

* recommendations
* architectural conclusions
* hardening proposals
* security assessments
* ADR evaluations

Preferred format:

Evidence:
- E1: Dockerfile review
- E2: compose configuration
- E3: docker inspect validation

Highest Evidence Level:
E3

---

## Mixed Evidence Rule

Most conclusions rely on multiple evidence levels.

Example:

Promtail readonly assessment

Evidence:

E1:
Dockerfile analysis

E2:
compose configuration

E3:
runtime inspection

E4:
CI validation

Highest Evidence Level:
E4

Result:

Validated but not yet production-certified.

---

## Production Certification Rule

The following topics should not be considered fully validated until E5 exists:

* hardening controls
* readonly filesystem
* capability reductions
* network restrictions
* runtime security controls
* observability changes
* backup changes

Until E5 exists:

State must be considered:

PROVISIONALLY VALIDATED

not

FULLY CERTIFIED

---

## ADR Requirements

ADR discussions should explicitly identify:

Evidence Used

Example:

Evidence:
- E1 Dockerfile review
- E2 Compose configuration
- E3 Runtime validation

Highest Evidence Level:
E3

Limitations:
No E4 or E5 available.

---

## Conflict Resolution

When evidence levels conflict:

Higher evidence level wins.

Example:

E1:
Application appears readonly-compatible.

E3:
Application fails at startup with readonly filesystem.

Conclusion:

E3 overrides E1.

Readonly compatibility rejected.

---

## Mandatory Limitation Reporting

Whenever evidence is incomplete:

AI assistants must explicitly identify:

Missing Evidence

Example:

Missing Evidence:
- E4 automated validation
- E5 production validation

Confidence reduced.

Further validation required.

---

## Certification States

The following states are mandatory.

### UNVERIFIED

Highest Evidence:

E0

### ANALYZED

Highest Evidence:

E1-E2

### VALIDATED

Highest Evidence:

E3-E4

### CERTIFIED

Highest Evidence:

E5

Only CERTIFIED states should be treated as fully proven operational behaviour.
