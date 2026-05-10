# ADR-0025 — Normalización del modelo de configuración SMTP

Fecha: 2026-05-10
Estado: Propuesta

## Contexto

El proyecto gestiona múltiples stacks y servicios que envían notificaciones por correo electrónico (alertas operativas, auditoría, pruebas). Históricamente existía lógica ambigua para la carga de credenciales SMTP desde archivos de secrets en host, variables de entorno o fallbacks silenciosos en tiempo de ejecución. Esto provocó:
- Errores en tiempo de ejecución difíciles de diagnosticar (p.ej. PermissionError interpretado erróneamente).
- Procesos que no deberían acceder a credenciales intentaban leer secrets del host, rompiendo el principio de mínimo privilegio.
- Dificultad para reproducir y testear comportamientos en CI y local.

Además, existe una necesidad operativa de soportar dos modos de operación claramente diferenciados:
- `relay`: el servicio sólo relaya correo (no requiere credenciales)
- `auth`: el servicio envía correo autenticándose contra un servidor SMTP

## Problema

Falta de una especificación clara y reproducible sobre cómo y cuándo los servicios deben consumir credenciales SMTP (secrets del host vs variables de entorno), y ausencia de un modo explícito que permita distinguir procesos que deben o no debe leer secrets. Esto produce riesgos de seguridad (exposición de secrets) y de operación (fallos silenciosos, pruebas no deterministas).

## Decisión

Normalizar el modelo de configuración SMTP con las siguientes reglas:

1. Introducir la variable de entorno obligatoria `SMTP_MODE`con valores permitidos `relay` y `auth`.

2. Comportamiento por `SMTP_MODE`:
   - `relay`: procesos en este modo no deben intentar leer secretos desde el host; sólo usan variables de entorno públicas y deben funcionar si las credenciales no están presentes.
   - `auth`: procesos en este modo requieren credenciales y, si `secrets` requeridos no están disponibles, deben fallar con un error claro en arranque (fail-fast).

3. API runtime y librería de configuración (`monitoring.common.config`):
   - Exponer `init_config()` y respetar `SMTP_MODE`.
   - Cuando `SMTP_MODE=relay`, callers deben invocar `init_config()` para evitar intentos de lectura de secrets.
   - Cuando `SMTP_MODE=auth`, `init_config()` valida la presencia de secrets y falla si faltan.

4. Docker Compose / stacks:
   - Cada stack debe declarar explícitamente `SMTP_MODE` en su `environment`.
   - Sólo el stack autorizado para autenticación (p.ej. `smtp_relay`) debe montar los archivos de secrets desde el host. Los mounts de secrets deben ser read-only.

5. Permisos host de secrets:
   - Los archivos de secrets en host serán preferentemente `0400` o `0440` y con propiedad y grupos controlados por el equipo de despliegue. Se documentará una política en un ADR o RULES anexa (pendiente: implementación operativa y guías de provisioning).

6. Logging y mensajes operativos:
   - La librería de configuración debe emitir mensajes claros y no ambiguos sobre el estado de carga de secrets (p.ej. "SMTP_MODE=relay — secrets skipped" o "SMTP_MODE=auth — missing SMTP_USER/SMTP_PASS: aborting").

7. Tests y CI:
   - Añadir pruebas unitarias e integración que verifiquen comportamiento en `relay` y `auth` (fail-fast en `auth` si faltan credenciales).
   - El pipeline CI debe ejecutar tests con `PYTHONPATH=src` y un job que valide que stacks que no requieren auth no tengan mounts de secrets en sus compose files (check estático de compose y variables expuestas).

## Razonamiento

Separar claramente los modos evita ambigüedades operativas y reduce riesgo de exposición de credenciales. El patrón `SMTP_MODE` es una mínima y explícita inversión de control que permite a la misma librería de configuración soportar ambos comportamientos sin heurísticas implícitas ni lectura silenciosa de secrets.

Fail-fast en `auth` mejora observabilidad y evita procesos parcialmente inicializados que luego fallan en runtime con mensajes difíciles de depurar.

## Alternativas consideradas

- Mantener el comportamiento actual (heurísticas y fallbacks silenciosos). Rechazada por los problemas de seguridad y diagnóstico descritos arriba.
- Usar un archivo de configuración global en lugar de `SMTP_MODE`. Rechazada por complejidad operativa y porque no cambia la necesidad de distinguir runtime entre relay/auth.

## Consecuencias

- Cambios en la librería de configuración (`monitoring.common.config`) y en todos los entrypoints: se debe revisar que aquellos procesos que no requieren credenciales llamen `init_config()`.
- Actualización de los `compose.yml` de stacks para declarar `SMTP_MODE`.
- Añadir documentación operativa sobre permisos de secrets y proceso de aprovisionamiento (host paths, permisos, owner/group, rotación).

## Plan de implementación

1. Añadir el ADR (este documento) y discutirlo con el equipo de infra/devops.
2. Implementar y publicar cambios mínimos en `monitoring.common.config` (ya prototipado en PR/branch asociado: `gestion_secretos`).
3. Actualizar entrypoints y `compose.yml` de stacks afectados (p.e. `smtp_relay` -> `SMTP_MODE=auth`, `cron` y `python` stacks -> `SMTP_MODE=relay`).
4. Añadir tests unitarios e integración que validen ambos modos (ya existen pruebas iniciales en `tests/unit` y `tests/integration`).
5. Documentar la política de permisos de secrets y publicar runbook de aprovisionamiento (host paths, permisos, owner/group, rotación).

## Referencias

- ADR-0024 — Container Privilege Exception Policy: [docs/decisiones/ADR-0024-Container_Privilege_Exception_Policy.md](docs/decisiones/ADR-0024-Container_Privilege_Exception_Policy.md)
- Implementación actual en rama `gestion_secretos` (ejemplos de código y tests en `src/monitoring/common/config.py` y `tests/`).

## Estado

Propuesta — pendiente revisión y aprobación por el equipo de arquitectura e infra.
