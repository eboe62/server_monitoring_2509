# ADR-1100: Knowledge Repository — Ubicación Física y Convención de Nombres de Knowledge Assets

Status: APPROVED

Date: 2026-07-26

Scope:
Knowledge

Category:
KNOWLEDGE

Domain: (Optional)
Research, Documentation

Tags:
taxonomy, classification, knowledge-asset, knowledge-repository

Related ADRs:
ADR-0033

Supersedes:
NONE

Superseded By:
NONE

---

## Context

`docs/Project_Definition/02_MASTER_ARCHITECTURE.md` (componente 4) define un componente arquitectónico llamado "Knowledge Repository": *"Contains the project's human-readable Knowledge Assets and supporting documentation"*. Este componente está definido conceptualmente desde el origen del proyecto, pero nunca se le asignó una ubicación física en el árbol de directorios.

De forma paralela, `ai/templates/30_knowledge_asset.md` y `ai/templates/31_relationship_record.md` existen como plantillas desde antes de este ADR, pero nunca habían sido instanciadas — no existe en el repositorio ningún ejemplo real de Knowledge Asset ni de Relationship Record.

Esta carencia se hizo evidente al catalogar tres artículos de la revista China Book International (Revista_CBI_2606) como Knowledge Assets: no había ni ubicación designada ni convención de nombres para los archivos resultantes. La solución ad hoc adoptada inicialmente (prefijar el nombre de archivo con el identificador de escaneo OCR del documento fuente, p. ej. `S45C-0i26072306440_slug.md`) resultó frágil: acopla el nombre de la ficha a un identificador mutable y ajeno al propio conocimiento curado, y duplica una trazabilidad que ya proporciona el Relationship Record — violando el principio arquitectónico "Relationships have priority over hierarchy" (`02_MASTER_ARCHITECTURE.md`).

`asignaturas/` (árbol curricular oficial, carpetas 011-042) y `fuentes/` (material de referencia externo/primario) ya tienen roles definidos y no son apropiados para alojar conocimiento curado por el propio proyecto.

---

## Decision

1. `conocimiento/` (raíz del repositorio, hermana de `asignaturas/`, `fuentes/`, `docs/`, `ai/`) se adopta como la implementación física del componente "Knowledge Repository" definido en `02_MASTER_ARCHITECTURE.md` §4.

2. Estructura interna:
   - `conocimiento/*.md` — instancias de `30_knowledge_asset.md` (archivos planos, sin subcarpetas por dominio mientras el volumen no lo justifique).
   - `conocimiento/relaciones/*.md` — instancias de `31_relationship_record.md`, usando el mismo nombre base que su Knowledge Asset emparejado (la subcarpeta ya distingue el tipo de artefacto; no se añade sufijo `_relacion`).

3. Convención de nombres para archivos de Knowledge Asset y su Relationship Record emparejado:

   ```
   YYMMDD-domain_principal-slug.md
   ```

   - `YYMMDD`: fecha en que se curó/redactó el Knowledge Asset (no la fecha de publicación de la fuente original, que puede no conocerse con precisión de día — evita fabricar datos, conforme al principio de veracidad de `00_PROJECT_VISION_Chino_Definicion_Proyecto.md`).
   - `domain_principal`: el primer término listado en el campo `Domain` de la ficha, en minúsculas, tomado del vocabulario canónico de `ADR-0033-Taxonomia_ADRs.md` § Domain.
   - `slug`: identificador breve en kebab-case del tema.

4. Los Knowledge Assets en `conocimiento/` referencian sus fuentes exclusivamente mediante `31_relationship_record.md` (relación `derived_from`). No se duplica contenido de la fuente ni se incrustan identificadores específicos de la fuente (p. ej. códigos de escaneo OCR) en el nombre del propio Knowledge Asset.

5. El campo `Domain` de `30_knowledge_asset.md` y `31_relationship_record.md` reutiliza el vocabulario canónico de `ADR-0033-Taxonomia_ADRs.md` § Domain como fuente única — no se mantienen listas de ejemplos divergentes entre plantillas.

---

## Consequences

### Positive

* El componente "Knowledge Repository", definido desde el origen del proyecto pero sin ubicación, queda materializado.
* Nombres de archivo ordenables cronológicamente, legibles por humanos y desacoplados de identificadores externos mutables.
* Vocabulario de `Domain` unificado entre ADRs y Knowledge Assets (una sola fuente canónica).

### Negative

* Requiere renombrar los 3 Knowledge Assets y 3 Relationship Records creados antes de este ADR para conformarlos a la convención.
* Introduce una nueva carpeta raíz que debe recordarse al auditar la estructura del repositorio.

### Risks Mitigated

* Acoplamiento de nombres de archivo a identificadores externos mutables (códigos de escaneo OCR).
* Ambigüedad sobre dónde debe residir el conocimiento curado por el proyecto.
* Divergencia futura y silenciosa de convenciones de nombrado entre distintas fichas.

---

## References

* ADR-0033-Taxonomia_ADRs.md
* docs/Project_Definition/02_MASTER_ARCHITECTURE.md
* ai/templates/30_knowledge_asset.md
* ai/templates/31_relationship_record.md
