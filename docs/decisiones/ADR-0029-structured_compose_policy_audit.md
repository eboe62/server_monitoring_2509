# ADR-0029 — Structured Compose Policy Audit

Status: APPROVED
Date: 2026-05-20
Decision Type: REVIEW_REQUIRED
Scope: Infrastructure
Tags: REVIEW_REQUIRED
Related ADRs: ADR-0027
Supersedes: NONE
Superseded By: NONE
Validation Reference: make test-policy-structured

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
- parte del tooling operacional Python debía ejecutarse desde host-side
- algunas validaciones parseaban salida humana
- las severidades no estaban centralizadas
- no existía salida machine-readable estable
- la correlación runtime ↔ compose no era determinista

El proyecto mantiene actualmente:
- Docker Compose standalone
- arquitectura single-node
- modelo híbrido Host-Controlled Docker Compose IaC
- runtime operacional basado en infra-stacks
- validaciones pragmáticas alineadas con ADR-0017
- separación explícita entre:
    - runtime funcional containerizado
    - control-plane operacional host-side
  definida en ADR-0011

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

Posteriormente se verificó además que el runtime actual:
- no incorpora docker CLI
- no incorpora docker compose
- no expone docker.sock
- no actúa como toolbox Docker host-level

Por tanto:
- la validación runtime debe degradar correctamente
- los fallos de resolución Compose no deben romper auditorías completas
- el sistema debe soportar fallback explícito
- el fallback YAML estático debe considerarse comportamiento operativo válido

## Problema identificado

Las validaciones heurísticas basadas en shell no proporcionaban suficiente robustez para:
- auditoría reproducible
- enforcement progresivo
- validación estructurada real
- integración CI/CD
- los runtimes funcionales containerizados no deben asumir capacidades Docker host-level

## Decisión

Se adopta un modelo de auditoría estructurada basado en parsing Compose mediante Python.

Se establece como motor oficial:
    ops/audit/compose_policy_checks.py

La validación estructurada se ejecuta preferiblemente desde el host mediante:
    python3 -m ops.audit.compose_policy_checks

sin depender del runtime containerizado monitoring-python.

El contenedor:
    monitoring-python

actúa como runtime Python aislado y NO se considera un toolbox Docker completo.

El runtime actual NO garantiza:
- disponibilidad docker CLI
- disponibilidad docker compose
- acceso operativo a docker.sock
- resolución compose runtime-resolved

Por tanto:
- docker compose config puede no estar disponible dentro del runtime
- el fallback YAML estático debe considerarse comportamiento operativo válido
- las validaciones deben degradar explícitamente sin romper auditorías

Cuando exista tooling Docker operativo dentro del runtime, podrá utilizarse:
    docker compose config

como representación runtime-resolved del estado Compose efectivo.

En ausencia de dichas capacidades:
- el sistema degradará explícitamente
- el fallback YAML estático será comportamiento válido
- las auditorías no deberán fallar completamente

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
- mantiene las operaciones Docker host-level

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
- reduce dependencia operacional del control-plane Docker

## Runtime Model

La lógica principal de validación se ejecuta dentro del runtime containerizado del proyecto.

Principios adoptados:

1 — El host no ejecuta lógica core de validación
El host:
- orquesta
- invoca runtime
- consume JSON
- presenta resultados
- mantiene control-plane Docker

No debe ejecutar:
- validaciones principales
- lógica policy core
- parsing Compose complejo

2 — Runtime operacional centralizado
El runtime principal válido es:
    monitoring-python

Este runtime:
- ejecuta lógica Python versionada
- realiza validaciones estructuradas best-effort
- consume configuraciones runtime del proyecto
- opera como runtime operacional de aplicación

El runtime NO garantiza:
- acceso Docker CLI
- acceso docker compose
- acceso docker.sock
- capacidades completas de toolbox Docker

Las operaciones Docker host-level permanecen fuera del contenedor.

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

Cuando la resolución runtime no esté disponible:
- se utilizará fallback YAML
- se emitirá warning explícito
- la validación continuará en modo best-effort

## Runtime checks

Se añade:
    --self-test

para validar:
- disponibilidad opcional docker CLI
- disponibilidad opcional docker compose
- operatividad opcional docker compose config
- acceso opcional docker.sock
- degradación fallback correctamente gestionada

La ausencia de capacidades Docker dentro del runtime NO constituye necesariamente fallo arquitectónico.

Objetivo:
- detectar degradaciones runtime
- validar capacidad operacional disponible
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
- deben degradar explícitamente cuando el runtime Compose no pueda resolverse
- no deben asumir capacidades Docker dentro del runtime Python

## Tradeoffs

### Ventajas
- reducción significativa de falsos positivos
- reducción significativa de falsos negativos
- validación estructurada real
- mejor mantenibilidad
- integración CI/CD más fiable
- enforcement progresivo
- menor deuda técnica shell-based
- mejor correlación YAML ↔ auditoría
- alineación con el modelo Host-Controlled Docker Compose IaC
- separación más clara entre:
    - runtime funcional containerizado
    - tooling operacional host-side
- reducción de superficie de ataque del runtime Python
- eliminación de dependencia de docker.sock dentro de runtimes funcionales

### Inconvenientes
- mayor complejidad respecto a shell puro
- dependencia parcial del fallback YAML
- pérdida parcial de correlación runtime ↔ compose
- necesidad de contexto Compose detectable
- mayor complejidad de degradación operacional

## Riesgos identificados

Persisten riesgos asociados a:
- divergencias entre runtime y YAML estático
- degradación best-effort del fallback
- resolución Compose parcial
- dependencia de rutas Compose detectables
- pérdida de correlación runtime ↔ compose cuando docker compose config no está disponible

En el runtime actual:
    monitoring-python

NO dispone de:
- docker CLI
- compose plugin
- acceso docker.sock

Esto reduce superficie de ataque respecto al diseño inicial, pero incrementa dependencia del fallback YAML estático.

Históricamente se contempló que:
    monitoring-python

pudiese requerir acceso parcial a:
    docker.sock

Sin embargo, el runtime actual en producción NO expone:
- docker.sock
- docker CLI
- docker compose

Las validaciones estructuradas operan actualmente mediante:
- parsing YAML estático
- degradación explícita
- validación best-effort

La resolución Compose runtime-resolved queda limitada a entornos donde el tooling Docker exista explícitamente.

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
- no montar docker.sock salvo excepción explícitamente documentada
- no introducir docker CLI dentro del runtime salvo necesidad operacional justificada

2 — Auditoría
- uso de docker.sock auditado automáticamente
- policy checks obligatorios
- degradación runtime auditada mediante warnings explícitos

3 — Runtime controlado
- scripts versionados
- ejecución auditada
- tooling conocido
- fallback deterministicamente gestionado

4 — Fallback explícito
- degradación controlada
- warnings visibles
- no ocultar fallo de docker compose config
- continuidad operacional best-effort

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
- separación más clara entre:
    - runtime funcional containerizado
    - control-plane operacional host-side
- reducción de superficie de ataque del runtime Python
- eliminación de dependencia estructural de docker.sock en monitoring-python
- alineación entre arquitectura declarada y runtime real observado
- enforcement progresivo viable
- mayor coherencia ADR ↔ runtime real

Negativas
- dependencia operacional del fallback YAML
- necesidad de mantener tooling Python adicional
- posibilidad de degradación fallback parcial
- pérdida parcial de resolución runtime efectiva
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
- fallback checks

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
- ADR-0024 — Container Privilege Exception Policy
- ADR-0027 — Tipología oficial de contenedores y política de healthchecks

## Estado
Aprobado.
Auditoría Compose estructurada normalizada.
Modelo runtime-aligned corregido respecto al runtime real.
Fallback Compose explícitamente formalizado.
Validación machine-readable establecida.
Degradación best-effort documentada oficialmente.
