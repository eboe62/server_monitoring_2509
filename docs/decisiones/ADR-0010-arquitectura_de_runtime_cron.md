# ADR-0010 - Arquitectura de runtime cron

Status: APPROVED
Date: 2026-03-05
Decision Type: REVIEW_REQUIRED
Scope: Runtime
Tags: REVIEW_REQUIRED
Related ADRs: ADR-0008, ADR-0011, ADR-0012
Supersedes: NONE
Superseded By: NONE
Validation Reference: NONE

## Contexto
El sistema server_monitoring requiere ejecutar tareas periódicas para:
- mantenimiento del sistema
- generación de backups
- operaciones de housekeeping
- ejecución de verificaciones de salud

En la arquitectura inicial se contemplaban:
- wrappers bash
- ejecución directa desde el host
- cronjobs distribuidos entre stacks

Durante la evolución del proyecto se detectaron varios problemas:
- Acoplamiento host ↔ contenedores
- Dificultad para versionar la lógica de cron
- Duplicación de scripts wrapper
- Falta de trazabilidad operacional

Adicionalmente, la gestión de backups PostgreSQL se trasladó al micro-stack postgres, eliminando la lógica externa de backup que anteriormente dependía de wrappers.

Esto obliga a definir una arquitectura clara del runtime de cron dentro del sistema.

## Decisión
Se adopta una arquitectura basada en contenedores dedicados para la ejecución de cronjobs.
Principios adoptados:
  - monitoring-cron es un contenedor del plano 2 (Infra-Stack)
    Su función es ejecutar tareas periódicas de infraestructura.
  - Los cronjobs se ejecutan directamente contra servicios Docker
      Ejemplo:
      monitoring-cron
        └ pg_dump -h postgres
    La resolución del servicio se realiza mediante DNS interno de Docker.
  - Eliminación de wrappers
    Los scripts wrapper intermedios quedan eliminados.
    Los cronjobs deben invocar directamente:
      - comandos del sistema
      - utilidades estándar
      - clientes de servicio (ej. pg_dump)
  - Separación de responsabilidades por stack
    Arquitectura resultante:
      Plano 2 — Infra-Stack
      monitoring-cron
        ├ tareas mantenimiento
        ├ housekeeping
        └ operaciones programadas infra

      Plano 1 — Micro-Stacks
      postgres
        ├ runtime base de datos
        └ lógica interna de backup
  - El runtime cron no contiene lógica de negocio
    Las tareas cron:
    - orquestan
    - invocan utilidades
    pero no implementan lógica compleja.

## Opciones consideradas
Opción A — Cron en el host

  host cron
    └ docker exec ...

  Ventajas
  - simplicidad inicial
  Inconvenientes
  - fuerte acoplamiento host
  - difícil versionado
  - menor reproducibilidad
  Resultado: rechazada

Opción B — Cron distribuido por contenedor

  container A
  container B
  container C
    └ cron propio

  Ventajas
  - encapsulación
  Inconvenientes
  - múltiples runtimes cron
  - difícil trazabilidad
  - mayor complejidad operativa
  Resultado: rechazada

Opción C — Contenedor cron dedicado (seleccionada)

  monitoring-cron
    ├ cron daemon
    ├ jobs definidos en repo
    └ acceso a servicios docker

  Ventajas
  - centralización
  - versionado en Git
  - observabilidad
  - arquitectura reproducible
  Resultado: aceptada

## Consecuencias
Positivas
  - arquitectura más predecible
  - cronjobs versionados en IaC
  - menor dependencia del host
  - eliminación de wrappers innecesarios
  - alineación con arquitectura por stacks

Negativas
  - necesidad de mantener un contenedor adicional
  - dependencia del networking docker interno
  - algunos comandos requieren clientes instalados en el contenedor cron

## Estado
Propuesto — pendiente de incorporación al compendio ADR.
