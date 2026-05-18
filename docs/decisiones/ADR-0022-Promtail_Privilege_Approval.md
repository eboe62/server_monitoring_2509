# ADR-0022 — Promtail Privilege Approval

Fecha: 2026-05-08
Estado: Aprobado
Contexto: server_monitoring_2509

## Contexto

Promtail (Grafana Labs) se usa para la ingestión de logs desde el host y contenedores. En la configuración actual Promtail requiere acceso a:

- `/var/log` del host
- `/var/lib/docker/containers` (para leer logs de contenedores)

Estos mounts permiten a Promtail leer ficheros del host y de otros contenedores, lo que implica un nivel de confianza elevado en el componente que ejecuta Promtail.

## Problema

Montar paths host en un contenedor concede la capacidad de leer información sensible del host y hace que el contenedor de Promtail sea un punto de confianza crítica. Negar este acceso impediría la recopilación de logs en la forma actual.

## Decisión

Se aprueba (estado: Aprobado) permitir que Promtail monte los directorios necesarios para la captura de logs en la configuración de observabilidad, atendiendo la Recomendación 1. Esto implica aceptar el componente como parte del plano de infraestructura de confianza y gestionarlo con controles operativos más estrictos.

Recomendación aplicada (alcance limitado a Recomendación 1):

- Mantener exclusivamente los mounts necesarios para observabilidad defensiva:
  `/var/log` en modo solo lectura (`:ro`) para observación de eventos críticos del host
  `/var/lib/docker/containers` en modo solo lectura (`:ro`) para ingestión de logs Docker
El estado interno de Promtail (positions file) no debe persistirse sobre rutas del host y se almacena mediante volumen Docker explícito dedicado (`promtail-data`).
La arquitectura adopta un modelo híbrido:
  - observabilidad container-centric para servicios Docker
  - observabilidad host-centric para eventos de seguridad del sistema anfitrión
- Ejecutar Promtail en el stack de observabilidad (`observability-net`) como servicio de infraestructura (no como servicio de aplicación).
- Garantizar imagen firmada/consistente y usar versiones fijas (no `:latest`).
- Limitar recursos (CPU/mem) y ejecutar bajo cuentas kernel-namespaced y políticas de seccomp/APPArmor lo más restrictivas posibles.

## Consecuencias

Pros:

- Conservamos la capacidad de ingestión de logs completos y la correlación necesaria para observabilidad.
- Evita reescrituras grandes en la arquitectura de logging a corto plazo.

Contras:

- Promtail se considera un componente de alta confianza; cualquier vulnerabilidad en Promtail o en su configuración de mounts puede comprometer información host.
- Requiere controles operativos (actualizaciones, hardening) y revisiones periódicas.

## Mitigaciones operativas (resumen)

- Marcar Promtail como componente infra-trusted en inventario y playbooks.
- Aplicar mounts `:ro` siempre que sea posible (actual configuración ya usa `:ro` en contenedores de logs).
- Mantener una política de actualización y escaneo de vulnerabilidades para la imagen Promtail.
- Registrar y auditar cambios en la configuración de Promtail.

## Relación con otros ADR

- ADR-0021 — Network Segmentation Strategy: Promtail queda en `observability-net` (coherente con la segmentación).
- ADR-0020 — Container Execution Model Privilege Strategy: refuerza la necesidad de delimitar componentes privilegiados.
- ADR-0018 — Docker security runtime and resilience requirements: se complementa con mitigaciones runtime.

## Estado

Aprobado
