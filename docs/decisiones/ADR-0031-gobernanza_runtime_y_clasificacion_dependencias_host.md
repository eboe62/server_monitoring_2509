# ADR-0031 – Gobernanza Runtime Docker y Clasificación de Dependencias Host

Fecha: 2026-05-24
Estado: Aprobado
Contexto: server_monitoring_2509

## Contexto

Tras completar las fases iniciales de:

- reproducibilidad
- aislamiento
- hardening runtime
- normalización de secretos

se realizó una auditoría estructural del runtime Docker del entorno PRO.

La auditoría identificó una situación intermedia:

- El entorno ya no depende estructuralmente del host para ejecutar aplicaciones.
- Sin embargo, persistían:
  - excepciones runtime no clasificadas
  - mounts host funcionales sin gobernanza formal
  - validaciones parciales HostConfig
  - ejecuciones operativas históricas fuera del modelo declarativo

Especialmente:
- cronjobs host-side ejecutando Python del proyecto
- mounts observabilidad host-centric no formalizados
- ausencia de taxonomía oficial de mounts permitidos/prohibidos
- control incompleto de privilegios runtime
- ausencia de matriz explícita de excepciones arquitectónicas

## Problema

La ausencia de una política runtime centralizada generaba:
- ambigüedad arquitectónica
- deuda técnica operativa
- validaciones inconsistentes
- dificultad de auditoría
- riesgo de regresión futura
- confusión entre:
  - excepción legítima
  - dependencia inválida
  - hardening requerido

## Decisión

Se adopta un modelo formal de:
“Gobernanza declarativa del runtime Docker”.

El entorno PRO pasa a regirse mediante:
- clasificación explícita de mounts
- política HostConfig auditada
- taxonomía de dependencias host
- validaciones runtime automáticas
- excepciones formalizadas mediante ADR

## Política Runtime Oficial

### 1. Prohibiciones estructurales

Queda prohibido en entorno PRO:
- privileged: true
- network_mode: host
- bind mounts de código runtime
- docker.sock
- ejecución host-side de Python del proyecto
- estado runtime crítico fuera de Docker

### 2. Dependencias host permitidas únicamente como excepción aprobada

Se permiten exclusivamente:
- /var/log:ro
- /var/lib/docker/containers:ro

cuando:
- exista justificación funcional
- estén asociadas a observabilidad host-centric
- sean readonly
- tengan ADR asociado

### 3. Configuración runtime

La configuración runtime debe cumplir:
- readonly
- declarativa
- versionable
- desacoplada del estado mutable

### 4. Estado mutable

Todo estado mutable debe residir en:
- volúmenes Docker nombrados
  o
- sistemas externos explícitamente aprobados

### 5. Ejecución operativa

Toda ejecución de lógica del proyecto debe ocurrir únicamente dentro de:
- monitoring-python
- monitoring-cron
  u otros contenedores explícitamente aprobados.

El host no ejecuta:
- módulos Python del proyecto
- cronjobs aplicativos
- lógica operacional runtime

## Consecuencias

### Positivas
- Reducción de ambigüedad operacional
- Mayor auditabilidad
- Menor riesgo de regresiones
- Hardening consistente
- Compatibilidad reforzada con modelo IaC
- Validaciones CI más fiables
- Separación clara entre:
  - excepción operacional
  - deuda técnica
  - violación arquitectónica

### Negativas
- Mayor carga documental
- Necesidad de mantener ADR de excepciones
- Endurecimiento operativo de debugging ad-hoc
- Mayor disciplina de despliegue

## Validación

La política se validará mediante:
- Makefile
- CI
- auditorías runtime
- inspección automática HostConfig
- validaciones Docker inspect
- revisión de mounts y privilegios

## Estado final esperado

El entorno PRO deberá quedar:
- completamente gobernado
- reproducible
- auditable
- sin privilegios implícitos
- sin dependencias host ambiguas
- con excepciones runtime explícitas y justificadas
