# Request Incident Review Template

## Incident Metadata
* Incident Identifier: [INC-YYYYMMDD-XX]
* Failure Timestamp: YYYY/MM/DD HH:MM:SS
* Affected Runtime Typology: [SERVICE / SUPERVISOR / TOOLBOX / INFRA_TRUSTED]
* Severity Level: [LOW / MEDIUM / HIGH / CRITICAL]

---

## Executive Summary
Provide a brief, technical description of the runtime failure, service degradation, or security anomaly. Avoid qualitative statements or conversational prose.

---

## Empirical Evidence Collected
Provide the direct, unedited telemetry captured during the event:
* Raw stdout/stderr Log Streams:
* Active Metric Threshold Anomalies:
* Host-Plane Command Outputs (e.g., docker inspect or system diagnostics):

---

## Chronological Timeline
Document every phase using absolute timestamps:
1. Detection [YYYY/MM/DD HH:MM:SS]: [How the alert or log drift was flagged]
2. Escalation [YYYY/MM/DD HH:MM:SS]: [Triggering of host-plane controls]
3. Mitigation [YYYY/MM/DD HH:MM:SS]: [Temporary or execution hotfixes applied]
4. Recovery [YYYY/MM/DD HH:MM:SS]: [Restoration of the baseline declarative state]

---

## Impact & Blast Radius Assessment
Quantify the operational damage within the single-node architecture:
* Service Availability: Total downtime or degraded performance metrics.
* Data Volume Persistence: Structural state check (State corruption or data loss evaluated).
* Observability Pipelines: Telemetry gaps or alert fatigue analysis.
* Security Isolation: Evaluation of potential host plane leaks or exposure vectors.

---

## Root Cause Analysis (RCA)
Deconstruct the mechanism of failure:
* Direct Causes: The explicit technical breakdown (e.g., OOM event due to missing limits).
* Contributing Factors: Environment configurations or dependency drops.
* Defeated Safetynets: Why existing health checks or constraints failed to prevent the incident.
Strictly separate CONFIRMED FACTS from HYPOTHESES.

---

## Corrective Actions & Mitigations
Define the structural remediation path using declarative IaC:
### Immediate Actions
* Immediate fixes to safely secure the runtime state without altering core architecture.
### Short-Term Actions
* Versioned adjustments to Compose resource limits or retry configurations.
### Long-Term Actions
* Formal proposals for new ADRs to modify baseline infrastructure or isolation policies.

---

## Validation & Success Criteria
* Corrective Action Verification: Specific local tests (e.g., make test-resilience-completo) required to simulate and verify the fix.
* Success Metrics: Target telemetry values confirming normal operational thresholds.
* Rollback Trigger Criteria: Conditions under which the corrective action must be immediately undone.

---

## Prohibited Behaviour
Do not:
* Speculate or formulate theories in the absence of explicit log or metric data.
* Assign blame or incorporate emotional filler text.
* Mix unverified assumptions with confirmed technical facts.
