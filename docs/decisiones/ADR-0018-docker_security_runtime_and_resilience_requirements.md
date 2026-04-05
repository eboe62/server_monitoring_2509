# ADR-0018 – Modelo de Seguridad Runtime Docker y Requisitos de Resiliencia

Fecha: 2026-04-05
Estado: Aprobado
Contexto: server_monitoring

## Contexto
Durante la FASE 5 se valida el comportamiento del sistema bajo condiciones reales de operación:
- Fallos de contenedores (crash)
- Fallos de base de datos
- Fallos de red
- Recuperación automática
- Observabilidad activa durante incidencias

Adicionalmente, se detecta la necesidad de formalizar un modelo explícito de:
- Seguridad en runtime de contenedores Docker
- Uso controlado de privilegios (docker.sock, capabilities, usuario)
- Reglas de exposición de red
- Requisitos mínimos de resiliencia verificables

## Decisión
Se establecen dos bloques normativos obligatorios:

# 1️⃣ Modelo de Seguridad Runtime Docker

## 1.1 Principios generales
- El host NO ejecuta lógica de aplicación
- Toda ejecución se realiza dentro de contenedores
- Se aplica principio de mínimo privilegio
- Toda excepción debe estar documentada en ADR

## 1.2 Usuarios en contenedores
Regla:
- Los contenedores deben ejecutarse con usuario no root siempre que sea viable

Excepción:
- Solo infra-stacks podrán ejecutar como root cuando sea estrictamente necesario

Control:
- Debe poder verificarse mediante:
  docker inspect <container> | grep User

## 1.3 Capacidades Linux (capabilities)
Regla:
- cap_drop: ALL por defecto
- Añadir únicamente capacidades necesarias

##  1.4 Sistema de archivos
Regla:
  read_only: true cuando sea compatible con el servicio

Objetivo:
- Reducir superficie de ataque en runtime

##  1.5 Exposición de puertos
Reglas:
Micro-stacks:
- NO deben usar ports

Servicios internos accesibles localmente:
- Bind obligatorio a loopback:
  127.0.0.1:<host_port>:<container_port>

Servicios públicos:
- Solo 80 y 443 expuestos en host

Control:
  docker ps --format "{{.Ports}}"
  ss -tulpn

##  1.6 Uso de docker.sock
Regla:
- Permitido SOLO en infra-stacks (ops/docker/)

Prohibido:
- En micro-stacks (ops/services/)

Riesgo:
- Equivalente a acceso root sobre el host Docker

Mitigaciones obligatorias:
- No exposición de puertos del contenedor
- Acceso únicamente desde red interna Docker
- No ejecución de código dinámico o no auditado
- Scripts versionados en repositorio
- Registro de actividad en logs
- Justificación explícita en ADR o README

Control:
  grep -R "docker.sock" ops/

##  1.7 Imágenes Docker
Reglas:
- Prohibido uso de :latest en producción
- Versionado explícito obligatorio
- Imágenes minimalistas

Objetivo:
- Reproducibilidad y reducción de superficie de ataque

##  1.8 Secrets
Reglas:
- No versionar secrets
- No incluir secrets en imágenes
- Uso de variables de entorno o mecanismos externos

2️⃣ Requisitos de Resiliencia

## 2.1 Definición
El sistema debe ser capaz de:
- Detectar fallos
- Degradarse de forma controlada
- Recuperarse automáticamente
- Mantener observabilidad durante incidencias

## 2.2 Requisitos obligatorios
R1 – Reinicio automático
  Todos los contenedores deben tener política de restart

  Control:
    docker inspect <container> | grep RestartPolicy

R2 – Healthchecks
  Servicios críticos deben definir healthcheck

  Estados esperados:
    healthy
    unhealthy

  Control:
    docker inspect <container> | grep Health

R3 – Recuperación ante crash
  El sistema debe:
  - Reiniciar contenedores automáticamente
  - Recuperar estado healthy

  Validación:
    make test-resilience-restart

R4 – Resiliencia ante fallo de base de datos
  El sistema debe:
  - Detectar fallo DB
  - Degradarse correctamente
  - Recuperarse automáticamente

  Validación:
    make test-resilience-db
    R5 – Resiliencia de red

R5 – Resiliencia de red
  El sistema debe:
  - Detectar pérdida de conectividad
  - Recuperarse tras restauración

  Validación:
    make test-resilience-network

R6 – Observabilidad durante fallos
  El stack de observabilidad debe:
  - Permanecer operativo durante incidencias
  - Permitir consulta de logs

  Validación:
    make test-observability

R7 – Procesamiento asíncrono (cron)
  El sistema debe:
  - Ejecutar tareas programadas en contenedor (no host)
  - Mantener ejecución tras reinicios

  Validación:
    make test-cron-execution

R8 – SMTP resiliente (infraestructura)
  El sistema debe:
  - Aceptar mensajes (Postfix OK)
  - Mantener cola operativa
  - Reintentar envío

  Nota:
  La entrega final depende de proveedor externo (ej. Postmark)

## 2.3 Validación obligatoria
La resiliencia debe validarse mediante:
  make test-resilience-completo

Este test debe cubrir:
- crash
- DB failure
- network failure
- observability

Justificación
- Centraliza reglas críticas de seguridad y resiliencia
- Elimina ambigüedad entre ADRs previos
- Permite auditoría automática
- Refleja comportamiento real validado en entorno
- Reduce riesgos de seguridad en runtime

Consecuencias
- Se formaliza un modelo de seguridad runtime verificable
- Se exige resiliencia como requisito explícito
- Se facilita auditoría continua (FASE 4/5)
- Se mejora mantenibilidad del sistema

Riesgos controlados
- Escalada de privilegios en contenedores
- Exposición accidental de servicios
- Uso inseguro de docker.sock
- Fallos no detectados en runtime
- Pérdida de observabilidad durante incidencias

Fuera de alcance
- Orquestación avanzada (Kubernetes, Swarm)
- Gestión externa de secretos (Vault, etc.)
- Autoescalado

## Relación con otros ADR
ADR-0006 — Gobernanza de imagen base monitoring-base
ADR-0008 — Clasificación de servicios - Micro-stack vs Infraestructura Operativa
ADR-0014 — Docker Port Exposure Policy
ADR-0015 — Docker Network Exposure Model

## Estado
Aprobado.
