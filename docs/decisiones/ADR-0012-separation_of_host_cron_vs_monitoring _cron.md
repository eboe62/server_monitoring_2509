# ADR-0012 — Separation of Host Cron vs Monitoring Cron (Runtime reproducible)

Fecha: 2026-03-12
Estado: ACCEPTED
Ámbito: server_monitoring_2509

## Contexto
El sistema server_monitoring se despliega en un servidor VPS bajo una arquitectura basada en Infrastructure as Code y contenedores Docker.

Durante la fase de diseño surgió ambigüedad sobre dónde deben ejecutarse las tareas programadas del sistema.

Existen dos tipos distintos de automatismos:
  - Automatismos del sistema operativo (mantenimiento del host)
  - Automatismos propios del runtime del proyecto

Sin una separación explícita, las auditorías pueden interpretar incorrectamente que el host ejecuta lógica de aplicación o asumir dependencias indebidas entre host y runtime Docker.

## Decisión
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

  Este contenedor ejecuta un cron interno (supercronic o equivalente) que invoca módulos Python del proyecto siguiendo el modelo oficial de ejecución definido en ADR-0011.

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
  - el host nunca ejecuta módulos Python del proyecto,
  - toda la lógica de aplicación se ejecuta dentro de contenedores,
  - monitoring-cron pasa a ser el scheduler oficial del runtime,
  - se refuerza el desacoplamiento entre host y runtime definido en ADR-0005.

## Referencias

- ADR-0005 — Política de inicialización runtime e import-time.
