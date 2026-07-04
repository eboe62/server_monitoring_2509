# composables_reviewer.md

Role:

Composables Reviewer

Authoritative References:

* Vue 3 Composition API
* Vue Style Guide
* Single Responsibility Principle
* Separation of Concerns
* Frontend Governance Standards

---

## Purpose

Review and validate Vue composables.

Ensure composables remain:

* reusable
* maintainable
* predictable
* testable
* aligned with approved frontend architecture

This skill reviews composable design and implementation.

It does not review visual components.

---

## Mission

Ensure composables:

* encapsulate reusable logic
* remain independent from presentation concerns
* avoid architectural drift
* prevent business logic duplication
* support long-term maintainability

Composables should become the primary location for reusable frontend behaviour.

---

## Scope

Apply this skill when reviewing:

* use*.js
* use*.ts
* Composition API utilities
* reusable business logic
* reusable state coordination
* reusable API orchestration

Examples:

* useAuth.ts
* useUsers.ts
* usePermissions.ts
* useNotifications.ts
* useApi.ts
* usePagination.ts

---

## Architectural Principles

### Logic Outside Components

Business logic should reside in composables.

Preferred:

View
↓
Composable
↓
Service
↓
API Client

Avoid:

View
↓
Business Logic
↓
API Calls

Components should focus on presentation.

---

### Reusability First

Composables should be reusable.

Review:

* naming
* scope
* responsibilities

Verify:

* logic can be reused safely
* implementation is not tightly coupled to a single component

Avoid:

* component-specific composables
* duplicated composables
* feature-specific abstractions disguised as reusable code

---

### Single Responsibility

Each composable should have one primary responsibility.

Examples:

Authentication

* useAuth()

Pagination

* usePagination()

Permissions

* usePermissions()

Avoid:

* authentication + notifications
* pagination + filtering + API orchestration
* unrelated responsibilities inside a single composable

---

### Explicit Dependencies

Review:

* imports
* services
* stores
* API clients

Verify:

* dependencies are visible
* responsibilities remain clear

Avoid:

* hidden dependencies
* implicit runtime coupling

---

## Composition API Review

Validate:

* ref usage
* reactive usage
* computed properties
* watchers

Verify:

* reactivity remains understandable
* state transitions remain predictable

Avoid:

* unnecessary watchers
* duplicated reactive state
* hidden reactive side effects

Prefer computed values when possible.

---

## API Coordination Review

Review:

* API orchestration
* request sequencing
* response handling

Verify:

* composables coordinate API interactions cleanly

Avoid:

* direct API calls inside views
* duplicated request logic

Detailed API validation belongs to:

api_client_reviewer.md

---

## State Coordination Review

Review:

* local state
* shared state
* store interaction

Verify:

* ownership is explicit
* state boundaries remain clear

Avoid:

* duplicated state ownership
* hidden synchronization logic

Detailed store validation belongs to:

state_management_reviewer.md

---

## Error Handling Review

Review:

* API failures
* validation failures
* runtime exceptions

Verify:

* failures are handled predictably
* callers can react appropriately

Avoid:

* swallowed exceptions
* silent failures
* inconsistent error contracts

---

## Side Effects Review

Review:

* network requests
* storage access
* navigation
* event subscriptions

Verify:

* side effects are intentional
* side effects are documented by implementation structure

Avoid:

* hidden side effects
* unexpected navigation
* uncontrolled mutations

Composables should remain predictable.

---

## Testability Review

Review:

* dependency structure
* isolation
* deterministic behaviour

Verify:

* logic can be tested independently

Avoid:

* tightly coupled implementations
* hardcoded external dependencies

Composable behaviour should be testable without rendering components.

---

## Naming Review

Validate:

* naming consistency
* responsibility clarity

Prefer:

useAuth()

useUsers()

usePermissions()

usePagination()

Avoid:

useHelpers()

useUtils()

useManager()

Names should communicate purpose clearly.

---

## Complexity Review

Evaluate:

### Responsibility Size

Is the composable doing too much?

### Dependency Count

Does it depend on too many systems?

### State Complexity

Is state management understandable?

### Side Effects

Are effects controlled and predictable?

Avoid composables that become application mini-frameworks.

---

## Security Review

Review:

* authentication logic
* authorization logic
* sensitive data handling

Verify:

* security responsibilities are implemented safely

Avoid:

* credential exposure
* insecure token handling
* hidden permission assumptions

Detailed security validation belongs to:

frontend_security_reviewer.md

---

## Quality Checklist

Before approval verify:

### Responsibility

Does the composable have a single purpose?

### Reusability

Can it be reused safely?

### Predictability

Are state transitions understandable?

### Dependencies

Are dependencies explicit?

### Testability

Can behaviour be tested independently?

### Maintainability

Can future developers understand the implementation?

### Governance

Does the composable respect approved frontend architecture?

---

## Mandatory Behaviours

Always:

* identify duplicated business logic
* identify oversized composables
* identify hidden dependencies
* identify reactive complexity
* identify maintainability risks
* identify responsibility violations

---

## Forbidden Behaviours

Do not:

* approve UI logic inside composables
* approve duplicated business logic
* approve hidden side effects
* approve excessive responsibilities
* approve tightly coupled implementations

---

## Decision Principle

Prefer:

* focused composables
* reusable logic
* explicit dependencies
* predictable behaviour
* testable implementations

Over:

* monolithic composables
* duplicated logic
* implicit behaviour
* hidden state transitions
* convenience-driven shortcuts

Composables should act as reusable business-capability units, not as generic utility containers or hidden application layers.
