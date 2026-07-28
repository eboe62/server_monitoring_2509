# ADR-0009 – Estrategia de Backups PostgreSQL

Status: APPROVED
Date: 2026-03-05
Scope: Database
Category: DATABASE
Tags: database, postgresql, backup
Related ADRs: ADR-0008, ADR-0010
Supersedes: NONE
Superseded By: NONE
Validation Reference: NONE

## Contexto
El sistema de monitorización utiliza PostgreSQL como micro-stack autónomo para persistencia de datos.

Inicialmente el sistema utilizaba wrappers en el host que ejecutaban scripts Python mediante cron para realizar backups.

Este enfoque introducía problemas arquitectónicos:
  - Violación parcial del modelo IaC
  - Dependencia de scripts host-level
  - Dificultad para reproducir el entorno

## Decisión
Se adopta la siguiente estrategia:
1. Los backups lógicos de PostgreSQL se gestionan dentro del runtime contenerizado del proyecto.
2. La lógica de backup se ubica dentro del micro-stack postgres:
     ops/services/postgres/scripts/
3. El scheduler oficial continúa siendo el contenedor monitoring-cron.
4. El proceso de backup se ejecuta mediante pg_dump contra el servicio postgres dentro de la red Docker backend-net.
      Ejemplo conceptual:
          monitoring-cron
            └ pg_dump -h postgres
5. Los backups se almacenan en:
      /ops/backups

montado desde el host.

## Consecuencias

Ventajas
  - Coherencia total con modelo IaC
  - Eliminación de dependencias del host
  - Backups reproducibles
  - Lógica de persistencia cercana al micro-stack de datos

Limitaciones
  - Dependencia del runtime Docker para ejecución del backup
  - No sustituye snapshots del droplet como mecanismo de contingencia

Alternativas consideradas
  A) Backups ejecutados desde host
    Rechazado por violar modelo IaC.
  B) Cron interno dentro del contenedor PostgreSQL
    Rechazado por mezclar responsabilidades en el micro-stack.
  C) Scheduler externo
    Considerado innecesario para el alcance del proyecto.

## Estado
Aprobado.
