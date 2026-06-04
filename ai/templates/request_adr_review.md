# Request ADR Review Template

## ADR Metadata
* ADR Identifier:
* ADR Title:
* Target Container Typology (if applicable): [SERVICE / SUPERVISOR / TOOLBOX / INFRA_TRUSTED / NONE]
* Current Status: [PROPOSED / SUPERSEDED]

---

## Review Objective
Provide a precise description of the architectural aspects under evaluation.
Focus Areas:
* Structural alignment with the single-node deployment model.
* Governance compliance and strict isolation of the Host Plane (Plano 3).
* Hardening and visibility cross-dependencies.
* Operational implementation feasibility via the host Makefile control-plane.

---

## Related Architectural Records
List and reference:
* Superseded ADRs:
* Dependent or Upstream ADRs:
* Referenced ADRs:

---

## Review Criteria
The specialized AI reviewer must evaluate:
* Clarity and technical language precision (avoiding ambiguous placeholders).
* Completeness of the technical debt, trade-offs, and negative consequences sections.
* Technical accuracy regarding the declarative Compose ecosystem constraints.
* Operational impact and blast radius assessment on data volumes and internal networks.

---

## Required Critical Output Structure
For each technical finding or inconsistency detected, the AI must output:
* Description: Clear definition of the architectural gap.
* Rationale: Standard or local governance rule being violated.
* Impact: Quantifiable risk to runtime stability or system isolation.
* Suggested Improvement: Precise declarative adjustment or constraint addition.

---

## Final Assessment Verdict
The review must conclude with one definitive classification:
* ACCEPTED (Complies fully with all governance layers).
* REQUEST CHANGES (Requires minor declarative adjustments or explicit risk updates).
* REJECTED (Violates core principles, threatens host isolation, or lacks a rollback path).

---

## Prohibited Behaviour
Do not:
* Automatically rewrite the proposal or change the author's intent.
* Introduce speculative architectures or external cloud-orchestrator features.
* Alter the stated business scope or accept implicit permissions.
