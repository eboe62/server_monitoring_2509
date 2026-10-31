# ADR-0609: Segregación de Espacio Justicia en un Backend Independiente ("SPJ")

Status: APPROVED

Date: 2026-08-20

Scope:
System

Category:
ARCHITECTURE

Tags:
REVIEW_REQUIRED

Related ADRs:
[ADR-0600, ADR-0601, ADR-0602, ADR-0603, ADR-0604, ADR-0605, ADR-0606, ADR-0607, ADR-0608, ADR-0610, ADR-0801]

Supersedes:
ADR-0607

Superseded By:
NONE

---

## Contexto

ADR-0607 formalizó `gda-comunicacion` como un microservicio más del backend GDA, alojado en el mismo Gateway (`api-gateway`, puerto 9100) y en el mismo esquema de despliegue que el resto de módulos de GDA. Una vez desplegado y en pruebas, se decidió que Espacio Justicia deja de ser una funcionalidad más de GDA y pasa a tratarse como **producto independiente**, con ciclo de release, infraestructura y punto de entrada propios — sin que ello implique duplicar la identidad de las personas ni el modelo de autenticación, que siguen siendo responsabilidad exclusiva de GDA.

Esto exige resolver una topología nueva: ¿cómo se segrega un dominio que hoy vive dentro de un monorepo/Gateway compartido, sin duplicar los microservicios que deben seguir siendo la fuente única de verdad (identidad de persona, autenticación)?

La decisión se tomó y ejecutó en tres fases, con evidencia real de cada una (no solo de diseño):

- **Fase 1 — Creación de repositorio.** Se crearon dos repositorios GitLab nuevos bajo el grupo `espacio-justicia/backend`: `spj-comunicacion` (forkeado de `gda-comunicacion`, con todo su historial) y `spj-api-gateway` (forkeado de `api-gateway`, con todo su historial). `api-gateway` permanece intacto como componente compartido de GDA — no se modificó como parte de esta segregación.
- **Fase 2 — Rebranding.** Renombrado de artefactos Maven y paquetes Java (`com.ineco.gda.comunicacion.*` → `com.ineco.spj.comunicacion.*`, `com.ineco.gda.apigateway.*` → `com.ineco.spj.apigateway.*`), nueva base de datos `spj_01_desa` con esquema `spj_comunicacion` (en vez de compartir `gda_03_desa`/`gda_comunicacion`), y despliegue Docker en infraestructura propia.
- **Fase 3 — Segregación de `spj-api-gateway`.** Eliminación de todo el código de dominios ajenos a Comunicación (Guardias, Agrupación, Estructura, Listado, Admingade, Log, controladores/servicios/DTOs asociados), reduciendo `RouteLocatorConfig` de ~60 rutas a 5, y `SecurityConfiguration` a los `pathMatchers` estrictamente necesarios (`/user/**`, `/comunicacion/**`, `/oauth/**`, `/swagger-ui/**`).

Verificación end-to-end realizada sobre el servidor de desarrollo real (`172.16.22.114`): login vía JWT, lectura (`/user/noticias`, `/user/eventos` con festivos reales compuestos desde `gda-imputacion`, `/comunicacion/categorias`), y escritura completa (`POST`/`PUT /comunicacion/noticias`, `POST /comunicacion/eventos`) con `usuarioModificacionId` resuelto correctamente desde el JWT y persistido en `spj_01_desa`.

> **Nota de actualización (2026-08-27):** la afirmación anterior de que la lectura (`/user/noticias`, `/user/eventos`) quedó verificada end-to-end no se sostuvo en la práctica: `SecurityConfiguration` de `spj-api-gateway` copió literalmente la lista de autoridades de `api-gateway` (roles `GDA_*`) para el `pathMatcher` de `/user/**`, sin adaptarla a los roles reales de Espacio Justicia (`COMUNICACION_MANAGER`, `COMUNICACION_RSP`, y el posterior `COMUNICACION_USER`). El resultado: cualquier usuario autenticado de Espacio Justicia recibía `401` (con `WWW-Authenticate: Basic`, el fallback por defecto de Spring Security) al leer noticias, eventos, categorías o etiquetas — bloqueando exactamente la funcionalidad que este párrafo daba por probada. Detectado por el equipo de Frontend al iniciar sus pruebas de integración, corregido (`/user/**` pasa a `.authenticated()`, sin lista de roles) y reverificado end-to-end el 2026-08-27. Este párrafo se conserva sin modificar como registro histórico de la verificación original — incompleta en este punto — de la Fase 3.

> **Nota de actualización (2026-09-03):** al intentar habilitar el Swagger de `spj-api-gateway` (heredado de `api-gateway` en la Fase 1, nunca probado hasta ahora) se descubrió que el Gateway llevaba desde el fork arrancando en **modo Servlet (Tomcat)**, no reactivo, pese a que todo su diseño (`@EnableWebFluxSecurity`, controllers devolviendo `Mono<...>`, `web-application-type: reactive`) asume lo contrario. Causa raíz: `spring-cloud-starter-function-web` (dependencia sin ningún uso real en el código, heredada del fork) arrastra `spring-boot-starter-web` sin excluir; la exclusión existente en `spring-cloud-starter-gateway` apuntaba a un artefacto inexistente (`org.springframework.boot:spring-cloud-starter-web`) y no hacía nada. Efecto real: `SecurityConfiguration` (basada en `SecurityWebFilterChain`, API reactiva) nunca se aplicaba de verdad — Spring Security caía al autoconfig de Servlet por defecto. Que las rutas de negocio (`/comunicacion/**`, `/user/**`) funcionasen correctamente pese a esto fue, en retrospectiva, casualidad de cómo Spring Cloud Gateway y Spring MVC pueden coexistir parcialmente, no diseño verificado. Corregido en `spj-api-gateway` (eliminación de la dependencia y de la exclusión inútil, más tres correcciones de rutas de seguridad relacionadas con Swagger: `/swagger-ui.html`, `/webjars/**`, `/api-docs/**`). **`api-gateway` (GDA) tiene exactamente el mismo defecto, sin corregir todavía** — mismo `pom.xml`, mismo fork de origen (ver ADR-0600).

## Decisión

Se adopta un **backend "gemelo" (twin), más pequeño, para Espacio Justicia**, segregado de GDA salvo en identidad y autenticación:

1. **Repositorios independientes**, forkeados con historial completo desde sus equivalentes GDA: `espacio-justicia/backend/spj-comunicacion` (de `gda-comunicacion`) y `espacio-justicia/backend/spj-api-gateway` (de `api-gateway`). `gda-comunicacion` queda retirado por completo (contenedor, esquema y entrada en `docker-compose.yml` de GDA eliminados) — `spj-comunicacion` lo sustituye íntegramente, no coexisten.
2. **Base de datos propia:** `spj_01_desa`, esquema `spj_comunicacion`, mismos roles de conexión (`userdesarrollo`/`usercomunicacion`) reutilizados por simplicidad operativa. Sin FK cruzada a `gda_persona.persona` (imposible entre bases de datos distintas en PostgreSQL): las columnas `usuario_modificacion_id` de `evento`/`noticia` permanecen como referencia de negocio no forzada por constraint.
3. **`gda-autenticacion` y `gda-persona` permanecen compartidos con GDA, sin réplica.** `spj-api-gateway` conserva `GdaAutenticacionApiClient`, `GdaPersonaApiClient` y `GdaImputacionApiClient` (este último para componer festivos reales en `/user/eventos`) como dependencias externas reales, igual que hacía `api-gateway`. Es la única frontera que no se segrega: la identidad de las personas y su autenticación siguen teniendo una única fuente de verdad en todo el ecosistema GDA + SPJ.
4. **Gateway propio y reducido** (`spj-api-gateway`, puerto 9110): `RouteLocatorConfig` limitado a las 5 rutas de Comunicación (lectura pública de noticias/eventos/categorías/etiquetas, gestión de noticias/categorías); todo el código de dominios ajenos (Guardias, Agrupación, Estructura, Listado, Admingade, Log) eliminado, no solo des-enrutado.
5. **Infraestructura Docker independiente** en el servidor de desarrollo: `/gda/REIR_GDACT/docker/SPJ/` (separada de `/gda/REIR_GDACT/docker/Actuaciones3.0/`), con su propio `docker-compose.yml` (`spj-comunicacion` puerto 9109, `spj-api-gateway` puerto 9110, ambos con `SPRING_PROFILES_ACTIVE=dev` explícito) y su propio script de control `SPJ-Espacio-Justicia.sh`, mismo patrón que `V3-ReirGdact.sh` (ver ADR-0801). El frontend (`spj-frontend-10`, puerto 9011) se incorporó después con el mismo patrón que el de GDA: build multi-stage que descomprime el `.zip` entregado por Front y lo sirve con nginx.

## Alternativas Consideradas

**A — Mantener Espacio Justicia dentro de GDA** (`gda-comunicacion` + `api-gateway` compartido, sin segregar). Mínimo esfuerzo de migración, pero acopla el ciclo de release de un producto conceptualmente independiente al de GDA, y expone en el mismo Gateway rutas y lógica de dominios que Espacio Justicia no necesita. Rechazada por la decisión de negocio de tratar Espacio Justicia como producto propio.

**B — Backend "gemelo" segregado, compartiendo solo identidad/autenticación** *(seleccionada)*. Aísla el ciclo de vida, despliegue y superficie de API de Espacio Justicia sin duplicar la fuente de verdad de personas y credenciales — el riesgo más costoso de duplicar (consistencia de datos de identidad, gestión de altas/bajas, políticas de contraseña).

**C — Independencia total, incluyendo réplica de `gda-autenticacion` y `gda-persona`.** Aislamiento máximo, pero obliga a sincronizar (o duplicar) identidad de personas entre dos sistemas, con el riesgo real de desincronización que eso implica. Rechazada explícitamente: la identidad de persona y su autenticación deben tener una única fuente de verdad en todo el ecosistema.

## Consecuencias

### Positivas (+)

* Espacio Justicia gana ciclo de release, infraestructura Docker y superficie de API completamente propios, sin bloquear ni ser bloqueado por cambios en el resto de GDA.
* `spj-api-gateway` es un artefacto significativamente más pequeño y auditable que `api-gateway` (5 rutas frente a ~60), reduciendo la superficie de ataque y el código muerto para este producto.
* La identidad de las personas y su autenticación mantienen una única fuente de verdad (`gda-autenticacion`, `gda-persona`), evitando el riesgo de desincronización de la Alternativa C.
* Verificado con evidencia real de extremo a extremo (login, lectura, escritura con auditoría de usuario) sobre el servidor de desarrollo, no solo a nivel de diseño.

### Negativas (-)

* **Acoplamiento de despliegue no eliminado, solo desplazado:** `spj-api-gateway` depende en tiempo de ejecución de `gda-autenticacion` (vía `SecurityFilter.java`, que resuelve `tipoAutoridad`/`tipoComunicacion` en cada petición) y de `gda-persona`. Un cambio de contrato en cualquiera de los dos obliga a coordinar el redespliegue con SPJ, igual que ya ocurría dentro de GDA.
* **Deuda de versión duplicada:** `spj-api-gateway/pom.xml` hereda el mismo problema ya documentado en ADR-0600 para `api-gateway/pom.xml` — `gda-autenticacion-commons` fijado a `4.1.0-SNAPSHOT` (no a una versión de release), porque `getTipoComunicacion()` es imprescindible y aún no existe una release `4.1.0` publicada.
* **Punto de divergencia futuro identificado y aún sin resolver:** el equipo backend está evaluando sustituir `usuario.tipo_comunicacion_id` por una tabla `aplicacion` que permita varias filas `usuario` por persona (una por aplicación). De aprobarse, obligará a reescribir `SecurityFilter.java` **en ambos Gateways simultáneamente** (`api-gateway` y `spj-api-gateway`) y a coordinar el redespliegue de `gda-autenticacion` con ambos — este ADR documenta la posición estable actual (un `usuario` por persona, `tipoComunicacion` como columna); si esa decisión se aprueba, este ADR deberá corregirse o ser superseded, no reescribirse en silencio.

  > **Nota de actualización (2026-08-25):** esta divergencia ha sido resuelta por **ADR-0610**. Contrario a lo previsto aquí, `SecurityFilter.java` de ambos Gateways **no requirió cambios** — la resolución de `aplicacionId` quedó contenida dentro de `gda-autenticacion`. Este párrafo se conserva sin modificar como registro histórico de la posición original; ADR-0610 documenta la decisión final y su ejecución real.
* Infraestructura Docker de SPJ (`docker-compose.yml`, `Dockerfile`, `SPJ-Espacio-Justicia.sh`) vive fuera del monorepo, con la misma deuda ya documentada en ADR-0801 para la infraestructura de GDA.

### Riesgos Mitigados

* Que Espacio Justicia quedase indefinidamente acoplado al ciclo de release de GDA sin justificación operativa, dificultando su evolución como producto propio.
* Que la segregación se hiciese de forma parcial (por ejemplo, solo des-enrutando en vez de eliminar código de dominios ajenos), dejando en `spj-api-gateway` superficie de ataque y mantenimiento innecesarios.
* Que se duplicase la fuente de verdad de identidad de personas (Alternativa C), con el riesgo de desincronización que eso conlleva.

---

## Referencias

* `GDA/backend/spj-comunicacion/` — repositorio real, forkeado de `gda-comunicacion` con historial completo (`espacio-justicia/backend/spj-comunicacion.git`).
* `GDA/spj-api-gateway/` — repositorio real, forkeado de `api-gateway` con historial completo (`espacio-justicia/backend/spj-api-gateway.git`).
* `GDA/spj-api-gateway/src/main/java/com/ineco/spj/apigateway/config/RouteLocatorConfig.java` — Gateway reducido a 5 rutas de Comunicación.
* `GDA/spj-api-gateway/src/main/java/com/ineco/spj/apigateway/security/SecurityFilter.java` — sin modificar respecto a `api-gateway`; resuelve autoridades en cada petición vía `gdaAutenticacionApiClient.getUsuarioByToken()`.
* `GDA/backend/spj-comunicacion/spj-comunicacion/src/main/java/com/ineco/spj/comunicacion/data/repository/NoticiaRepository.java` — corrección real de un fallo introducido por la segregación (schema `gda_comunicacion` hardcodeado en SQL nativo, no detectado por el renombrado de paquetes Java; corregido a `spj_comunicacion` el 2026-08-20).
* Esquema `spj_comunicacion` en base de datos `spj_01_desa` — sin FK a `gda_persona.persona` (eliminada, imposible entre bases de datos distintas).
* `/gda/REIR_GDACT/docker/SPJ/docker-compose.yml`, `/gda/REIR_GDACT/docker/SPJ/SPJ-Espacio-Justicia.sh` — infraestructura de despliegue real en el servidor de desarrollo.
* ADR-0607 (microservicio `gda-comunicacion`, superseded por este ADR — se conserva como registro histórico de la decisión original, no se reescribe).
* ADR-0600 (estrategia de despliegue; deuda de versión `gda-autenticacion-commons` ahora duplicada en `spj-api-gateway`), ADR-0601 (módulo-commons), ADR-0602 (comunicación inter-servicio), ADR-0603 (gestión de BBDD), ADR-0604 (composición del API Gateway — no aplica a `spj-api-gateway`, que usa exclusivamente rutas de paso simple), ADR-0605 (RBAC por prefijo), ADR-0606 (patrón de auditoría), ADR-0608 (almacenamiento de adjuntos de noticias), ADR-0801 (empaquetado y despliegue Docker).
* `.vscode/docs/Documentacion_BackEnd_EspacioJusticia_planaccion_2608.md` — plan de fases (Fase 1/2/3) y ledger de decisiones.
* `.vscode/docs/Documentacion_BackEnd_EspacioJusticia_servidor_2608.md` — evidencia real de despliegue y pruebas end-to-end sobre el servidor de desarrollo.
