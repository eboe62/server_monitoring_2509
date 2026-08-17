---
applyTo: "**/*"
---

# Repository AI Governance

This repository uses centralized AI governance.

Primary governance entry point:

* ./AI_ENTRYPOINT.md

All AI assistants must load and follow the governance, protocols, skills, templates and project documentation defined there.

---

## Context Resolution & Path Constraints

* **Strict Relative Resolution:** AI assistants MUST NOT expect, reference, or attempt to access absolute OS filesystem paths (e.g., `C:\WorkSpace\...`). All internal governance references, skills, templates, and codebase analysis MUST be executed using relative workspace paths (`./`) or files explicitly attached to the active session via chat references (`#` or `@`).
* **Path Alignment:** Any absolute path mentioned in prompts or configurations must be automatically translated by the AI to its equivalent relative position within the active VS Code workspace root.

---

## Governance Documents

Authoritative governance documents are located in:

* ai/governance/

Including:

* AI_CONSTITUTION.md
* DEVSECOPS_PRINCIPLES.md
* ANALYSIS_PROTOCOL.md
* EXECUTION_PROTOCOL.md
* USER_PREFERENCES.md

---

## Specialist Skills

Available specialist skills are located in:

* ai/skills/backend/
* ai/skills/common/
* ai/skills//
* ai/skills/frontend/documentation
* ai/skills/infrastructure/

Apply the skills relevant to the current task.

Skills act as mandatory review and validation layers.

---

## Templates

Available operational templates are located in:

* ai/templates/

Use templates when appropriate.

---

## Context

Additional project context is located in:

* ai/context/

Use relevant context documents when applicable.

---

## Authoritative Project Documentation

Authoritative project documentation includes:

* docs/decisiones/ADR-*.md
* docs/Project_Definition/
* docs/Project_Implementation/
* docs/Project_Corrections/
* docs/Project_ADRs/

Approved ADRs are normative and binding.

---

## Authoritative Ledgers

The user may explicitly designate authoritative project ledgers.

Do not assume that the newest file is authoritative.

When multiple versions exist:

* use the version explicitly designated by the user
* otherwise request clarification before proceeding

---

## Language

Default response language:

Spanish

Use English only when explicitly requested by the user.

Technical terminology may remain in English when doing so improves precision.

---

## Operational Rules

* **Architectural Precision:** Every proposed ADR must document a real, non-trivial structural design decision, boundary restriction, or topological pattern specific to the project. Generic framework setup, language versioning bump, linting rules, or standard library updates MUST NOT be generated as ADRs.
* Always separate analysis from execution.
* Never execute changes during analysis.
* Wait for explicit approval before modifying files.
* Request clarification when evidence is insufficient.
* Prefer evidence over assumptions.
* Prefer runtime validation over inference.

When evidence is insufficient:

* explicitly identify missing evidence
* request the required information
* do not infer critical architectural facts

---

## Scope Control

* Modify only files explicitly authorized.
* Never perform opportunistic refactors.
* Never introduce implicit improvements.
* Never expand scope without approval.
* If additional files are required, stop and request confirmation.

---

## Architecture Rules

* Approved ADRs are normative and binding.
* Approved architectural boundaries must be respected.
* No architectural redesign without explicit approval.
* No cross-service modifications unless explicitly authorized.
* No infrastructure redesign unless explicitly authorized.
* Docker Compose standalone architecture is the default model.
* No Docker Swarm unless explicitly approved.

---

## Execution Rules

* Present an implementation plan before changes.
* Wait for explicit approval.
* Maintain rollback capability.
* Preserve observability controls.
* Preserve operational stability.

---

## Design Philosophy

* Minimal changes.
* Deterministic behaviour preferred.
* Stability over optimization.
* Precision over productivity.
* Compatibility over customization.

---

## Conflict Resolution

If any governance document conflicts with:

* the user request
* approved ADRs
* repository architecture
* project constraints

identify the conflict and request clarification before proceeding.

## Authoritative Reference

You must strictly follow the rules, workflows, and roles defined in the authoritative repository file: ./AI_ENTRYPOINT.md. Do not execute or propose changes without complying with its sequential lifecycle.
