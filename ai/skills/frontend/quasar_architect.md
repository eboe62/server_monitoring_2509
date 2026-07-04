# Skill: Quasar Architect

Role:

Quasar Architect

Authoritative References:

* Quasar Framework Documentation
* Vue 3 Documentation
* Vue Style Guide
* Quasar Best Practices
* Material Design Principles
* Progressive Enhancement Principles

---

## Purpose

Review and validate the architectural use of Quasar Framework within frontend applications.

Ensure Quasar is used:

* consistently
* predictably
* maintainably
* efficiently
* in alignment with approved frontend governance

This skill reviews architectural integration.

It does not review business logic.

---

## Mission

Ensure Quasar remains:

* a presentation framework
* a UI composition layer
* a productivity accelerator

and does not become:

* a business logic container
* a state management mechanism
* an architectural dependency that restricts future evolution

---

## Scope

Apply this skill when reviewing:

* Quasar components
* Quasar layouts
* Quasar boot files
* Quasar plugins
* Quasar configuration
* responsive design implementation
* platform-specific integrations

Examples:

* QLayout
* QPage
* QDrawer
* QHeader
* QFooter
* QTable
* QForm
* QDialog
* Notify
* Loading
* Dark Mode
* Boot Files

---

## Architectural Principles

### Framework as UI Layer

Quasar is a presentation framework.

Responsibilities:

* visual composition
* UI interaction
* responsive behaviour
* platform integration

Avoid:

* business rules
* persistence logic
* authorization logic
* domain orchestration

Business logic belongs elsewhere.

---

### Vue-First Architecture

Vue remains the architectural foundation.

Verify:

* Vue conventions remain dominant

Avoid:

* Quasar-specific patterns replacing Vue architecture

Preferred:

View
↓
Composable
↓
Store
↓
API

Not:

View
↓
Quasar Utility
↓
Hidden Application Logic

---

### Separation of Concerns

Verify:

UI concerns remain separated from:

* state management
* business logic
* API integration

Avoid:

* API calls inside UI components
* business workflows inside dialogs
* domain logic inside layouts

---

## Layout Architecture Review

Review:

* application layouts
* navigation structure
* responsive behaviour

Verify:

* layouts remain reusable

Avoid:

* feature-specific layouts
* duplicated layout structures
* business logic embedded in layouts

Layouts should define structure, not behaviour.

---

## Component Usage Review

Review:

* component selection
* component composition

Verify:

* Quasar components are used appropriately

Avoid:

* unnecessary custom implementations
* overengineering standard UI behaviour

Prefer native Quasar capabilities when suitable.

---

## Responsive Design Review

Review:

* breakpoints
* adaptive layouts
* mobile behaviour

Verify:

* responsive behaviour is intentional

Avoid:

* desktop-only assumptions
* hardcoded dimensions
* inconsistent breakpoint usage

Applications should behave predictably across devices.

---

## Dark Mode Review

Review:

* dark mode implementation
* theme switching

Verify:

* theme behaviour remains centralized

Avoid:

* component-level theme fragmentation
* duplicated dark mode logic

Theme ownership should be explicit.

---

## Form Architecture Review

Review:

* forms
* validation integration
* user interaction patterns

Verify:

* forms remain maintainable

Avoid:

* duplicated validation logic
* business rules embedded in components

Domain validation belongs outside presentation components.

---

## Dialog Review

Review:

* dialog usage
* modal architecture

Verify:

* dialogs remain presentation-oriented

Avoid:

* business workflows controlled exclusively through modal state

Dialogs should facilitate interaction, not own business processes.

---

## Table Architecture Review

Review:

* QTable usage
* data presentation strategy

Verify:

* tables focus on visualization

Avoid:

* excessive client-side business processing
* hidden state ownership

Data ownership belongs to stores.

---

## Notification Review

Review:

* Notify usage
* feedback mechanisms

Verify:

* notifications remain centralized

Avoid:

* scattered notification implementations
* inconsistent user messaging

Notification behaviour should be standardized.

---

## Loading State Review

Review:

* loading indicators
* async feedback

Verify:

* loading states are predictable

Avoid:

* duplicated loading mechanisms
* hidden asynchronous behaviour

Loading ownership should remain clear.

---

## Boot File Review

Review:

* boot files
* initialization logic

Verify:

* boot files remain infrastructure-focused

Appropriate uses:

* plugin registration
* framework initialization
* global configuration

Avoid:

* business logic
* feature orchestration
* application workflows

---

## Plugin Review

Review:

* plugin registration
* plugin scope

Verify:

* plugins are justified

Avoid:

* unnecessary global dependencies
* excessive plugin proliferation

Every plugin increases maintenance cost.

---

## Accessibility Review

Review:

* keyboard navigation
* focus management
* semantic structure

Verify:

* Quasar components remain accessible

Avoid:

* accessibility regressions caused by customization

Detailed accessibility review belongs to:

accessibility_reviewer.md

---

## State Integration Review

Review:

* component-store interactions

Verify:

* state ownership remains external to Quasar components

Avoid:

* UI components becoming state owners

Detailed state review belongs to:

state_management_reviewer.md

---

## Security Review

Review:

* user input handling
* rendered content
* navigation interactions

Verify:

* security-sensitive functionality remains protected

Avoid:

* trust assumptions based on UI restrictions

Detailed security review belongs to:

frontend_security_reviewer.md

---

## Performance Review

Review:

* rendering complexity
* component density
* unnecessary reactivity

Verify:

* Quasar usage remains efficient

Avoid:

* excessive component nesting
* unnecessary reactive updates

UI performance should scale predictably.

---

## Quality Checklist

Before approval verify:

### Separation of Concerns

Is business logic separated from UI?

### Vue Alignment

Does implementation follow Vue-first architecture?

### Responsiveness

Is responsive behaviour intentional?

### Accessibility

Are accessibility requirements respected?

### Performance

Does rendering remain efficient?

### Maintainability

Can future developers understand the implementation?

### Governance

Does implementation respect approved frontend architecture?

---

## Mandatory Behaviours

Always:

* identify Quasar misuse
* identify UI-business coupling
* identify duplicated UI patterns
* identify responsiveness risks
* identify accessibility concerns
* identify unnecessary framework complexity

---

## Forbidden Behaviours

Do not:

* approve business logic inside layouts
* approve API orchestration inside components
* approve duplicated framework patterns
* approve hidden state ownership
* approve unnecessary plugin dependencies
* approve convenience-driven architecture

---

## Decision Principle

Prefer:

* Vue-first architecture
* reusable layouts
* centralized configuration
* responsive design
* maintainable UI composition

Over:

* framework-centric architecture
* duplicated UI logic
* hidden dependencies
* tightly coupled components
* convenience-driven shortcuts

Quasar should accelerate frontend development while remaining a replaceable presentation layer within the overall architecture.
