# Execution Protocol

## Objective
Define how approved infrastructure and repository changes must be executed by the AI assistant, ensuring deterministic deployment and zero environmental drift.

---

## Preconditions
Before any modification is written or proposed:
* The formal Analysis Protocol must be completed and outputted.
* All associated risks and blast radiuses must be explicitly identified.
* The specific target Container Typology must be categorized.
* Explicit user authorization must be granted.

---

## Scope Control
Implement exclusively the strictly approved scope.
Do not:
* Refactor unrelated code or configuration blocks.
* Modify network boundaries or shared volumes outside the authorized patch.
* Introduce undocumented features or speculative optimizations.

---

## Implementation Rules
Prefer:
* Minimal and surgical declarative changes in the Compose files.
* Reversible configuration structures.
* Fully documented parameters.

Maintain:
* Strict compliance with existing ADRs.
* Absolute Infrastructure as Code (IaC) integrity.
* Single-node operational predictability.
* Complete isolation of the Host Plane (Plano 3); no execution steps may imply opening access to host subsystems or exposing docker.sock.

---

## Validation Requirements
Every single executed change must deliver:
* A concrete verification method using existing telemetry streams or local tests.
* A clear, localized rollback procedure (e.g., repository reversion or volume state restoration).
* The expected output behavior mapped against live logs or process exit codes.

---

## Documentation Requirements
Update documentation immediately when a change modifies:
* Service runtime behavior or operational context.
* Declarative architecture variables or network mappings.
* Governance rules or recovery/operational procedures.

---

## Security Changes
Security and hardening controls must:
* Be evidence-based, utilizing active visibility baselines.
* Be progressive and validated against upstream software requirements.
* Be completely reversible without requiring a full infrastructure wipe.

Never deploy hardening controls (such as read_only or capability drops) blindly without an active validation and tracking path.

---

## Completion Criteria
A task or deployment proposal is considered complete only when:
* The declarative implementation is finished and syntax-validated.
* Local validation tests pass successfully (e.g., make test-resilience-completo).
* Corresponding documentation or ADR status is updated.
* The actionable rollback plan is explicitly documented.
