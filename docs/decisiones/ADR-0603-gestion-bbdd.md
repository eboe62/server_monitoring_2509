# ADR-0603: Políticas de Gestión de Bases de Datos en Microservicios

Status: APPROVED
Date: 2026-06-11 (revisado 2026-07-16 para reflejar la implementación real vigente en el backend GDA;
revisado 2026-07-21 con evidencia real de la deuda técnica de migraciones versionadas; revisado
2026-07-22 con segunda evidencia real, ampliación de esquema de `proveedor` con campos de auditoría;
revisado 2026-07-26 con evidencia real de catálogos compartidos sin filtro documentado, módulo Licencias)
Scope: Database
Category: DATABASE
Tags: REVIEW_REQUIRED
Related ADRs: ADR-0600
Supersedes: NONE
Superseded By: NONE
Validation Reference: NONE

## Contexto
En una arquitectura de microservicios desacoplados, cada servicio debe ser independiente en todos los aspectos, incluida la gestión de datos. Este ADR se ha revisado tras contrastarlo con la configuración real de los 8 módulos del backend (`gda-agrupacion`, `gda-autenticacion`, `gda-estructura`, `gda-finance/gda-admingade`, `gda-imputacion`, `gda-listado`, `gda-log`, `gda-persona`).

## Decisión
Adoptar el patrón "Base de datos por microservicio, mediante schema dedicado en una instancia PostgreSQL compartida", con las siguientes directrices alineadas con la práctica ya vigente:

1. **Segregación por schema:** todos los servicios comparten una única instancia PostgreSQL por entorno (p. ej. `gda_03_desa` en desarrollo, `GDA_REIR_02_PRO` en producción), pero cada uno usa su propio `currentSchema` (`gda_admingade`, `gda_persona`, `gda_agrupacion`, etc.), verificado en `application-<entorno>.yml` de los 8 módulos.
2. **Prohibición de joins entre schemas de distintos servicios:** la integración de datos entre servicios se realiza a través de APIs (vía API Gateway, ver ADR-0602), no mediante consultas SQL cruzadas entre schemas. **Excepción real detectada (2026-07-16):** la tabla `gda_persona.proveedor` tiene una foreign key real a nivel de base de datos (`proveedor_encargo_fk`) hacia `gda_admingade.encargo(id)`, cruzando schemas de dos módulos distintos. Es una excepción preexistente al principio de este punto, no introducida por el módulo Vendors — se documenta como deuda técnica (ver más abajo), no se corrige retroactivamente en este ADR.
3. **Gestión de esquema fuera del ciclo de vida de la aplicación:** todos los servicios tienen `ddl-auto: none` en los 4 entornos (local/dev/pre/pro); ningún módulo usa actualmente Flyway ni Liquibase. El esquema se gestiona manualmente/externamente al código de la aplicación.
4. **Independencia de configuración de despliegue:** cada servicio gestiona su propia configuración de datasource de forma independiente, aunque todos apunten a la misma instancia física.

## Deuda técnica / mejoras pendientes (no bloqueantes para nuevos módulos)
- **Migraciones versionadas:** ningún servicio usa Flyway/Liquibase hoy; los cambios de esquema se aplican manualmente. Se recomienda incorporar una herramienta de migración versionada de forma incremental, empezando por los módulos nuevos (p. ej. Vendors), sin bloquear su desarrollo por no tenerla aún el resto del backend. **Evidencia real (2026-07-21):** durante la verificación end-to-end del alta de `Proveedor` (módulo Vendors, Fase 3) se detectó que la secuencia IDENTITY de `gda_persona.proveedor.id` estaba desincronizada respecto al `id` máximo real de la tabla en la BD compartida de desarrollo (`gda_03_desa`), provocando un error 500 (`duplicate key value violates unique constraint "pk_proveedor"`) en el primer `INSERT` de prueba — causado por datos insertados en algún momento sin pasar por la secuencia (carga manual, script, o prueba anterior), posible precisamente porque no hay ninguna herramienta de migración/seed que garantice esa consistencia. Resuelto manualmente contra la BD compartida con `SELECT setval(pg_get_serial_sequence('gda_persona.proveedor', 'id'), (SELECT MAX(id) FROM gda_persona.proveedor));`. No es un fallo del código de Vendors — es el coste concreto, ya materializado, de esta deuda técnica ya documentada aquí desde el 2026-06-11.
- **Segunda evidencia real de ausencia de migraciones versionadas (2026-07-22):** la ampliación de
  `gda_persona.proveedor` con los campos de auditoría de Vendors (`persona_id`, `fecha_alta`,
  `fecha_baja`, `fecha_efecto` — ver `Documentacion_BBDD_GDA_2607_Vendors.md`) se aplicó mediante un
  `ALTER TABLE` manual ejecutado directamente por el usuario contra la BD compartida de desarrollo, sin
  ningún script versionado ni registro de migración. A diferencia del incidente de la Fase 3 (secuencia
  desincronizada), esta vez no se materializó ningún error, pero refuerza el mismo patrón: no hay forma
  automática de reproducir este cambio de esquema en otro entorno (pre/pro) ni de saber, sin consultar
  este documento, qué cambios de esquema manuales se han aplicado y en qué orden.
- **Instancias separadas:** actualmente todos los servicios comparten la misma instancia física de PostgreSQL (segregados solo por schema). Migrar a instancias realmente independientes por servicio queda fuera del alcance de este ADR y del backend actual.
- **Catálogos compartidos por varios dominios, sin filtro documentado (evidencia real, 2026-07-26,
  módulo Licencias):** `gda_persona.maestro_estado` resultó ser una tabla de estados **compartida por
  varios módulos** (`ambito` con valores reales `Vacantes`, `Certificaciones`, `Candidatos`,
  `Vacante_Principal`, `Vacante_Situacion`, más un grupo de filas con `ambito` a `NULL`), con
  `UNIQUE (nombre, ambito)` — el mismo `nombre` puede existir legítimamente varias veces bajo distinto
  `ambito` (verificado: `Cancelada` existe con `ambito = 'Vacante_Principal'` y con `ambito` a `NULL`).
  Nada en el esquema, en ningún ADR ni en ningún documento previo advertía de esto. El primer consumidor
  nuevo de esta tabla (`MaestroEstadoService.findAll()`, módulo Licencias, `GDAV3-446`) expuso un
  `findAll()` sin filtrar, mostrando en el desplegable de Licencias estados de dominios completamente
  ajenos mezclados con los suyos — reportado por el usuario como "Estados repetidos". Corregido con un
  método dedicado `findByAmbitoIsNull()` (las filas sin `ambito` resultaron ser las correctas para
  Licencias — ver `Documentacion_BackEnd_GDA_2607_Licenses.md` §8), pero el riesgo de fondo persiste
  para cualquier módulo futuro que consulte una tabla `maestro_*` compartida sin saberlo de antemano.
  **Recomendación para módulos futuros:** antes de exponer un `findAll()` sin filtrar sobre cualquier
  tabla de catálogo (`maestro_*` o equivalente), comprobar si tiene una columna discriminadora (`ambito`
  u otra) y confirmar el valor/condición correcto en vez de asumir que la tabla pertenece a un único
  dominio. `gda_persona.maestro_localizacion` no tiene columna `ambito` y no presenta este riesgo.
- **FK cruzada `gda_persona.proveedor.encargo_id` → `gda_admingade.encargo(id)`:** verificada en la DDL real de la tabla `proveedor` (constraint `proveedor_encargo_fk`). Es un acoplamiento a nivel de esquema más fuerte de lo que describe el punto 2 de este ADR (integración solo vía API). No se corrige de forma retroactiva porque el backend de `gda-persona`/`gda-admingade` ya está construido y no está en el alcance de este trabajo (responsabilidad de frontend); queda documentada para que no se repita el patrón en tablas nuevas y para que un futuro ADR de base de datos la evalúe explícitamente.

## Consecuencias

### Positivas (+)
- Refleja la arquitectura real y consistente ya adoptada por los 8 módulos del backend, evitando exigir a nuevos módulos una migración a Flyway/Liquibase que ni el resto del backend tiene.
- La segregación por schema ya cumple el objetivo de evitar joins cruzados y acoplamiento de datos entre servicios.

### Negativas (-)
- Compartir la misma instancia física de PostgreSQL entre todos los servicios es un punto único de fallo/contención a nivel de infraestructura, aunque los datos estén lógicamente segregados.
- La ausencia de migraciones versionadas dificulta la trazabilidad y el rollback de cambios de esquema.
