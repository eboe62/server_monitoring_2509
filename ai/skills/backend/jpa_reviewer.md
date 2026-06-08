# jpa_reviewer.md

## Purpose

This skill reviews JPA and Hibernate persistence implementations.

Its objective is to ensure:

* correct persistence design
* maintainable entity models
* efficient database access
* predictable transactional behaviour
* long-term scalability

This skill focuses on persistence architecture.

It does not define:

* system architecture
* microservice boundaries
* business requirements

These remain governed by:

* User instructions
* Approved ADRs
* AI Constitution
* Project documentation
* Spring Architect reviews

---

## Review Scope

Apply this skill when reviewing:

* JPA entities
* Hibernate mappings
* repositories
* JPQL queries
* Criteria queries
* entity relationships
* persistence configurations
* transactional persistence logic

Examples:

* @Entity classes
* @Repository implementations
* JpaRepository interfaces
* entity relationships
* custom queries
* persistence services

---

## Core Principles

### Persistence Simplicity

Persistence models should remain understandable.

Prefer:

* explicit mappings
* predictable relationships
* maintainable entities

Avoid:

* unnecessary complexity
* hidden persistence behaviour
* over-engineered mappings

---

### Entity Responsibility

Entities represent persisted domain state.

Prefer:

* persistence-focused entities
* clear ownership

Avoid:

* infrastructure responsibilities
* controller concerns
* excessive business orchestration

Entities should remain focused.

---

### Explicit Mapping

Relationships should be explicit.

Review:

* @OneToOne
* @OneToMany
* @ManyToOne
* @ManyToMany

Prefer:

* intentional relationships
* documented ownership

Avoid:

* unclear ownership
* accidental bidirectional complexity

Every relationship should have a clear purpose.

---

### Bidirectional Relationship Control

Bidirectional mappings increase complexity.

Prefer:

* unidirectional mappings when sufficient

Use bidirectional relationships only when justified.

Review:

* navigation requirements
* maintenance costs
* serialization risks

Avoid:

* unnecessary bidirectional relationships

---

### Lazy Loading First

Prefer:

* LAZY loading by default

Review:

* fetch strategy decisions

Avoid:

* indiscriminate EAGER loading

EAGER loading requires explicit justification.

---

### N+1 Query Prevention

Review:

* repository queries
* entity relationships
* fetch strategies

Identify:

* N+1 risks
* excessive query generation
* hidden database access

Prefer:

* fetch joins
* entity graphs
* optimized queries

Avoid:

* repeated query execution patterns

---

### Repository Responsibility

Repositories manage persistence access.

Prefer:

* persistence operations
* query execution

Avoid:

* business logic
* orchestration logic
* workflow decisions

Repositories should remain persistence-focused.

---

### Transaction Ownership

Review:

* transactional boundaries
* transaction scope

Prefer:

* service-level transaction ownership

Avoid:

* controller-managed transactions
* repository-managed business transactions

Transactions should support business consistency.

---

### Query Clarity

Review:

* JPQL queries
* native queries
* criteria queries

Prefer:

* readable queries
* maintainable queries

Avoid:

* opaque query logic
* unnecessary complexity

Query intent should remain understandable.

---

### Native Query Governance

Prefer:

* JPQL when sufficient

Use native SQL only when justified by:

* performance
* database-specific requirements
* unsupported JPA features

Native queries require documentation.

---

### DTO Projection Strategy

Review:

* projection usage
* entity exposure

Prefer:

* DTO projections for read models
* explicit contracts

Avoid:

* loading full entities unnecessarily

Read operations should retrieve only required data.

---

### Pagination

Review:

* large dataset retrieval
* API responses

Prefer:

* pagination
* bounded result sets

Avoid:

* unbounded queries
* full table retrieval

Large datasets should remain controllable.

---

### Entity Identity

Review:

* primary keys
* equality implementations

Prefer:

* stable identifiers
* explicit identity management

Avoid:

* mutable identity
* inconsistent equality definitions

Entity identity should remain predictable.

---

### Cascade Governance

Review:

* CascadeType usage

Prefer:

* minimal required cascades

Avoid:

* CascadeType.ALL by default

Cascade behaviour should be intentional.

---

### Orphan Removal Governance

Review:

* orphanRemoval usage

Prefer:

* explicit ownership models

Avoid:

* orphan removal without ownership clarity

Lifecycle behaviour should remain predictable.

---

### Auditing

Review:

* creation timestamps
* update timestamps
* auditing requirements

Prefer:

* explicit auditing policies

Avoid:

* hidden auditing behaviour

Auditing should be understandable.

---

### Concurrency Management

Review:

* concurrent updates
* optimistic locking
* pessimistic locking

Prefer:

* optimistic locking when appropriate

Review:

* @Version usage

Avoid:

* silent overwrite risks

Concurrency behaviour should be explicit.

---

### Entity Serialization

Review:

* API exposure
* JSON serialization

Prefer:

* DTO-based exposure

Avoid:

* direct entity exposure
* serialization loops
* persistence leakage

Entities are persistence models, not API contracts.

---

### Database Portability

Review:

* database-specific features

Prefer:

* vendor-neutral persistence

Avoid:

* unnecessary database lock-in

Portability should be preserved unless ADR-approved.

---

## Performance Review

Evaluate:

### Query Count

Are unnecessary queries generated?

### Fetch Strategy

Are relationships loaded efficiently?

### Data Volume

Are queries retrieving excessive data?

### Pagination

Are large datasets controlled?

### Transaction Scope

Are transactions appropriately bounded?

---

## Data Integrity Review

Evaluate:

### Relationship Consistency

Are relationships correctly defined?

### Referential Integrity

Can invalid references occur?

### Cascade Safety

Can unexpected modifications occur?

### Concurrency Protection

Can data races occur?

---

## Security Review

Review:

* SQL injection risks
* dynamic query generation
* repository exposure

Prefer:

* parameterized queries
* controlled query generation

Avoid:

* string-concatenated queries
* unsafe native SQL construction

Persistence layers should not introduce security vulnerabilities.

---

## Common Risks

Review for:

* N+1 queries
* EAGER loading abuse
* oversized transactions
* entity leakage
* missing pagination
* inefficient queries
* unnecessary cascades
* orphan lifecycle issues
* serialization loops
* concurrency conflicts

---

## Anti-Patterns

Flag:

* CascadeType.ALL everywhere
* EAGER by default
* business logic in repositories
* entity exposure through APIs
* unbounded queries
* repository orchestration logic
* controller-managed transactions
* native queries without justification
* missing pagination
* serialization of entity graphs
* bidirectional relationships without need

---

## Expected Review Output

When reviewing JPA implementations:

1. Context
2. Entity Model Review
3. Relationship Review
4. Repository Review
5. Query Review
6. Transaction Review
7. Performance Review
8. Data Integrity Review
9. Risks
10. Recommendations
11. Required Validations

Distinguish clearly between:

* confirmed findings
* assumptions
* recommendations

Never present assumptions as facts.

---

## Escalation Rules

If the review affects:

* persistence architecture
* entity ownership models
* transaction strategy
* database portability
* data lifecycle policies

request ADR validation before implementation.

Do not approve persistence architecture changes without verifying ADR compliance.

---

## Decision Principle

Prefer:

* explicit mappings
* lazy loading
* repository simplicity
* service-owned transactions
* DTO-based contracts
* predictable persistence behaviour

Over:

* hidden ORM behaviour
* eager loading
* repository business logic
* uncontrolled cascades
* entity exposure

Persistence should remain understandable, predictable and scalable.
