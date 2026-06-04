# Analysis Protocol

## Objective

Provide a structured, mandatory methodology for technical analysis before any implementation or repository modification is proposed by an AI assistant.

---

## Phase 1 - Context Collection

Identify:
* Primary objective and business logic need.
* Affected services and their official Container Typology (SERVICE, SUPERVISOR, TOOLBOX, INFRA_TRUSTED).
* Operational constraints (Single-node architecture, no external orchestrator).
* Upstream and internal dependencies.
* Existing and relevant ADRs.

If information is missing:
* Request additional evidence or telemetry from the user.
* Do not guess, infer, or proceed with assumptions.

---

## Phase 2 - Current State Assessment

Determine:
* Current declarative IaC implementation in the Compose ecosystem.
* Actual runtime behaviour and system state.
* Configuration state (Environment variables mapping, network attachment).
* Active operational dependencies.

Prefer:
* Runtime inspection data.
* Live logs and metrics.
* Source code and versioned configurations.
over structural assumptions or external documentation defaults.

---

## Phase 3 - Risk Assessment

Identify and define the specific blast radius for:
* Operational risks (Service degradation, boot loops).
* Security risks (Privilege escalation, unauthorized shared volume access).
* Performance risks (Memory exhaustion, OOM events, CPU starvation).
* Maintenance risks (Upstream breaking changes, configuration drift).

Classify Risk Levels:
* LOW: Localized, immediate automatic recovery via local Docker restart policies.
* MEDIUM: Temporary service degradation; might cause transient telemetry or log gaps.
* HIGH: Potential data inconsistency or stuck container state; requires a structured rollback.
* CRITICAL: Total environment drift; container fails to restart or threatens Host Plane integrity.

---

## Phase 4 - Impact Assessment

Evaluate and document the exact impact on:
* Co-located services sharing the same internal monitoring-network.
* Deployment lifecycle via the centralized host Control-Plane (Makefile).
* Observability pipelines (Log streams, metric parsing).
* Backups and volume state persistence.
* Security controls and applied constraints.

---

## Phase 5 - Options Analysis

Provide:
* Recommended option (Aligned with declarative IaC and least privilege).
* Alternative options (Including trade-offs and operational overhead).
* Rejected options (Explicitly detailing why they violate project boundaries or architectural principles).

Explain the technical rationale for each path, prioritizing simplicity and upstream compatibility.

---

## Phase 6 - Validation & Fallback Plan

Define:
* Required evidence to prove successful deployment.
* Specific test definitions (e.g., local resilience simulations, make test-resilience-completo).
* Actionable rollback strategy (Exact steps to reverse configurations and preserve data state).
* Unambiguous acceptance criteria.

---

## Analysis Output Format

Every technical analysis delivered must contain:

1. Context & Typology Identification
2. Current State Evidence
3. Findings & Drift Detection
4. Risks & Blast Radius Assessment
5. Options Analysis
6. Definitive Recommendation
7. Validation & Rollback Plan

Implementation code or configuration blocks must not be part of the analysis phase.
