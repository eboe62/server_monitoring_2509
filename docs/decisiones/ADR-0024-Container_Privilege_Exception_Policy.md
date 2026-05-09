# ADR-0024 - Container Privilege Exception Policy

Fecha: 2026-05-09
Estado: Propuesto / Aprobado (pendiente de integración en CI)
Ámbito: server_monitoring_2509

## Contexto

El sistema de monitoring está basado en una arquitectura Docker IaC con separación en tres planos:

- Micro-stacks autónomos (servicios externos)
- Infra-stacks (runtime interno del sistema)
- Seguridad del host

Durante la evolución del modelo de seguridad runtime se ha aplicado el principio de mínimo privilegio de forma uniforme a todos los contenedores, lo cual ha generado inconsistencias funcionales y validaciones incorrectas en contenedores basados en imágenes oficiales.

Se ha detectado que forzar UID != 0 de forma global introduce falsos supuestos de seguridad y rompe la compatibilidad con imágenes upstream que requieren root para su funcionamiento interno.

## Problema

El modelo anterior asumía:

- UID != 0 como requisito universal de seguridad

Esto genera los siguientes problemas:

- Falsos positivos en contenedores externos
- Incompatibilidad con imágenes oficiales (Postgres, Promtail, Postfix)
- Sobrecarga innecesaria de hardening en servicios que no controlamos
- Confusión entre seguridad del código propio y comportamiento upstream

## Decisión

Se establece una política explícita de clasificación de contenedores:

## 3.1 Contenedores PROPIOS (control del proyecto)

- monitoring-python
- monitoring-cron

Reglas obligatorias:
- Deben ejecutarse con UID != 0
- Deben utilizar usuario no-root (ej: appuser)
- Está prohibido el uso de root en runtime
- Está prohibido el uso de su, sudo o escaladas de privilegio
- Toda ejecución debe ser reproducible mediante python3 -m <modulo>

## 3.2 Contenedores EXTERNOS / infra-trusted

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
- Uso de volúmenes explícitos
- Evitar mounts sensibles en modo escritura
- Gestión controlada de secrets
- Exposición mínima de puertos

## Validación

La validación de privilegios debe realizarse en runtime mediante:

  docker exec <container> id -u

Reglas CI:
- Contenedores propios:
  FAIL si UID == 0
- Contenedores externos:
  WARN o EXCEPTION documentada

No se permite validación basada únicamente en:
- docker inspect .Config.User

## Consecuencias

Positivas:
- Eliminación de falsos positivos en CI
- Compatibilidad con imágenes oficiales
- Separación clara de responsabilidad de seguridad
- Modelo más realista de seguridad en contenedores

Negativas:
- Requiere documentación explícita de excepciones
- Introduce dualidad de tratamiento de seguridad

## Estado

Propuesto para integración inmediata en:
- CI/CD pipeline
- test-security-runtime
- documentación ADR principal del proyecto

## Acciones recomendadas (implementación inmediata)

- Actualizar `test-security-runtime` para usar `docker exec <container> id -u` y fallar si los contenedores propios ejecutan con UID 0. (Hecho: Makefile actualizado)
- Añadir en CI una fase que documente excepciones (contener la lista de imágenes infra-trusted) y publique un pequeño informe cuando haya diferencias.
- Revisar Dockerfiles propios para minimizar `chown` recursivos en build-time y limitar ajustes de ownership únicamente a directorios que requieran escritura en runtime (logs, runtime secrets). (Hecho: Dockerfiles actualizados)
- Eliminar uso de `sudo` embebido en scripts de auditoría y dejar checks host-only (advertir si no se ejecuta como root). (Hecho: `ops/audit/audit_repo_host.sh` actualizado)
- Registrar en el ADR la lista de contenedores permitidos en root y los controles compensatorios (redes, mounts `:ro`, secrets gestionados).

## Checklist de excepción aprobada

- `postgres` → imagen oficial (`postgres:14.3`) — excepción permitida; controlar a través de `ops/services/postgres/compose.yml` (volúmenes, init scripts, networks).
- `smtp-relay` → `boky/postfix` (o equivalente) — excepción permitida; exponer solo en `restricted-net`, mounts controlados y logs en volumen dedicado.
- `promtail` → `grafana/promtail` — excepción permitida; mounts `:ro` para `/var/log` y `/var/lib/docker/containers` y red de observabilidad.

## Seguimiento

- Integrar validación en CI que falle para contenedores propios ejecutando como root y que genere WARN para contenedores externos que ejecuten como root sin ADR documentado.
- Mantener ADR actualizado con nuevas excepciones y su justificación técnica.

## Nota Final
Este ADR corrige un exceso de generalización en el modelo de seguridad anterior, alineando el sistema con prácticas reales de seguridad en entornos Docker heterogéneos.
