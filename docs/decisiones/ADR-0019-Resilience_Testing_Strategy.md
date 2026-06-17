# ADR-0019 — Resilience Testing Strategy

Status: APPROVED
Date: 2026-04-25
Decision Type: REVIEW_REQUIRED
Scope: Runtime
Category: TESTING
Tags: REVIEW_REQUIRED
Related ADRs: ADR-0017
Supersedes: NONE
Superseded By: NONE
Validation Reference: NONE

## Contexto

Durante la implementación de tests de resiliencia en CI se han observado comportamientos no deterministas al simular fallos reales de red mediante:

docker network disconnect

Problemas detectados:
- conexiones TCP persistentes (keep-alive)
- caché DNS interna de Docker
- latencias del runtime en CI
- diferencias entre entorno local y CI

Esto provocó múltiples falsos negativos en pipeline.

Adicionalmente, se detectó acoplamiento indebido entre:
- bind mounts del host
- permisos de contenedores (USER no root)
- rutas de logs dependientes del host (/var/log montado desde host)

Esto rompía el principio de separación entre:
- runtime funcional containerizado
- control-plane operacional host-side

definido por el modelo IaC actual.

## Decisión
Se separa la estrategia de testing en dos niveles:

### 1. CI (determinista)
Se implementa:
    test-resilience-network-ci

Basado en:
- desconexión controlada de red Docker
- validación mediante healthchecks internos

NO se valida conectividad TCP real.

Objetivo:
- determinismo
- estabilidad en pipeline

### 2. Local / Staging (real)
Se implementa:
    test-resilience-network-real

Basado en:
- aislamiento real de red
- validación TCP (nc)
- simulación de fallos reales

Uso limitado a entornos controlados.

### Principio clave

Los tests de resiliencia NO deben depender de:
- bind mounts del host
- rutas del sistema (/var/log)
- comportamiento no determinista del runtime Docker

### Logs
Se elimina dependencia de:
    /var/log (host)

Se adopta:
    /opt/monitoring/logs

Motivo:
- coherencia con el modelo IaC híbrido actual
- separación funcional host/runtime
- reducción de dependencias host-side funcionales
- reproducibilidad operacional razonable

## Consecuencias
- CI más estable y determinista
- coherencia con modelo IaC
- aislamiento completo
- independencia del host
- reproducibilidad total

## Estado
Adoptado
