# ADR-0602: Estrategia de Comunicación Inter-Servicio en Arquitectura de Microservicios

Status: APPROVED
Date: 2026-06-11
Decision Type: REVIEW_REQUIRED
Scope: System
Category: ARCHITECTURE
Tags: REVIEW_REQUIRED
Related ADRs: ADR-0600, ADR-0801
Supersedes: NONE
Superseded By: NONE
Validation Reference: NONE

## Contexto
En un Monorrepo Maven Multi-Module con microservicios independientes, es fundamental establecer una estrategia de comunicación inter-servicio que garantice interoperabilidad, escalabilidad y desacoplamiento. Actualmente, no se han definido lineamientos claros sobre cómo los servicios deben interactuar entre sí, lo que puede generar inconsistencias en los contratos de API, problemas de compatibilidad y dificultades para realizar cambios sin afectar a otros servicios.

## Decisión
Adoptar una estrategia de comunicación basada en los siguientes principios:
1. **Contratos REST/JSON:** Cada microservicio expondrá sus APIs mediante REST utilizando JSON como formato de intercambio de datos.
2. **Documentación con OpenAPI:** Todos los servicios deberán documentar sus contratos de API utilizando OpenAPI (Swagger) para garantizar claridad y consistencia.
3. **Desacoplamiento:** Los servicios consumidores no deben depender directamente del código del servicio proveedor. En su lugar, consumirán las APIs a través de clientes generados dinámicamente o librerías desacopladas.
4. **Versionado de APIs:** Se implementará un esquema de versionado para garantizar compatibilidad hacia atrás en los contratos de API.

## Consecuencias

### Positivas (+)
- Garantiza interoperabilidad y claridad en la comunicación entre servicios.
- Facilita la integración con herramientas externas y la generación automática de clientes.
- Reduce el acoplamiento entre servicios, permitiendo cambios independientes.

### Negativas (-)
- Requiere un esfuerzo adicional para mantener actualizada la documentación de las APIs.
- Introduce complejidad en la gestión de versiones y compatibilidad de contratos.
