# ADR-0006 – Gobernanza de imagen base monitoring-base (Rechazado)

Status: DEPRECATED
Date: 2026-05-04
Decision Type: REVIEW_REQUIRED
Scope: Infrastructure
Tags: REVIEW_REQUIRED
Related ADRs: NONE
Supersedes: NONE
Superseded By: NONE
Validation Reference: NONE

## Contexto
Durante la definición del entorno PRO 260214 se adopta el modelo: “micro-stack autónomo con red compartida”.
Cada servicio debe poder:
- Construirse de forma independiente
- Desplegarse sin dependencias implícitas
- Ser trasladado a otro repositorio si fuera necesario
- Evaluación de alternativa descartada

Se evaluó la posibilidad de mantener una imagen base común denominada monitoring-base con los siguientes objetivos:
- Reducir duplicación de dependencias
- Estandarizar runtime Python
- Optimizar tiempos de build
- Garantizar coherencia de entorno
Sin embargo, esta aproximación introduce un riesgo estructural de acoplamiento, especialmente en ausencia de un sistema de gobernanza estricta y verificable.

Condiciones teóricas de implementación (no adoptadas)

En caso de haberse implementado, la imagen base debería haber cumplido:
- Uso de versiones explícitas (prohibido :latest)
- Superficie de ataque mínima (paquetes estrictamente necesarios)
- Ausencia de herramientas de debug en producción
- Separación total de configuración y secrets

## Decisión
Se rechaza completamente el uso de una imagen base compartida (monitoring-base), incluso en el caso de cumplir condiciones estrictas de diseño.

El rechazo aplica aunque la imagen:
- Contenga únicamente runtime común (Python y librerías compartidas)
- Incluya código fuente versionado del proyecto
- Se limite a dependencias declaradas en requirements.txt
- Mantenga configuración genérica no específica de servicio

También se rechaza aunque cumpla las siguientes garantías:
- Restricciones teóricas (no suficientes para su adopción)
- Ausencia de secrets y archivos .env
- No inclusión de configuración específica de servicios
- No ejecución de lógica dependiente de entorno en build-time
- Cumplimiento del principio de reemplazabilidad

Aunque cada servicio pudiera:
- Extender directamente una imagen oficial (python:slim, etc.)
- Sustituir monitoring-base sin romper la arquitectura

Se considera que esto no elimina el riesgo de acoplamiento estructural en la práctica.

Centralización de estado

Se rechaza incluso aunque no tenga centralización de estado:
- Ningún volumen ni dato persistente depende de la imagen base.
- El estado siempre reside en volúmenes declarados por servicio.
La existencia de una imagen base común seguiría introduciendo dependencia en fase de build.

## Consecuencias
Se acepta explícitamente la pérdida de las siguientes ventajas:
- Mayor duplicación de dependencias entre servicios
- Menor eficiencia en tiempos de build
- Menor reutilización de capas Docker
- Posible incremento del tamaño total de imágenes

Estas desventajas se consideran asumibles en favor de: aislamiento, reproducibilidad y coherencia con el modelo IaC PRO.

## Riesgos
Se identifican como riesgos estructurales:
- Crecimiento progresivo de responsabilidad de la imagen base
- Introducción de configuración específica (acoplamiento oculto)
- Dependencia implícita entre servicios en fase de build
- Dificultad de validación independiente en CI/CD
- Riesgo de convertir la imagen en dependencia no reemplazable

Estos riesgos se consideran críticos y suficientes para justificar su no adopción.

## Fuera de alcance:
- No se redefine la estructura de servicios.
- No se introduce pipeline de build automatizado.
- No se modifica el modelo de red compartida.
- No se altera la política de secrets.

## Estado
Rechazado.
