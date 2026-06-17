# ADR-0801: Estrategia de Empaquetado y Despliegue con Contenedores Docker

Status: APPROVED
Date: 2026-06-11
Decision Type: REVIEW_REQUIRED
Scope: Infrastructure
Category: DEPLOYMENT
Tags: REVIEW_REQUIRED
Related ADRs: ADR-0602, ADR-0802
Supersedes: NONE
Superseded By: NONE
Validation Reference: NONE

## Contexto
En un Monorrepo Maven Multi-Module con microservicios independientes, es necesario definir una estrategia de empaquetado y despliegue que garantice consistencia, eficiencia y portabilidad. Actualmente, no se han establecido lineamientos claros sobre cómo se deben construir y desplegar los contenedores Docker para cada microservicio.

## Decisión
Adoptar una estrategia de empaquetado basada en los siguientes principios:
1. **Dockerfiles Independientes:** Cada módulo Maven tendrá su propio Dockerfile, ubicado en la raíz del módulo.
2. **Builds Multi-Etapa:** Se utilizarán builds multi-etapa para optimizar el tamaño de las imágenes y mejorar la seguridad.
3. **Etiquetado Consistente:** Las imágenes Docker deberán seguir un esquema de etiquetado consistente que incluya el número de versión del servicio y el entorno de despliegue.
4. **Orquestación:** Se utilizarán herramientas de orquestación (ej. Kubernetes) para gestionar el despliegue de los contenedores.

## Consecuencias

### Positivas (+)
- Garantiza consistencia y portabilidad en los despliegues.
- Optimiza el tamaño de las imágenes Docker, reduciendo el tiempo de despliegue.
- Facilita la gestión de múltiples servicios en entornos distribuidos.

### Negativas (-)
- Requiere un esfuerzo inicial para configurar y mantener los Dockerfiles.
- Introduce complejidad en la gestión de múltiples imágenes y su orquestación.
