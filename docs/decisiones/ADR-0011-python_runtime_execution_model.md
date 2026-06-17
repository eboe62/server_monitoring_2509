# ADR-0011 - Python Runtime Execution Model (Determinismo)

Status: APPROVED
Date: 2026-03-05
Decision Type: REVIEW_REQUIRED
Scope: Runtime
Category: RUNTIME
Tags: REVIEW_REQUIRED
Related ADRs: ADR-0002, ADR-0003, ADR-0012
Supersedes: NONE
Superseded By: NONE
Validation Reference: NONE

## Contexto
El sistema server_monitoring incluye scripts operativos escritos en Python para:
- tareas de monitorización
- utilidades operativas
- automatizaciones ejecutadas por cron

En la arquitectura inicial del proyecto no estaba claramente definido:
- dónde debía residir el runtime Python,
- cómo debían ejecutarse los módulos del proyecto,
- qué relación existía entre runtime Python, contenedores y cron,
- ni cómo mantener coherencia operativa entre ejecución local, cron y contenedores.

Esto generaba varias ambigüedades:
- Posible instalación de Python en el host.
- Uso de wrappers bash para invocar scripts.
- Dependencias Python distribuidas en distintos lugares.
- Falta de aislamiento del entorno de ejecución.

Dado que el proyecto evoluciona hacia un modelo híbrido Host-Controlled Docker Compose IaC con runtime funcional containerizado, es necesario definir un modelo explícito para la ejecución de código Python.

## Decisión
La lógica funcional Python del proyecto se ejecutará exclusivamente dentro de contenedores Docker.

El host podrá ejecutar tooling operacional asociado a:
- auditoría IaC
- validaciones Compose
- parsing estructural
- orquestación Docker Compose
- verificaciones CI/runtime
- automatismos declarativos host-side

Estas excepciones no deben contener lógica funcional de negocio.

Los scripts Python se ejecutarán desde contenedores pertenecientes al Infra-Stack, principalmente el contenedor monitoring-cron.

Principios adoptados:

1 — Separación entre runtime funcional y control-plane operacional

El host se mantiene como:
- runtime Docker Compose standalone
- control-plane operacional
- entorno IaC declarativo
- plataforma de validación y auditoría

El host no debe utilizarse como:
- runtime funcional de negocio
- entorno persistente de ejecución de aplicación

Sin embargo, sí puede ejecutar:
- tooling operacional
- validaciones estructurales
- automatismos declarativos
- wrappers CI/runtime

2 — Runtime Python contenido en contenedores
  Los scripts Python se ejecutan desde contenedores que incluyen:
  - intérprete Python
  - dependencias necesarias
  - scripts versionados en el repositorio

  Modelo resultante:
    Infra-Stack
    monitoring-cron
      ├ cron daemon
      ├ python runtime
      └ scripts python

3 — Ejecución directa desde cron
Los cronjobs invocan directamente los scripts Python.
  Ejemplo:
  cron
    └ python /opt/monitoring/scripts/check_disk.py

  No se utilizan:
  - wrappers bash
  - capas intermedias de ejecución

4 — Dependencias gestionadas dentro del contenedor
Las dependencias Python se gestionan mediante:
  requirements.txt
  instaladas durante el build de la imagen.

  Ejemplo conceptual:
  Dockerfile

  COPY requirements.txt
  RUN pip install -r requirements.txt

Esto garantiza:
- reproducibilidad
- aislamiento
- versionado del entorno

5 — Los scripts Python son utilidades operativas
Los scripts Python en este sistema:
- realizan tareas de infraestructura
- ejecutan verificaciones
- automatizan operaciones

No implementan:
- servicios persistentes
- lógica de negocio compleja

## Opciones consideradas
Opción A — Python instalado en el host

  host
    └ python scripts

  Ventajas:
  - simplicidad inicial

  Inconvenientes:
  - rompe la separación entre:
      - runtime funcional containerizado
      - control-plane operacional host-side
  - incrementa dependencias funcionales fuera del runtime controlado
  - degrada reproducibilidad operacional
  - dificulta trazabilidad IaC

  Resultado: rechazada

Opción B — Python distribuido en varios contenedores
  container A
  container B
  container C
    └ python runtime

  Ventajas:
  - encapsulación
  Inconvenientes:
  - duplicación de runtimes
  - mayor complejidad operativa

  Resultado: rechazada

Opción C — Runtime Python centralizado en contenedor infra
Resultado: RECHAZADA de forma definitiva.
Motivo:
- Introduce acoplamiento innecesario entre servicios independientes.
- Dificulta la validación aislada y paralela en pipelines de CI/CD.
- Rompe el principio de autonomía e independencia de stacks operativos.

Opción D — Runtime Python autónomo por stack (Seleccionada)
Cada stack (p.e. monitoring-python, monitoring-cron) se rige bajo las siguientes directrices:
- Define su propio runtime Python aislado.
- Instala exclusivamente sus dependencias en build-time (requirements.txt).
- Es completamente independiente tanto en fase de build como en ejecución runntime, garantizando la resiliencia aislada del entorno.

Resultado: aceptada.


## Consecuencias
Positivas
- arquitectura coherente con Docker
- entorno Python reproducible
- eliminación de dependencias del host
- despliegue completamente versionado

Negativas
- algunos scripts pueden requerir herramientas adicionales en la imagen
- las utilidades Python se distribuyen entre stacks según responsabilidad:
    monitoring-python → ejecución manual / scripts
    monitoring-cron → ejecución programada

Ambos son independientes a nivel de runtime

El runtime Python containerizado NO debe asumir acceso obligatorio al control-plane Docker del host.

Las operaciones de:
- docker compose
- docker inspect
- docker ps
- docker compose config

pueden ejecutarse desde tooling operacional host-side cuando:
- el runtime containerizado no disponga de Docker CLI
- no exista acceso a docker.sock
- el modelo operacional priorice reducción de superficie de ataque
- el fallback host-side esté explícitamente documentado mediante ADR

La ejecución de:
- docker compose
- docker inspect
- docker ps
- docker compose config

queda fuera del alcance operacional garantizado del runtime Python salvo excepción explícitamente documentada.

## Relación con otros ADR
Este ADR complementa:
  ADR-0010 — arquitectura del runtime cron
  ADR-0009 — estrategia de backups PostgreSQL

Conjuntamente definen:

Infra-Stack
  monitoring-cron
    ├ cron runtime
    ├ python runtime
    └ tareas programadas
