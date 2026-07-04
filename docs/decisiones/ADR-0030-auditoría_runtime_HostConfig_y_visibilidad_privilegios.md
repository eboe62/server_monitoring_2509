# ADR-0030 – Auditoría Runtime HostConfig y Visibilidad de Privilegios Docker

Status: APPROVED
Date: 2026-05-23
Scope: Runtime
Category: GOVERNANCE
Tags: REVIEW_REQUIRED
Related ADRs: ADR-0020, ADR-0029
Supersedes: NONE
Superseded By: NONE
Validation Reference: make audit-runtime

## Contexto

Durante la evolución del hardening runtime del proyecto se identificó que las validaciones existentes cubrían únicamente una parte del estado real de privilegios Docker.

La auditoría actual ya verificaba:
- UID runtime efectivo
- uso de docker.sock
- privileged parcial
- mounts sensibles
- aislamiento de red
- validaciones Compose estructuradas

Sin embargo, todavía no existía visibilidad estructurada sobre:
- HostConfig runtime efectivo
- Linux capabilities
- seccomp runtime
- AppArmor runtime
- no-new-privileges
- readonly rootfs efectivo

Asimismo, parte de la auditoría seguía dependiendo de:
- correlaciones shell
- grep heurístico
- parsing textual parcial

El proyecto opera explícitamente bajo:
- Docker Compose standalone
- single-node runtime
- Host-Controlled IaC
- observabilidad híbrida
- diferenciación entre:
  - SERVICE_RUNTIME
  - INFRA_TRUSTED
  - TOOLBOX_RUNTIME

Por tanto, no resultaba coherente adoptar modelos de enforcement complejos inspirados en Kubernetes o plataformas cloud-native enterprise.

## Decisión

Se adopta una nueva fase de auditoría runtime basada en:
- docker inspect host-side
- validación HostConfig real
- runtime visibility estructurada
- parsing determinista

La fase inicial tendrá únicamente objetivos de:
- visibilidad
- baseline runtime
- inventario reproducible

NO de enforcement agresivo.

La auditoría runtime:
- NO dependerá de docker.sock dentro de contenedores
- NO ejecutará lógica Docker desde runtime containers
- NO bloqueará pipelines inicialmente
- NO impondrá hardening masivo automático

La información runtime recopilada incluirá visibilidad estructurada sobre:
- Privileged
- CapAdd
- CapDrop
- SecurityOpt
- ReadonlyRootfs
- AppArmorProfile
- tmpfs
- devices runtime

La fase actual tendrá carácter exclusivamente observacional (runtime visibility baseline), sin interpretar todavía los resultados como enforcement definitivo.

Las validaciones se ejecutarán exclusivamente desde el host mediante tooling estructurado existente.

## Consecuencias

### Positivas
- Mayor visibilidad runtime real
- Reducción parcial de drift Compose ↔ runtime
- Menor dependencia de parsing heurístico
- Auditoría más determinista
- Mejor alineación con ADR-0018 y ADR-0029
- Baseline reproducible de evidencia runtime
- Base futura para hardening incremental

### Negativas
- Incremento moderado de complejidad de auditoría
- Dependencia parcial de docker inspect host-side
- Posible aparición inicial de ruido operacional
- Ausencia todavía de clasificación runtime contextual
- Necesidad futura de baseline de excepciones runtime

## Limitaciones
Esta fase NO garantiza todavía:
- enforcement completo de mínimo privilegio
- diff estructurado Compose ↔ runtime
- clasificación runtime contextual
- baseline formal de excepciones runtime
- seccomp obligatorio
- AppArmor obligatorio
- cap_drop universal
- no-new-privileges universal

Tampoco sustituye:
- revisiones manuales
- excepciones ADR documentadas
- validación operacional progresiva

## Estado futuro esperado
La auditoría runtime servirá como baseline inicial para futuras fases de:
- diff Compose ↔ runtime estructurado
- clasificación runtime contextual
- baseline de excepciones runtime
- hardening incremental
- enforcement selectivo
- validación CI más precisa

manteniendo siempre compatibilidad con:
- Docker Compose standalone
- arquitectura single-node
- operabilidad del entorno PRO
- observabilidad híbrida existente
