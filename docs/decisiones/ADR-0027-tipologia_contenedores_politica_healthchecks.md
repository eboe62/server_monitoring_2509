# ADR-0027 — Tipología oficial de contenedores y política de healthchecks

Fecha: 2026-05-15
Estado: Aprobado
Contexto: server_monitoring_2602 – Fase 5 Hardening y Certificación Runtime

## Contexto

Se ha detectado una ambigüedad arquitectónica relacionada con:
- semántica runtime de contenedores
- validación healthchecks
- separación readiness/liveness
- criterios de certificación operativa

El entorno utilizaba healthchecks heterogéneos:
- readiness HTTP
- validación de procesos
- checks triviales
- ausencia de healthchecks

sin una clasificación formal de:
- función runtime
- comportamiento esperado
- política operativa

Esto generaba:
- falsos positivos
- falsos negativos
- incoherencias CI
- confusión durante auditoría
- riesgo de hardening artificial

Especialmente en:
- monitoring-python
- promtail
- smtp-relay

## Problema identificado

Docker HEALTHCHECK estaba siendo utilizado con semánticas distintas
según el tipo real de contenedor:

- servicios funcionales
- supervisores
- runtimes toolbox
- componentes infraestructurales

La arquitectura original asumía implícitamente:

    "todo contenedor debe tener healthcheck equivalente"

Esta premisa resultó incorrecta.

No todos los contenedores representan:
- APIs
- servicios HTTP
- procesos funcionales persistentes

Algunos contenedores existen explícitamente como:
- entornos operador
- runtimes persistentes
- targets controlados para docker exec
- tooling operacional IaC

Forzar readiness clásico sobre estos runtimes implicaría:
- complejidad artificial
- falsas dependencias
- semántica incorrecta
- degradación del modelo IaC

## Decisión

Se adopta una tipología oficial de contenedores.

Cada contenedor del entorno PRO debe clasificarse explícitamente
según su función arquitectónica real.

## Tipos oficiales

1. SERVICE_RUNTIME

Contenedores que exponen funcionalidad activa consumible.

Incluye:
- APIs
- interfaces web
- servicios DB
- observabilidad
- almacenamiento

Requieren:
- readiness checks reales
- validación funcional explícita

Ejemplos:
- grafana
- loki
- postgres

------------------------------------------

2. SUPERVISOR_RUNTIME

Contenedores cuya función principal es mantener
un supervisor o scheduler operativo.

Requieren:
- liveness checks de proceso

Ejemplo:
- monitoring-cron

------------------------------------------

3. TOOLBOX_RUNTIME

Contenedores persistentes utilizados como:
- entorno operador
- runtime controlado
- punto de entrada operacional
- runtime IaC

NO representan servicios funcionales expuestos.

Pueden:
- mantener procesos keepalive
- utilizar docker exec
- ejecutar tooling interno
- ejecutar scripts runtime

NO requieren:
- readiness HTTP
- validación semántica de servicio

Ejemplo:
- monitoring-python

------------------------------------------

4. INFRA_TRUSTED

Contenedores externos o upstream considerados
dependencias infraestructurales confiables.

Pueden requerir:
- readiness
- liveness

según su comportamiento real.

Ejemplos:
- promtail
- smtp-relay

## Política oficial de healthchecks

Los healthchecks deben alinearse con:
- función arquitectónica
- semántica runtime
- comportamiento real del contenedor

NO se asume arquitectura microservicio HTTP clásica
para todos los runtimes.

------------------------------------------
SERVICE_RUNTIME
------------------------------------------

Requieren readiness checks reales.

Los checks deben validar:
- aceptación de conexiones
- disponibilidad funcional
- operatividad semántica

Ejemplos válidos:
- pg_isready
- HTTP /ready
- HTTP /api/health

No se permiten:
- checks artificiales
- exit 0 permanentes
- validaciones no deterministas

------------------------------------------
SUPERVISOR_RUNTIME
------------------------------------------

Requieren:
- liveness checks de supervisor/proceso

Ejemplos válidos:
- pidof
- pgrep

El objetivo es detectar:
- caída del scheduler
- pérdida del supervisor
- corrupción runtime

------------------------------------------
TOOLBOX_RUNTIME
------------------------------------------

Pueden:
- no tener healthcheck
- utilizar keepalive explícito
- utilizar checks triviales documentados

NO deben:
- bloquear readiness gates
- bloquear CI/CD
- certificarse como microservicio funcional

Un healthcheck trivial solo es válido
cuando el contenedor esté explícitamente
clasificado como TOOLBOX_RUNTIME.

------------------------------------------
INFRA_TRUSTED
------------------------------------------

Deben utilizar:
- el mecanismo más apropiado
- según capacidades upstream reales

Debe evitarse:
- hardening artificial
- wrappers innecesarios
- sidecars no justificados

# Decisión específica monitoring-python

monitoring-python queda clasificado oficialmente como:
    TOOLBOX_RUNTIME

Su función oficial es:
- entorno runtime persistente
- ejecución controlada mediante docker exec
- runtime operador IaC
- tooling operacional

No representa:
- API
- servicio HTTP
- daemon funcional persistente

Por tanto:
- no requiere readiness HTTP
- puede utilizar keepalive explícito
- puede utilizar healthcheck trivial documentado

Este comportamiento es:
- intencional
- coherente con IaC
- arquitectónicamente válido

No constituye:
- desviación
- workaround
- anti-pattern

## Consecuencias

Se alinearán:
- Docker Compose
- Makefile
- CI
- scripts audit
- validaciones runtime

con la tipología oficial.

Las validaciones futuras deberán:
- diferenciar readiness y liveness
- evitar falsas alarmas
- evitar gates incorrectos
- respetar TOOLBOX_RUNTIME

Se permitirá:
- WARN controlado
- excepciones documentadas

cuando estén justificadas mediante:
- ADR
- clasificación runtime
- limitaciones upstream

## Restricciones

No se permitirá:
- introducir readiness artificial
- convertir toolboxes en pseudo-servicios
- crear endpoints fake
- introducir sidecars innecesarios
- degradar reproducibilidad IaC

Los healthchecks:
- no deben depender del host
- deben ejecutarse dentro del runtime
- deben ser deterministas
- deben devolver exit codes reales

## Validación futura

Las siguientes herramientas deberán alinearse con esta decisión:

- Makefile
- CI
- audit_repo_host.sh
- runtime validations
- security runtime tests
- resiliency tests

Se establecerá una fuente única de verdad para clasificación runtime de contenedores.

## Estado

Aprobado.
Arquitectura runtime oficialmente normalizada.
Tipología y semántica healthchecks formalizadas.
