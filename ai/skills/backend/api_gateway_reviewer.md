# api_gateway_reviewer.md

## Purpose

This skill reviews API Gateway implementations in distributed backend architectures.

Its objective is to ensure:

* clear separation of responsibilities
* proper service orchestration
* maintainable routing strategies
* controlled aggregation logic
* secure service exposure

This skill does not define architecture.

Architecture remains governed by:

* User instructions
* Approved ADRs
* AI Constitution
* Project documentation

---

## Review Scope

Apply this skill when reviewing:

* API Gateway modules
* Spring Cloud Gateway implementations
* OpenFeign integrations
* WebClient integrations
* gateway controllers
* service aggregation logic
* cross-service orchestration

Examples:

* RouteLocator configuration
* FeignClient definitions
* Gateway service implementations
* Public API controllers
* Request forwarding logic

---

## Core Principles

### Gateway as Orchestrator

The API Gateway should orchestrate requests.

The Gateway should not become a business domain.

Prefer:

* routing
* aggregation
* protocol translation
* authentication
* authorization
* request validation
* response composition

Avoid:

* domain business rules
* persistence logic
* repository access
* entity ownership

---

### Service Ownership

Business rules belong to the owning microservice.

The Gateway should consume services.

The Gateway should not replicate service logic.

Flag situations where:

* validation logic is duplicated
* business rules are duplicated
* data ownership becomes unclear

---

### API Consistency

Public APIs should remain predictable.

Review:

* endpoint naming
* request structure
* response structure
* error handling
* versioning strategy

Prefer consistency across all exposed endpoints.

---

### Aggregation Discipline

Aggregation should be intentional.

Accept:

* combining multiple service responses
* building composite DTOs
* simplifying frontend consumption

Flag:

* excessive chaining
* hidden business workflows
* orchestration complexity that belongs elsewhere

---

### DTO Isolation

Gateway DTOs should remain independent from persistence models.

Prefer:

* Request DTOs
* Response DTOs
* Composite DTOs

Avoid:

* exposing JPA entities
* exposing internal database structures
* leaking service implementation details

---

### Error Handling

Review:

* exception propagation
* timeout handling
* fallback strategies
* service unavailability behaviour

Ensure predictable client responses.

Avoid exposing internal stack traces.

---

### Security Review

Validate:

* authentication flow
* authorization enforcement
* endpoint exposure
* sensitive data handling

Flag:

* trust assumptions
* unrestricted internal endpoints
* excessive information disclosure

---

### Service Communication

Review:

* FeignClient usage
* WebClient usage
* retry behaviour
* timeout configuration

Prefer:

* deterministic communication
* explicit error handling
* observable failure modes

Avoid:

* hidden retries
* silent failures
* uncontrolled cascading calls

---

### Observability

Review:

* request tracing
* correlation identifiers
* structured logging
* auditability

The Gateway should improve visibility across services.

---

## Anti-Patterns

Flag:

* business logic implemented in Gateway controllers
* repository access from Gateway
* direct database access from Gateway
* duplicated service validations
* entity exposure
* uncontrolled aggregation chains
* excessive service coupling
* hidden orchestration workflows
* inconsistent API contracts

---

## Expected Review Output

When reviewing an API Gateway implementation:

1. Context
2. Findings
3. Architectural Risks
4. Security Risks
5. Maintainability Risks
6. Recommendations
7. Required Validations

Distinguish clearly between:

* confirmed findings
* assumptions
* recommendations

Never present assumptions as facts.

---

## Escalation Rules

If the review affects:

* service boundaries
* ownership responsibilities
* API contracts
* architectural decisions

request ADR validation before implementation.

Do not approve architectural changes without verifying ADR compliance.
