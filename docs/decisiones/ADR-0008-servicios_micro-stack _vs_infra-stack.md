# ADR-0008 – Clasificación de servicios: Micro-stack vs Infraestructura Operativa

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
- docker-compose.yml propio
- build independiente (contexto acotado al servicio)
- no depender de archivos fuera del directorio del servicio
- no depender de imágenes base internas del repositorio
- solo se permite el uso de imágenes base oficiales externas versionadas (ej. python:3.12-slim)
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
- usar build context superior (solo para acceso a código del repositorio)
- no definir imágenes base reutilizables por otros stacks
- montar rutas del host justificadas
- acceder a /var/run/docker.sock
- acceder a logs del host

Debe:
- declarar monitoring-net como external: true
- no versionar secrets
- no incluir secrets dentro de la imagen
- no introducir dependencias implícitas no documentadas

- documentar explícitamente:
  - uso de docker.sock (si aplica)
  - montajes de rutas del host
  - dependencias del host necesarias

- ser auditable mediante scripts automatizados (FASE 4/5)

Objetivo:
  Proveer capacidades operativas del entorno, no servicios exportables.

3️⃣ Uso de docker.sock
Los infra-stacks pueden montar:
  /var/run/docker.sock:/var/run/docker.sock

Únicamente cuando sea estrictamente necesario para capacidades de infraestructura (inspección, control del runtime o automatización declarativa).

RIESGO:
El acceso a docker.sock concede privilegios equivalentes a root sobre el host Docker, permitiendo:
- creación/eliminación de contenedores
- acceso a volúmenes
- ejecución arbitraria en el host

MITIGACIONES OBLIGATORIAS:

1) Alcance
- Exclusivo de infra-stacks (ops/docker/)
- Prohibido en micro-stacks (ops/services/)

2) Aislamiento
- Contenedor sin exposición de puertos
- No accesible desde el exterior (solo red interna Docker)

3) Control de ejecución
- No ejecutar código dinámico o no auditado dentro del contenedor
- Scripts versionados y revisados en repositorio

4) Principio de mínimo privilegio (reforzado)
- user != root cuando sea posible
- read_only: true cuando sea viable
- cap_drop: ALL (añadir solo las necesarias si aplica)

5) Trazabilidad
- Toda operación que use docker.sock debe quedar registrada en logs

6) Auditoría
- Debe existir comprobación automática (audit script) que detecte:
  - uso de docker.sock
  - contenedores que lo montan

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

## Riesgos controlados
- Crecimiento de infra-stacks con privilegios elevados (docker.sock, mounts host)
- Compromiso del host si un contenedor con docker.sock es vulnerado
- Mezcla de responsabilidades entre micro-stack e infra-stack
- Dependencias implícitas del host no documentadas

Controles:
- Auditoría automática (FASE 4/5)
- Restricción de exposición de red
- Revisión obligatoria de ADR para cualquier excepción

## Fuera de alcance:
- No se obliga a migrar postgres a micro-stack.
- No se reestructura el repositorio.
- No se modifica ADR-0006.
- No se introduce nuevo orquestador.

## Estado
Aprobado.
