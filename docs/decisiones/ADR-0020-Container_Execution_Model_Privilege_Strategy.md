# ADR-0020 — Container Execution Model & Privilege Strategy

Status: APPROVED
Date: 2026-05-04
Scope: Runtime
Category: SECURITY
Tags: REVIEW_REQUIRED
Related ADRs: ADR-0018, ADR-0024
Supersedes: NONE
Superseded By: NONE
Validation Reference: NONE

## Contexto

Durante la evolución del sistema se han identificado inconsistencias en el modelo de ejecución de contenedores:
- uso mixto de root y no-root sin criterio explícito
- dependencia histórica de bind mounts del host
- contenedores con propósitos distintos (runtime vs debug) tratados de forma homogénea

Estas inconsistencias generan:
- ambigüedad en el modelo de seguridad
- pérdida de reproducibilidad
- acoplamiento innecesario al host
- dificultad para escalar el sistema a otros entornos

Adicionalmente, el sistema debe servir como base portable para:
- despliegue de servicios (DB, web services)
- análisis forense
- evaluación de vulnerabilidades
- recuperación de sistemas

Esto exige un modelo de ejecución claro, consistente y replicable.

## Decisión

Se define un modelo explícito de ejecución de contenedores basado en su propósito:

### 1. Contenedores de runtime (infra-stacks)

Ejemplos:
- monitoring-cron
- monitoring-python
- observability stack

Características obligatorias:
- autocontenidos (sin dependencia del host)
- reproducibles (build determinista)
- sin bind mounts de código
- un proceso principal definido

Regla de privilegios:
Estos contenedores DEBEN ejecutarse como usuario no-root.

Motivo:
- principio de mínimo privilegio
- reducción de superficie de ataque
- coherencia con modelo IaC

El runtime:
    monitoring-python

NO debe considerarse un toolbox Docker completo.

Por defecto:
- no incorpora docker CLI
- no incorpora docker compose
- no monta docker.sock

Las operaciones Docker host-level deben ejecutarse desde:
- host control-plane
- scripts operacionales externos
- pipelines CI/CD autorizados

Cualquier excepción deberá documentarse explícitamente mediante ADR adicional.

### 2. Contenedores de servicio (micro-stacks)

Ejemplos:
- postgres
- smtp-relay
- servicios externos

Características:
- pueden depender de imágenes oficiales
- pueden requerir root internamente
- responsabilidad delegada al proveedor de la imagen

Regla de privilegios:
No se fuerza USER no-root si rompe compatibilidad.

Motivo:
- evitar desviaciones de imágenes oficiales
- mantener estabilidad y soporte upstream

### 3. Contenedores operativos / debug

Ejemplos:
- contenedores de diagnóstico
- tooling interactivo

Características:
- ejecución manual
- uso puntual
- no forman parte del runtime crítico

Regla de privilegios:

Pueden ejecutarse como root, de forma explícita y controlada.

Motivo:
- facilitar debugging
- permitir operaciones de bajo nivel

## Principios derivados

1. Separación por propósito
Cada contenedor debe tener un único rol claro:
- runtime
- servicio
- operativo

No se permite mezclar roles.

2. Eliminación de dependencias del host
- prohibido uso de bind mounts de código en producción
- el código debe integrarse en la imagen Docker durante el build
- permitido solo:
    logs específicos (controlados)
    datos persistentes definidos explícitamente
    sockets o recursos del host justificados documentalmente

Validación obligatoria:
    make test-reproducibilidad

El test debe validar:
- eliminación completa de contenedores
- eliminación de imágenes
- eliminación de volúmenes
 - recreación de las redes de monitoring (backend-net / observability-net / restricted-net)
- reconstrucción íntegra desde cero
- ausencia de dependencias implícitas del host

3. Coherencia con IaC

El comportamiento del sistema debe mantener:
- reproducibilidad operativa,
- independencia del host,
- coherencia entre build y runtime.

4. Seguridad contextual (no dogmática)

El uso de no-root:
- es obligatorio en runtime propio
- es opcional en servicios externos
- es irrelevante en contenedores de debug controlado

## Consecuencias

Positivas:
- modelo de seguridad claro y consistente
- reducción de ambigüedad en decisiones técnicas
- mejora de portabilidad del sistema
- base sólida para hardening futuro
- alineación con principios IaC

Negativas:
- necesidad de clasificar correctamente los contenedores
- posible refactor de imágenes existentes
- incremento inicial de complejidad conceptual

## Relación con otros ADR
- ADR-0008 (micro-stack vs infra-stack)
  → Este ADR refuerza la separación de roles
- ADR-0014 / ADR-0015 (exposición de servicios)
  → Complementa el aislamiento mediante privilegios
- ADR-0018 (seguridad runtime)
  → Define el criterio concreto de aplicación de no-root
- ADR-0019 (resilience testing)
  → Garantiza coherencia entre runtime y testing

## Estado
Adoptado
