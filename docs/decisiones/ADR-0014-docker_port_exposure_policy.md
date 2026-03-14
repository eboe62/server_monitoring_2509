# ADR-0014 — Docker Port Exposure Policy

Fecha: 2026-03-14
Estado: Aprobado
Ámbito: server_monitoring

## Contexto
El proyecto server_monitoring adopta una arquitectura container-first donde los servicios se ejecutan dentro de contenedores Docker y se comunican mediante redes internas.

Docker permite publicar puertos mediante la directiva:
    ports:
        - host_port:container_port

Esta funcionalidad puede provocar:
  - exposición accidental de servicios internos, incluso cuando el firewall del host está configurado con políticas restrictivas
  - bypass del firewall del host
  - aumento de superficie de ataque
  - inconsistencias entre despliegues

Por tanto se requiere una política explícita para controlar la exposición de puertos Docker.

## Decisión

Se adopta una política restrictiva de exposición de puertos.

Regla general:
Los contenedores no deben publicar puertos hacia el host por defecto.

La comunicación entre servicios debe realizarse mediante:
  - redes Docker internas
  - resolución DNS interna de Docker

Cuando sea necesario exponer un servicio al host debe utilizarse restricción de interfaz:

    127.0.0.1:<host_port>:<container_port>

Ejemplo permitido:
    ports:
      "127.0.0.1:3001:3001"

Ejemplo prohibido:
    ports:
      "3001:3001"

## Servicios que no deben exponerse
Los siguientes servicios son considerados internos:
  - PostgreSQL
  - Loki
  - Promtail
  - contenedores runtime internos
  - contenedores de automatización o cron
Estos servicios deben ser accesibles únicamente desde la red Docker interna.
## Servicios que pueden exponerse bajo justificación
  - Grafana
  - SMTP relay (si se usa como gateway interno)
  - interfaces administrativas explícitas

Incluso en estos casos se recomienda:
  - bind a localhost
  - protección mediante reverse proxy
  - autenticación obligatoria

El firewall del host (UFW) continúa siendo el mecanismo principal de control perimetral.

La política estándar del host es:
- permitir SSH
- permitir HTTP/HTTPS
- bloquear todo el resto
La política de exposición de puertos Docker no sustituye al firewall, sino que lo complementa reduciendo exposición innecesaria.

## Consecuencias
Positivas:
- reducción de superficie de ataque
- aislamiento claro entre red interna de contenedores y host
- menor riesgo de exposición accidental
- coherencia con arquitectura container-first

Negativas:
- algunas interfaces administrativas requieren acceso mediante reverse proxy o SSH tunnel.

## Estado
Aprobado.
