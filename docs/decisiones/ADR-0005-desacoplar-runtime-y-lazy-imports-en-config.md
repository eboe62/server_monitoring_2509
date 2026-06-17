# ADR-0005 – Desacoplamiento runtime y lazy imports en config (Runtime desacoplado)

Status: APPROVED
Date: 2026-01-27
Decision Type: REVIEW_REQUIRED
Scope: Runtime
Tags: REVIEW_REQUIRED
Related ADRs: ADR-0003, ADR-0025
Supersedes: NONE
Superseded By: NONE
Validation Reference: NONE

## Contexto

Durante FASE 3 se identificó acoplamiento crítico en import-time:
- Lectura de .env y secrets al importar módulos.
- Imports pesados (psycopg2, requests) que provocaban fallos tempranos.
FASE 8 inicia implementación incremental limitada a config.py.

## Decisión

- La carga de configuración sensible y credenciales se realiza exclusivamente en runtime mediante init_config().
- config.py debe poder importarse sin efectos secundarios ni dependencias operativas completas.
- psycopg2 y requests se importan de forma lazy únicamente en las funciones que los requieren.
- Se mantienen valores por defecto mediante variables de entorno para compatibilidad.

Este ADR define la política general de desacoplamiento runtime e import-time utilizada posteriormente por ADR especializados de runtime, secrets y configuración SMTP.

## Consecuencias

- init_config() pasa a ser obligatoria en los entrypoints funcionales.
- Los errores por falta de dependencias aparecen únicamente cuando se utilizan las funciones afectadas.
- Se mejora la portabilidad a CI/CD, cronjobs y contenedores mínimos.
- Se reduce el acoplamiento entre importación de módulos y configuración operativa.

## Fuera de alcance:
- No se modifican docker-compose, Makefiles ni entrypoints en este ADR.
- No se introducen validaciones de precondiciones automáticas (pendiente de fases futuras).

## Estado

Aceptado.
