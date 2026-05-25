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
- Persistían todavía:
    excepciones runtime no clasificadas
    mounts host funcionales sin gobernanza formal
    validaciones parciales HostConfig
    ejecuciones operativas históricas fuera del modelo declarativo

Especialmente:
- cronjobs host-side ejecutando Python del proyecto
- mounts observabilidad host-centric no formalizados
- ausencia de taxonomía oficial de mounts permitidos/prohibidos
- control incompleto de privilegios runtime
- ausencia de matriz explícita de excepciones arquitectónicas
- persistencia de hardening no validado operacionalmente

La evolución reciente del entorno confirmó además:
- la necesidad de distinguir entre hardening teórico y hardening operacionalmente compatible
- la aparición de incompatibilidades runtime reales al aplicar políticas readonly sobre determinados servicios upstream
- la necesidad de adoptar un modelo de hardening incremental y service-aware

# Problema

La ausencia de una política runtime centralizada generaba:
- ambigüedad arquitectónica
- deuda técnica operativa
- validaciones inconsistentes
- dificultad de auditoría
- riesgo de regresión futura
- confusión entre:
    excepción legítima
    dependencia inválida
    hardening requerido

Además:
- determinados servicios upstream requerían permisos runtime adicionales no documentados
- algunas medidas de hardening podían romper compatibilidad CI/CD o disponibilidad operacional
- no existía una taxonomía formal para distinguir:
    hardening obligatorio
    hardening recomendado
    hardening avanzado diferido
    incompatibilidad runtime aceptada

# Decisión

Se adopta un modelo formal de:
“Gobernanza declarativa del runtime Docker”.

El entorno PRO pasa a regirse mediante:
- clasificación explícita de mounts
- política HostConfig auditada
- taxonomía de dependencias host
- validaciones runtime automáticas
- excepciones formalizadas mediante ADR
- hardening incremental validado operacionalmente

La gobernanza runtime pasa a priorizar:
- reproducibilidad
- auditabilidad
- estabilidad operacional
- enforcement CI/CD
- endurecimiento progresivo compatible con upstream

# Política Runtime Oficial

## 1. Prohibiciones estructurales

Queda prohibido en entorno PRO:
- privileged: true
- network_mode: host
- bind mounts de código runtime
- docker.sock
- ejecución host-side de Python del proyecto
- estado runtime crítico fuera de Docker

Toda excepción deberá:
- documentarse explícitamente
- justificarse técnicamente
- validarse mediante ADR
- mantenerse auditada automáticamente

## 2. Dependencias host permitidas únicamente como excepción aprobada

Se permiten exclusivamente:
- /var/log:ro
- /var/lib/docker/containers:ro

cuando:
- exista justificación funcional
- estén asociadas a observabilidad host-centric
- sean readonly
- tengan ADR asociado

Quedan prohibidos:
- mounts RW sobre paths sensibles del host
- mounts runtime arbitrarios
- exposición del control plane Docker
- dependencias implícitas no auditadas

## 3. Configuración runtime

La configuración runtime debe ser:
- declarativa
- versionable
- reproducible
- desacoplada del estado mutable

Se consideran medidas baseline de hardening:
- cap_drop: ALL
- no-new-privileges:true
- eliminación de docker.sock
- prohibición de privileged=true
- prohibición de network_mode=host

Las políticas readonly deberán aplicarse únicamente:
- cuando el servicio sea compatible operacionalmente
- tras validar runtime completo
- tras identificar correctamente:
    caches
    tmpfs
    runtime dirs
    WAL
    plugins
    sockets
    directorios efímeros

No se aceptará hardening puramente teórico que:
- rompa disponibilidad
- invalide CI/CD
- introduzca falsos positivos operacionales
- genere degradación funcional no controlada

## 4. Estado mutable

Todo estado mutable debe residir en:
- volúmenes Docker nombrados
  o
- sistemas externos explícitamente aprobados

Queda prohibido:
- persistir estado aplicativo crítico en bind mounts host-side
- depender de directorios runtime no gobernados
- utilizar almacenamiento mutable no versionado ni auditado

## 5. Ejecución operativa

Toda ejecución de lógica del proyecto debe ocurrir únicamente dentro de:
- monitoring-python
- monitoring-cron
- u otros contenedores explícitamente aprobados

El host no ejecuta:
- módulos Python del proyecto
- cronjobs aplicativos
- lógica operacional runtime
- compilación nativa de componentes Python del proyecto

Las tareas operativas deberán ejecutarse mediante:
- contenedores efímeros
- stacks declarativos
- pipelines CI/CD
- servicios Docker gobernados

## 6. Modelo de hardening incremental

El proyecto adopta un modelo de hardening progresivo basado en:
- compatibilidad operacional
- validación CI/CD
- reducción incremental de superficie de ataque
- clasificación explícita de excepciones

Se distinguen:

### Hardening obligatorio

Incluye:
- eliminación de docker.sock
- cap_drop
- no-new-privileges
- prohibición privileged
- control de mounts
- enforcement CI

### Hardening recomendado

Incluye:
- readonly rootfs compatible
- tmpfs específicos
- separación estricta de runtime writable paths
- usuarios non-root cuando upstream lo permita

### Hardening avanzado diferido

Incluye:
- seccomp custom
- AppArmor explícito
- rootless containers
- syscall filtering avanzado
- immutable runtime
- readonly service-aware completo

La ausencia de medidas avanzadas diferidas:
- no invalida la gobernanza runtime
- no implica incumplimiento arquitectónico
- no constituye regresión mientras:
    exista trazabilidad
    exista justificación técnica
    permanezcan activas las medidas baseline

# Consecuencias

## Positivas
- Reducción de ambigüedad operacional
- Mayor auditabilidad
- Menor riesgo de regresiones
- Hardening consistente
- Compatibilidad reforzada con modelo IaC
- Validaciones CI más fiables
- Separación clara entre:
    excepción operacional
    deuda técnica
    violación arquitectónica
- Mayor estabilidad entre CI y PRO
- Reducción de hardening incompatible con upstream
- Mejor trazabilidad de excepciones runtime

## Negativas
- Mayor carga documental
- Necesidad de mantener ADR de excepciones
- Endurecimiento operativo de debugging ad-hoc
- Mayor disciplina de despliegue
- Necesidad de validar hardening por servicio
- Mayor complejidad operacional en observabilidad

# Validación

La política se validará mediante:
- Makefile
- CI
- auditorías runtime
- inspección automática HostConfig
- validaciones Docker inspect
- revisión de mounts y privilegios
- validación healthchecks
- auditoría de runtime writable paths
- comprobaciones automáticas de gobernanza runtime

Las validaciones deberán detectar:
- privileged=true
- network_mode=host
- docker.sock
- mounts RW peligrosos
- dependencias host ambiguas
- privilegios runtime indebidos
- regresiones de gobernanza

# Estado final esperado

El entorno PRO deberá quedar:
- completamente gobernado
- reproducible
- auditable
- sin privilegios implícitos
- sin dependencias host ambiguas
- con excepciones runtime explícitas y justificadas
- con enforcement CI/CD operativo
- con separación explícita entre:
    hardening baseline
    hardening recomendado
    hardening avanzado diferido

El modelo objetivo prioriza:
- estabilidad operacional
- trazabilidad arquitectónica
- seguridad incremental
- enforcement automatizado
- compatibilidad controlada con upstream
