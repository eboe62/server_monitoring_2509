# ADR-0014 — Docker Port Exposure Policy

Fecha: 2026-03-14
Estado: Aprobado
Ámbito: server_monitoring_2509

## Contexto
El proyecto server_monitoring adopta un modelo Host-Controlled Docker Compose IaC donde:
- los servicios funcionales se ejecutan dentro de contenedores Docker
- el control-plane operacional permanece parcialmente host-side
- la orquestación y auditoría Compose pueden ejecutarse desde el host


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

Excepción controlada:
Algunos servicios pueden publicar puertos cuando exista justificación operativa explícita y se cumplan las siguientes restricciones:
  - el puerto debe enlazarse a la interfaz loopback del host
  - el acceso externo debe controlarse mediante firewall o proxy
  - el servicio debe requerir autenticación

La comunicación entre servicios debe realizarse mediante:
  - redes Docker internas
  - resolución DNS interna de Docker

Cuando sea necesario exponer un servicio al host debe utilizarse restricción de interfaz:
    127.0.0.1:<host_port>:<container_port>

Tipos de exposición de puertos:
- Exposición pública:
    ports:
      "3001:3001"
  Esta forma queda prohibida ya que publica el servicio en todas las interfaces del host.

Exposición restringida a loopback:
    ports:
      "127.0.0.1:3001:3000"
  Esta forma es la única permitida cuando se requiere acceso administrativo desde el host.

## Servicios que no deben exponerse
Los siguientes servicios son considerados internos:
  - PostgreSQL
  - Loki
  - Promtail
  - contenedores runtime internos
  - contenedores de automatización o cron
Estos servicios deben ser accesibles únicamente desde la red Docker interna.

## Servicios que pueden exponerse bajo justificación
Algunos servicios pueden requerir exposición controlada hacia el host (por ejemplo para acceso administrativo o debugging local).

Ejemplos típicos:
  - Grafana
  - SMTP relay utilizado como gateway interno
  - interfaces administrativas explícitas

En estos casos la exposición DEBE restringirse a localhost:
    127.0.0.1:<host_port>:<container_port>

Ejemplo permitido:
    ports:
      - "127.0.0.1:3001:3001"

Queda prohibida la publicación global de puertos:
    ports:
      - "3001:3001"

Incluso en servicios autorizados.

Si se requiere acceso externo deberá realizarse mediante:
  - reverse proxy
  - túnel SSH
  - VPN

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
- coherencia con el modelo Host-Controlled Docker Compose IaC
- separación clara entre:
    - plano de datos containerizado
    - control-plane operacional host-side

Negativas:
- algunas interfaces administrativas requieren acceso mediante reverse proxy o SSH tunnel.

## Estado
Aprobado.
