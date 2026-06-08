# spring_architect.md

## Purpose

This skill reviews Spring Boot application architecture and implementation practices.

Its objective is to ensure:

* clean architectural layering
* maintainable service design
* proper dependency management
* clear separation of concerns
* long-term maintainability

This skill does not define system architecture.

System architecture remains governed by:

* User instructions
* Approved ADRs
* AI Constitution
* Project documentation
* Microservice Architect reviews

---

## Review Scope

Apply this skill when reviewing:

* Spring Boot applications
* service implementations
* controller implementations
* dependency injection patterns
* application structure
* business service design
* configuration management

Examples:

* @RestController classes
* @Service classes
* @Component implementations
* configuration classes
* Spring Boot modules
* package organization

---

## Core Principles

### Layered Architecture

Applications should maintain clear architectural layers.

Typical layers:

* controller
* service
* repository
* domain/model

Responsibilities should remain separated.

Avoid:

* controllers containing business logic
* repositories containing business logic
* service bypasses

---

### Separation of Concerns

Each component should have a single responsibility.

Prefer:

* focused services
* focused controllers
* focused repositories

Avoid:

* multi-purpose services
* utility dumping grounds
* god classes

A class should have one reason to change.

---

### Dependency Direction

Dependencies should flow inward.

Prefer:

```text
Controller
    ↓
Service
    ↓
Repository
```

Avoid:

```text
Repository
    ↓
Service
```

or

```text
Controller
    ↓
Repository
```

without architectural justification.

---

### Constructor Injection

Prefer constructor injection.

Review:

* dependency management
* immutability
* testability

Prefer:

* constructor injection
* final dependencies

Avoid:

* field injection
* hidden dependencies

---

### Service Design

Services should contain business behaviour.

Prefer:

* business-oriented methods
* domain-oriented operations
* explicit workflows

Avoid:

* anemic services
* pass-through services
* controllers implementing business rules

Business rules belong in services.

---

### Controller Design

Controllers should act as adapters.

Prefer:

* request validation
* request mapping
* response mapping

Avoid:

* business logic
* persistence logic
* orchestration complexity

Controllers should remain thin.

---

### Configuration Management

Configuration should remain externalized.

Review:

* application.yml
* application.properties
* environment variables
* configuration classes

Prefer:

* explicit configuration
* environment-driven values

Avoid:

* hardcoded configuration
* environment-specific logic in code

---

### Bean Management

Review:

* bean lifecycle
* bean scope
* bean registration

Prefer:

* explicit dependencies
* predictable initialization

Avoid:

* unnecessary bean complexity
* hidden application state

---

### Package Organization

Packages should reflect architecture.

Prefer:

```text
controller/
service/
repository/
model/
config/
dto/
```

or approved domain-oriented structures.

Avoid:

* arbitrary package structures
* mixed responsibilities

Package organization should support discoverability.

---

### DTO Usage

Review:

* Request DTOs
* Response DTOs
* Internal DTOs

Prefer:

* explicit contracts
* isolated transport objects

Avoid:

* exposing entities directly
* leaking persistence models

DTOs should define API contracts.

---

### Validation Strategy

Review:

* Bean Validation
* request validation
* business validation

Prefer:

* validation at boundaries
* business validation in services

Avoid:

* duplicated validation logic
* inconsistent validation behaviour

---

### Exception Handling

Review:

* exception propagation
* exception translation
* global exception handling

Prefer:

* predictable API responses
* centralized exception management

Avoid:

* generic exception swallowing
* stack trace exposure
* inconsistent error contracts

---

### Transaction Management

Review:

* transactional boundaries
* transaction ownership
* rollback behaviour

Prefer:

* service-level transaction ownership
* explicit transaction scopes

Avoid:

* controller-managed transactions
* repository-managed business transactions

Transactions should support business consistency.

---

### Spring Boot Simplicity

Prefer:

* standard Spring Boot patterns
* framework conventions
* maintainable code

Avoid:

* unnecessary abstractions
* custom frameworks
* excessive indirection

Complexity requires justification.

---

## Security Review

Review:

* endpoint exposure
* configuration exposure
* secret handling
* authorization enforcement

Flag:

* hardcoded credentials
* unrestricted endpoints
* sensitive information leakage

---

## Maintainability Review

Evaluate:

### Readability

Can a new developer understand the implementation?

### Testability

Can components be tested independently?

### Dependency Clarity

Are dependencies explicit?

### Configuration Clarity

Is runtime behaviour understandable?

### Responsibility Clarity

Does each component have a clear purpose?

---

## Anti-Patterns

Flag:

* fat controllers
* anemic services
* god services
* field injection
* entity exposure
* business logic in controllers
* business logic in repositories
* hardcoded configuration
* duplicated validation logic
* circular dependencies
* utility dumping classes
* hidden framework magic

---

## Expected Review Output

When reviewing a Spring Boot application:

1. Context
2. Layering Analysis
3. Dependency Analysis
4. Configuration Review
5. Security Review
6. Maintainability Review
7. Architectural Risks
8. Recommendations
9. Required Validations

Distinguish clearly between:

* confirmed findings
* assumptions
* recommendations

Never present assumptions as facts.

---

## Escalation Rules

If the review affects:

* architectural layers
* service responsibilities
* package structure standards
* application boundaries
* transaction ownership

request ADR validation before implementation.

Do not approve architectural changes without verifying ADR compliance.

---

## Decision Principle

Prefer:

* simplicity
* explicit dependencies
* framework conventions
* maintainable implementations

Over:

* clever abstractions
* unnecessary frameworks
* excessive indirection
* architectural complexity without demonstrated value

Code should remain understandable by the team responsible for maintaining it.
