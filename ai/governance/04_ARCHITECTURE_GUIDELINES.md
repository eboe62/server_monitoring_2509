# Micro-Architecture and Implementation Guidelines

This document outlines the mandatory coding standards, package structures, and software design principles for the GDA Monorepo. Both GitHub Copilot and development teams must adhere strictly to these guidelines.

---

## 1. Backend Micro-Architecture: Service Classification by Impact Levels (Tiers)

To ensure a proportional, cost-effective, and efficient design, microservices are classified into distinct tiers based on their business impact and operational complexity:

### Tier 1: Core Business Modules
- **Description:** Critical microservices that process core business logic and manage sensitive, complex, or domain-heavy data.
- **Architectural Requirements:**
  - Strict multi-layered package structure: `application`, `domain`, and `infrastructure`.
  - Mandatory use of Data Transfer Objects (DTOs) to decouple internal JPA entities from public API endpoints.
  - Mandatory use of MapStruct to handle all transformations between domain models, entities, and DTOs.
  - Absolute separation of concerns across all development layers.
- **Target Examples:** `gda-persona`, `gda-agrupacion`.

### Tier 3: Utility and Support Modules
- **Description:** Cross-cutting, technical support, or utility microservices with minimal to no direct impact on core business rules.
- **Architectural Requirements:**
  - Flat architectural pattern is permitted: `Controller -> Repository/Entity`.
  - Permission to centralize JPA entities, Spring Data repositories, and API data contracts directly inside the `-commons` submodule to reduce redundant boilerplate code.
  - MapStruct and DTO definitions are optional, provided their absence does not cause leakage across core business domains.
- **Target Examples:** `gda-log`.

### General Considerations
- All new microservices must be formally evaluated and assigned to their respective Tier during the initial design and technical scoping phase.
- Any change in a service's classification must be vetted by the architecture review board and documented in the corresponding Architecture Decision Record (ADR).

---

## 2. Frontend Micro-Architecture: Vue.js & Quasar Framework

### Project Structure
The Frontend application is powered by Vue.js and the Quasar Framework, utilizing a highly scalable **Feature-Driven Layout (Domain-Driven Structure)**. The codebase must be organized as follows:

- **`src/modules/`:**
  The core directory where each folder represents an isolated system feature or business capability. Every feature module must strictly contain:
  - `views/`: Main pages, layout wrappers, and screen entry points tied to application routes.
  - `components/`: Highly reusable UI components scoped exclusively to that specific feature.
  - `composables/`: Vue 3 Composition API reactive functions encapsulating state, local business constraints, and lifecycle logic.

- **`src/boot/axios.js`:**
  The centralized HTTP client configuration bootstrap file. It registers global Axios settings and implements global request interceptors to automatically capture and inject the JWT Authorization header.

- **`src/utils/axiosCall.js`:**
  A wrapper utility that encapsulates asynchronous HTTP requests. It reuses the core Axios boot configuration to expose standard, predictable fetch/mutation routines across the interface layer.

- **`src/models/`:**
  The centralized directory for data schemas and structural representations (e.g., `person.js`, `group.js`). These objects act as the frontend mirrors for the backend DTO contracts, enforcing structural data validation.

### API Consumption Rules
- Direct HTTP network calls using raw fetch or local Axios instances inside views are strictly prohibited. All requests must be handled via `src/utils/axiosCall.js`.
- Security tokens (JWT) must never be managed manually per request; they must be appended via the central request interceptors in `src/boot/axios.js`.

### Development Best Practices
- **Logic Isolation:** Keep layout files clean; all feature-specific logic, computational expressions, and asynchronous data orchestration must reside inside local composables (`src/modules/[module]/composables/`).
- **Data Integrity:** Always instantiate or parse network payloads using the schemas defined in `src/models/` to safeguard component rendering against unexpected structural schema breaking changes from backend APIs.
- **Zero Boilerplate in Views:** Avoid embedding inline state mutations or redundant HTTP handlers within `.vue` templates or script blocks.
