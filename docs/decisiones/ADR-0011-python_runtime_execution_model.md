# ADR-0011 - Python Runtime Execution Model

Fecha: 2026-03-05
Estado: Propuesto
Ámbito: server_monitoring

## Contexto
El sistema server_monitoring incluye scripts operativos escritos en Python para:
- tareas de monitorización
- utilidades operativas
- automatizaciones ejecutadas por cron

En la arquitectura inicial del proyecto no estaba claramente definido:
- dónde debía residir el runtime Python
- cómo se debían ejecutar los scripts
- qué relación tenían con los contenedores y con cron

Esto generaba varias ambigüedades:
- Posible instalación de Python en el host.
- Uso de wrappers bash para invocar scripts.
- Dependencias Python distribuidas en distintos lugares.
- Falta de aislamiento del entorno de ejecución.

Dado que el proyecto está evolucionando hacia una arquitectura container-first, es necesario definir un modelo explícito para la ejecución de código Python.

## Decisión
El runtime Python se ejecutará exclusivamente dentro de contenedores Docker, nunca en el host.
Los scripts Python se ejecutarán desde contenedores pertenecientes al Infra-Stack, principalmente el contenedor monitoring-cron.

Principios adoptados:

1 — Python no se instala en el host
  El host se mantiene como:
  - runtime Docker
  - base del sistema
  No se utiliza como entorno de ejecución de aplicaciones.

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
  - rompe el modelo container-first
  - dependencias fuera de control
  - difícil reproducibilidad

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
Resultado: rechazada
Motivo:
- introduce acoplamiento entre servicios
- dificulta la validación en CI/CD
- rompe el principio de autonomía de stacks

  Ventajas:
  - arquitectura simple
  - entorno reproducible
  - integración directa con cron
  - dependencias centralizadas

  Resultado: aceptada

Opción D — Runtime Python autónomo por stack
Cada stack (ej. monitoring-python, monitoring-cron):
- define su propio runtime Python
- instala sus dependencias
- es completamente independiente en build y ejecución
Resultado: aceptada

## Consecuencias
Positivas
- arquitectura coherente con Docker
- entorno Python reproducible
- eliminación de dependencias del host
- despliegue completamente versionado

Negativas
- las utilidades Python dependen del contenedor monitoring-cron
- algunos scripts pueden requerir herramientas adicionales en la imagen

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
