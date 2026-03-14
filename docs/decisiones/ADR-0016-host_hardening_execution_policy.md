# ADR-0016 — Host Hardening Execution Policy

Fecha: 2026-03-14
Estado: Aprobado
Ámbito: server_monitoring

## Contexto
El proyecto server_monitoring adopta una arquitectura container-first basada en Infraestructura como Código (IaC).

Principios fundamentales del proyecto:
  - El host no ejecuta lógica de aplicación
  - Todo procesamiento funcional se ejecuta dentro de contenedores
  - El comportamiento del sistema se define declarativamente mediante Docker Compose y el repositorio Git

Sin embargo, existen ciertas tareas que deben ejecutarse directamente en el host porque afectan a:
  - configuración del kernel
  - configuración del sistema operativo
  - límites de recursos del runtime Docker
  - políticas de seguridad del sistema

Estas tareas no forman parte de la lógica de aplicación, sino del **endurecimiento y configuración del host**.

Ejemplos presentes en el proyecto:
  - configure_docker_limits.sh
  - apply_ssh_ratelimit.sh

Si no se define explícitamente este modelo, puede parecer que estas ejecuciones violan el principio de arquitectura container-first.

Por ello se establece una política clara para la ejecución de scripts de hardening del host.

## Decisión
Se distingue explícitamente entre dos tipos de ejecución:
  - Lógica de aplicación
  - Configuración y hardening del host

### Lógica de aplicación
La lógica de aplicación incluye:
  - scripts Python
  - ingesta de logs
  - monitorización de recursos
  - tareas programadas del sistema
  - procesamiento de datos

Estas tareas deben ejecutarse exclusivamente dentro de contenedores Docker.

En este proyecto se ejecutan mediante:
  - contenedor monitoring-python
  - contenedor monitoring-cron
  - scheduler Supercronic

El host no debe ejecutar directamente código de aplicación del proyecto.

### Hardening y configuración del host
Algunas tareas afectan al sistema base y deben ejecutarse directamente en el host.

Ejemplos:
  - configuración de límites de Docker
  - políticas de seguridad SSH
  - parámetros del kernel
  - limitación de recursos del sistema
  - protección frente a ataques de fuerza bruta

Estas tareas se consideran **configuración de infraestructura** y están fuera del ámbito de ejecución de contenedores.

Por tanto pueden ejecutarse en el host.

## Modelo operativo
Las tareas de hardening del host deben cumplir las siguientes reglas.

Regla 1:
Los scripts deben estar claramente identificados como scripts de infraestructura.

Ejemplo de ubicación:
    /opt/monitoring/scripts/

Regla 2:
Estos scripts no deben contener lógica de aplicación.

Su objetivo debe limitarse a:
  - configuración del sistema
  - seguridad del host
  - políticas del runtime Docker

Regla 3:
Los scripts deben ser idempotentes siempre que sea posible, de forma que su ejecución repetida no produzca efectos no deseados.

Regla 4:
La ejecución puede realizarse mediante:
  - systemd
  - scripts de bootstrap del servidor
  - ejecución manual controlada

El proyecto evita utilizar cron del host para lógica de aplicación.

## Ejemplos en el proyecto
Scripts actuales que entran en esta categoría:
configure_docker_limits.sh
  - aplica límites de CPU y memoria a contenedores
  - evita saturación del host

apply_ssh_ratelimit.sh
  - configura limitación de conexiones SSH
  - protege frente a ataques masivos

Estos scripts forman parte del hardening del host y no de la lógica funcional del sistema.

## Consecuencias
Positivas
- clarificación del modelo container-first
- separación explícita entre aplicación e infraestructura
- reducción de ambigüedad arquitectónica
- facilidad para auditar cumplimiento del modelo IaC

Negativas
- necesidad de documentar correctamente scripts del host
- riesgo de confusión si se mezclan responsabilidades

## Relación con otros ADR
ADR-0014 — Docker Port Exposure Policy define la política de exposición de puertos.
ADR-0015 — Docker Network Exposure Model define los niveles de accesibilidad de red de los contenedores.
ADR-0016 — Host Hardening Execution Policy define qué tipo de tareas pueden ejecutarse directamente en el host sin violar el modelo container-first.

## Estado
Aprobado.
