# ADR-0026 — Estrategia de validación y testing del modelo SMTP (Estrategia de validación multinivel)

Status: APPROVED
Date: 2026-05-13
Decision Type: REVIEW_REQUIRED
Scope: Runtime
Tags: REVIEW_REQUIRED
Related ADRs: ADR-0025
Supersedes: NONE
Superseded By: NONE
Validation Reference: NONE

## Contexto

ADR-0025 define el modelo SMTP explícito y las reglas operativas asociadas. Este ADR define exclusivamente su estrategia de validación y testing.

Históricamente existían problemas relacionados con:
- lectura de credenciales SMTP durante import-time,
- heurísticas implícitas de autenticación,
- contaminación de CI por secrets presentes en runners,
- diferencias entre entornos locales, CI y contenedores,
- ausencia de validaciones automáticas sobre Compose y entrypoints.

Para reducir estos riesgos se adopta una estrategia de testing multinivel.

## Problema

La validación manual no permite detectar de forma fiable:
- regresiones entre modos relay/auth,
- lectura indebida de credenciales SMTP,
- side-effects durante importación,
- configuraciones inconsistentes en Compose,
- incumplimientos arquitectónicos.

Además, una conexión SMTP satisfactoria no garantiza cumplimiento arquitectónico ni coherencia operativa.

## Decisión

Se adopta una estrategia de validación basada en:
- unit tests,
- integration tests,
- policy tests,
- runtime smoke checks en CI.

### 1. Unit tests

Validan comportamiento aislado de:
- SMTP_MODE,
- init_config(),
- send_email(),
- fail-fast en auth.

Características:
- sin tráfico SMTP real,
- sin dependencia DNS,
- sin uso de credenciales reales,
- uso de mocking y monkeypatching.

### 2. Integration tests

Validan interacción entre librería y entorno controlado:
- carga de credenciales SMTP,
- comportamiento relay/auth,
- validación de errores por ausencia de credenciales.

Características:
- uso de tmp_path,
- filesystem temporal,
- sin infraestructura SMTP externa.

### 3. Policy tests

Validan cumplimiento arquitectónico y declarativo:
- presencia explícita de SMTP_MODE,
- consistencia entre auth y montaje de credenciales,
- placement correcto de init_config().

Se realizan mediante análisis estático sobre:
- Compose YAML,
- AST Python.

Objetivo:
detectar errores estructurales sin ejecutar código.

### 4. Runtime smoke checks en CI

CI debe validar:
- instalación correcta de dependencias,
- ejecución de tests,
- aislamiento de credenciales temporales,
- funcionamiento básico relay/auth.

Requisitos:
- PYTHONPATH=src,
- entorno aislado,
- dependencias instaladas desde requirements.txt.

## Razonamiento

La validación multinivel permite separar responsabilidades y reducir falsos diagnósticos.

Unit tests
    Permiten validar semántica interna y lógica de control:
    - autenticación,
    - validación de modos,
    - fail-fast,
    - decisiones runtime.

    El uso de mocks evita:
    - tráfico SMTP real,
    - dependencia de DNS,
    - flakiness,
    - latencia externa.

Integration tests
    Validan integración entre librería y filesystem controlado sin necesidad de infraestructura completa.

    Esto permite detectar:
    - errores de carga de secrets,
    - problemas de fallback,
    - incompatibilidades entre runtime y tests.

Policy tests
    El comportamiento esperado no depende únicamente del código Python, sino también de la infraestructura declarativa.

    La validación estática sobre Compose y AST permite detectar:
    - mounts inconsistentes,
    - uso incorrecto de SMTP_MODE,
    - llamadas a init_config() fuera de __main__,
    - side-effects en import-time.

    El análisis AST se adopta porque permite validar estructura sintáctica sin ejecutar módulos ni disparar efectos secundarios.

CI reproducible
    El aislamiento explícito de credenciales SMTP y dependencias reduce:
    - contaminación desde runners,
    - falsos negativos,
    - diferencias entre entornos.

    Esto mejora la auditabilidad y estabilidad del pipeline.

## Alcance actual

La estrategia actual valida:
- comportamiento relay/auth,
- fail-fast en auth,
- login SMTP condicional,
- ausencia de autenticación en relay,
- placement correcto de init_config(),
- consistencia básica de Compose,
- aislamiento de runtime durante CI.

## Limitaciones

La estrategia actual no valida:
- entrega SMTP real extremo a extremo,
- negociación TLS contra proveedores reales,
- permisos efectivos host,
- rotación dinámica de credenciales,
- enforcement runtime de mounts read-only,
- escenarios reales de timeout o latencia.

Los policy tests tampoco cubren:
- templating complejo de Compose,
- mounts dinámicos externos,
- llamadas indirectas a init_config().

## Consecuencias

Positivas:
- reducción de regresiones,
- detección temprana de errores,
- mayor estabilidad de validación en CI,
- reducción de side-effects durante importación,
- mayor coherencia entre infraestructura declarativa y runtime.

Operativas:
- nuevos entrypoints deben respetar la política de inicialización,
- nuevos stacks deben declarar SMTP_MODE,
- los tests deben mantenerse alineados con Compose y runtime real.

## Guía operativa

Cada nuevo servicio debe:
- declarar SMTP_MODE explícitamente,
- invocar init_config() únicamente dentro de:
  if __name__ == "__main__":
- evitar lectura de credenciales durante import-time.

Los tests deben:
- evitar dependencias externas,
- aislar filesystem y entorno,
- no reutilizar credenciales reales.

## Evolución futura

Líneas recomendadas:
- tests E2E SMTP en entorno controlado,
- validación automática de mounts read-only,
- tests de resiliencia y timeouts,
- consolidación de fixtures comunes,
- policy checks automáticos en pull requests,
- validación de rotación de credenciales.

## Referencias

- ADR-0005 — Runtime desacoplado y lazy imports
- ADR-0019 — Resilience Testing Strategy
- ADR-0024 — Container Privilege Exception Policy
- ADR-0025 — Modelo SMTP explícito y endurecimiento de configuración

Archivos relacionados:
- src/monitoring/common/config.py
- tests/unit/*
- tests/integration/*
- ops/stacks/*/compose.yml
- .github/workflows/ci.yml
- Makefile
