# Request Priority Analysis Template

## Priority Information

Priority Identifier:

Priority Title:

Priority Source Document:

Priority Status:

---

## Objective

Describe the intended outcome.

What problem is being solved?

Why is this priority important?

---

## Current State

Describe the current implementation.

Include:

* services
* configurations
* controls
* limitations

---

## Applicable ADRs

List all relevant ADRs.

For each ADR:

* identifier
* title
* relevance

---

## Available Evidence

Provide:

* logs
* docker inspect output
* metrics
* configuration
* runtime inspection
* audit results

---

## Constraints

Examples:

* no architecture redesign
* no downtime
* Docker Compose only
* single-node architecture
* upstream compatibility
* preserve observability

---

## Required Analysis

The analysis must include:

1. Current State Assessment
2. Runtime Evidence Review
3. Risk Assessment
4. Architectural Impact
5. Operational Impact
6. Security Impact
7. Options Analysis
8. Recommended Approach
9. Validation Plan
10. Rollback Strategy

---

## Evidence Classification

Classify findings as:

CONFIRMED

PROBABLE

UNCONFIRMED

INCORRECT

---

## Required Deliverable

Provide:

Executive Summary

Findings

Risks

Options

Recommendation

Validation Requirements

Rollback Requirements

Closure Criteria

---

## Explicitly Forbidden

Do not:

* implement changes
* generate code
* redesign architecture
* assume runtime behaviour
* classify findings without evidence

Analysis only.

Implementation requires a separate Execution Request.
