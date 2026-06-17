# ADR-0024 — Container Privilege Exception Policy (Mínimo privilegio contextual)

Status: APPROVED
Date: 2026-05-09
Decision Type: REVIEW_REQUIRED
Scope: Runtime
Category: SECURITY
Tags: REVIEW_REQUIRED
Related ADRs: ADR-0020, ADR-0018
Supersedes: NONE
Superseded By: NONE
Validation Reference: NONE

## Contexto

La plataforma utiliza una arquitectura Docker IaC organizada en:
- micro-stacks autónomos,
- infra-stacks internos,
- controles de seguridad host.

Durante el endurecimiento del runtime se aplicó inicialmente una política homogénea basada en:
- ejecución obligatoria con UID != 0,
- eliminación generalizada de privilegios.

La experiencia operativa demostró que este enfoque generaba incompatibilidades funcionales y falsos positivos de seguridad en imágenes oficiales externas.

Se detectó especialmente en:
- postgres,
- promtail,
- smtp-relay.

## Problema

El modelo anterior asumía que ejecutar contenedores como non-root era un requisito universal.

Consecuencias:
- incompatibilidad con imágenes oficiales,
- hardening artificial sobre componentes externos,
- falsos positivos en CI,
- confusión entre seguridad del código propio y comportamiento upstream.

La plataforma necesitaba diferenciar:
- contenedores desarrollados y controlados por el proyecto,
- dependencias externas consideradas infra-trusted.

## Decisión

Se establece una clasificación explícita de contenedores.

### 1. Contenedores propios

Ejemplos:
- monitoring-python
- monitoring-cron

Reglas obligatorias:
- ejecución con UID != 0,
- uso de usuario non-root,
- prohibido root en runtime,
- prohibido:
  - sudo,
  - su,
  - escaladas de privilegio,
  - chown runtime innecesarios,
- ejecución reproducible mediante:
  python3 -m <modulo>

La ausencia de:
- docker.sock
- docker CLI
- docker compose

en:
    monitoring-python

se considera medida de hardening válida y alineada con minimización de privilegios.

Las validaciones estructuradas deberán soportar degradación explícita cuando el runtime no disponga de capacidades Docker host-level.

### 2. Contenedores externos / infra-trusted

Ejemplos:
- postgres,
- smtp-relay,
- promtail.

Reglas:
- se permite UID = 0 si la imagen lo requiere,
- no se fuerza modificación del usuario interno,
- deben tratarse como dependencias infra-trusted,
- las excepciones deben quedar documentadas y auditables.

## Principio

El principio de mínimo privilegio debe aplicarse de forma contextual y proporcional al nivel de control sobre cada contenedor.

La política de endurecimiento se aplica prioritariamente al código controlado por el proyecto.

Las dependencias externas deben mantener compatibilidad funcional con sus imágenes oficiales, utilizando controles compensatorios cuando sea necesario.

## Controles compensatorios

Para contenedores externos ejecutados como root:
- redes Docker aisladas,
- exposición mínima de puertos,
- mounts preferentemente read-only,
- volúmenes explícitos,
- acceso restringido a credenciales SMTP y otros secretos operativos,
- separación funcional entre stacks.

## Validación

La validación de privilegios debe realizarse en runtime mediante:

  docker exec <container> id -u

Reglas CI:
- contenedores propios:
  FAIL si UID == 0
- contenedores externos:
  WARN permitido con excepción documentada

No se considera suficiente:
- docker inspect .Config.User

## Consecuencias

Positivas:
- reducción de falsos positivos,
- compatibilidad con imágenes oficiales,
- separación clara de responsabilidades,
- CI más fiable,
- modelo de seguridad más coherente.

Operativas:
- las excepciones deben documentarse,
- nuevos contenedores privilegiados requieren revisión explícita.

## Acciones obligatorias

- test-security-runtime debe validar UID efectivo mediante docker exec,
- los Dockerfiles propios deben evitar cambios de permisos innecesarios,
- los scripts host-only no deben usar sudo embebido y deben validar EUID.

## Excepciones aprobadas

postgres:
- imagen oficial postgres,
- excepción permitida,
- control mediante compose y volúmenes explícitos.

smtp-relay:
- postfix upstream,
- excepción permitida,
- exposición restringida y mounts controlados.

promtail:
- imagen oficial grafana/promtail,
- excepción permitida,
- mounts read-only para logs y runtime Docker.

## Seguimiento

Este ADR debe revisarse cuando:
- se añadan nuevos contenedores privilegiados,
- cambien las políticas runtime,
- se incorporen nuevos controles compensatorios.

## Referencias

- ADR-0005 — Runtime desacoplado y lazy imports
- ADR-0020 — Container Execution Model & Privilege Strategy
- ADR-0025 — Modelo SMTP explícito y endurecimiento de configuración
