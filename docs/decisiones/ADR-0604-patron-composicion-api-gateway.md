# ADR-0604: Patrón de Composición del API Gateway para Agregación de Datos Multi-Microservicio (BFF)

Status: APPROVED
Date: 2026-07-16 (revisado 2026-07-20 tras implementar la Fase 2 de Vendors: `ProveedorRequest`;
revisado 2026-07-25 tras confirmar un tercer caso real, Licencia)
Scope: System
Category: ARCHITECTURE
Tags: REVIEW_REQUIRED
Related ADRs: ADR-0602, ADR-0802
Supersedes: NONE
Superseded By: NONE
Validation Reference: NONE

## Contexto

El API Gateway (Spring Cloud Gateway + WebFlux, módulo `GDA/api-gateway`) es el único punto de entrada entre el frontend y los microservicios backend (ver ADR-0802). Auditando el módulo real durante el análisis del nuevo dominio Vendors (basado en el patrón Guards), se ha verificado que el Gateway implementa hoy **dos mecanismos distintos** para exponer un recurso al frontend, y que ninguno de los dos está documentado en un ADR:

1. **Rutas de paso simple**, declaradas en `RouteLocatorConfig.java` vía `RouteLocatorBuilder`: reescriben el path (`rewritePath`) y reenvían la petición tal cual al microservicio de dominio correspondiente, sin transformar el payload. Es el mecanismo usado para la mayoría de los recursos (`anios`, `meses`, `encargos`, `presupuestos`, `certificaciones`, `proyectos`, `paquetes`, `iniciativas`, `personas`, etc.).

2. **Una capa de composición propia por dominio**, verificada en el caso de Guardias: el Gateway tiene su propio `GuardiaController` (paquete `apigateway.web.controller.admingade`), su propio `GuardiaService`/`GuardiaServiceImpl`, y sus propios DTOs `GuardiaRequest`/`GuardiaResponse` (paquete `apigateway.dto.admingade.*`), distintos del `GuardiaDto` que expone el microservicio `gda-admingade`. `GuardiaServiceImpl` invoca en paralelo (`CompletableFuture`) los clientes Feign de `gda-admingade`, `gda-persona`, `gda-agrupacion` y `gda-estructura`, y combina los resultados con `ModelMapper` antes de devolver un único payload enriquecido al frontend. Esto es necesario porque `GuardiaDto` solo contiene identificadores (`personaId`, `proveedorId`, `grupoId`, `iniciativaId`) que no son directamente utilizables por el frontend sin resolver antes los datos completos de cada entidad relacionada.

**Segunda confirmación real (2026-07-16), al continuar el análisis de Vendors:** el propio dominio `Proveedor` (que resultó ser el backend real de "Vendors", en `gda-persona`, no en `gda-admingade`) usa exactamente el mismo mecanismo. El Gateway tiene su propio `ProveedorController` (paquete `apigateway.web.controller.persona`) y `ProveedorServiceImpl` (paquete `apigateway.service.persona.impl`), que invoca `GdaPersonaApiClient.getProveedores()` **y** `GdaAdmingadeApiClient.getEncargoVigente()` para filtrar los proveedores del encargo vigente antes de responder al frontend — la misma composición cruzada que `GuardiaServiceImpl`, esta vez entre `gda-persona` y `gda-admingade`. En el momento de esta segunda confirmación (2026-07-16), `ProveedorController` del Gateway aún **reutilizaba `ProveedorDto` directamente** como entrada/salida, sin DTOs `Request`/`Response` propios — una variante del mecanismo 2 que este ADR no había contemplado explícitamente (ver Decisión, punto 2).

**Actualización (2026-07-20, Fase 2 de Vendors completada):** al implementar `POST`/`PUT`/`DELETE` en `ProveedorController`, se introdujo `ProveedorRequest` (paquete `apigateway.dto.persona.request`), propio del Gateway y distinto de `ProveedorDto` — igualándose así al patrón que ya usaba `GuardiaController` (`GuardiaRequest`). `ProveedorDto` se sigue usando tal cual solo para el `GET` (lectura) y como DTO interno de comunicación con `gda-persona` vía Feign; ya no es el contrato de entrada para escritura. Proveedores deja de ser el ejemplo de "variante sin DTOs propios" del punto 2 de la Decisión — ese rol queda hoy sin un segundo ejemplo real verificado en el backend GDA, aunque el mecanismo (DTOs `Request`/`Response` opcionales dentro del patrón de composición) sigue siendo válido como se describe.

**Tercera confirmación real (2026-07-25), módulo Licencias:** a diferencia de Guardias y Proveedores
(entidades ya existentes al aplicar este ADR), Licencia se diseñó desde cero ya con el criterio del
punto 3 aplicado explícitamente antes de escribir código: `licencia.estado_id`/`localizacion_id`
necesitan `MaestroEstadoDto`/`MaestroLocalizacionDto` de `gda_persona`, así que se adoptó directamente
el mecanismo 2 sin pasar por una fase de duda. `LicenciaController`/`LicenciaServiceImpl` (paquete
`apigateway.*.admingade`) replican exactamente la variante con DTOs propios (`LicenciaRequest`/
`LicenciaResponse`, distintos de `LicenciaDto`) — la misma variante que `GuardiaController`, no la que
inicialmente usó `ProveedorController`. Aporta además dos matices no cubiertos por los dos casos
anteriores: (a) el `DELETE` reactivo de Licencia se modeló sobre `ProveedorServiceImpl.deleteProveedor()`
porque `GuardiaServiceImpl` nunca implementó esa operación — es la segunda aplicación real de ese patrón
de borrado, no solo la primera vuelta a usarlo; (b) el propio `LicenciaController` expone además dos
endpoints de solo *passthrough* sin ninguna composición (`admingade/maestrosEstado`/
`admingade/maestrosLocalizacion`, delegan 1:1 en `GdaPersonaApiClient`) colocados en el mismo controller
que la composición real — una variante ligera no descrita explícitamente en la Decisión, útil cuando un
endpoint de apoyo (aquí, los desplegables del formulario) es demasiado pequeño para justificar su propio
módulo de Gateway pero tampoco encaja como ruta de paso en `RouteLocatorConfig.java` porque el frontend
lo consume bajo el prefijo `admingade/` en vez del prefijo propio del microservicio origen.

Ni ADR-0602 (centrado en el contrato REST/JSON de cada microservicio de dominio) ni ADR-0802 (centrado en que el frontend solo hable con el Gateway) documentan cuál de los dos mecanismos debe usarse ni cuándo. Esta laguna se detectó al intentar planificar la integración de Vendors con el Gateway: no había ningún criterio escrito para decidir si el nuevo dominio necesita una capa de composición propia (como Guardias y, según se confirmó después, también Proveedores) o le basta una ruta de paso simple (como la mayoría de los demás recursos). Sin este criterio, cada módulo nuevo corre el riesgo de infra-diseñar la integración (obligando al frontend a resolver relaciones con varias llamadas) o sobre-diseñarla (creando Controller/Service/DTOs de Gateway innecesarios para un recurso autocontenido).

## Decisión

Se formalizan los dos mecanismos ya existentes como patrones válidos y mutuamente excluyentes por recurso, junto con el criterio obligatorio para elegir entre ellos:

1. **Ruta de paso simple (pass-through route).** Se declara en `RouteLocatorConfig.java`, reescribiendo el path hacia el microservicio de origen, sin lógica de transformación. Aplicable cuando el DTO que expone el microservicio de origen (definido en su `-commons`, ver ADR-0601) ya contiene toda la información que el frontend necesita, sin identificadores de otras entidades que deban resolverse contra otros microservicios.

2. **Capa de composición dedicada en el Gateway (Backend-for-Frontend por dominio).** Un `Controller` + `Service`/`ServiceImpl` propios, ubicados en `apigateway.web.controller.<dominio>` / `apigateway.service.<dominio>`, que invocan uno o más clientes Feign (el del propio dominio y los de cualquier otro microservicio cuyos datos deban combinarse) y agregan los resultados antes de responder al frontend. Los DTOs `Request`/`Response` propios del Gateway (paquete `apigateway.dto.<dominio>.*`) son **opcionales dentro de este mecanismo**: `GuardiaController` los usa (`GuardiaRequest`/`GuardiaResponse`, distintos del `GuardiaDto` del microservicio), mientras que `ProveedorController` reutiliza directamente `ProveedorDto` sin DTOs propios del Gateway — ambas variantes son válidas; la elección depende de si el Gateway necesita transformar/restringir el payload más allá de la agregación en sí. Aplicable cuando el DTO de origen expone identificadores de entidades que residen en otros microservicios y el frontend necesita esas entidades resueltas para renderizar la vista sin hacer llamadas adicionales.

3. **Criterio de decisión obligatorio.** Durante el diseño de cualquier módulo nuevo, antes de implementar su backend, debe responderse explícitamente y por escrito (en el documento de requisitos del módulo) la pregunta: *¿el recurso expuesto al frontend necesita datos que residen en otro microservicio?* Si la respuesta es no, se adopta el mecanismo (1). Si es sí, se adopta el mecanismo (2). Esta decisión debe quedar registrada antes de escribir el `VendorsController`/`Vendors*` (o equivalente) del Gateway.

## Alternativas Consideradas

**A. Agregación en el cliente (frontend).** El frontend haría una llamada por cada microservicio implicado (todas vía Gateway) y combinaría los datos en el composable o la vista. Rechazada: multiplica las llamadas HTTP visibles al frontend, filtra la topología interna de microservicios hacia el cliente, y duplica lógica de combinación en cada vista que la necesite — contradice directamente ADR-0802 (desacoplamiento del frontend respecto a los microservicios internos).

**B. Exigir siempre la capa de composición, incluso para recursos autocontenidos.** Simplificaría la regla a un único patrón universal, pero introduce boilerplate innecesario (Controller+Service+DTOs propios del Gateway) para la mayoría de los recursos actuales, que no lo necesitan — contradice el principio de proporcionalidad por Tiers de impacto ya establecido en `ai/governance/04_ARCHITECTURE_GUIDELINES.md` §1.

**C. Prohibir la capa de composición y extraerla a un futuro microservicio "BFF" independiente.** Más limpio en el largo plazo desde un punto de vista de separación de responsabilidades, pero no refleja la práctica ya implementada y validada en producción por Guardias, y exigiría una migración retroactiva no justificada por ninguna necesidad operativa actual.

Se selecciona el criterio condicional descrito en la Decisión por ser el que Guards ya sigue en producción, sin requerir ninguna migración ni introducir boilerplate donde no aporta valor.

## Consecuencias

### Positivas (+)
- Documenta un patrón real y ya validado en producción, verificado en **tres dominios independientes** (Guardias, Proveedores y Licencias), cerrando una laguna de gobernanza detectada durante el análisis del módulo Vendors.
- Proporciona un criterio objetivo y verificable — ¿el recurso necesita datos de otro microservicio? — para que cualquier módulo nuevo decida su integración con el Gateway sin ambigüedad y antes de implementar.
- Evita tanto la sub-ingeniería (alternativa A, que sobrecarga al frontend) como la sobre-ingeniería (alternativa B, que generaliza boilerplate innecesario).

### Negativas (-)
- La capa de composición (mecanismo 2) introduce DTOs `Request`/`Response` adicionales propios del Gateway, distintos de los DTOs del microservicio de origen (`gda-admingade-commons`), que deben mantenerse sincronizados manualmente al no existir generación automática de contratos entre ambos.
- El criterio de decisión depende de que el análisis de requisitos de cada módulo nuevo identifique correctamente sus relaciones entre microservicios; un análisis incorrecto puede derivar en llamadas N+1 evitables desde el frontend o en una capa de composición innecesaria.
- Este ADR no establece un límite de escalabilidad para los `Service`/`ServiceImpl` de composición cuando el número de microservicios a agregar en paralelo crezca (hoy `GuardiaServiceImpl` combina 4); ese límite queda fuera de su alcance.

## Referencias
- `GDA/api-gateway/src/main/java/com/ineco/gda/apigateway/web/controller/admingade/GuardiaController.java`
- `GDA/api-gateway/src/main/java/com/ineco/gda/apigateway/service/admingade/GuardiaService.java` y `.../impl/GuardiaServiceImpl.java`
- `GDA/api-gateway/src/main/java/com/ineco/gda/apigateway/web/controller/persona/ProveedorController.java` (segundo caso real verificado; con `POST`/`PUT`/`DELETE` desde 2026-07-20)
- `GDA/api-gateway/src/main/java/com/ineco/gda/apigateway/service/persona/ProveedorService.java` y `.../impl/ProveedorServiceImpl.java`
- `GDA/api-gateway/src/main/java/com/ineco/gda/apigateway/dto/persona/request/ProveedorRequest.java` (2026-07-20: DTO de escritura propio del Gateway, ver actualización de esta sección)
- `GDA/api-gateway/src/main/java/com/ineco/gda/apigateway/web/clients/GdaAdmingadeApiClient.java`
- `GDA/api-gateway/src/main/java/com/ineco/gda/apigateway/web/clients/GdaPersonaApiClient.java`
- `GDA/api-gateway/src/main/java/com/ineco/gda/apigateway/config/RouteLocatorConfig.java`
- ADR-0601 (Desacoplamiento de Capas mediante el Patrón Módulo-Commons)
- ADR-0602 (Estrategia de Comunicación Inter-Servicio en Arquitectura de Microservicios)
- ADR-0802 (Lineamientos de Integración Frontend con Microservicios Backend)
- `ai/governance/04_ARCHITECTURE_GUIDELINES.md` §1 (clasificación de microservicios por Tiers de impacto)
- `.vscode/docs/Documentacion_FrontEnd_GDA_2607_Vendors.md` §4 (hallazgo original que motivó este ADR)
- `.vscode/docs/knowledge-graph-vendors.json` (grafo de dependencias de Vendors a ajustar según el criterio de este ADR; movido desde `docs/decisiones/` el 2026-07-16 junto con el resto del análisis de Vendors)
- `GDA/api-gateway/src/main/java/com/ineco/gda/apigateway/web/controller/admingade/LicenciaController.java` (tercer caso real verificado, 2026-07-25; incluye además el matiz de endpoints de passthrough sin composición dentro del mismo controller)
- `GDA/api-gateway/src/main/java/com/ineco/gda/apigateway/service/admingade/LicenciaService.java` y `.../impl/LicenciaServiceImpl.java` (el `deleteLicencia` reactivo replica `ProveedorServiceImpl.deleteProveedor()`, segunda aplicación real de ese patrón de borrado)
- `.vscode/docs/Documentacion_BackEnd_GDA_2607_Licenses.md` §3, §7
