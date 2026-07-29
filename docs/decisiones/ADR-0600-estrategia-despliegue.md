# ADR-0600: Estrategia de Despliegue: Arquitectura de Microservicios Independientes basados en Maven Multi-Module

Status: APPROVED
Date: 2026-06-11 (revisado 2026-07-22 con evidencia real de deriva de versión entre módulos)
Scope: System
Category: ARCHITECTURE
Tags: REVIEW_REQUIRED
Related ADRs: ADR-0601, ADR-0602, ADR-0603
Supersedes: NONE
Superseded By: NONE
Validation Reference: NONE

## Contexto
El backend de la plataforma GDA está compuesto por múltiples carpetas de negocio diferenciadas (gda-finance, gda-imputacion, gda-persona, etc.). Cada una cuenta de forma nativa con su propio wrapper de Maven (`mvnw`), su directorio de configuración `.mvn` y su archivo `pom.xml` independiente. Esto demuestra que, aunque comparten el mismo repositorio de código (Monorrepo), no están concebidos como un único monolito acoplado en tiempo de compilación.

## Decisión
Establecer un modelo de arquitectura de Microservicios Desacoplados. Cada módulo se tratará como un artefacto con ciclo de vida, compilación y despliegue completamente independiente. Se prohíbe la creación de un `pom.xml` padre en la raíz que fuerce una compilación en bloque reactiva si no es estrictamente necesario para la canalización de CI/CD.

## Deuda técnica / mejoras pendientes (no bloqueantes para nuevos módulos)
- **Gestión de versiones entre módulos, sin BOM compartido:** confirmado en la práctica real (no solo como riesgo teórico, ver "Negativas" más abajo). Cada dependencia `-commons` en `api-gateway/pom.xml` fija una versión de release concreta (`gda-estructura-commons:4.4.1`, `gda-admingade-commons:4.6.1`, `gda-agrupacion-commons:4.2.0`, `gda-persona-commons:4.3.0`), sin ningún mecanismo (BOM, script, CI) que la mantenga sincronizada con la versión real del módulo productor. **Evidencia real (2026-07-22):** al ampliar `gda-persona` (versión de `pom.xml` en `4.4.0-SNAPSHOT`) con los campos de auditoría de Vendors (`persona_id`, ver `Documentacion_BackEnd_GDA_2607_Vendors.md` §14), `api-gateway/pom.xml` seguía fijado a `gda-persona-commons:4.3.0` — una versión de release anterior, ya en `.m2` desde antes de estos cambios. El resultado fue un error de compilación reproducible (`cannot find symbol: method setPersonaId`) que persistió incluso reinstalando `gda-persona-commons` en `.m2`, porque Maven resolvía la coordenada `4.3.0` (no tocada) en vez de la `4.4.0-SNAPSHOT` recién construida. Solución aplicada para desarrollo local: actualizar temporalmente el pin a `4.4.0-SNAPSHOT` (cambio que se excluye del commit, ver nota de la Fase 4 en el documento de backend); pendiente decidir el mecanismo definitivo (publicar `gda-persona-commons:4.4.0` como release real en Nexus y actualizar el pin, o adoptar un BOM compartido que reduzca este tipo de desajuste).

## Consecuencias

### Positivas (+)
- Permite desplegar cambios en un módulo (ej. `gda-finance`) sin necesidad de recompilar, probar o reiniciar los demás módulos (ej. `gda-persona`).
- Escalabilidad horizontal independiente por cada servicio según la carga de trabajo.

### Negativas (-)
- Exige una gestión rigurosa de las versiones de las dependencias de forma externa (o mediante un BOM compartido) para evitar la deriva tecnológica entre servicios.
