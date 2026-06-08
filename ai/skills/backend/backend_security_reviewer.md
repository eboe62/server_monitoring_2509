# backend_security_reviewer.md

## Purpose

This skill reviews backend application security.

Its objective is to ensure:

* secure API design
* proper authentication
* proper authorization
* secure data handling
* secure service communication
* secure configuration practices

This skill focuses on application security.

Infrastructure security remains governed by:

* DevSecOps Principles
* Infrastructure security reviews
* Platform-specific governance

---

## Review Scope

Apply this skill when reviewing:

* Spring Boot applications
* REST APIs
* API Gateway implementations
* authentication flows
* authorization mechanisms
* JWT implementations
* OAuth2 integrations
* service-to-service communication
* backend security controls

Examples:

* SecurityConfig classes
* JWT filters
* authentication providers
* authorization rules
* API endpoints
* backend integrations

---

## Core Principles

### Least Privilege

Every actor should receive only the permissions required.

Review:

* user permissions
* service permissions
* application permissions

Prefer:

* minimum required access
* explicit permissions
* narrow authorization scopes

Avoid:

* excessive privileges
* broad access grants
* implicit permissions

---

### Authentication Before Authorization

Authentication and authorization are separate concerns.

Review:

* identity validation
* access control enforcement

Prefer:

* authenticated identities
* explicit authorization checks

Avoid:

* authorization without authentication
* trust-based assumptions

---

### Deny By Default

Access should be denied unless explicitly granted.

Prefer:

* explicit allow rules
* restrictive defaults

Avoid:

* permissive defaults
* implicit access

Unknown access should be rejected.

---

### Secure API Exposure

Review:

* public endpoints
* protected endpoints
* internal endpoints

Prefer:

* minimal exposure
* documented exposure

Avoid:

* unnecessary endpoints
* forgotten endpoints
* test endpoints in production

---

### API Contract Protection

Review:

* request validation
* input handling
* output filtering

Prefer:

* explicit validation
* strict contracts

Avoid:

* trust in client input
* unrestricted payloads

Never assume external input is safe.

---

### Input Validation

Review:

* request bodies
* path parameters
* query parameters
* headers

Prefer:

* validation at boundaries
* schema validation
* type validation

Avoid:

* unchecked input
* trust-based validation

Validation should be explicit.

---

### Output Protection

Review:

* API responses
* error messages
* logging output

Prefer:

* minimum required disclosure
* sanitized responses

Avoid:

* internal implementation details
* stack traces
* sensitive information leakage

---

### Sensitive Data Protection

Review:

* credentials
* tokens
* personal data
* secrets

Prefer:

* controlled access
* minimum exposure
* secure storage

Avoid:

* logging secrets
* exposing credentials
* storing secrets in source code

---

### Secret Management

Review:

* environment variables
* configuration files
* secret providers

Prefer:

* externalized secrets
* managed secret stores

Avoid:

* hardcoded credentials
* committed secrets
* embedded tokens

Secrets should never appear in source code.

---

### JWT Security

Review:

* token generation
* token validation
* token expiration
* signing algorithms

Prefer:

* short-lived tokens
* explicit validation
* strong signing mechanisms

Avoid:

* disabled validation
* indefinite token validity
* trust without verification

---

### Authorization Enforcement

Review:

* endpoint access rules
* role validation
* ownership validation

Prefer:

* explicit authorization checks
* centralized policies

Avoid:

* client-side authorization
* hidden access rules

Authorization should be verifiable.

---

### Service-to-Service Security

Review:

* internal API calls
* service authentication
* trust relationships

Prefer:

* authenticated communication
* explicit trust boundaries

Avoid:

* unrestricted internal access
* network trust assumptions

Internal traffic is not automatically trusted.

---

### Security Configuration

Review:

* Spring Security configuration
* authentication providers
* filter chains
* security policies

Prefer:

* explicit configuration
* predictable behaviour

Avoid:

* overly permissive defaults
* unclear security flows

---

### Error Handling Security

Review:

* exception handling
* authentication failures
* authorization failures

Prefer:

* generic client responses
* detailed internal logging

Avoid:

* information disclosure
* security-sensitive error details

---

### Logging Security

Review:

* audit logs
* authentication logs
* authorization logs

Prefer:

* traceability
* accountability

Avoid:

* credential logging
* token logging
* personal data leakage

Logs should support investigation without exposing secrets.

---

### Dependency Security

Review:

* external libraries
* security dependencies
* authentication libraries

Prefer:

* maintained dependencies
* supported versions

Flag:

* vulnerable dependencies
* unsupported components
* abandoned libraries

---

## Security Review Areas

Evaluate:

### Authentication Security

Can identities be trusted?

### Authorization Security

Can access controls be bypassed?

### Data Protection

Is sensitive information adequately protected?

### API Security

Can the API be abused?

### Service Communication

Are trust boundaries enforced?

### Operational Security

Can security incidents be detected and investigated?

---

## Common Vulnerability Categories

Review for:

* broken authentication
* broken authorization
* insecure direct object references
* sensitive data exposure
* security misconfiguration
* injection risks
* excessive information disclosure
* insecure secret handling
* insecure API exposure
* trust boundary violations

---

## Anti-Patterns

Flag:

* hardcoded credentials
* disabled authentication
* disabled authorization
* unrestricted endpoints
* trusting client input
* exposing stack traces
* logging secrets
* logging tokens
* weak JWT validation
* shared service credentials
* implicit trust relationships
* security by obscurity

---

## Expected Review Output

When reviewing backend security:

1. Context
2. Authentication Review
3. Authorization Review
4. API Security Review
5. Sensitive Data Review
6. Service Communication Review
7. Dependency Review
8. Security Risks
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

* authentication architecture
* authorization model
* trust boundaries
* security policies
* identity management

request ADR validation before implementation.

Do not approve security architecture changes without verifying ADR compliance.

---

## Decision Principle

Prefer:

* explicit security controls
* least privilege
* defense in depth
* secure defaults
* verifiable protections

Over:

* implicit trust
* convenience-based security
* hidden assumptions
* security by convention

Security decisions should be demonstrable, reviewable and enforceable.
