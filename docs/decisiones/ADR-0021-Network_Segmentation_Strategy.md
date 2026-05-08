# ADR-0021 — Network Segmentation Strategy

Fecha: 2026-05-04
Estado: Aprobado
Contexto: server_monitoring

Nota: Durante la migración de la plataforma la red histórica `monitoring-net` se ha sustituido por un conjunto de redes segmentadas: `backend-net`, `observability-net` y `restricted-net`. Este documento refleja la estrategia y la transición.

## Contexto

Actualmente, todos los contenedores del sistema comparten una única red Docker:

monitoring-net

Este enfoque simplifica la conectividad pero introduce problemas críticos:
- comunicación lateral no restringida entre servicios
- imposibilidad de aislar dominios funcionales
- incremento de superficie de ataque
- inviabilidad de escenarios de análisis forense controlado
- dificultad para reutilizar la infraestructura en otros contextos

Este modelo entra en conflicto con:
- ADR-0008 (separación micro-stack vs infra-stack)
- ADR-0020 (separación por propósito y privilegios)
- objetivos del sistema:
  - despliegue de servicios
  - análisis de vulnerabilidades
  - entornos controlados y reproducibles

## Decisión
Se adopta un modelo de segmentación de red basado en dominios funcionales.
Se reemplaza el uso de una única red global por múltiples redes especializadas.

## Modelo de redes

Se definen las siguientes redes:

### 1. backend-net
Uso:
- comunicación entre servicios internos de negocio

Ejemplos:
- monitoring-cron → postgres
- monitoring-python → postgres

Características:
- acceso restringido a servicios backend
- no exposición externa
- no accesible desde contenedores de observabilidad

### 2. observability-net
Uso:
- ingestión y visualización de logs

Ejemplos:
- promtail → loki
- grafana → loki

Características:
- acceso limitado a stack de observabilidad
- no acceso directo a bases de datos
- desacoplado del backend

### 3. restricted-net
Uso:
- contenedores sensibles o entornos controlados

Ejemplos:
- análisis forense
- sandbox de vulnerabilidades
- servicios potencialmente comprometidos

Características:
- aislamiento fuerte
- sin acceso a otras redes salvo configuración explícita
- ideal para ejecución de cargas no confiables

### 4. edge-net (opcional)
Uso:
- exposición controlada hacia el exterior

Ejemplos:
- grafana (si se expone)
- reverse proxy

Características:
- único punto de entrada/salida
- control de puertos
- puede estar limitado a 127.0.0.1 o VPN

## Reglas de conexión
1. Principio de mínimo acceso
Un contenedor solo puede estar conectado a las redes estrictamente necesarias.

2. Prohibición de red global
No se permite el uso de una red única compartida por todos los servicios.

3. Conexiones explícitas
Toda comunicación entre servicios debe estar definida explícitamente mediante redes compartidas.

4. Aislamiento por defecto

Los nuevos servicios deben:
- empezar sin acceso a otras redes
- añadir conectividad solo si es necesario

## Ejemplo de aplicación

ANTES:

monitoring-cron → monitoring-net
postgres → monitoring-net
grafana → monitoring-net

DESPUÉS:

monitoring-cron → backend-net
postgres → backend-net

promtail → observability-net
loki → observability-net
grafana → observability-net + edge-net (opcional)

## Validación
Se deben implementar tests específicos:
- test-aislamiento-red
- test-arranque-desordenado
- test-dependencias-host

Validaciones esperadas:
- un contenedor no puede resolver ni conectar a servicios fuera de su red
- fallos de red no afectan a dominios no relacionados
- la observabilidad sigue funcionando sin acceso al backend

## Consecuencias
Positivas:
- reducción significativa de superficie de ataque
- eliminación de movimiento lateral entre servicios
- mejora de aislamiento para análisis forense
- mayor reutilización de la infraestructura
- alineación con arquitectura por dominios

Negativas:
- incremento de complejidad en docker-compose
- necesidad de definir correctamente dependencias
- posible refactor de configuraciones existentes

## Relación con otros ADR
- ADR-0008 (micro-stack vs infra-stack)
  → se refuerza el aislamiento entre dominios
- ADR-0014 / ADR-0015 (exposición de servicios)
  → edge-net centraliza exposición
- ADR-0018 (seguridad runtime)
  → segmentación reduce superficie de ataque
- ADR-0019 (resilience testing)
  → permite tests más realistas de fallo de red
- ADR-0020 (container execution model)
  → separación por propósito se refleja en red

## Estado
Adoptado
