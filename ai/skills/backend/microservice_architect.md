# microservice_architect.md

## Purpose

This skill reviews and evaluates microservice architectures.

Its objective is to ensure:

* clear domain boundaries
* proper service ownership
* controlled dependencies
* maintainable service interactions
* long-term architectural sustainability

This skill does not define architecture.

Architecture remains governed by:

* User instructions
* Approved ADRs
* AI Constitution
* Project documentation

---

## Review Scope

Apply this skill when reviewing:

* microservice architectures
* service decomposition
* domain boundaries
* service ownership
* service interactions
* API contracts
* inter-service communication

Examples:

* Spring Boot microservices
* REST service ecosystems
* service responsibilities
* domain modelling decisions
* service extraction proposals
* service consolidation proposals

---

## Core Principles

### Single Responsibility

Each microservice should own a clearly defined business capability.

Prefer:

* cohesive responsibilities
* well-defined ownership
* bounded functionality

Avoid:

* multi-domain services
* mixed responsibilities
* generic catch-all services

A service should have a clear reason to exist.

---

### Domain Ownership

Every business domain should have a single authoritative owner.

Prefer:

* explicit ownership
* clear responsibility boundaries

Avoid:

* shared ownership
* duplicated responsibilities
* competing sources of truth

Ownership ambiguity increases operational risk.

---

### Data Ownership

Each service owns its data.

Prefer:

* service-owned databases
* service-owned schemas
* service-owned persistence logic

Avoid:

* direct database sharing
* cross-service table access
* cross-service repository access

Services communicate through contracts, not databases.

---

### Contract-Driven Communication

Interactions between services should be explicit.

Review:

* REST APIs
* asynchronous events
* messaging contracts
* integration boundaries

Prefer:

* documented contracts
* versioned APIs
* backward compatibility

Avoid:

* hidden dependencies
* undocumented interfaces
* implicit behaviour

---

### Loose Coupling

Services should remain independently evolvable.

Review:

* dependency chains
* synchronous dependencies
* deployment dependencies

Prefer:

* autonomy
* explicit contracts
* controlled integrations

Flag:

* tight coupling
* circular dependencies
* dependency explosions

---

### Service Cohesion

Business rules should remain close to the owning domain.

Prefer:

* localized business logic
* cohesive implementations

Avoid:

* logic fragmentation
* duplicated business rules
* orchestration replacing ownership

High cohesion reduces maintenance costs.

---

### Scalability Boundaries

Review whether service decomposition supports future growth.

Consider:

* workload isolation
* deployment independence
* scaling requirements

Flag:

* artificial decomposition
* unnecessary fragmentation
* premature microservices

Microservices must solve a real problem.

---

### Resilience

Review:

* service availability
* failure isolation
* timeout strategies
* retry strategies
* degradation behaviour

Prefer:

* predictable failure modes
* controlled degradation
* resilience by design

Avoid:

* cascading failures
* uncontrolled retries
* systemic dependency chains

---

### Service Discoverability

Services should be understandable by new contributors.

Review:

* naming consistency
* domain alignment
* repository structure
* API discoverability

Prefer:

* descriptive service names
* explicit ownership
* predictable architecture

---

### Security Boundaries

Review:

* trust boundaries
* service authentication
* service authorization
* internal exposure

Prefer:

* least privilege
* explicit trust relationships
* controlled exposure

Avoid:

* implicit trust
* unrestricted internal access
* excessive privilege sharing

---

## Data Consistency

Review consistency requirements carefully.

Prefer:

* eventual consistency when appropriate
* transaction ownership by the owning service

Avoid:

* distributed transactions without justification
* hidden consistency assumptions

Flag:

* unclear ownership of business state
* conflicting data authorities

---

## Evolution Strategy

Review the ability to evolve services independently.

Consider:

* API versioning
* backward compatibility
* migration paths
* deprecation policies

Prefer:

* incremental evolution
* compatibility strategies

Avoid:

* breaking changes without migration plans
* undocumented contract changes

---

## Anti-Patterns

Flag:

* shared databases
* shared repositories
* shared entity ownership
* duplicated business rules
* circular dependencies
* service-to-service database access
* distributed monoliths
* excessive orchestration
* undocumented contracts
* artificial service decomposition
* chatty service interactions

---

## Architectural Review Criteria

Evaluate:

### Domain Alignment

Does the service represent a coherent business capability?

### Ownership Clarity

Is ownership clearly defined?

### Dependency Control

Are dependencies explicit and manageable?

### Contract Quality

Are APIs stable and understandable?

### Operational Sustainability

Can the service be maintained independently?

### Future Evolution

Can the service evolve without destabilizing the ecosystem?

---

## Expected Review Output

When reviewing a microservice architecture:

1. Context
2. Domain Analysis
3. Ownership Analysis
4. Dependency Analysis
5. Data Ownership Review
6. Architectural Risks
7. Security Risks
8. Maintainability Risks
9. Recommendations
10. Required Validations

Distinguish clearly between:

* confirmed findings
* assumptions
* recommendations

Never present assumptions as facts.

---

## Escalation Rules

If the review affects:

* domain ownership
* service boundaries
* API contracts
* data ownership
* architectural decomposition
* service consolidation

request ADR validation before implementation.

Do not approve architectural changes without verifying ADR compliance.

---

## Decision Principle

Prefer:

* clear ownership
* simple architectures
* explicit contracts
* independent evolution

Over:

* excessive decomposition
* premature optimization
* architectural complexity without demonstrated value

Architectural simplicity should be preserved whenever possible.
