# ADR-0606: Patrón de Campos de Auditoría en Entidades de Negocio

Status: APPROVED
Date: 2026-07-22 (revisado varias veces el mismo día: FK real a `gda_autenticacion.usuario`, corregida
a FK real a `gda_persona.persona`; y renombrado `fecha_efecto` → `fecha_modificacion`, con cambio de
semántica — ver punto 3. Esa revisión eleva este patrón de "recomendado" a **obligatorio para toda
tabla nueva** del backend GDA. Revisado de nuevo 2026-07-25: tercer caso real, Licencia — primera
entidad que aplica el patrón siendo **diseñada desde cero** ya con las 4 columnas presentes en la DDL
inicial, sin necesitar ningún `ALTER TABLE` correctivo como sí hizo falta para Proveedor)
Scope: System
Category: ARCHITECTURE
Tags: REVIEW_REQUIRED
Related ADRs: ADR-0601, ADR-0602, ADR-0603
Supersedes: NONE
Superseded By: NONE
Validation Reference: NONE

## Contexto
`gda_estructura.iniciativa` ya incorpora, desde su creación, un conjunto de columnas para registrar
quién y cuándo se creó/modificó/dio de baja un registro: `username` (texto libre, sin FK),
`fecha_alta`, `fecha_baja`, `fecha_efecto`. Al ampliar `gda_persona.proveedor` (módulo Vendors) con el
mismo tipo de necesidad, se decidió explícitamente replicar ese criterio en vez de inventar uno nuevo
— pero verificando el comportamiento real del código (no solo la DDL) se encontraron matices
importantes que la tabla por sí sola no muestra, y se tomaron dos decisiones que divergen
deliberadamente del precedente. Este ADR fija el criterio para que **futuras entidades** que necesiten
auditoría sepan qué replicar y qué no, sin tener que releer el código de Iniciativa cada vez.

Verificado en código real: `Iniciativa.java`/`IniciativaServiceImpl.java` (backend `gda-estructura` y
su composición en el API Gateway) y `Proveedor.java`/`ProveedorServiceImpl.java` (backend
`gda-persona` y su composición en el API Gateway), documentado con detalle en
`Documentacion_BBDD_GDA_2607_Vendors.md`, `Documentacion_BackEnd_GDA_2607_Vendors.md` §14 y
`Documentacion_FrontEnd_GDA_2607_Vendors.md` §15.

## Decisión
**A partir de esta fecha, toda tabla nueva del backend GDA debe incluir, al final de su esquema, las 4
columnas de auditoría siguientes** — deja de ser un patrón recomendado por analogía con Iniciativa para
pasar a ser la convención obligatoria del proyecto: `fecha_alta`, `fecha_modificacion`, `fecha_baja` y
un identificador del autor (`usuario_modificacion_id` u otro nombre igual de explícito). El criterio
exacto de relleno y edición de cada una se describe a continuación (no basta con replicar los nombres
y tipos de columna):

1. **Identidad del autor — columna `int8 NULL`, con o sin FK real según necesidad:** para entidades
   **nuevas**, usar un identificador de autor (no `username` de texto libre). Punto de partida siempre
   igual: en el **API Gateway** (nunca en el frontend ni en el microservicio de dominio), leer
   `((UserDetails) securityContext.getAuthentication().getPrincipal()).getUsername()` del
   `SecurityContext` reactivo y parsearlo a `Long` — este valor **es el `persona_id`** del usuario
   autenticado (no un username textual; el nombre del método `getUsername()` de Spring Security es
   engañoso en este contexto, ver `SecurityFilter.java` del Gateway), **no** el `id` propio de
   `gda_autenticacion.usuario` (son PKs de tablas distintas — verificado en `Usuario.java`/
   `UsuarioDto.java`, que tienen ambos campos `id` y `personaId` por separado).
   - **Si la columna se queda como `persona_id` (sin FK, como en Iniciativa) o lleva FK real a
     `gda_persona.persona(id)` (caso final de Proveedor, `usuario_modificacion_id` pese al nombre):**
     ese valor ya es directamente utilizable, sin pasos adicionales — es exactamente lo que la FK
     espera.
   - **Si en cambio la columna llevara FK real a `gda_autenticacion.usuario(id)` (decisión intermedia
     que se planteó y descartó para Proveedor el mismo día, ver `Documentacion_BBDD_GDA_2607_Vendors.md`
     §7):** hace falta un paso adicional de resolución, **no** una asignación directa del `personaId` —
     de lo contrario la FK se viola en cuanto `persona_id != usuario.id` para ese usuario (caso
     general). Resolver con `gdaAutenticacionApiClient.getUsuarioByPersona(personaId).getBody().getId()`
     (método Feign ya existente en `GdaAutenticacionApiClient`, mismo patrón ya usado en
     `GrupoServiceImpl`/`EquipoServiceImpl`/`UsuarioServiceImpl` del Gateway) — **documentado aquí como
     opción real disponible, no como lo que Proveedor usa finalmente.**
   - **Cuándo reasignarlo:** por defecto, solo en el alta (mismo criterio que `username` en Iniciativa,
     preservado sin cambios en la edición). Se permite reasignarlo también en cada edición cuando la
     entidad necesite semántica de "última persona que modificó el registro" en vez de solo "quién lo
     creó" — decisión a tomar explícitamente por entidad, y que debería reflejarse en el propio nombre
     de la columna (p. ej. `usuario_modificacion_id` dice explícitamente lo que `persona_id` no
     decía). Proveedor reasigna en cada edición; Iniciativa no.
2. **`fecha_alta` (`date NULL`) — CRITERIO FINAL, corregido tras el primer paso por Proveedor:** a
   diferencia de la primera versión de este ADR (que la trataba como 100% backend, sin frontend, igual
   que `username`/`fechaAlta` en Iniciativa), el criterio final para toda tabla nueva es: **campo
   visible y editable en el formulario de ALTA**, con valor por defecto la fecha vigente en el momento
   de crear el registro (prellenado explícitamente por el frontend con `moment().format(FORMAT_MASK_DATE)`
   al abrir el formulario de Añadir — no basta con confiar en que el usuario abra el selector de fecha,
   como si hacía el criterio anterior), pero **modificable por el usuario** si lo necesita. En
   Editar/Consultar, el campo se muestra siempre **deshabilitado** (sin la marca de obligatorio, que no
   tiene sentido en un campo no editable) y el backend del microservicio de dominio **preserva siempre
   el valor original** leído de BD en cada edición, ignorando cualquier valor que llegue en el DTO —
   esto es lo único que sí se mantiene igual que en el criterio anterior: `fecha_alta` nunca cambia
   después del alta, solo que ahora el valor inicial lo puede ajustar el usuario, no solo el sistema.
3. **`fecha_modificacion` (`date NULL`) — sustituye a `fecha_efecto`/`fecha_baja` como campo 100%
   automático:** se corrigió el nombre de esta columna (antes `fecha_efecto`, un campo de negocio
   editable por el frontend — criterio descartado, ver histórico en
   `Documentacion_BBDD_GDA_2607_Vendors.md` §8) precisamente para invertir su naturaleza: ahora es
   **puramente de auditoría, gestionada solo por el backend del microservicio de dominio**, nunca
   expuesta en el `Request` del Gateway ni editable desde el frontend (el frontend solo la muestra en el
   listado, en modo lectura). Se fija a `LocalDate.now()` **tanto en el alta como en cada edición** —
   a diferencia de `fecha_alta`, que solo se fija una vez, `fecha_modificacion` se reescribe en
   cualquier cambio posterior de los datos.
4. **`fecha_baja` (`date NULL`):** campo de negocio, no puramente de auditoría — su tratamiento
   **depende de si la entidad tiene un ciclo de vida propio con estado** (ej. Iniciativa, con
   `estado` Cerrada/Detenida) o no (ej. Proveedor). Si lo tiene, se gestiona vía el PUT normal de
   edición cuando el estado cambia a uno terminal, sin necesidad de un endpoint de baja específico
   (Iniciativa mantiene además un `DELETE` físico real, totalmente aparte). Si no lo tiene, y se decide
   que el campo debe existir igualmente, debe declararse explícitamente **intocable vía API** (backend
   preserva siempre el valor original en la edición, sin excepción) y el frontend debe mostrarlo, si lo
   hace, siempre en modo solo lectura.
   - **Caso real que sí requería la decisión explícita — Licencia, decisión corregida el 2026-07-26:**
     a diferencia de Proveedor (sin ningún campo `estado`), `licencia` sí tiene un `estado_id` (FK a
     `gda_persona.maestro_estado`) visible en su propio formulario. La primera versión de esta fase
     (2026-07-25) asumió, sin confirmarlo con el usuario, que ningún valor de `maestro_estado` se trataba
     como "terminal" en el dominio de Licencia, y adoptó el criterio de Proveedor (`fecha_baja`
     intocable). **Corregido** al confirmarse que sí existe un valor terminal real: el usuario pidió
     explícitamente que, en Editar, seleccionar el estado **"Baja Definitiva"** cargue `fecha_baja` con
     la fecha del día. Licencia sigue por tanto el mecanismo de **Iniciativa** (punto 4, primera rama):
     `fecha_baja` se gestiona vía el PUT normal de edición, sin endpoint de baja específico, cuando el
     estado alcanza ese valor terminal — con la diferencia de que el frontend, no el backend, decide
     cuándo escribirlo (comparando la `description` del estado seleccionado contra el literal
     `"Baja Definitiva"`, sin ID hardcodeado — ver la nota sobre por qué no se usó el mecanismo de
     `ID_TYPES_STATES_CLOSED`/`ID_TYPES_STATES_STOPPED` de Iniciativa, más abajo). `editLicencia` ya no
     preserva `fecha_baja` del registro original (sí sigue preservando `fecha_alta`, sin cambios); el
     valor que llegue en el DTO del `PUT` se persiste tal cual. Lección para módulos futuros: cuando una
     entidad nueva tiene su propio campo `estado`, **no asumir** que no existe un valor terminal sin
     preguntar explícitamente — a diferencia de Iniciativa (`ID_TYPES_STATES_CLOSED`/
     `ID_TYPES_STATES_STOPPED`, IDs hardcodeados en `constants/common.js`, estables porque Iniciativa
     tiene su propio catálogo de estados dedicado), Licencia compara por **texto** (`nombre` del
     `maestro_estado`) porque `maestro_estado` es un catálogo más genérico (columna `ambito`, ver
     `Documentacion_BackEnd_GDA_2607_Licenses.md` §8) cuyos IDs no son un contrato estable conocido —
     ver `Documentacion_BackEnd_GDA_2607_Licenses.md` §7-8 y `Documentacion_FrontEnd_GDA_2607_Licenses.md`
     §11 para el detalle completo, incluida la corrección pendiente de acotar `maestro_estado` por
     `ambito` (hallazgo distinto, en curso).
5. **Serialización de `LocalDate` en el DTO:** obligatorio anotar cada campo `LocalDate` del DTO de
   `-commons` con `@JsonSerialize`/`@JsonDeserialize` usando una clase serializadora propia del módulo
   (ver `com.ineco.gda.persona.util.LocalDateSerializer`/`LocalDateDeserializer` en `gda-persona-commons`,
   o el equivalente `com.ineco.gda.estructura.util.LocalDateSerializer`/`LocalDateDeserializer` en
   `gda-estructura-commons`) — **no basta con anotar el campo `LocalDate` sin más ni con `@JsonFormat`
   en el `Request` del Gateway.** Motivo: `ACSFeignConfiguration.java` (Gateway) usa un `ObjectMapper`
   sin `JavaTimeModule` para las llamadas Feign; sin la anotación a nivel de campo en el DTO
   `-commons`, cualquier fecha se pierde silenciosamente al pasar por Feign (ver ADR-0602, deuda
   técnica actualizada).

## Consecuencias

### Positivas (+)
- Da a los desarrolladores de nuevos módulos un criterio único y verificado (no solo "cópialo de
  Iniciativa", que por sí sola no explica los matices) para implementar auditoría sin reproducir el
  bug de serialización de fechas ya sufrido dos veces (implícitamente en Iniciativa, explícitamente
  documentado ahora en Proveedor).
- Deja explícito que `persona_id`/`fecha_alta`/`fecha_baja` no deben depender nunca de lo que envíe el
  frontend, reduciendo superficie de manipulación de datos de auditoría desde el cliente.

### Negativas (-)
- El punto 1 (cuándo reasignar `persona_id`) exige una decisión explícita por entidad en vez de una
  regla única — riesgo de inconsistencia entre módulos si no se documenta la decisión tomada en cada
  caso (mitigado exigiendo que quede anotada en la documentación de fase de cada módulo, como se ha
  hecho aquí).
- El punto 5 (serializador manual por campo) es un parche por módulo, no una solución centralizada; si
  `ACSFeignConfiguration` incorpora en el futuro `JavaTimeModule` de forma global, estas anotaciones
  pasarán a ser redundantes pero no dañinas (no se retiran de forma proactiva en ese momento).

### Riesgos Mitigados
- Pérdida silenciosa de fechas de auditoría al pasar por Feign (ya materializada una vez en Proveedor,
  detectada y corregida durante esta misma fase).
- Manipulación de `persona_id`/`fecha_alta`/`fecha_baja` desde el frontend (mitigado no exponiendo
  estos campos en el `Request` del Gateway y preservando su valor original en la edición del lado
  servidor).
- Violación de FK por confundir `persona_id` con `usuario.id`: riesgo real identificado (no solo
  teórico) durante la decisión intermedia de Proveedor (FK a `gda_autenticacion.usuario(id)`), que
  llevó a corregir la FK definitiva hacia `gda_persona.persona(id)` — el mismo espacio de IDs que ya se
  estaba guardando, eliminando el riesgo por completo en vez de parchearlo con una resolución adicional
  (ver `Documentacion_BBDD_GDA_2607_Vendors.md` §7 para el histórico completo de la decisión).

## Referencias
- `Documentacion_BBDD_GDA_2607_Vendors.md` §7 (renombrado a `usuario_modificacion_id`, FK real, y riesgo de violación de FK con datos existentes)
- `Documentacion_BackEnd_GDA_2607_Vendors.md` §14 (implementación backend/Gateway, Fase 4)
- `Documentacion_FrontEnd_GDA_2607_Vendors.md` §15 (implementación frontend, Fase 7)
- `Documentacion_BackEnd_GDA_2607_Licenses.md` §4, §7 (tercer caso real, 2026-07-25 — único hasta ahora diseñado desde cero con las 4 columnas ya en la DDL inicial; decisión explícita de `fecha_baja` intocable pese a tener `estado_id` propio)
- `Documentacion_FrontEnd_GDA_2607_Licenses.md` §10 (implementación frontend de `fecha_alta` como campo de Añadir)
- ADR-0601 (patrón módulo-commons — los DTOs de auditoría viven en `-commons`)
- ADR-0602 (comunicación inter-servicio — deuda técnica del `ObjectMapper` de Feign)
- ADR-0603 (gestión de BBDD — sin migraciones versionadas, `ALTER TABLE` manual)
