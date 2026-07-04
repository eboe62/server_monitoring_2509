# backend_testing_reviewer.md

## Purpose

This skill reviews backend testing strategies and test implementations.

Its objective is to ensure:

* reliable test coverage
* maintainable test suites
* appropriate test isolation
* meaningful validation
* long-term confidence in system behaviour

This skill reviews testing quality.

It does not define:

* system architecture
* business requirements
* implementation decisions

Architecture remains governed by:

* User instructions
* Approved ADRs
* AI Constitution
* Project documentation

---

## Review Scope

Apply this skill when reviewing:

* unit tests
* integration tests
* service tests
* controller tests
* repository tests
* API tests
* test strategies
* test coverage proposals

Examples:

* JUnit tests
* Mockito tests
* Spring Boot tests
* MockMvc tests
* repository validations
* service behaviour tests

---

## Core Principles

### Test Purpose Clarity

Every test should validate a specific behaviour.

Prefer:

* focused tests
* single-purpose validations
* explicit expectations

Avoid:

* oversized tests
* multi-purpose tests
* unclear intentions

A reader should immediately understand what is being verified.

---

### Behaviour Over Implementation

Tests should validate behaviour.

Prefer:

* observable outcomes
* business behaviour
* contract validation

Avoid:

* implementation details
* internal framework mechanics
* unnecessary private logic validation

Tests should survive refactoring.

---

### Isolation

Unit tests should remain isolated.

Review:

* dependency mocking
* service boundaries
* external integrations

Prefer:

* deterministic execution
* isolated dependencies

Avoid:

* hidden external dependencies
* environmental assumptions
* unstable execution conditions

---

### Deterministic Results

Tests should produce consistent outcomes.

Prefer:

* repeatable execution
* predictable assertions

Avoid:

* timing dependencies
* random behaviour
* environmental variability

Tests should not fail intermittently.

---

### Arrange Act Assert

Prefer:

```text
Arrange
Act
Assert
```

or

```text
Arrange
Act
Assert
Verify
```

when mocking is involved.

Structure should remain readable.

---

### Meaningful Assertions

Review:

* assertion quality
* validation depth

Prefer:

* business-relevant assertions
* explicit expected outcomes

Avoid:

* weak assertions
* superficial validation

A passing test should provide confidence.

---

### Mocking Discipline

Review:

* @Mock usage
* @InjectMocks usage
* dependency substitution

Prefer:

* mocking external dependencies
* mocking infrastructure boundaries

Avoid:

* excessive mocking
* mocking the system under test
* reproducing implementation details

Mocks should support isolation.

---

### Service Testing

Review:

* business rules
* workflow execution
* validation logic

Prefer:

* behaviour verification
* business outcome validation

Avoid:

* persistence assumptions
* framework behaviour testing

Service tests should validate business logic.

---

### Controller Testing

Review:

* endpoint behaviour
* request validation
* response generation

Prefer:

* contract verification
* status validation
* response validation

Avoid:

* duplicating service tests
* testing framework internals

Controllers should be tested as API boundaries.

---

### Repository Testing

Review:

* query behaviour
* persistence behaviour
* data access rules

Prefer:

* data-related validation
* repository responsibilities

Avoid:

* business rule testing
* service behaviour testing

Repositories should only validate persistence concerns.

---

### Integration Testing

Review:

* component interactions
* configuration validation
* contract integration

Prefer:

* realistic interactions
* critical workflow validation

Avoid:

* replacing all integration tests with mocks

Integration tests should validate system composition.

---

### Contract Validation

Review:

* API contracts
* DTO contracts
* service contracts

Prefer:

* explicit contract verification
* backward compatibility validation

Avoid:

* undocumented assumptions

Contracts should remain stable and testable.

---

### Test Naming

Review:

* readability
* intent communication

Prefer:

```text
shouldCreateUserWhenInputIsValid
shouldRejectRequestWhenTokenIsInvalid
```

Avoid:

```text
test1
validateStuff
checkMethod
```

Names should describe behaviour.

---

### Test Maintainability

Evaluate:

* readability
* duplication
* complexity

Prefer:

* clear setup
* reusable fixtures
* maintainable structure

Avoid:

* duplicated arrangements
* excessive complexity
* fragile tests

---

### Coverage Philosophy

Coverage is a signal, not a goal.

Prefer:

* meaningful coverage
* critical path validation
* business risk coverage

Avoid:

* coverage-driven development
* testing solely to increase percentages

Coverage metrics should support quality, not replace it.

---

## Security Testing Considerations

Review:

* authentication validation
* authorization validation
* input validation
* error handling validation

Prefer:

* security-sensitive path coverage
* access control verification

Avoid:

* assuming security behaviour without tests

---

## Common Testing Risks

Review for:

* missing negative scenarios
* missing boundary conditions
* insufficient validation
* hidden dependencies
* flaky tests
* duplicated tests
* unmaintainable test suites
* false positives
* false confidence

---

## Anti-Patterns

Flag:

* testing private methods
* excessive mocking
* implementation-driven tests
* duplicated assertions
* duplicated setup logic
* fragile timing-dependent tests
* environment-dependent tests
* weak assertions
* meaningless coverage goals
* tests without clear intent

---

## Test Pyramid Review

Review balance between:

### Unit Tests

Fast and isolated.

### Integration Tests

Validate component interaction.

### End-to-End Tests

Validate critical user workflows.

Avoid:

* over-reliance on end-to-end testing
* absence of integration testing
* absence of unit testing

Testing layers should complement each other.

---

## Expected Review Output

When reviewing backend testing:

1. Context
2. Test Strategy Review
3. Coverage Assessment
4. Isolation Assessment
5. Maintainability Review
6. Security Testing Review
7. Risks
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

* testing standards
* quality gates
* release criteria
* validation requirements

request ADR validation before implementation.

Do not approve testing policy changes without verifying ADR compliance.

---

## Decision Principle

Prefer:

* behaviour-focused tests
* deterministic execution
* maintainable test suites
* meaningful validation
* business-oriented coverage

Over:

* implementation-driven tests
* excessive mocking
* coverage chasing
* fragile test suites

Tests should increase confidence, not simply increase numbers.
