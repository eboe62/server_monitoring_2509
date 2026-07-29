# ADR-0602: Estrategia de Comunicación Inter-Servicio en Arquitectura de Microservicios

Status: APPROVED
Date: 2026-06-11 (revisado 2026-07-16 para reflejar la implementación real vigente en `gda-admingade` / Guards; revisado 2026-07-22 con hallazgo real de serialización de fechas en Feign)
Scope: System
Category: ARCHITECTURE
Tags: REVIEW_REQUIRED
Related ADRs: ADR-0600, ADR-0801
Supersedes: NONE
Superseded By: NONE
Validation Reference: NONE

## Contexto
En un Monorrepo Maven Multi-Module con microservicios independientes, es fundamental establecer una estrategia de comunicación inter-servicio que garantice interoperabilidad, escalabilidad y desacoplamiento. Este ADR se ha revisado tras contrastarlo con la implementación real del módulo `gda-admingade` (feature Guards: `GuardiaController`, `GuardiaService`, `GuardiaRepository`), que es hoy el patrón de referencia ya validado en producción para el resto de módulos del backend GDA (p. ej. el nuevo módulo Vendors).

## Decisión
Adoptar una estrategia de comunicación basada en los siguientes principios, alineados con la práctica ya vigente:

1. **Contratos REST/JSON:** cada microservicio expone sus APIs mediante REST utilizando JSON como formato de intercambio de datos (verificado: `GuardiaController` expone `GET/POST/PUT/DELETE /guardias`).
2. **Generación base de OpenAPI:** cada módulo backend incluye `springdoc-openapi-starter-webmvc-ui` y `springdoc-openapi-starter-webmvc-api` en su `pom.xml`, que generan automáticamente la especificación OpenAPI a partir de los controllers `@RestController`, sin necesitar anotación manual adicional para el nivel base.
3. **Desacoplamiento vía API Gateway:** los consumidores (frontend y, en su caso, otros servicios) no llaman directamente a los microservicios; toda la comunicación se canaliza a través del API Gateway (`GDA/api-gateway`), que centraliza el enrutado (ver ADR-0802).
4. **Rutas planas, sin versionado por ahora:** los endpoints se exponen como recursos planos sin prefijo de versión (p. ej. `/guardias`, no `/v1/guardias`). No se adopta un esquema de versionado mientras no exista un cambio incompatible que lo requiera.

## Deuda técnica / mejoras pendientes (no bloqueantes para nuevos módulos)
- **Documentación enriquecida de OpenAPI:** los controllers actuales (p. ej. `GuardiaController`) no llevan anotaciones `@Operation`/`@Tag`/`@ApiResponse`; la especificación generada es mínima (solo firmas de método). Se recomienda incorporarlas de forma incremental, empezando por los módulos nuevos.
- **Versionado de contratos:** si en el futuro un endpoint ya publicado necesita un cambio incompatible, se introducirá versionado explícito (`/v1/...` o cabecera `Accept-Version`) en ese momento; no es un requisito para los endpoints actuales.
- **`ObjectMapper` de Feign sin módulo de fechas Java 8, hallazgo real (2026-07-22):** `ACSFeignConfiguration.java` (API Gateway) define, para **todas** las llamadas Feign salientes del Gateway (no solo hacia `gda-persona`), un `ObjectMapper` construido manualmente (`new ObjectMapper()`) sin registrar `JavaTimeModule`. Cualquier campo `LocalDate`/`LocalDateTime` sin anotación `@JsonSerialize`/`@JsonDeserialize` explícita a nivel de campo se pierde silenciosamente al pasar por Feign (sin excepción visible), tanto en la escritura (Gateway → microservicio) como en la lectura (microservicio → Gateway). Detectado al ampliar `Proveedor` con campos `LocalDate` de auditoría (`Documentacion_BackEnd_GDA_2607_Vendors.md` §14, Hallazgo 1). `gda-persona-commons` ya tenía este problema resuelto de facto en 9 DTOs existentes (`CandidatoDto`, `PersonaDto`, etc.) mediante clases propias `com.ineco.gda.persona.util.LocalDateSerializer`/`LocalDateDeserializer`, aplicadas campo a campo — un parche por módulo, no una solución centralizada en `ACSFeignConfiguration`. Se recomienda, como mejora futura, registrar `JavaTimeModule` directamente en el `ObjectMapper` de `ACSFeignConfiguration` para que cualquier DTO con `LocalDate` funcione correctamente por defecto sin necesitar anotación por campo — no abordado en esta fase por ser un cambio transversal a todos los Feign clients del Gateway, fuera del alcance de Vendors.

## Consecuencias

### Positivas (+)
- El ADR refleja la práctica ya validada en producción por Guards, en vez de exigir a nuevos módulos (p. ej. Vendors) un estándar que ni siquiera el módulo de referencia cumple.
- Las mejoras pendientes quedan documentadas como deuda técnica explícita en lugar de perderse.
- Facilita auditar el cumplimiento real de los módulos existentes y futuros contra un ADR realista.

### Negativas (-)
- Al no exigir versionado ni documentación enriquecida desde ya, el riesgo de romper compatibilidad se traslada al momento en que aparezcan más consumidores del contrato.
- Requiere revisar este ADR de nuevo cuando se decida abordar la deuda técnica señalada.
