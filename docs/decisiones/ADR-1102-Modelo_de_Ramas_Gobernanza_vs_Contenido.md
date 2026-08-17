# ADR-1102: Modelo de Ramas — Gobernanza vs. Contenido (Fuentes/Conocimiento)

Status: APPROVED

Date: 2026-07-26

Scope:
System

Category:
PROCESS

Domain: (Optional)
Documentation, Research

Tags:
governance, repository-structure, branch-policy

Related ADRs:
ADR-1100, ADR-1101

Supersedes:
NONE

Superseded By:
NONE

---

## Context

Durante la creación de ADR-1100/ADR-1101 se estableció, de forma verbal y puntual dentro de esta conversación, que la gobernanza reside en `develop` y el conocimiento adquirido (`fuentes/`, `conocimiento/`) reside en ramas paralelas de contenido (p. ej. `cbi_260726`). Esta regla nunca quedó documentada como tal en ningún artefacto de gobernanza — solo aparecía, de pasada, en el punto 5 de `ADR-1101`, referida al caso concreto de esa migración.

La ausencia de una regla escrita explícita permitió una anomalía real: una instrucción puntual ("hacemos commit de los cambios en la rama develop") llevó, de forma literal y razonable en ese momento, el renombrado de `fuentes/01_grado-en-estudios-de-asia-y-africa-arabe.{md,pdf}` a `develop` (commit `b96218a`). El propio usuario detectó la anomalía después y decidió no reescribir el historial — solo dejar constancia y reforzar la regla hacia adelante.

Aparte de esa regla de separación, se ha clarificado durante esta sesión un segundo aspecto no documentado hasta ahora: la jerarquía y el ciclo de vida completo de las ramas del repositorio (`master` ← `develop` ← ramas de contenido), y el hecho de que la separación actual es una fase transitoria, no permanente.

---

## Decision

1. **Jerarquía de ramas de tres niveles**:

   ```
   master
     ↑ (integración futura, una vez develop esté maduro)
   develop
     ↑ (integración futura, una vez la rama de contenido esté madura)
   rama(s) de contenido — p. ej. cbi_260726
   ```

2. **`develop` contiene exclusivamente artefactos de gobernanza**: `ai/` (governance, templates, skills), `docs/Project_Definition/`, `docs/decisiones/` (ADRs). Nunca contiene cambios en `fuentes/` ni `conocimiento/`, incluso si una instrucción puntual lo solicita literalmente — esta ADR prevalece sobre instrucciones ad hoc que la contradigan sin revisarla explícitamente primero.

3. **El conocimiento adquirido vive en una o varias ramas de contenido**, paralelas a `develop`. El número y el criterio de creación de estas ramas (una única rama evergreen, o una nueva rama por cada fuente/tema/adquisición) queda **deliberadamente abierto** mientras el proyecto define sus objetivos, gestión y procedimientos — no se fuerza una convención de nomenclatura o de una-rama-por-adquisición todavía.

4. **Flujo de integración descendente únicamente en un sentido durante la fase actual**: los cambios de gobernanza se autoran en `develop` y se integran en las ramas de contenido por `merge` (`develop` → rama de contenido). El sentido inverso (contenido → `develop`) **no ocurre mientras la rama de contenido esté en fase activa/experimental**.

5. **Integración ascendente diferida**: cuando una rama de contenido alcance suficiente madurez — objetivos, gestión y procedimientos ya definidos y estables —, se integrará en `develop`; posteriormente, `develop` se integrará en `master`. Esta ADR no define todavía los criterios de madurez que activan ese momento; quedan para una decisión posterior.

6. **Sin mecanismo de bloqueo automático**: se evaluó y se descarta explícitamente un hook `pre-commit` que impidiera commits de `fuentes/`/`conocimiento/` mientras `develop` está activa. El criterio adoptado es que los errores de este tipo son puntuales, de bajo impacto y fácilmente asumibles (como demuestra el propio caso que motiva esta ADR): se corrigen por revisión manual cuando se detectan, sin reescribir historial, en lugar de imponer una restricción técnica permanente.

---

## Consequences

### Positive

* Deja escrita, por primera vez, una regla que ya se aplicaba de facto pero que había fallado una vez por no estar documentada.
* Reconoce explícitamente que la separación actual es una fase transitoria y no una arquitectura final — evita que futuras decisiones asuman erróneamente que la separación es permanente.
* Evita sobre-ingeniería (no impone un hook, no impone una convención de nombrado de ramas todavía) — coherente con "minimum necessary governance" (`02_MASTER_ARCHITECTURE.md`).

### Negative

* Al no haber mecanismo técnico de bloqueo, la regla depende de disciplina manual y puede volver a incumplirse puntualmente.
* Quedan deliberadamente sin definir: el criterio de madurez para la integración ascendente, y el criterio de una-rama-vs-varias para el contenido — riesgo de tener que revisar esta ADR pronto.

### Risks Mitigated

* Repetición de la anomalía por ausencia de regla escrita.
* Asunción implícita de que la separación actual de ramas es definitiva, cuando en realidad es transitoria.

---

## References

* ADR-1100-Knowledge_Repository_Ubicacion_y_Naming.md
* ADR-1101-Migracion_Fuentes_Miscelanea_y_Naming.md
* Commit b96218a (caso que motiva esta ADR)
* ai/templates/10_repository_event.md (convención de nombres de commit por rama)
