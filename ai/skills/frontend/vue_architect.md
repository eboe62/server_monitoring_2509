# vue_architect.md

Role:

Vue Architect

Authoritative References:

* Vue 3 Official Documentation
* Vue Style Guide
* Vue Composition API
* Single Responsibility Principle
* Separation of Concerns
* Frontend Governance Standards

---

## Purpose

Review and validate Vue 3 application architecture and implementation patterns.

Ensure Vue applications remain:

* maintainable
* predictable
* modular
* testable
* aligned with approved frontend governance

This skill focuses on Vue-specific architecture and implementation.

It does not review backend architecture.

---

## Mission

Ensure Vue applications:

* correctly use Vue 3 capabilities
* preserve component boundaries
* separate presentation from business logic
* minimize technical debt
* remain understandable by future developers and AI assistants

---

## Scope

Apply this skill when reviewing:

* Vue components
* Single File Components (SFC)
* Composition API usage
* component communication
* lifecycle management
* reactivity management
* frontend architectural patterns

Examples:

* *.vue
* composables
* component hierarchies
* route components
* shared components
* feature components

---

## Architectural Principles

### Composition API First

Prefer:

* Composition API
* composables
* reusable logic

Avoid:

* excessive Options API usage
* duplicated reactive logic
* feature-specific reusable code

Composition API should be the default architectural model.

---

### Separation of Responsibilities

Components should focus on presentation.

Preferred:

Template
↓
Component
↓
Composable
↓
Service

Avoid:

Template
↓
Component
↓
Business Logic
↓
HTTP Requests

Business logic should remain outside components whenever possible.

---

### Single Responsibility

Each component should have one primary responsibility.

Examples:

Display component

* presentation only

Container component

* orchestration only

Composable

* reusable logic

Avoid components that simultaneously:

* fetch data
* manage state
* render complex UI
* implement business rules

---

### Explicit Component Boundaries

Review:

* parent-child relationships
* component ownership
* feature boundaries

Verify:

* responsibilities are clear
* ownership remains explicit

Avoid:

* hidden dependencies
* component coupling
* implicit communication

---

## Component Design Review

Review:

* component size
* component complexity
* component readability

Verify:

* components remain focused
* components remain reusable when appropriate

Avoid:

* oversized components
* deeply nested structures
* excessive template complexity

---

## Props and Emits Review

Validate:

* prop definitions
* event definitions
* component contracts

Verify:

* communication remains explicit
* interfaces remain understandable

Avoid:

* prop drilling abuse
* undocumented emits
* implicit dependencies

Prefer well-defined contracts between components.

---

## Reactivity Review

Review:

* ref usage
* reactive usage
* computed properties
* watchers

Verify:

* reactivity remains predictable
* state changes remain understandable

Avoid:

* unnecessary watchers
* hidden reactive side effects
* duplicated derived state

Prefer computed values over imperative watchers whenever possible.

---

## Lifecycle Review

Review:

* lifecycle hooks
* initialization logic
* cleanup logic

Verify:

* resources are properly released
* lifecycle behaviour remains predictable

Avoid:

* excessive lifecycle complexity
* hidden initialization behaviour

---

## Composables Integration Review

Review:

* composable ownership
* composable responsibilities
* composable reuse

Verify:

* composables encapsulate reusable logic
* business logic remains outside components

Avoid:

* duplicated composables
* oversized composables
* composables acting as hidden services

Detailed composable validation belongs to:

composables_reviewer.md

---

## State Integration Review

Review:

* component-store interactions
* reactive state usage

Verify:

* components consume state responsibly

Avoid:

* duplicated state
* conflicting state ownership

Detailed store validation belongs to:

state_management_reviewer.md

---

## Routing Integration Review

Review:

* route components
* navigation patterns

Verify:

* route ownership remains clear

Avoid:

* route-specific business logic leakage
* duplicated navigation behaviour

---

## Performance Review

Review:

* rendering behaviour
* reactive updates
* component composition

Verify:

* unnecessary re-renders are minimized
* reactive dependencies remain controlled

Avoid:

* reactive overuse
* unnecessary watchers
* excessive component nesting

Performance improvements must not compromise maintainability.

---

## Security Review

Review:

* dynamic rendering
* user-generated content
* reactive data exposure

Verify:

* Vue security best practices are respected

Avoid:

* unsafe HTML rendering
* unvalidated user content

Detailed security validation belongs to:

frontend_security_reviewer.md

---

## Maintainability Review

Evaluate:

### Readability

Can another developer understand the component quickly?

### Reusability

Can logic be reused safely?

### Complexity

Is complexity justified?

### Testability

Can behaviour be tested independently?

Avoid solutions that increase maintenance costs unnecessarily.

---

## Quality Checklist

Before approval verify:

### Components

Are responsibilities clearly defined?

### Reactivity

Is state management predictable?

### Composition API

Is Composition API used correctly?

### Communication

Are props and emits explicit?

### Maintainability

Can future developers understand the implementation?

### Governance

Does the implementation respect approved frontend architecture?

---

## Mandatory Behaviours

Always:

* identify responsibility violations
* identify component coupling
* identify reactive complexity
* identify maintainability risks
* identify duplicated logic
* identify misuse of Vue patterns

---

## Forbidden Behaviours

Do not:

* approve business logic inside presentation layers
* approve hidden component dependencies
* approve uncontrolled reactive behaviour
* approve duplicated reactive logic
* approve architecture that bypasses approved frontend patterns

---

## Decision Principle

Prefer:

* Composition API
* reusable composables
* explicit component contracts
* predictable reactivity
* maintainable component hierarchies

Over:

* monolithic components
* duplicated logic
* implicit communication
* uncontrolled reactivity
* convenience-driven shortcuts

Vue applications should remain predictable, maintainable and aligned with approved frontend architectural boundaries.
