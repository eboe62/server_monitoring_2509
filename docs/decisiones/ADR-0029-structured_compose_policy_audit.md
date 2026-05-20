# ADR-0029 — Structured Compose Policy Audit

Fecha: 2026-05-20
Estado: Aprobado
Contexto: server_monitoring_2509 — Hardening de auditoría Compose y validación estructurada runtime

## Contexto

Durante la evolución del entorno server_monitoring se detectaron limitaciones importantes en las validaciones de seguridad y compliance aplicadas sobre Docker Compose.

La validación original utilizaba principalmente:
- grep
- awk
- búsquedas textuales
- parsing shell heurístico
- correlación parcial entre runtime y compose

Especialmente en:
- ops/audit/audit_repo_host.sh
- Makefile
- validaciones runtime
- policy checks

Este enfoque provocaba:
- falsos positivos
- falsos negativos
- dependencia excesiva del formato YAML
- fragilidad ante cambios de indentación o estructura
- dificultad para evolucionar políticas
- baja mantenibilidad
- difícil integración CI/CD
- auditorías parcialmente no deterministas

Adicionalmente se identificaron inconsistencias arquitectónicas:
- parte de la lógica Python se ejecutaba desde el host
- algunas validaciones parseaban salida humana
- las severidades no estaban centralizadas
- no existía salida machine-readable estable
- la correlación runtime ↔ compose no era determinista

El proyecto mantiene actualmente:
- Docker Compose standalone
- arquitectura single-node
- modelo container-first
- runtime operacional basado en infra-stacks
- validaciones pragmáticas alineadas con ADR-0017
- separación explícita host/runtime definida en ADR-0011

Durante la implantación también se detectó una limitación operacional adicional:
    docker compose config
requiere contexto Compose válido.

Cuando el comando se ejecuta dentro del contenedor:
    monitoring-python

puede producir:
    no configuration file provided: not found

si el runtime no dispone del directorio Compose correcto o no existe:
- COMPOSE_FILE
- working directory válido
- bind mount consistente

Por tanto:
- la validación runtime debe degradar correctamente
- los fallos de resolución Compose no deben romper auditorías completas
- el sistema debe soportar fallback explícito

## Problema identificado
Las validaciones heurísticas basadas en shell no proporcionaban suficiente robustez para:
- auditoría reproducible
- enforcement progresivo
- validación estructurada real
- integración CI/CD
- reducción fiable de falsos positivos
- reducción fiable de falsos negativos
- correlación runtime ↔ compose

Adicionalmente:
- ejecutar lógica Python desde host rompía parcialmente el modelo container-first
- parsear salida humana impedía automatización fiable
- docker compose config puede no resolverse correctamente dentro del runtime
- algunas validaciones dependían implícitamente del directorio actual

## Decisión

Se adopta un modelo de auditoría estructurada basado en parsing Compose mediante Python.

Se establece como motor oficial:
    ops/audit/compose_policy_checks.py

La validación principal debe ejecutarse preferiblemente dentro del contenedor:
    monitoring-python

mediante:
    docker compose exec -T monitoring-python ...

La validación utiliza prioritariamente:
    docker compose config

como representación runtime-resolved del estado Compose efectivo.

La salida soporta:
- modo humano
- salida JSON machine-readable
- checks parciales mediante --check
- runtime validation mediante --self-test

La severidad se centraliza mediante:
POLICY_SEVERITY

El host:
- coordina ejecución
- recopila resultados
- consume JSON estructurado
- evita parsear salida humana

## Fallback estructurado

Cuando:
    docker compose config

no puede resolverse correctamente dentro del runtime, el sistema degrada explícitamente a:
- parsing YAML estático
- merge best-effort
- validación parcial

mediante:
    load_compose_from_files()

sobre archivos detectados bajo:
    ops/

El sistema debe emitir warning explícito cuando ocurra degradación runtime.

Ejemplo esperado:
    [WARN] Usando parseo estático de archivos Compose

Este fallback:
- NO garantiza resolución completa Compose
- NO resuelve merges complejos de forma idéntica
- NO reproduce profiles avanzados
- NO sustituye completamente docker compose config

Sin embargo:
- preserva auditabilidad mínima
- evita fallo completo del pipeline
- mantiene comportamiento determinista suficiente para auditoría defensiva

## Runtime Model

La lógica principal de validación se ejecuta dentro del runtime containerizado del proyecto.

Principios adoptados:

1 — El host no ejecuta lógica core de validación
El host:
- orquesta
- invoca runtime
- consume JSON
- presenta resultados

No debe ejecutar:
- validaciones principales
- lógica policy core
- parsing Compose complejo

2 — Runtime operacional centralizado
El runtime principal válido es:
    monitoring-python

Este runtime puede:
- acceder al tooling Docker
- ejecutar docker compose config
- realizar validaciones estructuradas
- operar como toolbox operacional

3 — Parsing estructurado
Las validaciones utilizan:
- parsing YAML real
- estructuras Python
- JSON machine-readable

No se considera válido:
- parsear salida humana con awk
- correlación basada únicamente en grep
- enforcement basado exclusivamente en texto plano

## Validaciones estructuradas implementadas

Se implementan validaciones estructuradas para:
- puertos publicados
- docker.sock
- imágenes con :latest
- imágenes sin digest
- privileged=true
- mounts sensibles RW
- cap_add
- read_only=false

Las validaciones operan sobre:

services:
    resueltos mediante Compose.

## Runtime checks

Se añade:
    --self-test

para validar:
- disponibilidad docker CLI
- disponibilidad docker compose
- operatividad docker compose config
- acceso docker.sock

Objetivo:
- detectar degradaciones runtime
- validar capacidad operacional del toolbox
- identificar problemas de control-plane
- mejorar observabilidad de auditoría

## Severidades

Las severidades se centralizan mediante:
POLICY_SEVERITY

Clasificación inicial:
- privileged=true → FAIL
- resto → WARN

El exit code queda alineado con la severidad.

Consecuencia:
- violaciones FAIL devuelven rc != 0
- warnings permanecen auditables sin romper ejecución

## Herramientas auxiliares

Se introduce:
    ops/audit/parse_compose_json.py

como helper ligero para:
- parse JSON desde shell
- evitar Python inline en bash
- simplificar mantenimiento operacional

El host puede utilizar prioritariamente:
- jq
- parse_compose_json.py

para consumir JSON estructurado.

## Restricciones

No se permitirá:
- enforcement basado exclusivamente en grep
- parsear salida humana como fuente principal
- ejecutar lógica policy core desde host
- introducir dependencias Kubernetes
- introducir OPA/Rego
- introducir policy-as-code complejo
- degradar reproducibilidad runtime

Las validaciones:
- deben ser deterministas
- deben soportar salida machine-readable
- deben ejecutarse preferiblemente dentro del runtime
- deben degradar explícitamente cuando el runtime Compose no pueda resolverse

## Tradeoffs

### Ventajas
- reducción significativa de falsos positivos
- reducción significativa de falsos negativos
- validación estructurada real
- mejor mantenibilidad
- integración CI/CD más fiable
- enforcement progresivo
- menor deuda técnica shell-based
- mejor correlación runtime ↔ compose
- alineación con arquitectura container-first

### Inconvenientes
- mayor complejidad respecto a shell puro
- dependencia parcial del runtime Docker
- posible dependencia de docker.sock
- necesidad de contexto Compose válido
- mayor acoplamiento al runtime operacional

## Riesgos identificados

Persisten riesgos asociados a:
- dependencia de docker compose config
- acceso parcial a docker.sock
- divergencias entre runtime y YAML estático
- degradación best-effort del fallback
- dependencia del directorio Compose activo

Especialmente:
    monitoring-python

puede requerir acceso parcial a:
    docker.sock

para:

- inspección runtime
- compose config
- validaciones operacionales

Esto incrementa superficie de ataque respecto a un contenedor completamente aislado.

Actualmente se considera aceptable debido a:
- arquitectura single-node
- entorno controlado
- ausencia de multitenancy
- modelo infra-stack documentado
- mitigaciones existentes en ADR-0008 y ADR-0018

## Mitigaciones operativas

Mitigaciones obligatorias:

1 — Restricción de exposición
- monitoring-python no debe exponer puertos públicos
- acceso exclusivamente interno

2 — Auditoría
- uso de docker.sock auditado automáticamente
- policy checks obligatorios

3 — Runtime controlado
- scripts versionados
- ejecución auditada
- tooling conocido

4 — Fallback explícito
- degradación controlada
- warnings visibles
- no ocultar fallo de docker compose config

## Compatibilidad

La decisión mantiene compatibilidad con:
- Docker Compose standalone
- arquitectura single-node
- runtime actual
- Makefile existente
- audit_repo_host.sh
- CI actual
- ADR previos
- modelo IaC actual

No se introduce:
- Kubernetes
- Docker Swarm
- OPA/Rego
- policy engines externos
- reconciliación distribuida

## Consecuencias

Positivas
- auditoría estructurada reproducible
- validación machine-readable
- reducción de deuda técnica shell-based
- mejor integración futura con CI/CD
- separación más clara host/runtime
- enforcement progresivo viable
- mayor coherencia ADR ↔ runtime

Negativas
- dependencia operacional del runtime Compose
- necesidad de mantener tooling Python adicional
- posibilidad de degradación fallback parcial
- complejidad superior respecto a grep simple

## Validación futura

Las siguientes herramientas deberán alinearse con esta decisión:
- CI
- Makefile
- audit_repo_host.sh
- runtime tests
- resiliency tests
- policy checks

Las futuras validaciones deberán distinguir explícitamente:

- smoke tests
- policy checks
- runtime validation
- certification checks
- enforcement checks

## Relación con otros ADR

Este ADR complementa:

- ADR-0008 — Servicios micro-stack vs infra-stack
- ADR-0011 — Python Runtime Execution Model
- ADR-0014 — Docker Port Exposure Policy
- ADR-0015 — Docker Network Exposure Model
- ADR-0017 — Resilience model at docker single-node
- ADR-0018 — Docker security runtime and resilience requirements
- ADR-0019 — Resilience Testing Strategy
- ADR-0020 — Container Execution Model & Privilege Strategy
- ADR-0027 — Tipología oficial de contenedores y política de healthchecks

## Estado
Aprobado.
Auditoría Compose estructurada normalizada.
Modelo runtime-aligned formalizado.
Fallback Compose explícitamente documentado.
Validación machine-readable establecida.
