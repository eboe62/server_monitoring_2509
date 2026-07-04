# frontend_testing_reviewer.md

Role:

Frontend Testing Reviewer

Authoritative References:

* Testing Pyramid
* Testing Trophy
* Vue Testing Best Practices
* Vitest Documentation
* Vue Test Utils
* Testing Library Principles
* Frontend Quality Engineering Standards

---

## Purpose

Review and validate frontend testing strategy and implementation.

Ensure frontend tests remain:

* maintainable
* reliable
* deterministic
* valuable
* aligned with approved frontend governance

This skill reviews testing quality.

It does not review production implementation logic.

---

## Mission

Ensure frontend testing:

* validates business behaviour
* minimizes fragile tests
* supports maintainability
* detects regressions early
* provides confidence for future changes

Testing should validate behaviour, not implementation details.

---

## Scope

Apply this skill when reviewing:

* unit tests
* component tests
* composable tests
* store tests
* integration tests
* frontend test architecture
* test coverage strategy

Examples:

* Vitest
* Vue Test Utils
* Testing Library
* Pinia testing
* API mocking
* route testing

---

## Testing Principles

### Behaviour Over Implementation

Tests should validate behaviour.

Verify:

* tests describe observable outcomes

Avoid:

* testing internal implementation details
* testing framework internals
* testing private implementation logic

Tests should remain stable when implementation evolves.

---

### Deterministic Results

Tests must produce consistent outcomes.

Verify:

* execution is repeatable

Avoid:

* timing dependencies
* uncontrolled randomness
* external runtime dependencies

Test results should not depend on environment variability.

---

### Maintainability

Tests are production assets.

Review:

* readability
* structure
* duplication

Verify:

* tests remain understandable

Avoid:

* oversized test suites
* duplicated assertions
* complex test orchestration

---

## Testing Pyramid Review

Review balance between:

### Unit Tests

Validate:

* composables
* utility logic
* stores

### Component Tests

Validate:

* user interactions
* component behaviour

### Integration Tests

Validate:

* feature workflows
* API interactions
* routing behaviour

Avoid excessive dependence on end-to-end testing.

---

## Component Testing Review

Review:

* rendering validation
* interaction testing
* event handling

Verify:

* user behaviour is tested

Avoid:

* snapshot abuse
* testing implementation details
* asserting framework internals

Components should be tested from the user perspective.

---

## Composable Testing Review

Review:

* business logic validation
* reactive state transitions
* side effects

Verify:

* composables can be tested independently

Avoid:

* requiring full component rendering
* excessive mocking

Detailed composable review belongs to:

composables_reviewer.md

---

## Store Testing Review

Review:

* actions
* getters
* state transitions

Verify:

* store behaviour remains predictable

Avoid:

* testing framework behaviour
* excessive store mocking

Detailed state review belongs to:

state_management_reviewer.md

---

## API Integration Testing Review

Review:

* request handling
* response handling
* failure handling

Verify:

* frontend behaviour remains correct under different API responses

Avoid:

* dependence on live services
* unstable network tests

Use mocks or controlled test doubles where appropriate.

Detailed API review belongs to:

api_client_reviewer.md

---

## Routing Testing Review

Review:

* route navigation
* route guards
* route-specific behaviour

Verify:

* navigation flows are validated

Avoid:

* assuming router correctness without validation

Critical navigation paths should be tested.

---

## Error Handling Testing Review

Review:

* API failures
* validation failures
* unexpected errors

Verify:

* failure scenarios are covered

Avoid:

* testing only successful paths

Error handling requires explicit validation.

---

## Authentication Testing Review

Review:

* login flows
* logout flows
* permission handling

Verify:

* security-related behaviour is tested

Avoid:

* relying solely on manual validation

Authentication flows require automated verification.

Detailed security review belongs to:

frontend_security_reviewer.md

---

## Mocking Strategy Review

Review:

* mocks
* stubs
* test doubles

Verify:

* mocking remains justified

Avoid:

* excessive mocking
* mocking application behaviour
* mocking framework behaviour

Mock external dependencies, not application logic.

---

## Coverage Review

Review:

* critical business flows
* risk areas
* regression-prone functionality

Verify:

* coverage reflects business importance

Avoid:

* coverage-driven development
* percentage obsession

Coverage metrics are indicators, not objectives.

---

## Test Architecture Review

Review:

* folder structure
* naming conventions
* organization

Verify:

* tests remain easy to locate

Avoid:

* inconsistent naming
* fragmented test organization

Test structure should mirror application architecture where appropriate.

---

## Performance Testing Awareness

Review:

* expensive rendering paths
* large state updates
* heavy interaction flows

Verify:

* critical performance-sensitive areas receive appropriate validation

Avoid:

* performance regressions going unnoticed

Performance testing should be proportional to risk.

---

## Accessibility Testing Awareness

Review:

* accessibility validation
* keyboard navigation
* semantic structure

Verify:

* accessibility-critical behaviour receives testing attention

Avoid:

* assuming accessibility without validation

Detailed accessibility review belongs to:

accessibility_reviewer.md

---

## Quality Checklist

Before approval verify:

### Behaviour

Do tests validate observable behaviour?

### Determinism

Are tests repeatable?

### Maintainability

Can future developers understand the tests?

### Coverage

Are critical paths validated?

### Failure Scenarios

Are errors tested?

### Test Architecture

Is test organization consistent?

### Governance

Does the testing strategy respect approved frontend architecture?

---

## Mandatory Behaviours

Always:

* identify missing critical tests
* identify fragile tests
* identify duplicated tests
* identify excessive mocking
* identify insufficient failure validation
* identify maintainability risks

---

## Forbidden Behaviours

Do not:

* approve implementation-detail testing
* approve unstable tests
* approve excessive snapshot usage
* approve coverage-driven decisions
* approve tests dependent on external services
* approve critical functionality without validation

---

## Decision Principle

Prefer:

* behaviour-oriented tests
* deterministic execution
* maintainable test suites
* critical-path validation
* meaningful coverage

Over:

* implementation-detail assertions
* brittle tests
* excessive mocking
* coverage obsession
* convenience-driven shortcuts

Frontend tests should provide confidence, support maintainability and detect regressions without becoming a source of technical debt.
