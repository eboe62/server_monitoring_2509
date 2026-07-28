# ADR-0605: Modelo de Autorización RBAC por Prefijo de Ruta en el API Gateway

Status: APPROVED

Date: 2026-07-20

Scope:
System

Category:
SECURITY

Tags:
REVIEW_REQUIRED

Related ADRs:
[ADR-0604, ADR-0802, ADR-0803]

Supersedes:
NONE

Superseded By:
NONE

---

## Context

El API Gateway (`GDA/api-gateway`, Spring Cloud Gateway + WebFlux) implementa desde antes de este ADR un modelo de autorización real en `SecurityConfiguration.java`, verificado en código: cada grupo de rutas se protege con `.pathMatchers("<prefijo>/**").hasAnyAuthority(<roles>)` (p. ej. `/admingade/**` → `ADMINGADE`, `ADMINGADE_RSP_EQP`, `GDA_SUPERGESTOR`, `ADMINGADE_MANAGER`; patrones equivalentes para `/rsp_grp/**`, `/rsp_eqp/**`, `/super/**`, `/user/**`). Los microservicios de dominio (verificado en `gda-persona/SecurityConfiguration.java`) no implementan autorización propia — su `SecurityConfiguration` solo configura CORS — y confían en que el Gateway ya filtró la petición antes de reenviarla vía Feign.

Este modelo lleva tiempo en producción (es el que ya protege Guardias, Personas, Encargos, etc.) pero no estaba documentado en ningún ADR. La laguna se hizo visible el 2026-07-20 al decidir los permisos del nuevo módulo Vendors (`Documentacion_BackEnd_GDA_2607_Vendors.md` §7.5/§8): el requisito de producto era "solo acceden las mismas personas que ya acceden al resto de pantallas del menú Gestión Admingade, con CRUD completo, sin rol de escritura separado". Verificar si el modelo actual ya
cumplía ese requisito, o si hacía falta diseñar algo nuevo, requirió leer directamente el código de seguridad porque no había ningún documento de referencia — el mismo tipo de laguna de gobernanza que motivó ADR-0604 para el patrón de composición del Gateway.

## Decision

Se formaliza como modelo de autorización vigente del sistema el ya implementado en `SecurityConfiguration.java` del API Gateway:

1. **El API Gateway es el único punto de aplicación de autorización.** Los microservicios de dominio no implementan control de acceso propio por rol; confían en que toda petición que les llega ya fue    autorizada por el Gateway. Cualquier microservicio nuevo debe seguir este mismo modelo de confianza — no debe añadir `hasAnyAuthority`/`hasRole` ni equivalente en su propia `SecurityConfiguration`.
2. **La autorización se concede por prefijo de ruta, no por verbo HTTP.** Un `pathMatchers("<prefijo>/**")` con un conjunto fijo de authorities cubre todos los métodos (`GET`/`POST`/`PUT`/`DELETE`) expuestos bajo ese prefijo. El modelo **no distingue** "rol de lectura" de "rol de escritura": quien tiene autoridad para leer un recurso bajo un prefijo, la tiene también para crearlo, editarlo y eliminarlo.
3. **Todo módulo nuevo reutiliza el prefijo y el conjunto de roles del menú/agrupación funcional al que pertenece**, en vez de introducir un rol nuevo por defecto. Ejemplo aplicado: Vendors expone sus rutas bajo `/admingade/proveedores` (mismo prefijo que el resto de "Gestión Admingade"), por lo que hereda automáticamente `ADMINGADE`, `ADMINGADE_RSP_EQP`, `GDA_SUPERGESTOR`, `ADMINGADE_MANAGER`sin necesidad de tocar `SecurityConfiguration.java`.
4. **Introducir un rol nuevo, o distinguir lectura de escritura, requiere una decisión de producto explícita y una ampliación deliberada de `SecurityConfiguration.java`** (nuevo `pathMatchers` con su propio conjunto de authorities, o `@PreAuthorize`/comprobación a nivel de método si se necesita granularidad por verbo). No es el comportamiento por defecto del sistema.

## Consequences

### Positive

* Documenta con evidencia de código (no solo de diseño) un patrón ya validado en producción, cerrando una laguna de gobernanza análoga a la que resolvió ADR-0604 para la composición del Gateway.
* Da a cualquier módulo nuevo un criterio explícito y verificable: reutilizar el prefijo/roles del menú al que pertenece, en vez de decidir permisos caso a caso sin referencia escrita.
* Evita over-engineering (crear un rol de escritura nuevo para cada módulo que no lo necesita) y under-engineering (dejar la decisión de permisos sin resolver o sin documentar, como ocurrió antes de este ADR).

### Negative

* El modelo es intrínsecamente de grano grueso: no es posible, sin trabajo adicional de diseño e implementación, dar a un usuario acceso de solo lectura a un recurso sin darle también escritura, mientras ambos compartan prefijo de ruta.
* La asignación real de roles a usuarios (qué usuario tiene `ADMINGADE_RSP_EQP`, por ejemplo) vive fuera de este repositorio (proveedor de identidad/autenticación), por lo que este ADR documenta el mecanismo de autorización, no la política de asignación de roles a personas.
* Si en el futuro un módulo necesita separar lectura de escritura, no hay un mecanismo ya construido para ello — habrá que diseñarlo explícitamente y probablemente revisar este ADR.

### Risks Mitigated

* Que un módulo nuevo introduzca un rol de autorización ad-hoc sin verificar primero si el modelo ya existente lo resuelve (sobre-ingeniería de seguridad).
* Que la decisión de permisos de un módulo nuevo se tome sin verificar el código real de `SecurityConfiguration.java`, apoyándose solo en suposiciones de diseño.

---

## References

* `GDA/api-gateway/src/main/java/com/ineco/gda/apigateway/config/SecurityConfiguration.java`
  (implementación real del modelo, `pathMatchers`/`hasAnyAuthority` por prefijo)
* `GDA/backend/gda-persona/gda-persona/src/main/java/com/ineco/gda/persona/config/SecurityConfiguration.java`
  (confirmación de que el microservicio de dominio no implementa autorización propia)
* ADR-0604 (Patrón de Composición del API Gateway) — mismo tipo de laguna de gobernanza detectada y cerrada durante el análisis de un módulo nuevo (Vendors)
* ADR-0802 (Lineamientos de Integración Frontend con Microservicios Backend)
* ADR-0803 (Estrategias de Seguridad y Gestión de Secretos en Microservicios) — complementario: cubre autenticación JWT/secretos, no el modelo de autorización por roles que cubre este ADR
* `.vscode/docs/Documentacion_BackEnd_GDA_2607_Vendors.md` §7.5 y §8 (caso real que motivó este ADR: decisión de permisos del módulo Vendors)
