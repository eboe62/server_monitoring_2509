# ADR-0018 – Modelo de Seguridad Runtime Docker y Requisitos de Resiliencia

Fecha: 2026-04-05
Estado: Aprobado
Contexto: server_monitoring_2509

## Contexto
Durante la FASE 5 se valida el comportamiento del sistema bajo condiciones reales de operación:
- Fallos de contenedores (crash)
- Fallos de base de datos
- Fallos de red (parcialmente controlables en entorno Docker)
- Recuperación automática
- Observabilidad activa durante incidencias

Adicionalmente, se formaliza un modelo explícito de:
- Seguridad en runtime de contenedores Docker
- Uso controlado de privilegios (docker.sock, capabilities, usuario)
- Reglas de exposición de red
- Requisitos mínimos de resiliencia verificables mediante tests automatizados

## Decisión
Se establecen dos bloques normativos obligatorios:

# 1️⃣ Modelo de Seguridad Runtime Docker

## 1.1 Principios generales
- El host NO ejecuta lógica funcional de aplicación
- La ejecución funcional se realiza dentro de contenedores
- El host puede ejecutar tooling operacional asociado a:
    - Docker Compose
    - validaciones runtime
    - auditoría estructural
    - automatización declarativa
    - verificaciones CI/IaC
- Se aplica principio de mínimo privilegio
- Toda excepción debe estar documentada en ADR

Cada contenedor funcional:
- define su propio entorno de ejecución
- evita dependencias implícitas con otros stacks

El control-plane operacional host-side:
- no debe introducir acoplamiento funcional
- debe permanecer declarativo y auditado

## 1.2 Usuarios en contenedores
Regla:
- Los contenedores deben ejecutarse como usuario no root siempre que sea viable

Excepción:
- Infra-stacks pueden usar root si es necesario (ej: postfix, docker tooling)

Control:
- docker inspect <container> | grep User

## 1.3 Capacidades Linux (capabilities)
Regla:
- cap_drop: ALL por defecto
- Añadir únicamente capacidades necesarias

## 1.4 Sistema de archivos

Regla:
- read_only: true cuando sea compatible con el servicio

Objetivo:
- Reducir superficie de ataque en runtime

## 1.5 Exposición de puertos
Reglas:
Micro-stacks:
- NO deben usar ports

Servicios internos accesibles localmente:
- Bind a loopback:
  127.0.0.1:<host_port>:<container_port>

Servicios públicos:
- Solo 80 y 443 expuestos en host

Control:
- docker ps --format "{{.Ports}}"
  ss -tulpn

## 1.6 Uso de docker.sock
Regla:
- Permitido SOLO bajo excepción ADR explícita y documentada
- El uso de docker.sock debe considerarse privilegio equivalente a root host

Prohibido:
- En micro-stacks (ops/services/)
- En TOOLBOX_RUNTIME
- En runtimes operativos persistentes utilizados únicamente para tooling
- Como dependencia implícita de validaciones CI/runtime

El acceso a docker.sock:
- no puede asumirse como capacidad base del sistema
- debe minimizarse progresivamente
- debe sustituirse por validaciones host-side estructuradas cuando sea viable

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
- grep -R "docker.sock" ops/

## 1.7 Imágenes Docker

Reglas:
- Prohibido uso de :latest
- Versionado explícito
- Imágenes minimalistas

Objetivo:
- Reproducibilidad y reducción de superficie de ataque

## 1.8 Secrets
Reglas:
- No versionar secrets
- No incluir secrets en imágene

## 1.9 Validación automática de seguridad

La seguridad runtime debe validarse mediante:

  make test-security-runtime

Este test debe verificar:
- usuario (root vs no root)
- exposición de puertos
- uso de docker.sock
- coherencia básica de runtime

2️⃣ Requisitos de Resiliencia

## 2.1 Definición
El sistema debe ser capaz de:
- Detectar fallos
- Degradarse de forma controlada cuando sea posible
- Recuperarse automáticamente
- Mantener observabilidad durante incidencias

La resiliencia se garantiza a nivel de contenedor individual.
Cada servicio debe:
- poder reiniciarse de forma independiente
- no depender de runtime compartido
- mantener funcionamiento degradado si otros servicios fallan

Nota:
La degradación de red puede no ser completamente determinista en Docker.

## 2.2 Requisitos obligatorios
R1 – Reinicio automático
Todos los contenedores deben tener política de restart tras un fallo

  Control:
    docker inspect <container> | grep RestartPolicy

Validación:
  make test-resilience-restart

R2 – Healthchecks
Servicios críticos deben exponer estado

  Estados esperados:
    healthy
    unhealthy

  Control:
    docker inspect <container> | grep Health

Validación:
  make test-python-health

R3 – Recuperación ante crash
El sistema debe reiniciarse y volver a healthy:
  - Reiniciar contenedores automáticamente
  - Recuperar estado healthy

  Validación:
    make test-resilience-restart

R4 – Resiliencia ante fallo de base de datos
 El sistema debe:
  - Detectar caida DB
  - Recuperarse automáticamente

  Validación:
    make test-resilience-db

R5 – Resiliencia de red
El sistema debe:
  - Tolerar pérdida de conectividad
  - Recuperarse tras restauración


Nota:
La detección de degradación puede depender del healthcheck del servicio.

  Validación:
    make test-resilience-network

R6 – Observabilidad
El stack de observabilidad debe:
  - Permanecer operativo durante incidencias
  - Permitir consulta de logs

  Validación:
    make test-observability

R7 – Procesamiento asíncrono (cron)
Debe ejecutarse dentro de contenedor

  Validación:
    make test-cron-execution

R8 – SMTP resiliente (infraestructura)
El sistema debe:
  - Aceptar mensajes (Postfix OK)
  - Mantener cola operativa
  - Permitir trazabilidad vía logs

Validación:
  make test-smtp-all

  Nota:
  La entrega final depende de proveedor externo (ej. Postmark

## 2.3 Validación obligatoria
La resiliencia se valida mediante:
  make test-resilience-completo

Este test debe cubrir:
- crash
- DB failure
- network (best-effort)
- observability

## Justificación
- Alinea documentación con comportamiento real
- Permite validación automática en CI
- Reduce ambigüedad
- Refleja límites reales de Docker

## Consecuencias
- Seguridad verificable automáticamente
- Resiliencia basada en tests reales
- Mayor coherencia CI ↔ ADR

## Riesgos controlados
- Privilegios excesivos
- Exposición accidental de servicios
- Uso indebido de docker.sock
- Fallos no detectados en runtime
- Pérdida de observabilidad durante incidencias

## Fuera de alcance
- Orquestación avanzada (Kubernetes, Swarm)
- Gestión externa de secretos (Vault, etc.)
- Autoescalado

## Relación con otros ADR
ADR-0008 — Clasificación de servicios - Micro-stack vs Infraestructura Operativa
ADR-0014 — Docker Port Exposure Policy
ADR-0015 — Docker Network Exposure Model

## Estado
Aprobado.
