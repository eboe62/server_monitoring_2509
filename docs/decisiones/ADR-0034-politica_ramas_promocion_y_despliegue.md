# ADR-0034 – Política de ramas, promoción y despliegue a PRO

Status: APPROVED
Date: 2026-10-30
Scope: Process
Category: PROCESS
Tags: governance, branch-policy, ci, deployment
Related ADRs: ADR-0019, ADR-0028, ADR-0031, ADR-1102, ADR-1103
Supersedes: NONE
Superseded By: NONE
Validation Reference: make audit-runtime-ci (ejecutado por .github/workflows/ci.yml)

---

## Context

Hasta el 30/10/2026 el repositorio no tenía una política de ramas escrita y su estado real era:

* 19 ramas remotas, la mayoría ya integradas y sin uso.
* `master` sin cambios desde el 12/10/2025 (425 commits por detrás del trabajo real).
* Producción (`/opt/monitoring`) desplegada desde `certificacion_sre_hardening` sobre una rama local llamada `migracion`, cuyo nombre ya no describía su contenido.
* `migracion` funcionaba de hecho como rama de integración previa a producción: recibía PRs de las ramas de trabajo y su CI actuaba como filtro ante despliegues anómalos.
* Los workflows de CI se disparaban en `main` (inexistente), `develop` (abandonada desde enero) y `migracion`. `audit-runtime.yml` dependía de un runner self-hosted nunca registrado: no se ejecutó nunca, y por tanto el gate de ADR-0031 no existía en la práctica.

ADR-1102 y ADR-1103 definen un modelo `master ← develop ← ramas de contenido`, pero su alcance es el repositorio de gobernanza/conocimiento (`fuentes/`, `conocimiento/`), no las ramas de código de este proyecto.

---

## Decision

### 1. Ramas permanentes

* `master`: estado desplegable en PRO. Lo que está en `master` es lo que puede estar en producción.
* `develop`: rama de integración. Sustituye a `migracion` en su función de filtro previo a producción.

No existen otras ramas permanentes.

### 2. Ramas de trabajo

* Nombre: `<tipo>/<aammdd>-<tema>`, con `tipo` ∈ {`cierre`, `fix`, `feat`, `docs`, `ops`, `chore`} y sufijo de fecha `aammdd` (coherente con la convención de nombres de la Visión).
* Se crean desde `develop`, se integran en `develop` mediante PR y se borran tras el merge.
* Una rama por tarea o bloque del plan.

### 3. Promoción a producción

* `develop → master` mediante PR, como decisión deliberada (nunca automática).
* Estrategia de merge: "Create a merge commit".
* Tras el merge, `develop` se alinea con `master` por fast-forward.

### 4. Integración continua

* `.github/workflows/ci.yml` se ejecuta en `push` y `pull_request` sobre `develop` y `master`.
* El pipeline incluye `make audit-runtime-ci` (ADR-0031): un hallazgo `forbidden` bloquea el merge.
* Solo runners alojados por GitHub. Se descartan los runners self-hosted mientras el repositorio sea público (cualquier código que llegue a una rama disparada se ejecutaría en esa máquina).
* `setup-buildx-action` con `driver: docker`: el driver `docker-container` arranca un contenedor BuildKit privilegiado que la auditoría marca, correctamente, como `forbidden`.

### 5. Despliegue en PRO

* El servidor sigue `origin/master`. En el servidor no se hacen commits.
* Procedimiento:
  1. Snapshot del droplet con los contenedores parados (consistencia de los ficheros de PostgreSQL; el ahorro de tamaño es marginal).
  2. `git pull` de `master`.
  3. `make deploy` (solo si el cambio afecta al runtime).
  4. Verificación mediante StatusQuo (Apéndice B del documento de implementación).
  5. Tag de hito (`faseN_cierre`) cuando se cierra una fase.
* No se ejecutan en PRO con datos reales los targets destructivos `test-reproducibilidad` ni `test-SRE-completo`.

### 6. Archivado y tags

* Antes de borrar una rama con commits no integrados se crea un tag `archivo/<rama>`.
* Tags de hito: `faseN_cierre` (continúa con `fase4_cierre`).

### 7. Alcance respecto a ADR-1102 y ADR-1103

ADR-1102 y ADR-1103 rigen el repositorio de gobernanza/conocimiento. Este ADR rige las ramas de código y despliegue de server_monitoring_2509. Ambos modelos comparten la jerarquía `master ← develop ← ramas cortas`.

---

## Consequences

### Positive

* El nombre de cada rama vuelve a describir su función; producción despliega `master`.
* El CI se ejecuta en todos los puntos de integración y, por primera vez, aplica el gate de ADR-0031.
* Mismo modelo de ramas en el proyecto y en la gobernanza, lo que facilita reutilizarlo en otros proyectos.
* El borrado de ramas es reversible para lo no integrado (tags `archivo/`).

### Negative

* `develop` añade un paso de promoción y exige alinearla tras cada merge en `master`.
* No hay entorno intermedio de pruebas: la validación previa a PRO depende del CI y de la revisión del PR.
* Sin protección de rama configurada en GitHub, la política depende de disciplina manual.

### Risks Mitigated

* Despliegues desde ramas cuyo nombre no refleja su contenido.
* Gates de CI que existen en la documentación pero no se ejecutan.
* Pérdida de trabajo al limpiar ramas.

### Lecciones operativas

* Al dejar de versionar un fichero y añadirlo a `.gitignore`, un checkout a una rama o commit antiguo que todavía lo versiona lo sobrescribe sin aviso (git trata los ficheros ignorados como prescindibles). Hacer copia antes de cambiar a commits anteriores al cambio.
* Los commits de merge de una rama de integración (p. ej. `migracion`) pueden no aparecer en el historial de `master` aunque todo su contenido esté integrado. Verificar comparando árboles (`git rev-parse <rama>^{tree}`) y no solo commits.

---

## References

* .github/workflows/ci.yml
* Makefile: `audit-runtime-ci`, `test-reproducibilidad`, `test-SRE-completo`
* docs/Project_Implementation/Servidor_DigitalOcean_Implementacion.txt (FASE 3, FASE 7, Apéndice B)
* ADR-0031 (auditoría runtime en CI), ADR-0019 (estrategia de tests de resiliencia), ADR-0028 (reproducibilidad)
* ADR-1102, ADR-1103 (modelo de ramas del repositorio de gobernanza/conocimiento)
* Tags: `fase4_cierre`, `archivo/gobernanza_ia`
