# ADR-0024 - Container Privilege Exception Policy

Fecha: 2026-05-09
Estado: Aprobado
Ámbito: server_monitoring_2509

## Contexto

El sistema de monitoring está basado en una arquitectura Docker IaC con separación en tres planos:

- Micro-stacks autónomos (servicios externos)
- Infra-stacks (runtime interno del sistema)
- Seguridad del host

Durante la evolución del modelo de seguridad runtime se aplicó el principio de mínimo privilegio de forma homogénea a todos los contenedores
Esto generó inconsistencias funcionales y falsos positivos de seguridad en contenedores basados en imágenes oficiales.

Se detectó que forzar UID != 0 de forma global:
- rompe compatibilidad funcional
- introduce hardening artificial
- mezcla responsabilidades entre código propio y dependencias externas

## Problema

El modelo anterior asumía:

- UID != 0 como requisito universal de seguridad

Consecuencias:
- Falsos positivos en CI (contenedores externos)
- Incompatibilidad con imágenes oficiales (Postgres, Promtail, Postfix)
- Sobrecarga innecesaria de hardening en servicios que no controlamos
- Confusión entre seguridad del código propio y comportamiento upstream

Especialmente en:
- postgres
- promtail
- smtp-relay

## Decisión

Se establece una política explícita de clasificación de contenedores:

## 3.1 Contenedores PROPIOS (control del proyecto)

- monitoring-python
- monitoring-cron

Reglas obligatorias:
- Deben ejecutarse con UID != 0
- Deben utilizar usuario no-root (ej: appuser)
- Está prohibido el uso de root en runtime
- Está prohibido el uso de:
    su
    sudo
    escaladas de privilegio
    chown runtime
- Toda ejecución debe ser reproducible mediante python3 -m <modulo>

## 3.2 Contenedores EXTERNOS / infra-trusted

Servicios:
- postgres (imagen oficial)
- smtp-relay (boky/postfix u otros upstream)
- promtail (grafana/promtail)

Reglas:
- Se permite UID = 0 si la imagen lo requiere funcionalmente
- No se fuerza cambio de usuario interno
- Deben ser tratados como dependencias infra-trusted
- Deben ser validados y documentados como excepción arquitectónica

## Principio

- El principio de mínimo privilegio es contextual, no absoluto
- La seguridad se aplica principalmente a código controlado por el proyecto
- Las dependencias externas deben respetarse funcionalmente
- Las excepciones deben ser explícitas, justificadas y auditables

## Controles Compensatorios

Para contenedores externos en root:
- Redes Docker aisladas por dominio funcional
- Evitar mounts sensibles en modo escritura
- Preferencia por :ro
- Uso de volúmenes explícitos
- Gestión controlada de secrets
- Exposición mínima de puertos

## Validación

La validación de privilegios debe realizarse en runtime mediante:

  docker exec <container> id -u

Reglas CI:
- Contenedores propios:
  FAIL si UID == 0
- Contenedores externos:
  WARN permitido
  Excepcion documentada

No se permite validación basada únicamente en:
- docker inspect .Config.User

## Consecuencias

Positivas:
- Eliminación de falsos positivos en CI
- Compatibilidad upstream con imágenes oficiales
- Separación clara de responsabilidad de seguridad
- Modelo más realista de seguridad en contenedores
- Coherencia arquitectónica
- CI más fiable

Negativas:
- Requiere documentación explícita de excepciones
- Introduce dualidad de tratamiento de seguridad

## Acciones obligatorias:

- test-security-runtime debe usar:
  docker exec <container> id -u

- los Dockerfiles propios deben:
    evitar chown recursivos
    evitar permisos runtime innecesarios

- los scripts host-only:
    no deben usar sudo embebido
    deben validar EUID

## Checklist de excepción aprobada

postgres:
- imagen oficial (`postgres:14.3`)
- excepción permitida; controlar a través de `ops/services/postgres/compose.yml` (volúmenes, init scripts, networks).

smtp-relay:
- `boky/postfix` (o equivalente)
- excepción permitida; exponer solo en `restricted-net`, mounts controlados y logs en volumen dedicado.

promtail:
- `grafana/promtail`
- excepción permitida; mounts `:ro` para `/var/log` y `/var/lib/docker/containers` y red de observabilidad.

## Seguimiento

El ADR debe actualizarse cuando:
- aparezcan nuevos contenedores privilegiados
- cambien políticas runtime
- se añadan nuevos controles compensatorios

## Nota Final
Este ADR corrige un exceso de generalización en el modelo de seguridad anterior, alineando el sistema con prácticas reales de seguridad en entornos Docker heterogéneos.
