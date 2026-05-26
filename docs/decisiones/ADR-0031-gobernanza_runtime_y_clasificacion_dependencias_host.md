# ADR-0031 – Gobernanza Runtime Docker y Clasificación de Dependencias Host

Fecha: 2026-05-26
Estado: Aprobado
Contexto: server_monitoring_2509

## Contexto

Tras completar las fases de:
- reproducibilidad
- segmentación de red
- endurecimiento runtime inicial
- normalización de secretos
- separación host/runtime
- auditoría HostConfig

se ejecutó una validación operacional completa del runtime Docker en entorno PRO DigitalOcean.

La auditoría se realizó utilizando:
- docker inspect
- HostConfig runtime
- validación de capabilities Linux
- análisis de mounts
- validación de puertos publicados
- comprobaciones UFW
- healthchecks runtime
- validación compose discovery
- revisión de usuarios runtime

La evidencia operacional confirmó:
Estado actual confirmado
- Aislamiento y privilegios
    No existe docker.sock montado en ningún contenedor.
    No existe privileged=true.
    No existe network_mode=host.
    monitoring-python y monitoring-cron ejecutan como appuser.
    grafana y loki ejecutan con usuarios no-root explícitos.
    cap_drop: ALL se aplica correctamente en:
        grafana
        loki
        promtail
        monitoring-cron
        monitoring-python

- Red y exposición
    PostgreSQL NO expone puertos al exterior.
    Loki y Grafana publican únicamente sobre 127.0.0.1.
    UFW aplica:
        deny incoming por defecto
        allow únicamente 22/80/443
    No existen puertos de BBDD expuestos públicamente.

- Observabilidad
    monitoring-python posee healthcheck operativo.
    promtail utiliza mounts readonly explícitos.
    observability stack permanece desacoplado de backend-net.

- Persistencia
    PostgreSQL utiliza volúmenes Docker nombrados.
    No se detectó persistencia crítica en bind mounts arbitrarios.

Hallazgos relevantes

La auditoría también confirmó:

- Hardening parcial
    ReadonlyRootfs=false permanece en todos los servicios.
    Esto confirma:
        el entorno NO está aún en modo immutable runtime
        existe compatibilidad operacional priorizada sobre hardening agresivo
        el proyecto adopta un enfoque service-aware incremental

- Servicios con privilegios superiores al baseline ideal
    monitoring-smtp-relay:
        - ejecuta como root
        - mantiene capabilities Linux activas:
            cap_net_bind_service
            cap_net_raw
            cap_setuid
            cap_setgid
            otras capabilities baseline Docker

PostgreSQL:
    no define usuario explícito
    mantiene modelo upstream por defecto
    no utiliza cap_drop explícito

promtail:
    requiere acceso readonly host-centric:
        /var/log
        /var/lib/docker/containers

- Descubrimiento Compose
No existe:
    compose raíz unificado

La arquitectura Compose actual está segmentada:
    ops/stacks/python
    ops/stacks/cron
    ops/stacks/observability
    ops/services/postgres
    ops/services/smtp_relay

Esto invalida parcialmente:
    tooling legacy que asume compose monolítico

y obliga a:
    descubrimiento multi-compose
    auditoría runtime federada

# Problema

La ausencia de una política runtime consolidada generaba:
- ambigüedad operacional
- deuda técnica de hardening
- validaciones inconsistentes
- falta de taxonomía de excepciones
- incompatibilidad entre hardening teórico y runtime real
- tooling legacy incompatible con arquitectura Compose distribuida

Además:
- algunos servicios upstream requieren privilegios reales
- readonly rootfs completo rompe compatibilidad operacional
- observabilidad host-centric necesita mounts readonly del host
- SMTP relay requiere capacidades Linux específicas

# Decisión

Se adopta un modelo oficial de:
“Gobernanza Runtime Declarativa Basada en Evidencia Operacional”.

El hardening deja de basarse exclusivamente en:
- teoría
- benchmarks genéricos
- enforcement absoluto

y pasa a priorizar:
- compatibilidad operacional
- auditabilidad
- reproducibilidad
- enforcement incremental
- validación runtime real
- clasificación explícita de excepciones

# Política Runtime Oficial

## 1. Prohibiciones estructurales

Queda prohibido:
- privileged=true
- network_mode=host
- docker.sock
- bind mounts RW sensibles host-side
- ejecución host-side de Python aplicativo
- publicación externa de PostgreSQL
- lógica runtime fuera de contenedores gobernados

Toda excepción requiere:
- ADR explícito
- justificación técnica
- evidencia operacional
- validación CI
- revisión arquitectónica

## 2. Clasificación oficial de mounts
Permitidos baseline
- volúmenes Docker nombrados
- mounts readonly de configuración
- secrets readonly

Permitidos por excepción auditada
    /var/log:ro
    /var/lib/docker/containers:ro

únicamente para:
- observabilidad
- log shipping
- correlación runtime

Prohibidos
- docker.sock
- mounts RW sobre host crítico
- mounts arbitrarios no documentados
- bind mounts de código runtime

## 3. Hardening baseline obligatorio

Obligatorio:
- cap_drop: ALL cuando el servicio lo soporte
- no-new-privileges:true
- prohibición privileged
- prohibición host network
- aislamiento de redes
- usuarios non-root cuando upstream lo permita
- validación HostConfig automática

## 4. Hardening incremental service-aware

Readonly rootfs:
- NO será obligatorio globalmente
- se aplicará únicamente tras validación operacional

Servicios upstream compatibles podrán migrarse progresivamente a:
- readonly rootfs
- tmpfs específicos
- runtime writable isolation

La ausencia temporal de readonly rootfs:
- NO constituye incumplimiento arquitectónico
- NO invalida gobernanza runtime
- NO implica regresión

mientras permanezcan activos:
- cap_drop
- no-new-privileges
- aislamiento runtime
- validación CI
- control de mounts

## 5. Servicios con excepciones explícitas

monitoring-smtp-relay
    Excepción aprobada:
        ejecución como root
        capabilities Linux específicas

    Justificación:
        compatibilidad upstream SMTP relay
        binding/red/network stack requerido

    Restricciones:
        red restringida
        mounts limitados
        sin docker.sock
        sin privileged
        revisión periódica obligatoria

PostgreSQL
    Excepción aprobada:
        readonly rootfs deshabilitado
        usuario upstream implícito

    Justificación:
        WAL
        runtime mutable legítimo
        compatibilidad upstream oficial

    Restricciones:
        sin publicación externa
        backend-net únicamente
        persistencia gobernada
        límites CPU/memoria activos

promtail
    Excepción aprobada:
        acceso readonly host-centric

    Justificación:
        shipping logs Docker
        observabilidad operacional

    Restricciones:
        readonly estricto
        sin control plane Docker
        sin docker.sock

6. Arquitectura Compose
La plataforma adopta oficialmente:
    arquitectura Compose distribuida

No existe obligación de:
    compose raíz único

El tooling deberá:
    soportar multi-compose discovery
    descubrir stacks automáticamente
    correlacionar runtime federado

Quedan prohibidas:
    suposiciones hardcoded sobre compose monolítico

# Consecuencias

Positivas
- reducción de ambigüedad operacional
- hardening compatible con upstream
- menor riesgo de regresiones
- enforcement CI realista
- mayor auditabilidad
- reducción de drift runtime
- separación clara entre:
    baseline obligatorio
    excepción válida
    deuda técnica
    hardening diferido

Negativas
- mayor complejidad documental
- necesidad de mantener excepciones explícitas
- auditorías runtime más sofisticadas
- necesidad de tooling multi-compose

# Validación

Las auditorías deberán validar automáticamente:
    Seguridad
        privileged=true
        docker.sock
        network_mode=host
        mounts RW peligrosos
        publicación externa indebida
        capabilities no justificadas

    Runtime
        usuarios runtime
        SecurityOpt
        healthchecks
        restart policies
        segmentación de redes
        readonly compatibility

    Arquitectura
        descubrimiento compose distribuido
        coherencia HostConfig
        correlación runtime vs compose
        clasificación de excepciones

# Estado objetivo

El entorno PRO deberá permanecer:
    gobernado
    auditable
    reproducible
    sin privilegios implícitos
    sin exposición externa indebida
    compatible operacionalmente
    endurecido progresivamente
    validado automáticamente

La prioridad arquitectónica oficial pasa a ser:
    estabilidad operacional
    enforcement incremental
    auditabilidad
    compatibilidad upstream
    reducción progresiva de superficie de ataque

## Relación con otros ADR

## Estado
