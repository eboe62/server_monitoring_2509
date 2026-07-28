# ADR-1105: Procedimiento de Elaboración y Verificación de Knowledge Assets por Lotes

Status: APPROVED

Date: 2026-07-26

Scope:
Knowledge

Category:
KNOWLEDGE

Domain: (Optional)
Documentation, Research, Governance

Tags:
knowledge-asset, knowledge-repository, methodology, taxonomy, batch-processing

Related ADRs:
ADR-1100, ADR-1101, ADR-1102, ADR-1103, ADR-1104

Supersedes:
NONE

Superseded By:
NONE

---

## Context

Durante la elaboración de 54 Knowledge Assets y 54 Relationship Records a partir del corpus `fuentes/260726_ABC/` (54 artículos de prensa depurados), se aplicó un procedimiento completo — ingesta, depuración, chequeo de cobertura `Domain`/`Tags`/Ontology, elaboración en lotes paralelos, verificación post-elaboración y secuencia de ramas — que **no está documentado en ningún ADR existente**. `ADR-1103.md` regula el *merge* entre ramas, pero no cómo se elabora contenido dentro de una rama de contenido; `ADR-1100.md` y `ADR-1101.md` regulan ubicación y naming, pero no el proceso de curación en sí.

Este procedimiento tiene valor duradero: se repetirá con cada nuevo corpus incorporado al proyecto (ya ocurrió antes, de forma menos sistemática, con `fuentes/260726_revista_CBI/`). Dejarlo sin documentar implica que cada sesión futura tendría que re-derivarlo, con riesgo de inconsistencia (criterios de verificación distintos, tamaños de lote arbitrarios, o —el riesgo más importante observado en la práctica— fichas que declaran relaciones no verificadas entre sí por simple coincidencia temática).

**Nota de gobernanza**: este ADR fue aprobado explícitamente por el usuario el 2026-07-26, junto con la activación del skill `ai/skills/documentation/elaborar_knowledge_assets.md` que lo operacionaliza.

Evidencia concreta de por qué el procedimiento es necesario, observada durante su aplicación:

* Sin un chequeo de cobertura previo (`ADR-1104.md`), 3 de los 54 documentos no habrían tenido un `Domain` adecuado (`Society`, `Education`, `Ecology`).
* Sin una regla explícita de lectura íntegra de la fuente antes de escribir, dos lotes paralelos habrían podido duplicar la misma ficha bajo nombres distintos (ocurrió un caso límite: los ficheros `130201_NYT_Economia.md` y `130202_NYT_Economia.md` recibieron sugerencias de `Domain`/slug cruzadas por error del orquestador; dos lotes distintos lo detectaron y corrigieron de forma independiente durante la lectura, sin necesidad de intervención humana).
* Sin una regla explícita de "no declarar relación sin verificación cruzada", el hallazgo de temática solapada entre varias fichas (dos perfiles de Mao Zedong, tres artículos sobre inmigración china en España, dos artículos sobre Zheng He) se documentó como nota en `Notes`/`Related Assets`, no como una relación `related_to` fabricada — este es precisamente el comportamiento que se quiere formalizar como regla, no como buena suerte.

---

## Decision

Se adopta el siguiente procedimiento como Knowledge Asset Elaboration Procedure, obligatorio para cualquier corpus de fuentes ya ingerido conforme a `ADR-1101.md`.

### Fase 1 — Ingesta y depuración de fuentes

* Ubicación conforme a `ADR-1101.md` (`fuentes/<corpus>/`).
* Depuración de contenido ajeno al tema principal del proyecto (estudios chinos) cuando el escaneo original mezclaba artículos no relacionados.
* Corrección del nombre de fichero al día real de publicación cuando el propio documento lo revele (patrón `YYMMDD`, sin inventar el dato si no está disponible).

### Fase 2 — Chequeo de cobertura Domain/Tags/Ontology

* Antes de iniciar la elaboración de fichas, contrastar el tema principal de cada documento del corpus contra el vocabulario canónico vigente (`ADR-0033-Taxonomia_ADRs.md` § Domain) y las familias de `docs/Project_Definition/03_ONTOLOGY.md`.
* Si existen huecos de cobertura reales (no forzables con el vocabulario vigente), proponer su ampliación mediante un ADR específico (siguiendo el precedente de `ADR-1104.md`) **en la rama `develop`**, antes de continuar a la Fase 3.
* No proceder a la Fase 3 usando términos de `Domain` fuera del vocabulario canónico vigente.

### Fase 3 — Elaboración de fichas en lotes paralelos

* Tamaño de lote recomendado: **~9 documentos por lote** (equilibrio observado entre paralelismo y carga de contexto por agente).
* Cada lote se asigna a un agente independiente con: la lista exacta de ficheros fuente asignados, el vocabulario `Domain` vigente completo, los niveles de confianza de `05_EVIDENCE_CONFIDENCE.md`, y una sugerencia inicial de `Domain`/slug por documento (ajustable tras la lectura).
* **Regla obligatoria**: cada agente debe leer el fichero fuente completo antes de escribir su ficha — no se infiere contenido a partir del nombre de fichero o de metadatos.
* **Regla obligatoria**: toda desviación respecto al `Domain`/slug sugerido debe justificarse explícitamente en el campo `Purpose` de la ficha resultante.
* **Regla obligatoria**: ninguna ficha declara una relación (`Related Knowledge Assets`, `related_to`) con otra ficha salvo que se haya verificado explícitamente por lectura cruzada — el solapamiento temático detectado sin verificación cruzada se documenta como nota informativa, nunca como relación formal.
* Knowledge Type, Status y Confidence Level se asignan conforme a `ai/templates/30_knowledge_asset.md`, `ai/templates/31_relationship_record.md` y `05_EVIDENCE_CONFIDENCE.md` respectivamente.

### Fase 4 — Verificación post-elaboración (checklist obligatorio)

Antes de considerar completa la elaboración de un lote o corpus:

1. **Cobertura**: cada fichero fuente del corpus tiene exactamente una ficha Knowledge Asset (ni huérfanos ni duplicados).
2. **Emparejamiento**: cada Knowledge Asset tiene un Relationship Record con nombre base idéntico en `conocimiento/relaciones/`.
3. **Integridad estructural**: ninguna ficha está truncada (verificar que termina en el bloque `Prohibited Actions` de la plantilla).
4. **Sin colisiones**: no hay nombres de fichero duplicados entre lotes paralelos.
5. **Solapamientos documentados, no inventados**: los casos de temática solapada detectados se listan aparte, sin relaciones formales no verificadas.

### Fase 5 — Secuencia de ramas y commits

* La elaboración de fichas ocurre en la rama de contenido (nunca se commitea automáticamente: se espera confirmación explícita del usuario, conforme al principio general de separación análisis/ejecución).
* Tras la verificación de la Fase 4 y la confirmación del usuario, se commitea el lote completo en la rama de contenido.
* El resto de la secuencia (merge a `develop`, regeneración del grafo de conocimiento, merge a `master`) sigue `ADR-1102.md` y `ADR-1103.md` sin modificación.

### Diagrama del pipeline completo

```
 fuentes/<corpus>/ (escaneo bruto, ADR-1101)
        │
        ▼
 Fase 1 — Depuración
   • quitar contenido ajeno
   • corregir YYMMDD real
        │
        ▼
 Fase 2 — Chequeo Domain/Tags/Ontology
   • contrastar contra ADR-0033 §Domain + 03_ONTOLOGY.md
   • ¿hueco real de cobertura?
        │           │
        │ no        │ sí
        │           ▼
        │     ADR de ampliación (ver ADR-1104)
        │     — se redacta y aprueba en `develop` —
        │           │
        └─────┬─────┘
              ▼
 Fase 3 — Elaboración por lotes paralelos (~9 docs/lote)
   • leer fuente completa antes de escribir
   • Domain/slug sugerido → ajustar y justificar en Purpose
   • no declarar relaciones sin verificación cruzada
        │
        ▼
 Fase 4 — Verificación (checklist)
   1. cobertura 1:1 fuente→KA
   2. emparejamiento KA↔RR
   3. integridad estructural (sin truncados)
   4. sin colisiones de nombre
   5. solapamientos documentados, no inventados
        │
        ▼
 Fase 5 — Ramas y commits
   rama de contenido (sin commit automático)
        │  ← confirmación explícita del usuario
        ▼
   commit en rama de contenido
        │  ← usuario decide cerrar la rama (ADR-1103)
        ▼
   merge → develop
        │
        ▼
   regenerar knowledge graph (/understand)
        │  ← develop por delante de master + grafo fresco (ADR-1103)
        │  ← confirmación explícita del usuario
        ▼
   merge → master
```

---

## Consequences

### Positive

* El procedimiento aplicado ad hoc en la sesión que originó este ADR queda reproducible para futuros corpus (p. ej. futuras incorporaciones a `fuentes/`).
* Reduce el riesgo de relaciones fabricadas entre Knowledge Assets — riesgo real observado (solapamientos temáticos genuinos que podrían haberse convertido en relaciones no verificadas).
* Establece un tamaño de lote de referencia (9 documentos) basado en experiencia real, evitando improvisación futura.
* El checklist de verificación de la Fase 4 es mecánico y auditable (recuento de fuentes citadas, comprobación de sufijo `Prohibited Actions`, diff de nombres de fichero).

### Negative

* Añade una fase de gobernanza (Fase 2) antes de poder empezar a elaborar fichas, lo que puede percibirse como sobrecarga en corpus pequeños o de un solo documento.
* El tamaño de lote recomendado (9) es una observación empírica de un único corpus (54 documentos) y puede no ser óptimo para corpus de tamaño muy distinto.

### Risks Mitigated

* Fichas Knowledge Asset con `Domain` forzado por ausencia de una opción adecuada.
* Relaciones `related_to` fabricadas a partir de similitud temática superficial, sin verificación cruzada real.
* Fichas truncadas o incompletas pasando desapercibidas tras interrupciones de sesión (observado en la práctica: un lote se cortó por límite de sesión y la verificación posterior confirmó que, pese al corte, ningún fichero quedó incompleto).
* Commits prematuros de contenido de conocimiento antes de completar la verificación.

---

## References

* ADR-1100-Knowledge_Repository_Ubicacion_y_Naming.md
* ADR-1101-Migracion_Fuentes_Miscelanea_y_Naming.md
* ADR-1102-Modelo_de_Ramas_Gobernanza_vs_Contenido.md
* ADR-1103-Procedimiento_Validado_de_Integracion_de_Ramas.md
* ADR-1104-Ampliacion_Domain_Tags_Corpus_ABC.md
* ai/templates/30_knowledge_asset.md
* ai/templates/31_relationship_record.md
* docs/Project_Definition/05_EVIDENCE_CONFIDENCE.md
* ai/skills/documentation/elaborar_knowledge_assets.md (skill que operacionaliza este procedimiento)
* fuentes/260726_ABC/ y conocimiento/ (54+54 fichas elaboradas como caso de referencia de este procedimiento)
