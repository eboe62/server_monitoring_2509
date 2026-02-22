ADR-0008 – Clasificación de servicios: Micro-stack vs Infraestructura Operativa

Fecha: 2026-02-17
Estado: Propuesto
Contexto: Migración PRO server_monitoring_2602 – Clarificación del modelo arquitectónico

## Contexto
Durante la FASE 4 se adopta el modelo “micro-stack autónomo con red compartida”.
Sin embargo, en la implementación actual coexisten dos tipos de despliegue:
- Servicios ubicados en:
    ops/services/<servicio>/
    (ej. smtp_relay)
- Infra-stacks (infraestructura operativa): Stacks agregados definidos en:
    ops/docker/
    (cron, python runner, postgres, observability)
La documentación inicial de FASE 4 no distingue formalmente ambas categorías, generando ambigüedad sobre qué componentes deben cumplir estrictamente el modelo micro-stack autónomo.
Se requiere una clasificación explícita para mantener coherencia arquitectónica.

## Decisión
Se definen dos categorías formales de despliegue:

1️⃣ Micro-stack Autónomo
Ubicación:
  ops/services/<servicio>/

Debe cumplir obligatoriamente:
- Dockerfile propio
- docker-compose.yaml propio
- build independiente (contexto acotado al servicio)
- no depender de archivos fuera del directorio del servicio
- no montar rutas absolutas del host como dependencia estructural
- no versionar secrets
- no incluir secrets ni .env en la imagen
- declarar monitoring-net como external: true

Objetivo:
Permitir que el servicio pueda copiarse a otro repositorio y desplegarse de forma independiente.

2️⃣ Stack de Infraestructura Operativa
Ubicación:
  ops/docker/

Incluye:
- cron
- python runner
- postgres (si se mantiene agregado)
- observability

Puede:
- usar build context superior
- montar rutas del host justificadas
- acceder a /var/run/docker.sock
- acceder a logs del host

Debe:
- declarar monitoring-net como external: true
- no versionar secrets
- no incluir secrets dentro de la imagen
- no introducir dependencias implícitas no documentadas

Objetivo:
  Proveer capacidades operativas del entorno, no servicios exportables.

## Justificación
- No todos los contenedores tienen naturaleza exportable.
- Forzar infraestructura operativa a modelo micro-stack incrementa complejidad sin beneficio claro.
- La separación explícita evita ambigüedades futuras.
- Permite mantener rigor arquitectónico sin sobredimensionar el sistema.

## Consecuencias
- FASE 4 aplica estrictamente solo a micro-stacks autónomos.
- Los stacks operativos quedan formalmente fuera del requisito de portabilidad.
- Se mejora la coherencia documental.
- Se evita refactorización innecesaria.

## Riesgos controlado
- Que infraestructura operativa crezca sin gobernanza.
- Que se mezclen responsabilidades entre categorías.
- Que en el futuro se requiera convertir un stack operativo en micro-stack (deberá evaluarse caso a caso).

## Fuera de alcance:
- No se obliga a migrar postgres a micro-stack.
- No se reestructura el repositorio.
- No se modifica ADR-0006.
- No se introduce nuevo orquestador.

## Estado
Propuesto.
