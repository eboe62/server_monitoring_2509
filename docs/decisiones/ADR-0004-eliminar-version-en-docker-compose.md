# ADR-004 - Eliminación del atributo version en docker-compose (Docker Compose v2)

Fecha: 2026-01-27
Estado: Aprobado
Contexto: Migración IaC server_monitoring_2509

## Contexto

El proyecto server_monitoring utiliza múltiples ficheros docker-compose
distribuidos en distintos subdirectorios (ops/docker, ops/services, etc.).

Al ejecutar comandos como `docker-compose ps` o `make status` en entornos
actuales, se detecta el uso de Docker Compose v2 (plugin `docker compose`),
que emite warnings cuando los ficheros docker-compose incluyen el atributo
`version`.

Ejemplo de warning observado:

  "the attribute `version` is obsolete, it will be ignored"

Aunque este warning no impide la ejecución, introduce ruido operativo,
confusión durante la validación y dificulta la lectura de logs y salidas
automatizadas.

Los ficheros afectados identificados actualmente son:

- ops/stacks/cron/compose.yml
- ops/stacks/observability/compose.yml
- ops/stacks/python/compose.yml
- ops/services/smtp_relay/compose.yml
- ops/services/postgres/compose.yml

## Decisión

Se decide eliminar el atributo `version` de todos los ficheros docker-compose
del proyecto.

A partir de este ADR:
- No se incluirá `version:` en nuevos docker-compose
- Los docker-compose existentes deberán migrarse eliminando dicho atributo
- El esquema será detectado automáticamente por Docker Compose v2

Esta decisión asume explícitamente Docker Compose v2 como estándar del proyecto.

## Consecuencias

Positivas:
- Eliminación de warnings en tiempo de ejecución
- Configuración alineada con el estándar actual de Docker
- Ficheros docker-compose más simples y claros
- Mejor experiencia en CI/CD y automatizaciones (Makefile)

Negativas:
- Pérdida de compatibilidad explícita con Docker Compose v1 (asumido como aceptable)

# Alternativas consideradas

1. Mantener `version` y aceptar los warnings
   - Rechazada por introducir ruido y deuda técnica

2. Forzar uso de Docker Compose v1
   - Rechazada por ir en contra de la evolución natural del stack

# Notas

Tras aplicar esta decisión, se ha validado que comandos como:
  make status
  docker-compose ps

funcionan correctamente sin warnings ni errores.

Esta decisión afecta a múltiples docker-compose y debe aplicarse de forma consistente en todo el repositorio.

## Estado

Aceptado.
