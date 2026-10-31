# ADR-0610: Modelo de Identidad Multi-Aplicación en `gda-autenticacion`

Status: APPROVED

Date: 2026-08-25

Scope:
System

Category:
ARCHITECTURE

Tags:
[architecture, microservices, authentication, database, migration]

Related ADRs:
[ADR-0609, ADR-0600]

Supersedes:
NONE

Superseded By:
NONE

---

## Contexto

ADR-0609 documentó la segregación del backend de Espacio Justicia (SPJ) manteniendo `gda-autenticacion` y `gda-persona` como fuente única compartida de identidad para todo el ecosistema GDA + SPJ, y señaló explícitamente como "punto de divergencia futuro identificado y aún sin resolver" que el modelo entonces vigente asumía **una única fila `usuario` por `persona_id`**, usando la columna `tipo_comunicacion_id` (FK a `tipo_autoridad`) como mecanismo ad-hoc para resolver el rol de una persona dentro de Espacio Justicia. Este mecanismo no escalaba a más de dos aplicaciones y acoplaba el rol de una aplicación secundaria dentro de la misma fila de identidad de la aplicación primaria (GDA).

El equipo backend planteó sustituir ese modelo por uno que soporte varias aplicaciones sobre el mismo conjunto de personas (hoy GDA y SPJ, con más aplicaciones previstas a futuro), mediante una tabla `aplicacion` nueva y una fila `usuario` por combinación (persona, aplicación), cada una con credenciales independientes.

## Decisión

Se adopta un modelo de identidad multi-aplicación en `gda_autenticacion`:

1. Nueva tabla `gda_autenticacion.aplicacion` (`id`, `codigo`, `nombre`), sembrada con `(1, '1', 'gda')` y `(2, '2', 'spj')`.
2. `usuario` gana la columna `aplicacion_id` (FK `NOT NULL` a `aplicacion`), y el constraint `UNIQUE(persona_id, aplicacion_id)` sustituye la antigua asunción implícita de una fila por persona.
3. Todos los puntos de resolución de usuario por persona en `gda-autenticacion` (`login`, `addUsuario`, `relogin`, `findByPersonaId`, `findByPersonaIdList`, `findUsuarioByToken`, y el `UserDetailsService` de Spring Security) quedan *scoped* por `(persona_id, aplicacion_id)` en lugar de por `persona_id` en solitario.
4. El JWT emitido por `gda-autenticacion` incorpora el claim `aplicacionId`; su ausencia (tokens emitidos antes de este cambio) se trata como `aplicacionId = 1` (gda), preservando la validez de sesiones activas en el momento del corte.
5. `/login` acepta el código de aplicación como parámetro (dentro de `UsuarioDto.aplicacion.codigo`), resuelto server-side a la aplicación real; cada API Gateway (`api-gateway`, `spj-api-gateway`) inyecta su propio código de aplicación fijo (`property.aplicacion.codigo`: `"1"`/`"2"` respectivamente) en cada llamada relevante a `gda-autenticacion`.
6. `SecurityFilter.java` de ambos Gateways **no requiere ningún cambio**: nunca decodifica el JWT, se limita a reenviar el token a `gda-autenticacion` vía `getUsuarioByToken()` y a consumir el `UsuarioDto` ya resuelto — toda la resolución de `aplicacionId` ocurre dentro de `gda-autenticacion`.
7. La columna `tipo_comunicacion_id` de `usuario`, y su mapeo `Usuario.tipoComunicacion`/`UsuarioDto.tipoComunicacion`, quedan retirados una vez migrado su único consumidor real (la concesión de autoridad adicional en `SecurityFilter.java` de ambos Gateways) — el rol que antes vivía en `tipo_comunicacion_id` pasa a ser el `tipo_autoridad_id` propio de la fila `usuario` de la aplicación correspondiente.
8. Migración de datos: las personas con `tipo_comunicacion_id` relleno en el momento del corte (11 personas reales verificadas en Desa: `persona_id` 2, 7, 200, 360, 365, 366, 367, 1025, 1201, 4073, 4257) obtienen una segunda fila `usuario` con `aplicacion_id = 2`, `tipo_autoridad_id` = valor que tenía `tipo_comunicacion_id`, y contraseña inicial copiada (hash) de su fila GDA — sin propagación de cambios posteriores entre aplicaciones.

> **Nota de actualización (2026-08-26):** los códigos de aplicación pasaron de `'1'`/`'2'` a `'GDA'`/`'SPJ'` — cambio solicitado por el Senior para usar literales descriptivos en vez de códigos numéricos opacos, implementado por el equipo (Ricardo González) tras la ejecución de este ADR. Afecta a los puntos 1 y 5 de esta decisión: la semilla de `gda_autenticacion.aplicacion` (ahora `(1, 'GDA', ...)` y `(2, 'SPJ', ...)`) y el valor de `property.aplicacion.codigo` en ambos Gateways. El resto de la decisión — estructura, relaciones, JWT, migración de datos — permanece sin cambios y verificado funcionando con los nuevos literales.

## Alternativas Consideradas

**A — Mantener `tipo_comunicacion_id` como mecanismo permanente**, extendiéndolo con una columna nueva por cada aplicación futura. Rechazada: no escala — cada aplicación nueva exigiría una migración de esquema y código específica sobre `Usuario`.

**B — Tabla `aplicacion` + fila `usuario` por (persona, aplicación)** *(seleccionada)*. Escala a N aplicaciones sin cambios de esquema futuros; cada aplicación gestiona sus propias credenciales de forma independiente tras el corte inicial.

**C — Modelo de "roles múltiples" dentro de una única fila `usuario`** (lista de roles por aplicación, sin duplicar la fila completa). Evitaría la duplicación de filas, pero obliga a compartir una única contraseña entre aplicaciones — contradice el requisito explícito del Senior de contraseñas independientes por aplicación tras la duplicación inicial. Rechazada.

## Consecuencias

### Positivas (+)

* Modelo escalable a nuevas aplicaciones sin cambios de esquema — solo una fila nueva en `aplicacion` y, cuando proceda, filas `usuario` adicionales.
* Aislamiento real de credenciales y roles por aplicación, verificado extremo a extremo en Desa: la persona 200 opera con rol `GDA_SUPERGESTOR` en GDA y `COMUNICACION_MANAGER` en SPJ, en sesiones y tokens JWT completamente independientes.
* Compatibilidad retroactiva con tokens ya emitidos (fallback `aplicacionId = 1`), sin invalidar sesiones activas en el corte.
* `SecurityFilter.java` de ambos Gateways permanece sin cambios — el rediseño quedó contenido dentro de `gda-autenticacion`, reduciendo el *blast radius* real frente a lo inicialmente estimado en el plan de fases.

### Negativas (-)

* *Blast radius* de código mayor al inicialmente estimado: además de los puntos de `UsuarioServiceImpl` ya identificados en el análisis de riesgos previo, se localizaron 13 puntos de consumo adicionales en los Gateways (`GdaAutenticacionApiClient`, `UsuarioServiceImpl`, `PersonaServiceImpl`, `GrupoServiceImpl`, `EquipoServiceImpl`) y un punto crítico no anticipado — `JpaUserDetailsService.loadUserByUsername()`, invocado por `AuthenticationManager` dentro de `login()` — que también asumía una única fila por persona y requirió resolverse codificando `persona_id:aplicacion_id` como principal de autenticación.
* Tras el corte, la contraseña de la fila SPJ diverge de la fila GDA de forma permanente (sin sincronización) — una persona con acceso a ambas aplicaciones gestiona desde ese momento dos contraseñas independientes.
* `findByTipoAutoridad`/`getUsuarioByTipoAutoridadCodigo` no quedó migrado a *scope* por aplicación (fuera del alcance de este ADR) — riesgo residual bajo (su único consumidor real, `ImputacionServiceImpl` en `api-gateway`, usa un código de rol administrativo de GDA con baja probabilidad de colisión con los roles SPJ migrados), documentado y pendiente de revisión futura si se detecta colisión real.

### Riesgos Mitigados

* Colisión de dominio entre `tipo_autoridad_id` y `tipo_comunicacion_id`: ambos ya apuntaban al mismo catálogo `tipo_autoridad`, sin riesgo de incompatibilidad de valores al promover `tipo_comunicacion_id` a `tipo_autoridad_id` en la fila SPJ.
* Orden de despliegue: la migración de BBDD (duplicación de filas) y el despliegue del código migrado en `gda-autenticacion`, `api-gateway` y `spj-api-gateway` deben ejecutarse de forma coordinada — desplegar el código sin la migración de BBDD, o viceversa, produce `IncorrectResultSizeDataAccessException` para las personas con fila duplicada.

---

## Referencias

* `.vscode/docs/Documentacion_BackEnd_EspacioJusticia_planaccion_260821.md` — plan de fases (A→D) y ledger de decisiones de esta iniciativa.
* ADR-0609 — señala este mismo rediseño como "punto de divergencia futuro identificado y aún sin resolver"; este ADR lo resuelve. Ver nota de actualización añadida en ADR-0609.
* `GDA/backend/gda-autenticacion/gda-autenticacion/src/main/java/com/ineco/gda/autenticacion/data/model/Usuario.java`, `Aplicacion.java`
* `GDA/backend/gda-autenticacion/gda-autenticacion/src/main/java/com/ineco/gda/autenticacion/service/impl/UsuarioServiceImpl.java`, `JwtServiceImpl.java`, `JpaUserDetailsService.java`
* `GDA/api-gateway/src/main/java/com/ineco/gda/apigateway/security/SecurityFilter.java`, `GDA/spj-api-gateway/src/main/java/com/ineco/spj/apigateway/security/SecurityFilter.java` — sin cambios, confirmado.
* Esquema `gda_autenticacion` en `gda_03_desa` — tabla `aplicacion`, columna `usuario.aplicacion_id`, `UNIQUE(persona_id, aplicacion_id)`.
