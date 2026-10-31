# ADR-0801: Estrategia de Empaquetado y Despliegue con Contenedores Docker

Status: APPROVED
Date: 2026-06-11 (revisado 2026-07-16; **corregido 2026-08-15 — la premisa "sin contenerización" era errónea, ver evidencia real más abajo**; **corregido 2026-08-20 — referencias a `gda-comunicacion` y afirmación sobre `SPRING_PROFILES_ACTIVE` obsoletas, ver ADR-0609**)
Scope: Infrastructure
Category: DEPLOYMENT
Tags: REVIEW_REQUIRED
Related ADRs: ADR-0602, ADR-0802
Supersedes: NONE
Superseded By: NONE
Validation Reference: NONE

## Contexto

En un Monorrepo Maven Multi-Module con microservicios independientes, es necesario definir una estrategia de empaquetado y despliegue.

**Corrección (2026-08-15):** la revisión de 2026-07-16 afirmaba, tras "verificar" el repositorio, que ningún módulo del backend GDA tenía `Dockerfile` y que el despliegue era JAR + entorno de ejecución externo (JVM/systemd) sin contenedores. Esa verificación se limitó al monorepo de código (donde en efecto no hay `Dockerfile` versionado junto a cada módulo) y no comprobó el servidor de desarrollo real. Al preparar el despliegue de `gda-comunicacion` (Espacio Justicia, rama `GDAV3-455`) se recogió evidencia directa del servidor (`172.16.22.114`, host `ineco.ietreir01sdes`) que contradice esa premisa:

```
$ docker ps
CONTAINER ID   IMAGE                             ...   NAMES
44e0482eef5e   actuaciones30-gda-apigateway      ...   gda-apigateway-v3
958f361a8a82   actuaciones30-gda-admingade       ...   gda-admingade
80ec7f9dc7c5   actuaciones30-gda-persona         ...   gda-persona
03a37c5bc224   actuaciones30-gda-estructura      ...   gda-estructura
1da70870b51a   actuaciones30-gda-agrupacion      ...   gda-agrupacion
ea1583e26664   actuaciones30-gda-imputacion      ...   gda-imputacion
f22d11fbad4d   actuaciones30-gda-listado         ...   gda-listado
0d57ff810d59   actuaciones30-gda-log             ...   gda-log
52c8127052f6   actuaciones30-gda-autenticacion   ...   gda-autenticacion
```

Los 9 microservicios de dominio, más el API Gateway y el frontend, corren como contenedores Docker, orquestados desde `/gda/REIR_GDACT/docker/Actuaciones3.0/backend/Repository/docker-compose.yml` mediante un script de control (`V3-ReirGdact.sh`, fuera de este repositorio) con opciones `Start/Stop/Restart` por servicio o para el conjunto. Cada servicio tiene su propio `Dockerfile` en una carpeta homónima junto al `docker-compose.yml` — **el `Dockerfile` no vive en el monorepo de código** (por eso la revisión de 2026-07-16 no lo encontró), sino en el árbol de infraestructura del servidor, gestionado fuera de este repositorio.

## Decisión

Se corrige la estrategia vigente, ya documentada como evidencia real (no como propuesta):

1. **Empaquetado como JAR ejecutable:** cada módulo (`packaging: jar` + `spring-boot-maven-plugin`) se empaqueta como un JAR autocontenido ejecutable con `java -jar`, gestionado con Maven — esto no cambia respecto a la versión anterior de este ADR.
2. **Contenerización Docker, gestionada fuera del monorepo:** el JAR de cada módulo se empaqueta en una imagen Docker mínima (`azul/zulu-openjdk-alpine:17-jre-latest`), con un `Dockerfile` de patrón fijo por servicio:
   ```dockerfile
   FROM azul/zulu-openjdk-alpine:17-jre-latest
   VOLUME /tmp
   EXPOSE <puerto>
   ADD <modulo>-*.jar <modulo>.jar
   ENTRYPOINT ["java","-jar","/<modulo>.jar"]
   ```
   Estos `Dockerfile`, el `docker-compose.yml` que los orquesta y el script de control (`V3-ReirGdact.sh`) viven en el servidor de desarrollo (`/gda/REIR_GDACT/docker/`), no en el monorepo — son infraestructura operada por el equipo, no código de aplicación versionado junto a los módulos.
3. **Versionado y release vía GitLab CI:** el pipeline (`stage: release`, disparo manual sobre `master`) retira el sufijo `-SNAPSHOT`, etiqueta la versión (`git tag`), publica a `master` y sube automáticamente la versión `minor` en `develop`. El pipeline empaqueta el JAR; la construcción de la imagen Docker y el despliegue del contenedor son un paso posterior, manual, en el servidor (copiar el JAR nuevo a la carpeta del servicio y `docker compose build --no-cache <servicio> && docker compose up -d <servicio>` vía `V3-ReirGdact.sh`) — no está automatizado en el CI del monorepo.
4. **Sin builds multi-etapa:** el `Dockerfile` de cada servicio es una imagen de una sola etapa (copia el JAR ya construido, no compila dentro del contenedor).

## Deuda técnica / mejoras pendientes (no bloqueantes para nuevos módulos)

- **`Dockerfile`/`docker-compose.yml` fuera de control de versiones del monorepo:** al vivir solo en el servidor, no hay historial de cambios, revisión de PR ni forma de reproducir el entorno de despliegue desde el propio repositorio de código. Un cambio manual en el servidor (como el que motivó esta corrección) puede quedar sin reflejar aquí durante meses.
- **Despliegue a Docker no automatizado en CI:** el pipeline de GitLab CI (punto 3) libera el JAR, pero copiarlo al servidor y reconstruir el contenedor sigue siendo un paso manual vía `V3-ReirGdact.sh`.
- **`docker-compose.yml` sin gestión de variables de entorno ni volúmenes salvo excepciones puntuales:** ningún servicio de GDA fija `SPRING_PROFILES_ACTIVE` (todos arrancan con el perfil `local` embebido por defecto en su JAR) ni monta volúmenes. El primer caso real que lo necesitó fue `gda-comunicacion` (almacenamiento de ficheros de Noticias, Espacio Justicia; ver `ADR-0608-almacenamiento-adjuntos-noticias.md`), servicio hoy retirado y sustituido por `spj-comunicacion` (ver ADR-0609).

**Corrección (2026-08-20):** `gda-comunicacion` fue retirado por completo del servidor de desarrollo (contenedor, esquema y entrada en `docker-compose.yml` de GDA eliminados) al segregarse Espacio Justicia en un backend independiente — ver ADR-0609. En su lugar corren `spj-comunicacion` (puerto 9109) y `spj-api-gateway` (puerto 9110), orquestados desde una infraestructura Docker separada (`/gda/REIR_GDACT/docker/SPJ/`, script de control propio `SPJ-Espacio-Justicia.sh`), que replica exactamente el patrón descrito en este ADR (mismo `Dockerfile` de una sola etapa, misma imagen base) y confirma, en vez de contradecir, la afirmación de "ningún servicio fija `SPRING_PROFILES_ACTIVE`" anterior: ambos servicios de SPJ sí lo fijan explícitamente a `dev` en su `docker-compose.yml`, corrigiendo además el descuido detectado durante su propio despliegue (el bloque de `spj-api-gateway` se creó inicialmente sin esa variable, causando que arrancase en el perfil `local` con el puerto equivocado).

## Consecuencias

### Positivas (+)

- Aislamiento de proceso y de dependencias de runtime por servicio (imagen mínima Alpine + JRE 17), sin necesidad de gestionar versiones de Java en el host directamente.
- Ciclo de vida uniforme de arranque/parada/reinicio para todos los servicios vía un único script de control.
- Reutiliza la misma imagen base ligera (`azul/zulu-openjdk-alpine:17-jre-latest`) en todos los módulos, sin builds multi-etapa innecesarios para JARs ya compilados.

### Negativas (-)

- La infraestructura de despliegue (`Dockerfile`, `docker-compose.yml`, script de control) vive fuera del monorepo y de su control de versiones — no auditable ni reproducible solo desde este repositorio; ver deuda técnica.
- El paso de "JAR liberado por CI" a "contenedor corriendo en el servidor" es manual, con riesgo de desajuste entre la versión etiquetada en Git y la que realmente corre en el servidor (mismo tipo de riesgo de deriva ya documentado en ADR-0600 para las dependencias `-commons`, aplicado aquí al propio artefacto desplegado).
