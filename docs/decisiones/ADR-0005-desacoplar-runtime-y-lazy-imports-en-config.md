ADR-0005 – Desacoplamiento runtime y lazy imports en config.py

Fecha: 2026-01-27
Estado: Aprobado
Contexto: Migración IaC server_monitoring_2509

## Contexto

Durante FASE 7 se identificó acoplamiento crítico en import-time:
- Lectura de .env y secrets al importar módulos.
- Imports pesados (psycopg2, requests) que provocaban fallos tempranos.
FASE 8 inicia implementación incremental limitada a config.py.

## Decisión

- La carga de .env y secrets se realiza exclusivamente en runtime mediante init_config().
- config.py debe ser importable en entornos sin dependencias completas.
- psycopg2 y requests se importan de forma lazy en las funciones que los requieren.
- Se mantienen valores por defecto desde variables de entorno para compatibilidad.

## Consecuencias

- init_config() pasa a ser obligatoria en los entrypoints funcionales.
- Los errores por falta de dependencias aparecen solo cuando se usan las funciones afectadas.
- Se mejora la portabilidad a CI/CD, cronjobs y contenedores mínimos.

## Fuera de alcance:
- No se modifican docker-compose, Makefiles ni entrypoints en este ADR.
- No se introducen validaciones de precondiciones automáticas (pendiente de fases futuras).

## Estado

Aceptado.
