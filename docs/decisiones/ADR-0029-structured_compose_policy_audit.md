# ADR-0029 — Structured Compose Policy Audit

Fecha: 2026-05-19
Estado: Accepted
Contexto: server_monitoring_2509

## Contexto

El proyecto utilizaba validaciones heurísticas basadas principalmente en:
- grep
- awk
- búsquedas textuales sobre YAML
- parsing shell no estructurado

Especialmente en:

ops/audit/audit_repo_host.sh

Este enfoque presentaba múltiples problemas:
- falsos positivos
- falsos negativos
- fuerte dependencia del formato textual
- dificultad de evolución
- escasa reutilización
- difícil integración futura con CI/CD
- baja robustez ante Compose complejos

El proyecto utiliza actualmente:
- Docker Compose standalone
- arquitectura single-node
- runtime containerizado
- contenedor principal `monitoring-python`
- modelo IaC pragmático
- ADR de hardening progresivo

Se identificó además la necesidad de:
- mantener reproducibilidad runtime
- evitar dependencia Python host
- permitir validaciones machine-readable
- reducir deuda técnica shell-based

## Problema

Las validaciones heurísticas basadas en grep y parsing textual no proporcionaban suficiente robustez para:
- auditoría reproducible
- enforcement futuro
- validación estructurada real
- integración CI/CD
- reducción fiable de falsos positivos/negativos

Adicionalmente:
- parte del tooling Python estaba ejecutándose desde host
- existía incoherencia con el modelo containerizado del proyecto
- la salida no era machine-readable
- las severidades no estaban centralizadas

## Decisión

Se adopta un modelo de auditoría estructurada basado en parsing Compose mediante Python.

Se introduce:
    ops/audit/compose_policy_checks.py

como motor estructurado de validación.

La ejecución principal se realiza exclusivamente dentro del contenedor:
    monitoring-python

mediante:
    docker compose exec -T monitoring-python ...

El sistema prioriza:
    docker compose config

como fuente runtime-resolved efectiva.

La salida soporta:
- modo humano
- salida JSON machine-readable
- checks parciales mediante --check
- runtime validation mediante --self-test

## Validaciones implementadas

Se implementan validaciones estructuradas para:
- puertos publicados
- docker.sock
- imágenes :latest
- imágenes sin digest
- privileged=true
- mounts sensibles RW
- cap_add
- read_only=false

## Severidades

Se centraliza la severidad mediante:

POLICY_SEVERITY

Inicialmente:
- privileged=true → FAIL
- resto → WARN

Las severidades podrán evolucionar posteriormente según madurez operacional.

## Runtime Model

La lógica principal de validación se ejecuta dentro del runtime containerizado del proyecto.

El host:
- orquesta ejecución
- recopila resultados
- realiza parse JSON ligero

El runtime principal válido es:
    monitoring-python

No se considera válido depender del Python instalado en host para ejecutar lógica core del proyecto.

## Runtime Checks

Se añade:
    --self-test

para validar:
- disponibilidad docker CLI
- disponibilidad docker compose
- funcionamiento compose config
- acceso docker.sock

Esto permite detectar degradaciones runtime explícitamente.

## Fallback YAML

Cuando:

docker compose config

no está disponible, el sistema degrada a parsing YAML estático best-effort.

Este fallback:
- no garantiza resolución completa Compose
- puede no reproducir merges complejos
- puede no resolver profiles/overrides avanzados

El sistema debe emitir warning explícito cuando esto ocurra.

## Tradeoffs

### Ventajas

- reducción de falsos positivos
- reducción de falsos negativos
- validación estructurada real
- machine-readable
- mejor integración futura CI/CD
- menor dependencia grep/awk
- mejor mantenibilidad
- mejor separación responsabilidades

### Inconvenientes

- mayor complejidad que shell puro
- dependencia parcial runtime Docker
- posible necesidad control-plane Docker
- aumento moderado superficie de ataque

## Riesgos Residuales

El contenedor:
    monitoring-python

puede requerir acceso parcial a:
    docker.sock

para ejecutar:
    docker compose config

Esto aumenta superficie de ataque respecto a un contenedor completamente aislado.

Actualmente se considera aceptable debido a:
- entorno single-node controlado
- despliegue Compose standalone
- hardening progresivo
- ausencia de multitenancy
- política pragmática ADR existentes

## Compatibilidad

La decisión mantiene compatibilidad con:
- Docker Compose standalone
- arquitectura single-node
- Makefile actual
- auditorías existentes
- runtime actual
- ADR previos
- modelo IaC actual

No se introduce:
- Kubernetes
- OPA/Rego
- policy-as-code pesado
- orquestación distribuida

## Consecuencias

El proyecto dispone ahora de:
- auditoría estructurada reproducible
- validación machine-readable
- base compatible con enforcement futuro
- menor deuda técnica shell-based
- mejor alineación runtime/IaC

## Evolución Futura

Posibles evoluciones futuras:
- enforcement CI/CD
- severidades configurables
- perfiles de policy
- export estable JSON
- validaciones más estrictas
- integración jq opcional
- validaciones Compose avanzadas

Sin introducir:
- Kubernetes
- OPA/Rego
- frameworks policy-as-code complejos
