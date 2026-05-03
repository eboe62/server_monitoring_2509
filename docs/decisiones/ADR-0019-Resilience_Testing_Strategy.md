# ADR-0019 — Resilience Testing Strategy

Fecha: 2026-04-25
Estado: Aprobado
Contexto: server_monitoring

## Contexto

Durante la implementación de tests de resiliencia en CI se han observado
comportamientos no deterministas al simular fallos reales de red mediante:

    docker network disconnect

Problemas detectados:
- conexiones TCP persistentes (keep-alive)
- caché DNS interna de Docker
- latencias del runtime en CI
- diferencias entre entorno local y CI

Esto provocó múltiples falsos negativos en pipeline.

Adicionalmente, se detectó un acoplamiento entre:
- permisos de contenedores (USER no root)
- escritura de logs en /var/log (montado desde host)

Esto rompía los tests de observabilidad al no poder escribir logs.

## Decisión
Se separa la estrategia de testing en dos niveles:

### 1. CI (determinista)
Se implementa:
    test-resilience-network-ci

Basado en:
- desconexión controlada
- validación vía healthchecks

NO se valida conectividad TCP real.

### 2. Local / Staging (real)
Se implementa:
    test-resilience-network-real

Basado en:
- aislamiento real de red
- validación TCP (nc)

Uso limitado a entornos controlados.

### Logs
Se elimina dependencia de:
    /var/log (host)

Se adopta:
    /opt/monitoring/logs

Motivo:
- control total de permisos
- evitar interferencia de volúmenes
- compatibilidad con USER no root

## Consecuencias
- CI más estable y determinista
- reducción de falsos negativos
- separación clara entre testing funcional y testing realista
- mejora de seguridad (no root viable)

## Estado
Adoptado
