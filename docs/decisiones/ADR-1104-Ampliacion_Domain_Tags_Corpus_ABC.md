# ADR-1104: Ampliación del vocabulario Domain y Tags a partir de la cobertura temática del corpus 260726_ABC

Status: APPROVED

Date: 2026-07-26

Scope:
Knowledge

Category:
KNOWLEDGE

Domain: (Optional)
Governance, Research

Tags:
taxonomy, classification, knowledge-asset, domain-vocabulary, ontology

Related ADRs:
ADR-0033, ADR-1100

Supersedes:
NONE

Superseded By:
NONE

---

## Context

Antes de iniciar la elaboración de fichas de Knowledge Asset (`ai/templates/30_knowledge_asset.md`) y Relationship Records (`ai/templates/31_relationship_record.md`) para el corpus depurado en `fuentes/260726_ABC/` (54 documentos de prensa española — ABC, El País, NYT, Metrópoli — sobre China), se ha realizado una revisión de cobertura: se ha contrastado el tema principal de cada uno de los 54 documentos contra:

* el vocabulario canónico del campo `Domain` definido en `ADR-0033-Taxonomia_ADRs.md` § Domain (21 términos: Anthropology, Culture, Documentation, Economics, Engineering, Geography, Governance, Hiking, History, Infrastructure, Language, Literature, Megaprojects, Mountaineering, Politics, Research, Study_Planning, Technology, TFG, Translation, Travel);
* las familias de Entity Type definidas en `docs/Project_Definition/03_ONTOLOGY.md` (ACADEMIC, LANGUAGE, GEOGRAPHY, HISTORY, POLITICS, ECONOMICS, ENGINEERING, CULTURE, SOCIETY, PERSONAL INTERESTS, KNOWLEDGE).

La mayoría del corpus encaja sin ambigüedad en el vocabulario existente (Economics, Politics, History, Engineering, Geography, Travel, Technology cubren razonablemente ~48 de los 54 documentos, incluyendo el bloque temático más numeroso — "colonialismo"/expansión geopolítica china, 11 documentos — bien cubierto por `Politics`).

Sin embargo, se han identificado tres huecos de cobertura concretos y uno adicional recomendado, con evidencia directa en el corpus:

1. **SOCIETY** — la familia `SOCIETY` ya existe en `03_ONTOLOGY.md` (Ethnic Group, Population, Community, Social Phenomenon, Demographic Indicator) pero **no** está presente en el vocabulario `Domain` de `ADR-0033.md`. Esto es una inconsistencia entre ambos documentos. Afecta directamente a: `050301_ABC_Inmigracion.md`, `060820_Pais_Inmigracion_Qingtian.md`, `131215_Pais_Inmigracion.md` (inmigración/diáspora china en España — fenómeno social/demográfico) y `121101_ABC_Recursos_Alimentacion_China.md` (escándalos alimentarios como fenómeno social).

2. **EDUCATION** — ausente tanto de `Domain` como de las familias de `03_ONTOLOGY.md`. Afecta a `131201_ABC_Educacion_Jincai.md` (ranking PISA, sistema educativo de Shanghái, comparativa con Singapur/Taiwán/Corea del Sur) y, de forma parcial, a `151206_Pais_Meritocracia.md` (sistema de exámenes imperial/meritocracia, tradicionalmente ligado a la educación como institución social).

3. **ECOLOGY** — ausente tanto de `Domain` como de `03_ONTOLOGY.md`. Afecta a `220901_ABC_Ecologia.md` (entrevista a Gretchen Daily sobre servicios ecosistémicos y biodiversidad en China). `Geography` no cubre conceptualmente ecosistemas/biodiversidad (sus entidades son Country/Province/City/Mountain/River, espacio físico, no sistemas ecológicos).

4. **ASTRONOMY / SPACE EXPLORATION** (recomendado, no estrictamente bloqueante) — 3 documentos (`190201_ABC_Astronomia_Exploracion_Change5.md`, `210509_ABC_Astronomia_Exploracion.md` [radiotelescopio FAST], `210516_ABC_Astronomia_Exploracion_Marte.md`) tratan del programa espacial chino. `Technology` puede forzarse para cubrirlos, pero es un término genérico que no distingue exploración espacial/astronomía de tecnología industrial o de consumo.

Adicionalmente, el catálogo de Tags de `ADR-0033.md` está orientado a la clasificación de ADRs de infraestructura/DevSecOps (docker, security, runtime, etc.) y solo dispone de un bloque `Knowledge` genérico (language, linguistics, grammar, hanzi, pinyin, curriculum, learning, research, classification, taxonomy, ontology, history, culture, translation, knowledge-asset, knowledge-repository). Las tres fichas de Knowledge Asset ya existentes en `conocimiento/` (creadas antes de este ADR, a partir de `fuentes/260726_revista_CBI/`) ya emplean tags de contenido ad hoc fuera de este catálogo (p. ej. `zheng-yongnian`, `china-economy`, `anti-involution`) — práctica permitida por la regla 3 de `ADR-0033.md` ("cuando no exista un tag adecuado, podrán incorporarse nuevos conceptos estables") pero nunca formalizada en el catálogo conforme a la regla 5.

---

## Decision

1. Ampliar el vocabulario canónico `Domain` de `ADR-0033.md` § Domain añadiendo cuatro términos: **Society, Education, Ecology, Astronomy**.

2. Ampliar `docs/Project_Definition/03_ONTOLOGY.md` § ENTITY TYPES:
   - Formalizar `SOCIETY` (ya existente) como anclaje ontológico del nuevo Domain `Society` — sin cambios en su lista de entidades.
   - Añadir nueva familia `ECOLOGY` (Ecosystem, Species, Conservation_Status, Pollution_Source, Environmental_Policy).
   - Añadir nueva familia `EDUCATION` (Educational_System, School, Examination, Curriculum, Student_Population) — distinta de `ACADEMIC`, que queda reservada al propio itinerario académico del estudiante (Degree/Course/Subject/TFG), mientras que `EDUCATION` describe sistemas educativos como objeto de estudio (p. ej. el sistema educativo chino).
   - No se crea familia `ASTRONOMY` en la ontología (se considera cubierta por `PERSONAL INTERESTS > Technology` a nivel de entidad), pero sí se añade `Astronomy` como `Domain` para permitir una clasificación de ficha más precisa que el genérico `Technology`.

3. Ampliar el catálogo de Tags de `ADR-0033.md` con un nuevo bloque **"China Studies / Contenido"**, poblado con temas recurrentes identificados directamente en el corpus `fuentes/260726_ABC/`: `china-africa-relations`, `neocolonialism`, `south-china-sea`, `silk-road`, `rare-earths`, `xinjiang`, `terracotta-army`, `genghis-khan`, `mongolia`, `great-wall`, `immigration-diaspora`, `food-safety`, `five-year-plan`, `space-exploration`, `ecosystem-services`, `education-pisa`, `meritocracy-keju`, `tech-war`.

4. Sustituir, en `ai/templates/30_knowledge_asset.md` y `ai/templates/31_relationship_record.md`, la lista de ejemplos de `Domain` (actualmente duplicada literalmente) por una referencia explícita a `ADR-0033-Taxonomia_ADRs.md` § Domain como fuente única — eliminando el riesgo de divergencia futura entre plantillas y ADR que `ADR-1100.md` punto 5 ya identificaba como principio pero no aplicaba de forma completa (las plantillas seguían manteniendo una copia literal de la lista).

5. Registrar este ADR en `ai/governance/14_ADR_INDEX.md` con estado `PROPOSED`.

**Nota de gobernanza**: este ADR fue aprobado explícitamente por el usuario el 2026-07-26 (cambio de Status de `PROPOSED` a `APPROVED`). Los puntos 1–4 de esta Decision se aplicaron en el mismo momento sobre `ADR-0033.md`, `03_ONTOLOGY.md` y las plantillas correspondientes, y `14_ADR_INDEX.md` fue actualizado en consecuencia.

---

## Consequences

### Positive

* Cobertura temática completa del corpus `260726_ABC` (54/54 documentos con un Domain adecuado, frente a 48/54 con el vocabulario actual).
* Resuelve la inconsistencia preexistente entre `03_ONTOLOGY.md` (que ya incluye `SOCIETY`) y `ADR-0033.md` (que no lo listaba en `Domain`).
* Formaliza una práctica de tagging de contenido que ya se venía aplicando de facto en `conocimiento/` sin respaldo documental explícito.
* Elimina la duplicación de la lista de ejemplos de `Domain` entre `ADR-0033.md` y las dos plantillas, reduciendo mantenimiento futuro.

### Negative

* Modifica un ADR ya `APPROVED` (`ADR-0033.md`), lo que requiere revisión explícita antes de aplicarse.
* Introduce dos nuevas familias en la ontología (`ECOLOGY`, `EDUCATION`), lo que amplía la superficie conceptual a mantener.
* El bloque de Tags "China Studies" es específico de este proyecto de estudios chinos y no sigue el mismo patrón (infra/DevSecOps) que el resto del catálogo — puede requerir su propio criterio de gobernanza a futuro si el proyecto amplía su alcance más allá de China.

### Risks Mitigated

* Fichas de Knowledge Asset futuras forzando un `Domain` inadecuado (p. ej. clasificar un artículo sobre biodiversidad como `Geography` solo por ausencia de una opción mejor).
* Divergencia silenciosa futura entre el vocabulario `Domain` de `ADR-0033.md` y las listas de ejemplo de las plantillas.

---

## References

* ADR-0033-Taxonomia_ADRs.md
* ADR-1100-Knowledge_Repository_Ubicacion_y_Naming.md
* docs/Project_Definition/03_ONTOLOGY.md
* ai/templates/30_knowledge_asset.md
* ai/templates/31_relationship_record.md
* fuentes/260726_ABC/ (54 documentos revisados como evidencia de esta propuesta)
