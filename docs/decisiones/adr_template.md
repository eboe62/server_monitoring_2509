# ADR-XXXX: [Short, Descriptive Title of the Decision]

- **Status:** [PROPOSED | APPROVED | SUPERSEDED | DEPRECATED]
- **Date:** [YYYY-MM-DD]
- **Author:** [Name/Role]
- **Supersedes:** [NONE | ADR-YYYY]
- **Superseded By:** [NONE | ADR-ZZZZ]
- **Scope:** [System | Host | Runtime | Infrastructure | Database]
- **Dependencies:** [List of core infrastructure requirements or constraints]
- **Related ADRs:** [e.g., ADR-0014, ADR-0021]

---

## Context & Problem Statement
[Clear description of the architectural problem or context driving this decision. What is the current limitation, risk, or technical debt? Include concrete technical drivers.]

## Decision Drivers
1. [Driver 1: e.g., Attack surface reduction (DevSecOps)]
2. [Driver 2: e.g., Host independence and reproducibility]
3. [Driver 3: e.g., API consumption and cost optimization]

## Considered Options
1. **Option 1:** [Short name of option 1]
2. **Option 2:** [Short name of option 2]
3. **Option 3:** [Short name of option 3]

## Decision Outcome
Chosen option: **Option X**, because [comprehensive technical justification explaining why this option wins over the alternatives under current constraints].

### Consequences & Impact
* **Positive:** [Benefit 1, e.g., Port exposure limited to 127.0.0.1]
* **Negative:** [Drawback 1, e.g., Adds 50 lines of configuration to docker-compose]
* **Risks Mitigated:** [Describe security or runtime risks solved by this choice]

---

## Validation & Compliance Gates
- [ ] Verification script/command: `[e.g., make test-security-runtime]`
- [ ] Expected output or green state definition.
- [ ] CI/CD validation target integration.
