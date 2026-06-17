# ADR-0028 – Política de reproducibilidad Docker y endurecimiento de validaciones IaC

Status: APPROVED
Date: 2026-05-18
Decision Type: REVIEW_REQUIRED
Scope: Infrastructure
Tags: REVIEW_REQUIRED
Related ADRs: ADR-0004
Supersedes: NONE
Superseded By: NONE
Validation Reference: make validate-dockerfiles

## Contexto

Durante la evolución de las validaciones de infraestructura del proyecto server_monitoring_2509 se detectaron varios problemas relacionados con:
- uso implícito de tags mutables en imágenes Docker
- ausencia de validaciones de reproducibilidad
- falsos positivos en auditorías de Dockerfiles
- bloqueo excesivo de auditorías por estados runtime transitorios
- incoherencia entre hardening teórico y operativa real del entorno

Las validaciones iniciales introducidas en:
- ops/audit/validate_reproducibility.sh
- ops/audit/validate_dockerfiles.sh

permitían detectar:
- uso de :latest
- imágenes upstream sin digest
- requirements Python no fijados
- apt-get install sin versiones explícitas
- imágenes dangling

Sin embargo, durante validaciones reales sobre el servidor se observaron problemas operativos relevantes:

- falsas detecciones de latest implícito en:
    FROM ${BASE_IMAGE}

- bloqueo innecesario de auditorías debido a imágenes dangling temporales
  generadas por Docker BuildKit

- incompatibilidad entre ciertas imágenes upstream y tags inexistentes
  (caso boky/postfix:3.6.0)

- endurecimiento excesivo para un entorno no orientado a supply-chain
  crítica

Además, se detectó necesidad de mejorar reproducibilidad mínima de runtime sin introducir complejidad excesiva ni drift operacional.

## Decisión

Se adopta una política pragmática de reproducibilidad Docker basada en:

### 1. Digest obligatorio en imágenes upstream runtime

Las imágenes upstream utilizadas directamente en compose.yml deberán fijarse mediante digest SHA256.

Ejemplos adoptados:
- postgres:14.3@sha256:...
- grafana/promtail:2.9.3@sha256:...
- grafana/loki:2.9.3@sha256:...
- grafana/grafana:10.4.2@sha256:...

Objetivo:
- evitar mutabilidad silenciosa de tags
- mejorar reproducibilidad de despliegue
- mantener trazabilidad de imágenes

### 2. Prohibición de :latest explícito

Se mantiene prohibición explícita de:
    :latest

tanto en:
- compose.yml
- Dockerfiles

La validación permanece bloqueante (FAIL).

### 3. Excepción explícita para FROM parametrizado

Se acepta el patrón:
    FROM ${BASE_IMAGE}

cuando:
- BASE_IMAGE esté definido mediante ARG
- exista resolución explícita de versión o digest

Motivación:
- evitar falsos positivos
- permitir reutilización controlada
- mantener flexibilidad CI/CD

La validación pasa a:
- WARN informativo
- no FAIL

### 4. Política pragmática sobre dangling images

Las imágenes dangling pasan a considerarse:
- condición operacional temporal
- no incumplimiento arquitectónico

Motivación:
- Docker BuildKit puede generar dangling legítimos
- bloquear auditorías por este motivo introduce ruido operacional

Nueva política:
- WARN operativo
- nunca FAIL bloqueante

Se añade recomendación explícita:
    make clean-dangling
como limpieza posterior a builds o despliegues.

### 5. Requirements Python no fijados

Las dependencias Python no completamente fijadas:
    >=
    PyYAML sin versión
    etc.

pasan a clasificarse como:
- WARN
- recomendación de mejora futura

y no como:
- FAIL bloqueante

Motivación:
- evitar sobre-endurecimiento prematuro
- mantener compatibilidad operativa
- priorizar estabilidad del pipeline actual

### 6. apt-get install sin versiones explícitas

Las instalaciones apt sin pinning:
- permanecen permitidas
- generan únicamente WARN informativo

Motivación:
- Debian slim introduce complejidad alta para pinning estricto
- el beneficio operacional actual no justifica el coste

## Consecuencias

Positivas:
- mejora moderada de reproducibilidad runtime
- reducción de falsos positivos
- auditorías más alineadas con operativa real
- pipeline CI más estable
- menor drift respecto a upstream

Negativas / trade-offs:
- reproducibilidad aún no completamente hermética
- requirements Python siguen parcialmente mutables
- apt packages continúan dependiendo de repositorios Debian runtime

Riesgos aceptados:
- cambios menores futuros en dependencias Python
- variabilidad limitada en paquetes apt
- dependencia de disponibilidad de digests upstream

## Validaciones realizadas

Se validó satisfactoriamente:

### validate_reproducibility.sh
- detección correcta de imágenes sin digest
- aceptación de imágenes locales con tag explícito
- dangling images degradadas a WARN

### validate_dockerfiles.sh
- detección correcta de :latest explícito
- exclusión correcta de:
    FROM ${BASE_IMAGE}

- requirements no fijados degradados a WARN
- apt-get install sin pinning degradado a WARN

### Runtime validado

Servicios operativos correctamente:
- postgres
- promtail
- loki
- grafana
- monitoring-python
- monitoring-cron
- smtp-relay

## Alternativas consideradas

### Opción A — Reproducibilidad estricta total

Incluyendo:
- pinning completo apt
- requirements totalmente fijados
- builds herméticos
- bloqueo por dangling images

Rechazada por:
- complejidad excesiva
- alto coste operacional
- sobreingeniería para el alcance actual

### Opción B — Mantener validaciones mínimas anteriores

Rechazada por:
- insuficiente control de mutabilidad
- ausencia de trazabilidad runtime
- riesgo de drift silencioso

## Estado

Aceptado.

## Notas

Esta decisión representa:
- endurecimiento moderado
- no hardening extremo

El objetivo explícito es:
- mejorar reproducibilidad práctica
- minimizar falsos positivos
- preservar mantenibilidad operacional

Las validaciones actuales deben entenderse como:
- guardrails operativos
- no como framework completo de supply-chain security
