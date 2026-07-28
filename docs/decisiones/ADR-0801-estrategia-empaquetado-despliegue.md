# ADR-0801: Estrategia de Empaquetado y Despliegue con Contenedores Docker

Status: APPROVED
Date: 2026-06-11 (revisado 2026-07-16 para reflejar la implementación real vigente en el backend GDA)
Scope: Infrastructure
Category: DEPLOYMENT
Tags: REVIEW_REQUIRED
Related ADRs: ADR-0602, ADR-0802
Supersedes: NONE
Superseded By: NONE
Validation Reference: NONE

## Contexto
En un Monorrepo Maven Multi-Module con microservicios independientes, es necesario definir una estrategia de empaquetado y despliegue. Este ADR se ha revisado tras verificar que ningún módulo del backend GDA (incluido `gda-finance/gda-admingade`, que aloja Guards) tiene actualmente un `Dockerfile`, y que su pipeline de CI (`.gitlab-ci.yml`) no realiza build ni publicación de imágenes Docker.

## Decisión
Adoptar como estrategia vigente el empaquetado como artefacto Maven ejecutable (JAR Spring Boot) con versionado y release gestionados por CI, en lugar de la contenerización Docker por módulo originalmente propuesta:

1. **Empaquetado como JAR ejecutable:** cada módulo (`packaging: jar` + `spring-boot-maven-plugin`) se empaqueta como un JAR autocontenido ejecutable con `java -jar`, sin Dockerfile propio.
2. **Versionado y release vía GitLab CI:** el pipeline (`stage: release`, disparo manual sobre `master`) retira el sufijo `-SNAPSHOT`, etiqueta la versión (`git tag`), publica a `master` y sube automáticamente la versión `minor` en `develop`. No incluye pasos de `docker build` ni publicación a un registry de imágenes.
3. **Sin builds multi-etapa por ahora:** al no existir Dockerfile, no aplica la estrategia de builds multi-etapa originalmente propuesta.

## Deuda técnica / mejoras pendientes (no bloqueantes para nuevos módulos)
- **Contenerización:** si en el futuro se decide migrar a despliegue vía contenedores/Kubernetes, se deberá crear un `Dockerfile` multi-etapa por módulo y añadir los pasos `docker build`/`push` al pipeline existente. Ningún módulo lo tiene hoy, por lo que no se exige a los módulos nuevos (p. ej. Vendors) incorporarlo antes que el resto del backend.

## Consecuencias

### Positivas (+)
- Refleja la práctica real y ya probada en producción (release Maven vía GitLab CI), sin introducir una exigencia (Dockerfile) que ningún módulo backend cumple hoy.
- Simplifica el pipeline actual: no depende de un registry de imágenes ni de infraestructura de orquestación de contenedores.

### Negativas (-)
- Sin contenerización, el despliegue depende del entorno de ejecución del JAR (JVM, systemd, etc.) gestionado fuera de este repositorio, con menor portabilidad y aislamiento que un contenedor.
- Si en el futuro se decide contenerizar, será un esfuerzo de migración retroactivo sobre todos los módulos existentes, no solo sobre los nuevos.
