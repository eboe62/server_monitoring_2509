# ADR-0000 – Trabajo paralelo fuera de Git durante refactor estructural

Status: APPROVED
Date: 2026-01-24
Decision Type: REVIEW_REQUIRED
Scope: System
Tags: REVIEW_REQUIRED
Related ADRs: NONE
Supersedes: NONE
Superseded By: NONE
Validation Reference: NONE

## Contexto

Durante la refactorización mayor del proyecto Monitoring Stack,
se decidió desarrollar la nueva estructura (`server_monitoring_2511`)
fuera del repositorio Git principal para evitar:

- Riesgo de corrupción del histórico
- Commits intermedios incoherentes
- Mezcla de código legacy y refactorizado

## Decisión

El trabajo se realizó en un directorio externo sin `.git`,
y posteriormente se migró manualmente al repositorio original
mediante una copia controlada de estructura y ficheros.

## Consecuencias

- Mayor control del estado final
- Menor ruido en el histórico Git
- Necesidad de validación manual previa al primer commit

## Estado

Aceptado – migración única
