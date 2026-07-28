# ADR-0016 — Política de aislamiento y segmentación de redes Docker

Status: APPROVED
Date: 2026-05-06
Scope: Infrastructure
Category: SECURITY
Tags: security, hardening, network
Related ADRs: ADR-0015, ADR-0021
Supersedes: NONE
Superseded By: NONE
Validation Reference: NONE

## Contexto

La plataforma está basada en múltiples stacks Docker desacoplados mediante Compose e infraestructura declarativa.

Durante la evolución del sistema aparecieron varios riesgos:
- comunicación excesivamente permisiva entre servicios,
- exposición innecesaria de puertos,
- acoplamiento entre stacks,
- dificultad para delimitar dominios funcionales,
- y propagación potencial de incidentes entre contenedores.

Además, algunos servicios externos requieren exposición parcial controlada mientras que otros deben permanecer únicamente accesibles desde redes internas.

## Problema

El uso de redes Docker compartidas sin segmentación explícita:
- dificulta aplicar el principio de mínimo privilegio,
- incrementa superficie de ataque,
- reduce trazabilidad de comunicaciones,
- y complica la evolución segura de la arquitectura.

Era necesario definir una política homogénea de segmentación de redes y exposición de servicios.

## Decisión

Se adopta una estrategia de segmentación explícita mediante redes Docker diferenciadas por dominio funcional.

Principios generales:

- Cada stack debe conectarse únicamente a las redes estrictamente necesarias.
- La exposición de puertos debe minimizarse.
- Los servicios internos no deben exponerse directamente al host salvo necesidad justificada.
- Las comunicaciones entre dominios deben ser explícitas y auditables.

Clasificación de redes:

- Redes internas de aplicación
  Uso:
  - comunicación privada entre servicios del mismo dominio funcional.

- Redes compartidas controladas
  Uso:
  - integración explícita entre stacks relacionados.

- Redes restringidas
  Uso:
  - servicios sensibles,
  - relay SMTP,
  - observabilidad,
  - componentes con requisitos especiales de endurecimiento.

## Reglas operativas

- Evitar el uso indiscriminado de:
  network_mode: host

- Evitar contenedores conectados a múltiples redes sin justificación funcional.

- Priorizar:
  internal: true
  cuando el servicio no requiera acceso externo.

- La pertenencia de un servicio a una red debe reflejar una necesidad funcional explícita.

- La infraestructura declarativa (Compose) debe representar de forma visible la política de segmentación.
## Ejemplos en el proyecto
Scripts actuales que entran en esta categoría:
configure_docker_limits.sh
  - aplica límites de CPU y memoria a contenedores
  - evita saturación del host

apply_ssh_ratelimit.sh
  - configura limitación de conexiones SSH
  - protege frente a ataques masivos

## Razonamiento

La segmentación reduce superficie de ataque y limita propagación lateral entre servicios.

Separar dominios funcionales mejora:
- auditabilidad,
- aislamiento operativo,
- trazabilidad de comunicaciones,
- y capacidad de endurecimiento progresivo.

La infraestructura declarativa permite revisar y validar la política de conectividad sin depender exclusivamente del runtime.

Esta política complementa:
- ADR-0005 para desacoplamiento runtime,
- y ADR-0024 para endurecimiento contextual y principio de mínimo privilegio aplicado a contenedores.

## Consecuencias

Positivas:
- menor exposición innecesaria,
- mejor aislamiento entre stacks,
- mayor claridad arquitectónica,
- reducción de acoplamiento,
- mejora de auditabilidad.

Operativas:
- nuevos servicios deben declarar explícitamente sus redes,
- cambios de conectividad requieren actualización de Compose,
- redes compartidas deben justificarse arquitectónicamente.

Negativas:
- incremento moderado de complejidad declarativa,
- necesidad de mantenimiento explícito de topología de red.

## Validación

La validación debe realizarse mediante:
- revisión de Compose,
- inspección de redes Docker,
- validaciones CI sobre exposición de puertos y redes compartidas,
- revisión arquitectónica de nuevos stacks.

## Referencias

- ADR-0005 — Política de inicialización runtime e import-time.
- ADR-0024 — Política de excepciones de privilegios en contenedores.

## Estado

Aprobado.
