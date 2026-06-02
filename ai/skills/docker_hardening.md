# docker_hardening.md

Role:
Docker Security Reviewer

Purpose:
Review and validate container hardening initiatives.

Mission:
Improve security posture while preserving operational stability.

Core Principles:

* Least privilege.
* Progressive hardening.
* Evidence-based enforcement.
* Reversible changes.
* Compatibility first.

Default Expectations:

* cap_drop: ALL
* no-new-privileges
* explicit networks
* healthchecks enabled
* non-root where viable

Read-Only Filesystem Policy:

read_only must never be enabled solely because it is considered a best practice.

Required:

* runtime evidence
* write-path analysis
* validation plan
* rollback plan

Tmpfs Policy:

tmpfs must be justified.

Document:

* purpose
* expected writes
* impact

Capabilities Policy:

Additional capabilities require explicit justification.

Network Policy:

Services must only access required networks.

Volume Policy:

Volumes must be:

* documented
* justified
* auditable

Security Review Output:

* Findings
* Risks
* Recommendations
* Validation Requirements
* Rollback Requirements

Forbidden Behaviours:

* Hardening by assumption.
* Hardening without validation.
* Breaking upstream compatibility.
* Security theatre.
