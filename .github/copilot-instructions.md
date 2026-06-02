# Copilot Governance – server_monitoring_2509

This repository uses centralized AI governance.

Authoritative governance documents:

* ai/governance/AI_CONSTITUTION.md
* ai/governance/DEVSECOPS_PRINCIPLES.md
* ai/governance/ANALYSIS_PROTOCOL.md
* ai/governance/EXECUTION_PROTOCOL.md
* ai/governance/USER_PREFERENCES.md

Available specialist skills:

* ai/skills/devsecops_architect.md
* ai/skills/runtime_auditor.md
* ai/skills/docker_hardening.md
* ai/skills/adr_reviewer.md
* ai/skills/observability_reviewer.md

Authoritative project documents include:

* docs/decisiones/ADR-*.md
* docs/Project_Definition/Servidor_DigitalOcean_Definicion_Proyecto.txt
* docs/Project_Implementation/Servidor_DigitalOcean_Implementacion.txt
* docs/Project_Corrections/Servidor_DigitalOcean_Correccion.txt

Operational Rules:

* Always separate analysis from execution.
* Never execute changes during analysis.
* Wait for explicit approval before modifying files.
* Request clarification when evidence is insufficient.
* Prefer evidence over assumptions.
* Prefer runtime validation over inference.

Scope Control:

* Modify only files explicitly authorized.
* Never perform opportunistic refactors.
* Never introduce implicit improvements.
* Never expand scope without approval.
* If additional files are required, stop and request confirmation.

Architecture Rules:

* ADRs are normative and binding.
* Approved architectural boundaries must be respected.
* No architectural redesign without explicit approval.
* No cross-service modifications unless explicitly authorized.
* No infrastructure redesign unless explicitly authorized.
* Docker Compose standalone architecture is the default model.
* No Docker Swarm unless explicitly approved.

Execution Rules:

* Present an implementation plan before changes.
* Wait for explicit approval.
* Maintain rollback capability.
* Preserve observability controls.
* Preserve operational stability.

Design Philosophy:

* Minimal changes.
* Deterministic behaviour preferred.
* Stability over optimization.
* Precision over productivity.
* Compatibility over customization.

If any governance document conflicts with the request, identify the conflict and request clarification before proceeding.
