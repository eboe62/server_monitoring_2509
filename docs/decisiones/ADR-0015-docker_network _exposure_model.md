# ADR-0015 — Docker Network Exposure Model

Status: APPROVED
Date: 2026-03-14
Decision Type: REVIEW_REQUIRED
Scope: Infrastructure
Category: INFRASTRUCTURE
Tags: REVIEW_REQUIRED
Related ADRs: ADR-0014, ADR-0021
Supersedes: NONE
Superseded By: NONE
Validation Reference: NONE

## Contexto
El proyecto server_monitoring adopta un modelo Host-Controlled Docker Compose IaC donde:
- los servicios funcionales se ejecutan dentro de contenedores Docker
- el control-plane operacional permanece parcialmente host-side
- la orquestación y auditoría Compose pueden ejecutarse desde el host

La comunicación funcional entre servicios se realiza principalmente mediante redes Docker internas.

Adicionalmente:
- ciertos mecanismos operacionales
- auditorías estructurales
- tooling de validación
- verificaciones Compose

pueden ejecutarse desde el host como parte del plano operacional IaC. Sin embargo, algunos servicios requieren diferentes niveles de accesibilidad:
  - acceso interno entre contenedores
  - acceso administrativo desde el host
  - acceso público controlado desde Internet

Sin una clasificación explícita de estos niveles de exposición pueden producirse:
  - exposiciones accidentales de puertos
  - inconsistencias entre stacks
  - errores de configuración de firewall
  - confusión entre servicios internos y públicos

Para evitarlo se define un modelo formal de exposición de red.

## Decisión
Se adopta un modelo de tres niveles de exposición de red para contenedores Docker.

Nivel 1 — Internal Only
Servicios accesibles únicamente desde redes Docker internas.

Características:
  - no publican puertos hacia el host
  - sólo accesibles mediante DNS interno Docker
  - conectados únicamente a redes internas del stack

Ejemplos típicos:
  - PostgreSQL
  - Promtail
  - workers internos
  - contenedores de automatización
  - contenedores de cron
  - contenedores de runtime interno

Ejemplo docker-compose:
    services:
      postgres:
        networks:
          - backend-net
        # sin ports

Nivel 2 — Host Local Access (Internal + Debug Loopback)
Servicios accesibles desde el host únicamente mediante loopback.

Características:
  - publicación de puertos restringida a 127.0.0.1
  - no accesibles directamente desde Internet
  - utilizados para acceso administrativo, debugging, validación operativa, testing manual
  - nunca deben exponerse en interfaces públicas (0.0.0.0)

Servicios típicos:
  - Grafana
  - Loki (para observabilidad/debug)

Ejemplo de exposición:
    ports:
      - "127.0.0.1:3001:3001"

Ejemplos típicos:
  - Grafana
  - interfaces administrativas
  - herramientas de diagnóstico

El acceso remoto debe realizarse mediante:
  - SSH tunnel
  - reverse proxy
  - VPN

El uso de exposición en loopback (127.0.0.1) debe estar justificado por necesidades operativas.
No debe utilizarse como mecanismo de comunicación entre servicios.

Nivel 3 — Public Access
Servicios accesibles desde Internet de forma explícita.

En este proyecto estos servicios deben exponerse preferiblemente mediante reverse proxy o infraestructura dedicada.

Características:
  - controlados por firewall del host
  - autenticación obligatoria
  - TLS obligatorio cuando aplica

Ejemplos típicos:
  - reverse proxy
  - gateways de API
  - servicios web públicos

El stack server_monitoring no expone directamente servicios de Nivel 3 por defecto.

## Reglas operativas
Regla 1
Todos los servicios deben clasificarse explícitamente en uno de los tres niveles definidos.

Regla 2
NO usar ports: Los servicios internos (Nivel 1) no deben definir la directiva "ports" en Docker Compose.


Regla 3
Los servicios accesibles localmente (Nivel 2) deben usar obligatoriamente binding a loopback:
    127.0.0.1:<host_port>:<container_port>

Regla 4
Los servicios de exposición pública (Nivel 3) debe justificarse mediante documentación explícita y solo 80/443 gestionados por el host

## Consecuencias
Positivas
- modelo claro de exposición de red
- reducción de superficie de ataque
- coherencia entre stacks
- facilidad para auditar configuraciones Docker

Negativas
- mayor disciplina en configuración
- necesidad de documentación adicional para servicios públicos

## Relación con otros ADR
ADR-0014 — Docker Port Exposure Policy: define la política específica de publicación de puertos.
ADR-0015 — Docker Network Exposure Model: define el modelo conceptual de niveles de exposición.

## Estado
Aprobado.
