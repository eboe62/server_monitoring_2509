# ADR-0027 — Tipología oficial de contenedores y política de healthchecks

Fecha: 2026-05-17
Estado: Aprobado
Contexto: server_monitoring_2509 — Hardening runtime, validación CI/CD y normalización de healthchecks

## Contexto

Durante la evolución del entorno server_monitoring se detectaron inconsistencias en:
- validación de healthchecks
- clasificación semántica de contenedores
- criterios CI/CD
- auditoría runtime
- separación entre readiness y liveness

La validación original utilizaba:
- grep textual sobre compose
- detección heurística de healthchecks
- correlación parcial entre service_name y container_name

Esto provocaba:
- falsos positivos
- falsos negativos
- ambigüedad arquitectónica
- drift entre ADR y runtime real
- enforcement inconsistente

Especialmente en:
- monitoring-python
- promtail
- smtp-relay
- monitoring-cron

Adicionalmente se detectó que algunos contenedores eran tratados como microservicios HTTP tradicionales cuando realmente representaban:

- runtimes operativos
- supervisores
- tooling persistente
- componentes infraestructurales

La validación anterior asumía implícitamente:
    “todo contenedor debe tener un healthcheck homogéneo”

Esta premisa resultó incorrecta.

No todos los contenedores:
- exponen APIs
- representan servicios funcionales
- requieren readiness HTTP
- participan en tráfico de negocio

## Problema identificado

Los healthchecks estaban siendo utilizados con semánticas distintas según la naturaleza real del contenedor.

Esto generaba:
- checks artificiales
- validaciones incorrectas
- gates CI poco fiables
- confusión operacional
- auditorías ambiguas

Se identificaron además limitaciones técnicas en:
- parsing YAML manual
- detección basada en grep
- resolución indirecta de compose
- correlación runtime ↔ compose

## Decisión

Se adopta una clasificación oficial de contenedores y una política explícita de healthchecks.

Cada contenedor debe clasificarse según su función arquitectónica real.

La validación runtime debe utilizar:
- docker compose config
- parsing estructurado
- correlación determinista service/container

Se establece además un archivo centralizado:
    ops/runtime_containers.yml

como fuente única de verdad para:
- clasificación runtime
- política de healthchecks
- enforcement CI
- auditoría operacional

## Tipología oficial de contenedores

### 1. SERVICE_RUNTIME

Contenedores que exponen funcionalidad activa consumible.

Ejemplos:
- postgres
- grafana
- loki

Requisitos:
- readiness checks reales
- validación funcional explícita
- detección determinista de disponibilidad

Checks válidos:
- pg_isready
- HTTP /ready
- HTTP /health

No se permiten:
- exit 0 artificiales
- keepalive falsos
- checks semánticamente vacíos

---

### 2. SUPERVISOR_RUNTIME

Contenedores cuyo objetivo principal es mantener un scheduler o supervisor operativo.

Ejemplo:
- monitoring-cron

Requisitos:
- liveness checks
- validación del proceso supervisor

Checks válidos:
- pidof
- pgrep

Objetivo:
- detectar caída del scheduler
- detectar corrupción runtime

---

### 3. TOOLBOX_RUNTIME

Contenedores persistentes utilizados como:
- entorno operador
- runtime controlado
- tooling operacional
- punto de entrada IaC

Ejemplo:
- monitoring-python

Características:
- pueden utilizar keepalive explícito
- pueden ejecutarse mediante docker exec
- no representan servicios funcionales externos

No requieren:
- readiness HTTP
- validación semántica de API

Los healthchecks triviales son aceptables únicamente si:
- están documentados
- la clasificación TOOLBOX_RUNTIME es explícita

---

### 4. INFRA_TRUSTED

Contenedores upstream o infraestructurales considerados dependencias confiables.

Ejemplos:
- promtail
- smtp-relay

Los healthchecks deben alinearse con las capacidades reales del upstream.

Debe evitarse:
- hardening artificial
- wrappers innecesarios
- sidecars sin justificación

## Política oficial de healthchecks

Los healthchecks deben alinearse con:
- semántica runtime
- comportamiento real del contenedor
- función arquitectónica

No se asume un modelo homogéneo basado exclusivamente en microservicios HTTP.

## Implementación adoptada

Se introduce:
- ops/runtime_containers.yml
- ops/runtime_containers.sh
- validación CI estructurada
- enforcement runtime por clasificación
- auditoría basada en docker compose config

La validación ya no depende exclusivamente de:
- grep textual
- coincidencias heurísticas
- comentarios YAML

## Modelo de validación runtime

El script:
ops/runtime_containers.sh

implementa:
- parseo estructurado de runtime_containers.yml
- resolución determinista compose
- correlación entre:
    service_name
    container_name
- detección explícita de healthchecks

Se incorpora:
    check-health <container>

como mecanismo oficial de validación.

Formato de salida:
    container|FOUND|compose|service|healthcheck

Estados soportados:
- FOUND
- NOT_FOUND
- COMPOSE_INVALID

## Decisión específica sobre promtail

promtail queda clasificado como:

INFRA_TRUSTED

Se adopta readiness basado en:
    [http://localhost:9080/ready](http://localhost:9080/ready)

Healthcheck oficial:
    wget -qO- [http://localhost:9080/ready](http://localhost:9080/ready) || exit 1

Objetivo:
- validar disponibilidad real del agente
- evitar healthchecks artificiales
- mantener coherencia upstream

## Decisión específica sobre monitoring-python

monitoring-python queda clasificado oficialmente como:

TOOLBOX_RUNTIME

Su función es:
- runtime persistente
- tooling operacional
- ejecución controlada mediante docker exec
- entorno operador

No representa:
- API
- microservicio HTTP
- daemon funcional expuesto

Por tanto:
- no requiere readiness HTTP
- puede utilizar keepalive documentado
- puede tener enforcement warn

Esto NO constituye:
- anti-pattern
- workaround
- desviación arquitectónica

## Consecuencias

Positivas:
- reducción de falsos positivos
- validación CI más determinista
- coherencia ADR ↔ runtime
- mejor auditabilidad
- separación formal readiness/liveness
- enforcement centralizado

Operativas:
- nuevos contenedores deben declararse en runtime_containers.yml
- CI y Makefile dependen de la clasificación runtime
- los tests deben respetar la semántica del contenedor

## Limitaciones conocidas

La presencia de healthcheck NO garantiza por sí sola estado healthy.

Durante la validación se observó:
    promtail → unhealthy

incluso existiendo healthcheck declarado.

Esto implica que:
- el endpoint /ready puede no estar respondiendo correctamente
- puede existir dependencia runtime no satisfecha
- el contenedor puede estar funcionalmente degradado

Por tanto:
- CI valida presencia y coherencia del healthcheck
- la salud runtime real debe validarse adicionalmente mediante:
    docker ps
    docker inspect
    logs runtime

## Restricciones

No se permitirá:
- readiness artificial
- endpoints fake
- sidecars innecesarios
- checks semánticamente vacíos
- degradar reproducibilidad IaC

Los healthchecks:
- deben ejecutarse dentro del contenedor
- deben ser deterministas
- deben devolver exit codes reales
- no deben depender del host

## Riesgos identificados

Persisten riesgos asociados a:
- parsing YAML manual mediante awk
- dependencia de docker compose config
- divergencias entre compose renderizado y runtime real
- validación parcial de healthchecks upstream

# ==========================================

## Validación futura

Las siguientes herramientas deben alinearse con esta decisión:
- CI
- Makefile
- audit_repo_host.sh
- runtime tests
- resiliency tests
- policy checks

Las futuras validaciones deberán distinguir explícitamente:
- smoke tests
- policy checks
- certification checks
- runtime enforcement

## Relación con otros ADR

Este ADR complementa:
- ADR-0008 — Servicios micro-stack vs infra-stack
- ADR-0010 — Arquitectura runtime cron
- ADR-0014 — Docker Port Exposure Policy
- ADR-0015 — Docker Network Exposure Model
- ADR-0017 — Resilience model at docker single-node
- ADR-0018 — Docker security runtime and resilience requirements
- ADR-0019 — Resilience Testing Strategy
- ADR-0020 — Container Execution Model & Privilege Strategy

## Estado

Aprobado.
Arquitectura runtime normalizada.
Clasificación de contenedores formalizada.
Política de healthchecks alineada con semántica operacional real.
