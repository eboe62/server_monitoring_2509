# Prompting Guide

## Objective
Provide a consistent interaction model across AI platforms. to enforce project governance.

---

## Preferred Workflow
Step 1: Provide context and live runtime evidence.
Step 2: Request structured analysis (Analysis Protocol execution).
Step 3: Review recommendations and trade-offs.
Step 4: Approve scope and grant explicit authorization.
Step 5: Execute declarative implementation.
Step 6: Trigger automated validation and verify rollback readiness.

---

## Analysis Requests
Preferred formatting template for the user:

Context:
...
Objective:
...
Constraints:
...
Available Evidence:
...
Expected Deliverable:
...

---

## Execution Requests
Preferred formatting template for the user:

Context:
...
Approved Scope:
...
Constraints:
...
Expected Deliverable (Declarative IaC plain text):
...
Validation & Rollback Requirements:
...

---

## Review Requests
Preferred formatting template for the user:

Artifact:
...
Objective:
...
Review Focus (Hardening, Observability, Resilience, or ADR compliance):
...
Constraints:
...

---

## Evidence Requirements
When requesting an assessment, the user should provide, and the AI must actively demand:
* Structured log outputs or active telemetry diagnostics.
* Live shell command or verification script outputs.
* Explicit declarative configurations (Compose blocks).
* Current state runtime metrics.

The AI assistant must refuse to provide structural conclusions or security enforcements in the absence of evidence.

---

## Preferred Behaviour
AI assistants must:
* Actively challenge assumptions and hidden dependencies.
* Identify operational risks and define their blast radius.
* Point out missing telemetry or gaps in evidence.
* Propose automated validation methods linked to the project's native control-plane automation.

---

## Avoid
The AI must flag and decline vague, imperative prompts such as:
* "Fix everything"
* "Optimize the container network"
* "Make the infrastructure secure"
Every prompt must be strictly bounded by scope, specific container typologies, and clear operational objectives.

---

## Golden Rule
Analysis precedes implementation.
Evidence precedes conclusions.
Validation precedes enforcement.
