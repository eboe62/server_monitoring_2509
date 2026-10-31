# ADR-0035 – Consumo de la gobernanza y la documentación IA compartidas

Status: APPROVED
Date: 2026-10-31
Scope: System
Category: GOVERNANCE
Tags: governance, ai, cross-project, sparse-checkout, adr-index, reproducibility
Related ADRs: ADR-0033, ADR-0034
Supersedes: NONE
Superseded By: NONE
Validation Reference: herramienta de configuración de cada proyecto (§3); §Verification de governance/14_ADR_INDEX.md

---

## Context

Varios proyectos (server_monitoring_2509, GDA y, más adelante, Chino) comparten dos repositorios:

* `governance_ia_2607`: la gobernanza IA (protocolos, skills, plantillas, índice de ADR).
* `governance_ia_docs_2609`: la documentación IA.

Hasta el 31/10/2026 cada proyecto resolvía por su cuenta cómo consumirlos:

* Qué partes se traen a local solo quedaba en la configuración de git de cada copia (`.git/info/sparse-checkout`), que no se versiona. Un clon nuevo trae el repositorio completo.
* Los puntos de entrada (`CLAUDE.md`, `AI_ENTRYPOINT.md`) cambiaban entre fichero propio y enlace simbólico.
* Las ADR se copiaban entre proyectos sin un repositorio de referencia ni una comprobación de que las copias coincidieran. ADR-0033 acabó con versiones distintas en server_monitoring_2509 y en governance_ia_docs_2609 sin que nada avisara.

Este ADR es transversal: se aplica a todo proyecto que consuma estos repositorios.

---

## Decision

### 1. Papel de cada repositorio

| Repositorio | Contenido |
|---|---|
| `governance_ia_2607` | Gobernanza común: protocolos, skills, plantillas e índice integral de ADR (`governance/14_ADR_INDEX.md`) |
| `governance_ia_docs_2609` | Repositorio único de la documentación IA de todos los proyectos: `decisiones/` (todas las ADR, propias de cada proyecto y transversales) y `Project_Definition/<proyecto>/` |
| Repositorio de cada proyecto | Código, infraestructura y documentación operativa propia |

### 2. ADR

1. **Conjunto completo en cada entorno.** Cada entorno mantiene todas las ADR de todos los proyectos en su `docs/decisiones/` y usa solo las que le aplican: las suyas, las transversales y, dentro de estas, la sección de su perfil.
2. **Referencia.** `governance_ia_docs_2609/decisiones/` es la referencia. El `docs/decisiones/` de cada entorno debe ser idéntico a ella (§Verification del índice).
3. **Propiedad.** Cada ADR la modifica solo el entorno al que pertenece, según su rango: 00xx server_monitoring_2509, 06xx y 08xx GDA, 11xx Knowledge/Chino. Una ADR transversal la comparten todos, pero cada entorno modifica solo su propia sección.
4. **Transversales.** Una ADR transversal es un único fichero, igual para todos. Las diferencias entre entornos van en secciones por entorno dentro de ella, nunca en variantes con el mismo número.
5. **Cambios.** Crear o modificar una ADR incluye, en el mismo bloque de trabajo:
   * Publicarla en `governance_ia_docs_2609` (rama corta y PR).
   * Si el entorno guarda `docs/decisiones/` en su propio repositorio, actualizar esa copia en el mismo bloque.
   * Actualizar `governance/14_ADR_INDEX.md` en `governance_ia_2607` (rama corta y PR).
   * Ejecutar §Verification desde la raíz del proyecto.
   * Los demás entornos actualizan su copia desde `governance_ia_docs_2609`.

### 3. Reglas comunes de consumo

1. **Ubicación.** La gobernanza se clona en `ai/`, en la raíz del proyecto, como repositorio git independiente. El repositorio del proyecto la ignora o no la contiene.
2. **Rama.** Los repositorios compartidos se siguen en `develop` y se actualizan solo con `git pull --ff-only`.
3. **Checkout parcial.** Cada proyecto puede excluir partes que no use. Requisitos:
   * Nunca se excluyen `governance/`, `skills/` ni `templates/` de `governance_ia_2607`: ahí están el punto de entrada, el índice y los ficheros que estos citan.
   * Los patrones y su motivo se documentan en el perfil del proyecto (§4).
4. **Punto de entrada.** Cada proyecto tiene su propio `CLAUDE.md`. El punto de entrada común es `governance/00_AI_ENTRYPOINT.md`. Cómo lo enlaza cada proyecto (symlink, fichero, `@include`) consta en su perfil.
5. **Finales de línea.** LF obligatorio, impuesto por `.gitattributes` (`* text=auto eol=lf`; pdf/pptx binarios), según `Configuracion_Equipo_2608`. Se recomienda `core.autocrlf=false`.
6. **Reproducibilidad.** Cada proyecto tiene una herramienta idempotente (target de make, script) que clona los repositorios compartidos si no existen y aplica su checkout parcial. Volver a ejecutarla no cambia nada.
7. **Cambios en los repositorios compartidos.** Nunca se edita directamente en `develop`:
   * Antes de empezar, `git pull --ff-only`.
   * Rama corta `<tipo>/<aammdd>-<tema>` desde `develop` y PR a `develop`.
   * Promoción `develop → master` mediante PR ("Create a merge commit"). Después, fast-forward de `develop` a `master`.

### 4. Perfiles de proyecto

Añadir un proyecto consiste en añadir su columna; no requiere un ADR nuevo.

| | server_monitoring_2509 | GDA |
|---|---|---|
| `docs/decisiones/` | Copia versionada en el repositorio del proyecto, comparada con `ai-docs/decisiones/` (`make adr-check`) | Es el propio clon de `governance_ia_docs_2609` (`docs/`) ⚠️ pendiente de confirmar |
| Clon de `governance_ia_docs_2609` | `ai-docs/`, ignorado, checkout parcial solo de `/decisiones/` | `docs/` ⚠️ pendiente de confirmar |
| Checkout parcial de `ai/` (modo) | no-cone | ⚠️ pendiente de confirmar (cone o no-cone) |
| Patrones de `ai/` | `/*`, `!/claude_code/`, `!/opencode/`, `!/governance/00_CLAUDE.md` | `governance/`, `skills/`, `templates/` ⚠️ pendiente de confirmar los patrones literales |
| Motivo de las exclusiones | `claude_code/` y `opencode/` se conservan solo en el remoto; `00_CLAUDE.md` porque el proyecto tiene su propio `CLAUDE.md` | `claude_code/` (Docker) no aplica: GDA se desarrolla en Windows sin Docker. ⚠️ pendiente de confirmar el resto |
| `CLAUDE.md` | Fichero propio versionado en el proyecto | Fichero en la raíz con `@ai/governance/00_CLAUDE.md` ⚠️ pendiente de valorar: el `CLAUDE.md` efectivo de GDA vive en el repositorio compartido |
| Punto de entrada | `AI_ENTRYPOINT.md` → symlink versionado a `ai/governance/00_AI_ENTRYPOINT.md` | `ai/governance/00_AI_ENTRYPOINT.md`, sin enlace en la raíz ⚠️ pendiente de confirmar |
| Copilot | `.github/copilot-instructions.md` propio | No existe ⚠️ pendiente de decidir |
| Herramienta de configuración | `make ai-setup` | ⚠️ pendiente (script de Git Bash; `make` puede no estar disponible en Windows) |
| `core.autocrlf` | `false` (WSL) | `true` en la configuración de sistema ⚠️ pendiente de alinear |
| Necesita las ADR en PRO | No: el servidor no las usa; `make audit` solo comprueba que exista `docs/decisiones/` | No aplica |

---

## Consequences

### Positive

* Un repositorio de referencia para todas las ADR y una comprobación que detecta cualquier copia divergente, la que faltó con ADR-0033.
* Cada entorno ve todas las decisiones de los demás, aunque solo aplique las suyas.
* Reglas comunes para todos los proyectos. Lo que es propio de cada proyecto queda escrito en su perfil, no en su configuración local de git.
* Un clon nuevo reproduce el entorno con un solo comando.

### Negative

* Las ADR existen en más de un sitio (el repositorio central y la copia de cada proyecto que la versiona en su propio repositorio). La coherencia depende de la regla §2.5 y de la comprobación del índice.
* Un cambio de ADR requiere varios PR (repositorio central, copia del proyecto si la hay, índice).
* Los repositorios compartidos no quedan fijados a un commit concreto (no son submódulos): cada proyecto avanza cuando decide.

### Risks Mitigated

* Divergencia silenciosa de ADR copiadas entre proyectos.
* Pérdida de la configuración de checkout parcial al reclonar.
* Sobrescritura del `CLAUDE.md` de un proyecto con el de otro.
* Conflictos al editar el índice desde varios proyectos a la vez.

---

## References

* governance/14_ADR_INDEX.md (§ADR Registry, §Verification)
* .gitattributes de `governance_ia_2607`
* server_monitoring_2509: Makefile, targets `ai-setup` y `adr-check`
* ADR-0033 (taxonomía de ADR), ADR-0034 (política de ramas de server_monitoring_2509; mismo modelo de ramas)
* Configuracion_Equipo_2608
