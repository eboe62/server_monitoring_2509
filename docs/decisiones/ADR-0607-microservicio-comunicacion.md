# ADR-0607: Introducción del Microservicio `gda-comunicacion` para Noticias y Eventos (Espacio Justicia)

Status: SUPERSEDED

Date: 2026-08-14 (superseded 2026-08-20 — ver ADR-0609)

Scope:
System

Category:
ARCHITECTURE

Tags:
REVIEW_REQUIRED

Related ADRs:
[ADR-0600, ADR-0601, ADR-0602, ADR-0603, ADR-0604, ADR-0605, ADR-0606]

Supersedes:
NONE

Superseded By:
ADR-0609

---

## Contexto

El portal **Espacio Justicia** requiere dos capacidades nuevas orientadas al usuario final: un blog de noticias (el Gestor de Contenido/Administrador publica; el resto de usuarios consume en lectura) y un calendario de eventos corporativo, con recurrencia y excepciones. Ninguna capacidad existente del backend GDA (`gda-agrupacion`, `gda-autenticacion`, `gda-estructura`, `gda-finance`, `gda-imputacion`, `gda-listado`, `gda-log`, `gda-persona`) cubre este dominio.

La decisión de topología (un microservicio nuevo, dos microservicios separados, o ampliar uno existente) se analizó y se tomó en una sesión de trabajo el 2026-07-22 (`Documentacion_BackEnd_EspacioJusticia_2607.md`), que produjo un borrador de ADR. Ese borrador nunca se guardó en `docs/decisiones/` — el número que se le iba a asignar (ADR-0604) fue ocupado después por una decisión distinta ya aprobada (patrón de composición del API Gateway). Este ADR formaliza esa misma decisión, ya con evidencia real de implementación (no solo de diseño): repositorio Git propio creado, estructura Maven multi-módulo funcionando, migraciones Flyway ejecutadas de verdad contra `gda_03_desa` — ver Referencias.

## Decisión

Se adopta la creación de un único microservicio, **`gda-comunicacion`**, que aloja como dominios internos diferenciados tanto **Noticias** como **Eventos**, siguiendo el patrón estándar del proyecto:

1. Repositorio Git propio (`gdact-reir/gdact-3.0/backend/gda-comunicacion`) y artefacto Maven multi-módulo (`gda-comunicacion` + `gda-comunicacion-commons`), con `pom.xml` padre independiente (`packaging=pom`, sin agregador cruzado a otros microservicios — ADR-0600).
2. Estructura de capas estándar del proyecto (`config`, `data/model`, `data/repository`, `service`/`service/impl`, `web/controller`, `exception`), calcada de `gda-imputacion` a petición explícita del usuario.
3. Sin lógica de autenticación/autorización propia: `SecurityConfiguration` limitada a CORS, delegando en el API Gateway (ADR-0605).
4. Esquema de base de datos propio y dedicado (`gda_comunicacion`) en la instancia PostgreSQL compartida (`gda_03_desa` en desarrollo), conforme a ADR-0603.
5. Separación interna por dominio dentro del mismo servicio: tablas independientes `noticia`/`evento` (con sus tablas de apoyo), sin acoplamiento SQL entre ambos dominios más allá de la relación de negocio explícita Noticia↔Evento (FK simple y opcional `evento.noticia_id`, no una tabla puente muchos-a-muchos — la cardinalidad real es asimétrica: una noticia puede vincularse a varios eventos, un evento como mucho a una noticia).

## Alternativas Consideradas

**A — Dos microservicios independientes (`gda-noticias`, `gda-eventos`).** Máxima fidelidad al patrón "un dominio = un servicio", pero duplica repos, pipelines, esquemas y bloques de rutas del Gateway para dos dominios de baja complejidad y misma audiencia. Rechazada por sobrecarga operativa desproporcionada.

**B — Un microservicio `gda-comunicacion` con dos dominios internos** *(seleccionada)*. Mínima infraestructura nueva respetando el patrón; cohesión por audiencia y ciclo de vida (ambos dominios comparten el mismo modelo de seguridad y el mismo conjunto de roles gestores); un único punto de integración en el Gateway.

**C — Ampliar un microservicio existente** (p. ej. `gda-persona` o `gda-estructura`). Rechazada por romper el contexto acotado del servicio anfitrión e introducir responsabilidades ajenas a su dominio.

## Consecuencias

### Positivas (+)

* Mantiene el patrón "un contexto acotado = un microservicio" con la mínima infraestructura nueva.
* Reutiliza sin cambios el arquetipo Maven, el modelo de seguridad (JWT en Gateway), el manejo de excepciones y el patrón de perfiles de configuración ya usados en `gda-imputacion`.
* La separación interna por dominio (paquetes/tablas independientes) permite una futura escisión en dos servicios sin reescritura, si Noticias y Eventos llegaran a divergir mucho.

### Negativas (-)

* Acoplamiento de despliegue: Noticias y Eventos comparten ciclo de release; un cambio en uno obliga a redesplegar el servicio completo.
* Introduce una dependencia de almacenamiento de objetos (imágenes/documentos/vídeos de noticias) que no existe en ningún otro módulo del backend GDA, y cuya ruta real de escritura en el servidor de despliegue está todavía sin verificar (pendiente de Fase 2).
* Añade un nuevo repositorio, esquema de base de datos y (pendiente) pipeline de CI al inventario operativo — este último todavía no creado, a diferencia de los 8 módulos existentes.

### Riesgos Mitigados

* Que Noticias y Eventos se implementasen como dos servicios separados sin justificación operativa (sobre-ingeniería) o se colgasen de un servicio existente ajeno a su dominio (acoplamiento indebido).
* Que la relación Noticia↔Evento se modelase como una tabla puente muchos-a-muchos genérica sin reflejar su cardinalidad real asimétrica (ver Referencias, hallazgo de Fase 1).

---

## Referencias

* `GDA/backend/gda-comunicacion/pom.xml`, `gda-comunicacion/pom.xml`, `gda-comunicacion-commons/pom.xml` — estructura Maven real.
* Esquema `gda_comunicacion` en `gda_03_desa` — aplicado mediante DDL manual, igual que el resto del backend GDA (ADR-0603). Se evaluó Flyway como mejora propuesta (adopción real 2026-08-14, revertida 2026-08-15 — ver ADR-0603 para el detalle y el punto de retorno conservado en git).
* ADR-0600 (estrategia de despliegue), ADR-0601 (módulo-commons), ADR-0602 (comunicación inter-servicio), ADR-0603 (gestión de BBDD), ADR-0604 (composición del API Gateway), ADR-0605 (RBAC por prefijo), ADR-0606 (patrón de auditoría).
* `.vscode/docs/Documentacion_BackEnd_EspacioJusticia_2607.md` — sesión de origen de la decisión (2026-07-22), sin formalizar hasta este ADR.
* `.vscode/docs/Documentacion_BackEnd_EspacioJusticia_2607_requisitos02.2.md`, `Documentacion_BackEnd_EspacioJusticia_Endpoints_2607.md`, `Documentacion_BackEnd_EspacioJusticia_planaccion_2608.md` — requisitos, contrato de endpoints y plan de fases vigentes.
