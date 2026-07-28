# ADR-1101: Migración de Fuentes Primarias Ubicadas en asignaturas/ y Convención de Nombres en fuentes/

Status: APPROVED

Date: 2026-07-26

Scope:
System

Category:
ARCHITECTURE

Domain: (Optional)
Documentation, Research

Tags:
architecture, repository-structure, migration, sources

Related ADRs:
ADR-0033, ADR-1100

Supersedes:
NONE

Superseded By:
NONE

---

## Context

`AI_ENTRYPOINT.md` documenta el contrato de `asignaturas/` explícitamente: *"asignaturas/ (folders 011 to 042, one per UAM subject)"*. La carpeta `asignaturas/000-00000_miscelanea/` queda fuera de ese rango numérico — nunca fue una asignatura real, sino un cajón misceláneo que aloja material de origen externo (la revista China Book International, en `Revista_CBI_2606/`: 19 fragmentos OCR con nombre de escaneo más una versión consolidada), no estructura curricular.

`fuentes/` ya cumple, de facto, el rol de repositorio de material de referencia externo/primario (`04_SOURCE_MODEL.md`), y contiene tres patrones de nombrado no documentados pero consistentes:

* `NN_slug-kebab.{md,pdf}` — referencias institucionales oficiales numeradas.
* `YYMMDD_Tema.txt` — notas/compilaciones personales fechadas.
* `autor_tema_YYMMDD.md` — obras externas de autoría identificada.

Ninguno de los tres cubre el caso de una colección multi-archivo (una revista completa, con decenas de fragmentos escaneados). Este vacío se hizo evidente al crear Knowledge Assets (ADR-1100) que citan como fuente contenido ubicado en `asignaturas/000-00000_miscelanea/`, fuera del contrato documentado de esa carpeta.

---

## Decision

1. El contenido cuya naturaleza es material de fuente externa/primaria (según las categorías de `04_SOURCE_MODEL.md`) reside en `fuentes/`, con independencia de a qué asignatura o bloque temático sirva pedagógicamente. `asignaturas/` queda reservada exclusivamente para el árbol curricular oficial (carpetas 011-042, una por asignatura UAM), conforme a `AI_ENTRYPOINT.md`.

2. Las colecciones de fuente multi-archivo (p. ej. un número completo de revista escaneada) se organizan como subcarpeta de `fuentes/`, nombrada:

   ```
   YYMMDD_slug
   ```

   donde `YYMMDD` es la fecha de migración/curación de la colección al repositorio (no necesariamente la fecha de publicación original, que puede no conocerse con precisión de día) y `slug` es una etiqueta descriptiva breve.

3. Dentro de una colección así, el documento consolidado/curado (cuando existe) se renombra para coincidir con el nombre de su carpeta contenedora (`YYMMDD_slug.md`), de forma que sea el punto de entrada evidente. Los artefactos de escaneo individuales (fragmentos OCR con identificador generado por el escáner) **no se renombran**: su identificador original se preserva como evidencia inmutable del lote de escaneo físico, conforme al principio de trazabilidad de `04_SOURCE_MODEL.md`.

4. Como primera aplicación de esta regla: `asignaturas/000-00000_miscelanea/Revista_CBI_2606/` se migra a `fuentes/260726_revista_CBI/`, y su documento consolidado se renombra a `fuentes/260726_revista_CBI/260726_revista_CBI.md`. La carpeta `asignaturas/000-00000_miscelanea/`, ya vacía, se elimina.

5. **Separación por rama**: esta ADR es un artefacto de gobernanza y reside en la rama `develop`. Su ejecución material (el `git mv` descrito en el punto 4, y la actualización consecuente de los Knowledge Assets de ADR-1100) se realiza en la rama que contiene el conocimiento adquirido correspondiente (`cbi_260726` a fecha de este ADR), conforme al criterio explícito del usuario: *gobernanza en `develop`, conocimiento adquirido en su rama propia*. `develop` conserva la regla; la rama de contenido aplica el cambio físico.

---

## Consequences

### Positive

* `asignaturas/` vuelve a cumplir exactamente su contrato documentado (011-042, una por asignatura).
* `fuentes/` gana un cuarto patrón de nombrado explícito y documentado, coherente con los tres ya existentes de facto.
* Corrige la inconsistencia en su origen en lugar de documentarla como excepción permanente.

### Negative

* Rompe las rutas relativas ya citadas en los 3 Knowledge Assets y 3 Relationship Records de ADR-1100 — requiere actualización coordinada en la rama de contenido.
* Invalida el `knowledge-graph.json` actual (`layer:asignaturas`, paso 9 del tour, y el `filePath` del nodo del documento afectado) hasta una nueva ejecución de `/understand`.
* Los 19 fragmentos OCR individuales permanecen con nombre de escaneo no legible — aceptado como deuda temporal, ya que según el usuario probablemente se eliminarán.

### Risks Mitigated

* Perpetuar un contrato de repositorio documentado pero incumplido.
* Ambigüedad sobre dónde ubicar futuro material de fuente no curricular (p. ej. próximos números de revista).

---

## References

* ADR-1100-Knowledge_Repository_Ubicacion_y_Naming.md
* docs/Project_Definition/04_SOURCE_MODEL.md
* AI_ENTRYPOINT.md
* docs/Project_Definition/02_MASTER_ARCHITECTURE.md
