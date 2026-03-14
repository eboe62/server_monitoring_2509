# ADR-0012 — Separation of Host Cron vs Monitoring Cron

Fecha: 2026-03-12
Estado: Propuesto
Ámbito: server_monitoring

## Contexto
El sistema server_monitoring se despliega en un servidor VPS bajo una arquitectura basada en Infrastructure as Code y contenedores Docker.

Durante la fase de diseño surgió ambigüedad sobre dónde deben ejecutarse las tareas programadas del sistema.

Existen dos tipos distintos de automatismos:
  - Automatismos del sistema operativo (mantenimiento del host)
  - Automatismos propios del runtime del proyecto

Sin una separación explícita, las auditorías pueden interpretar incorrectamente que el host ejecuta lógica de aplicación.

## Decision
Se establece una separación explícita entre:
- Host Cron:
  El crontab del host se utiliza exclusivamente para tareas de mantenimiento del sistema operativo.

  Ejemplos permitidos:
    - rotación de logs del sistema
    - mantenimiento de paquetes
    - backups del host
    - hardening
    - monitorización del propio servidor

  El host no ejecuta lógica de aplicación del proyecto.

- Monitoring Cron Container:
  Las tareas programadas del runtime del proyecto se ejecutan mediante el contenedor:

  monitoring-cron

  Este contenedor ejecuta un cron interno (supercronic o equivalente) que lanza los módulos Python del proyecto.

  Ejemplo de ejecución válida:
  python3 -m log_ingestor.log_fail2ban_batch

  Estas tareas incluyen:
  - ingestión de logs
  - procesamiento de eventos
  - geolocalización de ataques
  - automatismos internos del sistema de monitorización

## Consecuencias
Ventajas
  - separación clara entre infraestructura y aplicación
  - cumplimiento del principio IaC
  - auditoría simplificada
  - menor superficie de ataque en el host
  - portabilidad del runtime

Implicaciones
  - el host nunca ejecuta módulos Python del proyecto
  - toda la lógica de aplicación se ejecuta dentro de contenedores
  - el contenedor monitoring-cron pasa a ser el scheduler oficial del runtime
