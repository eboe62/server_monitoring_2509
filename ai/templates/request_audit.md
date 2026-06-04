# Request Audit Template

## Audit Target & Scope
* Target Services/Volumes/Networks:
* Declared Container Typologies Involved:
* Core Standards Applied: CIS Docker Benchmark / NIST SP 800-190 / Local DevSecOps Principles.

---

## Evidence Available for Verification
Provide live data from the declarative and running environments:
* Active Docker Compose configuration files:
* Runtime metadata outputs (docker inspect or compose config):
* Live system metrics and stdout log streams:
* Reference ADR constraints:

---

## Audit Focus Areas
The execution must actively audit and cross-reference:
* Declarative compliance vs actual running state (Drift detection).
* Explicit resource constraints enforcement (cpus, mem_limit boundaries).
* Host Plane exposure vectors (verifying zero socket or root-level bind mounts).
* Capability mapping (cap_drop: ALL compliance) and process privilege escalation constraints.
* Typology validation (e.g., ensuring no application probes are enforced on toolbox/supervisor blocks).

---

## Required Finding Output Format
For every non-compliance, vulnerability, or drift detected, output:
* Finding Identifier & Typology Context.
* Empirical Evidence: Reference the exact code line or runtime parameter.
* Severity Classification: [Informational / Low / Medium / High / Critical].
* Operational Impact: Evaluation of the local blast radius and potential host degradation.
* Remediation Recommendation: The exact declarative IaC syntax required to fix the issue.

---

## Severity Classification Matrix
* Informational: Minor documentation mismatch or temporary toolbox state; zero structural risk.
* Low: Non-critical telemetry gap or minor configuration drift with local automatic restart protection.
* Medium: Missing resource constraints or non-essential capability exposure; potential localized performance gap.
* High: Unauthorized filesystem write access, missing health checks on service runtimes, or unmapped volume drifts.
* Critical: Threat to Host Plane isolation, docker.sock exposure, or configurations causing infinite runtime crash loops.

---

## Deliverable Structure
1. Executive Summary & Typology Compliance Score
2. Detailed Findings & Drift Inventory
3. Risk & Blast Radius Matrix
4. Declarative Recommendations (IaC Code Blocks)
5. Validation Requirements via Host-Plane Control Tooling (Makefile)

---

## Prohibited Behaviour
Do not:
* Invent configuration states or assume compliance in the absence of explicit files.
* Propose runtime corrections meant to execute inside the container workspace.
* Downgrade severity rankings to accommodate deployment speed or operational convenience.
