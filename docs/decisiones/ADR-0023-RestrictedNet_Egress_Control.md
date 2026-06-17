# ADR-0023 — Egress Control for restricted-net (Propuesto)

Status: APPROVED
Date: 2026-05-08
Decision Type: REVIEW_REQUIRED
Scope: Infrastructure
Tags: REVIEW_REQUIRED
Related ADRs: ADR-0021
Supersedes: NONE
Superseded By: NONE
Validation Reference: NONE

## Contexto

El objetivo de `restricted-net` es alojar contenedores o cargas con confianza reducida o entornos de análisis forense/sandbox. Por defecto Docker permite egress (salida) desde contenedores a Internet, lo que deja una vía de exfiltración y comunicación no controlada.

## Problema

Sin controles de egress, un contenedor comprometido en `restricted-net` puede establecer conexiones salientes hacia Internet u otras redes, exponiendo datos o recibiendo instrucciones de control remoto.

## Propuesta / Decisión (Propuesto)

Se propone aplicar un modelo de egress-control basado en defensa en profundidad con las siguientes medidas recomendadas:

1) Default-deny a egress para `restricted-net` a nivel host
- Implementar reglas de firewall (iptables/nftables) que bloqueen todo tráfico saliente desde las interfaces Docker asociadas a `restricted-net`, salvo excepciones explícitas.

2) Egress proxy centralizado (recomendado)
- Provisionar un `egress-proxy` (HTTP/HTTPS/TCP) en `edge-net` o en un host dedicado.
- Todos los contenedores de `restricted-net` con permiso de salida deben usar el proxy para acceder a recursos externos (configurar variables `HTTP_PROXY/HTTPS_PROXY` y reglas transparentes si procede).
- El proxy permite inspección, filtrado de dominios y registro de solicitudes salientes.

3) Reglas de excepción (white-list)
- Mantener una lista mínima de destinos autorizados (IPs, FQDN) y puertos para usos operativos (actualizaciones controladas, DNS, servicios internos).
- Registrar y revisar cambios en la lista.

4) Telemetría y bloqueo granulado
- Integrar logs del proxy con la plataforma de observabilidad (Loki) para auditoría.
- Rechazar o saturar conexiones no autorizadas y generar alertas.

5) Controles de mitigación local
- Usar userland proxies ligeros (p. ej. `squid`, `tinyproxy`, `envoy`) para casos específicos.
- En entornos donde no sea posible un proxy, aplicar reglas eBPF/iptables que limiten IPs y puertos.

## Argumentos a favor

- Reduce vector de exfiltración y comando-control.
- Facilita auditoría de tráfico saliente y detección temprana.
- Centraliza la política de salida y permite aplicar controles de seguridad (filtrado, autenticación, TLS inspection si procede).

## Costes y consecuencias

- Aumento de complejidad operativa (gestión del proxy y de listas de permisos).
- Latencia potencial y puntos únicos de fallo (mitigable con alta disponibilidad para el proxy).
- Requiere planificación para actualizaciones de contenedores y repositorios de imágenes (excluyendo hosts de actualización autorizados).

## Recomendación operativa

- Implementar primero un proxy de egress en modo observabilidad (registro/log-only) para monitorizar el impacto.
- Tras un periodo de validación, aplicar default-deny y promover excepciones justificadas.
- Automatizar la gestión de reglas (infra-as-code) y documentar el runbook de emergencia.

## Pruebas sugeridas (alta nivel)

- Test de conectividad controlada: levantar un contenedor en `restricted-net` y validar que sólo puede acceder a destinos permitidos a través del proxy.
- Test de bypass: intentar conexiones directas (no-proxy) y comprobar bloqueo y registros.

## Relación con otros ADR

- ADR-0021: segmentación de redes — `restricted-net` forma parte de la estrategia.
- ADR-0020 / ADR-0018: ejecución y hardening — complementa políticas de runtime.

## Estado

Propuesto
