# ADR-0035 – Consumo de la gobernanza IA compartida

Status: APPROVED
Date: 2026-10-31
Scope: Process
Category: GOVERNANCE
Tags: governance, ai, sparse-checkout, adr-index, reproducibility
Related ADRs: ADR-0033, ADR-0034
Supersedes: NONE
Superseded By: NONE
Validation Reference: make ai-setup; §Verification de ai/governance/14_ADR_INDEX.md

---

## Context

La gobernanza IA (protocolos, skills, plantillas, índice de ADR) vive en el repositorio compartido `governance_ia_2607`, que consumen varios proyectos (server_monitoring_2509, GDA). Las ADR de otros proyectos se publican en `governance_ia_docs_2609`.

Hasta el 31/10/2026 la forma en que este proyecto consumía esa gobernanza no estaba escrita:

* Qué partes del repositorio compartido se traen a local y cuáles no se decidió en sesión, y solo quedó reflejado en `ai/.git/info/sparse-checkout`, que no se versiona. Un clon nuevo de `ai/` trae el repositorio completo.
* Los puntos de entrada (`CLAUDE.md`, `AI_ENTRYPOINT.md`) habían ido cambiando entre fichero propio y enlace simbólico.
* El índice de ADR pasó a ser integral (todos los proyectos) y su comprobación de coherencia dejó de ser válida para cualquier proyecto consumidor.

---

## Decision

### 1. Ubicación

* `ai/` es un clon de `https://github.com/eboe62-appvisibility/governance_ia_2607.git` en la rama `develop`.
* Está ignorado por este repositorio (`.gitignore`: `ai/`) y se versiona de forma independiente.
* Los cambios en la gobernanza compartida se hacen en `ai/` con ramas cortas y PR hacia `develop` del repositorio compartido, con el mismo modelo que ADR-0034. Nunca se editan copias en este repositorio.

### 2. Checkout parcial (sparse-checkout, modo no-cone)

| Patrón | Motivo |
|---|---|
| `/*` | Todo lo demás se trae a local |
| `!/claude_code/` | Infraestructura de la jaula de Claude Code: se conserva solo en el remoto |
| `!/opencode/` | Configuración de opencode: se conserva solo en el remoto |
| `!/governance/00_CLAUDE.md` | Cada proyecto tiene su propio `CLAUDE.md` (punto 3) |

`04_ARCHITECTURE_GUIDELINES.md` sí se trae: lo citan `00_AI_ENTRYPOINT.md` y las skills, y el propio documento limita su alcance al desarrollo de aplicaciones backend/frontend, de modo que en este proyecto no aplica pero las referencias no quedan rotas.

La configuración se aplica con `make ai-setup` (idempotente), que clona `ai/` si no existe y fija estos patrones.

### 3. Puntos de entrada

* `CLAUDE.md`: fichero propio de este proyecto, versionado aquí. No se sincroniza desde el remoto.
* `AI_ENTRYPOINT.md`: enlace simbólico versionado a `ai/governance/00_AI_ENTRYPOINT.md`.
* `.github/copilot-instructions.md`: fichero propio de este proyecto.

### 4. Finales de línea

`ai/.gitattributes` impone LF (`* text=auto eol=lf`; pdf/pptx binarios), según `Configuracion_Equipo_2608`.

### 5. ADR

* Las ADR de este proyecto (0000–0035) se escriben en `docs/decisiones/`.
* Las ADR de GDA (06xx, 08xx) y de Knowledge (11xx) se copian desde `governance_ia_docs_2609` para mantenerlas actualizadas aunque no sean de este proyecto. En caso de divergencia prevalece la versión del remoto.
* Excepción: ADR-0033 conserva la versión local hasta que se comparen ambas.
* `ai/governance/14_ADR_INDEX.md` es un registro integral de todos los proyectos. Las filas sin fichero local son esperables. La coherencia se comprueba con §Verification (1a: toda ADR local tiene fila; 1b: sin filas duplicadas; 2: toda ADR aprobada aparece en el resumen por categoría).

---

## Consequences

### Positive

* Un clon nuevo reproduce el mismo entorno de gobernanza con un solo comando.
* Queda escrito qué se excluye y por qué, en lugar de depender de la configuración local de git.
* Un único índice de ADR para todos los proyectos, con una verificación válida en cualquiera de ellos.

### Negative

* `ai/` no queda fijado a un commit concreto (no es submódulo): cada proyecto avanza con `git pull --ff-only` cuando decide.
* La copia de ADR de otros proyectos en `docs/decisiones/` es manual hasta que exista un mecanismo de sincronización.

### Risks Mitigated

* Pérdida de la configuración de checkout parcial al reclonar `ai/`.
* Sobrescritura del `CLAUDE.md` del proyecto con el de otro proyecto.
* Falsos positivos de la verificación del índice integral.

---

## References

* Makefile: `ai-setup`
* ai/governance/14_ADR_INDEX.md (§ADR Registry, §Verification)
* ai/.gitattributes
* ADR-0033 (taxonomía de ADR), ADR-0034 (política de ramas)
* /mnt/d/WorkSpace/Proyectos/Configuracion_Equipo_2510/Configuracion_Equipo_2608.txt
