# ADR-0030 – Auditoría Runtime HostConfig y Visibilidad de Privilegios Docker

Fecha: 2026-05-23
Estado: Aprobado
Contexto: server_monitoring_2509 - Hardening runtime y auditoría Host-Controlled IaC

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

La información runtime recopilada incluirá:
- Privileged
- CapAdd
- CapDrop
- SecurityOpt
- ReadonlyRootfs
- AppArmorProfile
- tmpfs
- devices runtime

Las validaciones se ejecutarán exclusivamente desde el host
mediante tooling estructurado existente.

## Consecuencias

### Positivas
- Mayor visibilidad runtime real
- Reducción de drift Compose ↔ runtime
- Menor dependencia de parsing heurístico
- Auditoría más determinista
- Mejor alineación con ADR-0018 y ADR-0029
- Base futura para hardening incremental

### Negativas
- Incremento moderado de complejidad de auditoría
- Dependencia parcial de docker inspect host-side
- Posible aparición inicial de ruido operacional
- Necesidad futura de clasificación runtime más precisa

## Limitaciones

Esta fase NO garantiza todavía:
- enforcement completo de mínimo privilegio
- seccomp obligatorio
- AppArmor obligatorio
- cap_drop universal
- no-new-privileges universal

Tampoco sustituye:
- revisiones manuales
- excepciones ADR documentadas
- validación operacional progresiva

## Estado futuro esperado

La auditoría runtime servirá como base para futuras fases de:
- hardening incremental
- enforcement selectivo
- clasificación runtime estructurada
- validación CI más precisa

manteniendo siempre compatibilidad con:
- Docker Compose standalone
- arquitectura single-node
- operabilidad del entorno PRO
- observabilidad híbrida existente
