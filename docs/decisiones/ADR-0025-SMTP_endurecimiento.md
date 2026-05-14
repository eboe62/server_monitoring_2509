# ADR-0025 — Modelo SMTP explícito y endurecimiento de configuración

Fecha: 2026-05-13
Estado: Aprobado

## Contexto

La plataforma gestiona múltiples stacks y servicios que generan notificaciones por correo electrónico.
Históricamente la configuración SMTP evolucionó mediante heurísticas y convenciones implícitas, produciendo:
- Lectura ambigua de credenciales desde filesystem y variables de entorno.
- Inicialización de configuración sensible durante import-time, generando side-effects durante imports y tests. La política general de desacoplamiento runtime e inicialización explícita queda definida en ADR-0005; este ADR especializa dicha política para el caso concreto de configuración SMTP.
- Diferencias de comportamiento entre stacks y entrypoints.
- Dependencia implícita de credenciales SMTP provisionadas desde infraestructura.
- Comportamientos no deterministas entre local, CI y producción.

Esto generaba:
- Riesgo de exposición innecesaria de secrets.
- Violaciones del principio de mínimo privilegio.
- Fallos difíciles de diagnosticar.
- Tests frágiles y dependientes del entorno.
- Side-effects durante importación de módulos.
- Ambigüedad operativa sobre qué procesos requerían autenticación SMTP.

La arquitectura necesita soportar dos modos diferenciados:

- relay
   El proceso relaya correo sin autenticación SMTP y no debe depender de secrets del host.
- auth
   El proceso requiere autenticación SMTP y debe fallar explícitamente si las credenciales no están disponibles.

## Problema

La ausencia de un modelo SMTP explícito provocaba:
- Lectura accidental de secrets en procesos que no debían consumirlos.
- Dependencias implícitas de mecanismos de provisión de credenciales SMTP.
- Heurísticas difíciles de auditar y mantener.
- Side-effects durante importaciones Python.
- Inconsistencias entre CI, local y producción.
- Fallos silenciosos o ambiguos en runtime.

La plataforma necesita:
- Separar explícitamente los modos relay y auth.
- Aplicar principio de mínimo privilegio.
- Eliminar inicialización sensible durante import-time.
- Garantizar comportamiento reproducible entre runtime, CI y testing.
- Hacer visible la política SMTP en la infraestructura declarativa.

## Decisión

1. Introducción de SMTP_MODE
Se introduce la variable de entorno:
   SMTP_MODE=relay|auth

Valores permitidos:
   relay
   auth

Valores inválidos deben provocar error explícito y fail-fast.

2. Semántica de operación
relay

   Características:
   - No requiere autenticación SMTP.
   - No exige secrets.
   - No debe intentar leer secrets del host.
   - Puede utilizar variables de entorno públicas si existen.
   - Debe funcionar aunque no existan credenciales.

   Objetivo:
   - Reducir superficie de exposición.
   - Evitar privilegios innecesarios.

auth

   Características:
   - Requiere autenticación SMTP.
   - Requiere credenciales válidas.
   - Puede cargar configuración desde .env.
   - Lee credenciales desde filesystem o entorno explícitamente configurado.
   - Si faltan credenciales:
      aborta explícitamente,
      genera error claro,
      aplica fail-fast.

   Objetivo:
   - Evitar estados parcialmente configurados.
   - Mejorar diagnóstico operativo.

3. Eliminación de side-effects en import-time

La inicialización de configuración SMTP no debe ejecutarse durante importación de módulos.

La carga de configuración SMTP debe realizarse explícitamente desde los entrypoints de ejecución.

Objetivos:
- Permitir imports sin efectos secundarios.
- Mejorar testabilidad y reutilización.
- Evitar lectura accidental de secrets.
- Reducir fragilidad en packaging y CI.

4. Inicialización SMTP explícita

La inicialización SMTP pasa a realizarse mediante un punto único de inicialización explícita.

Características:
- Lectura dinámica de SMTP_MODE.
- Configuración coherente entre runtime, CI y testing.
- Soporte para entornos aislados de pruebas.
- Eliminación de heurísticas implícitas.

5. Política de Compose e infraestructura declarativa

Todos los stacks deben declarar explícitamente:
   environment:
   SMTP_MODE: relay|auth

Reglas:
- Sólo stacks autorizados para autenticación SMTP deben usar:
   SMTP_MODE=auth
   mounts de credenciales SMTP
- Los stacks relay-only:
   no deben depender de secrets,
   no deben requerir privilegios adicionales.

Objetivo:
- Hacer visible la intención operativa en IaC.
- Facilitar revisión y auditoría de seguridad.

6. Gestión de credenciales SMTP
as credenciales SMTP pasan a considerarse recursos restringidos conforme al principio de mínimo privilegio definido en ADR-0024..
Recomendaciones:
- Permisos host:
   0400
   0440
- Montajes read-only.
- Paths explícitos y controlados.

Objetivo:
- Reducir exposición accidental
- Reforzar el endurecimiento operativo del modelo SMTP.

7. Logging y observabilidad

La librería de configuración debe emitir mensajes explícitos sobre:
- modo SMTP activo,
- lectura de configuración,
- carga de secrets,
- ausencia de credenciales,
- errores de autenticación.

Objetivo:

- Mejorar diagnóstico y troubleshooting operativo.

8. Estrategia de testing y CI
La plataforma debe incorporar validaciones automatizadas que aseguren:
- comportamiento correcto de relay/auth
- fail-fast en auth
- ausencia de side-effects durante importación
- coherencia declarativa en Compose e infraestructura

La estrategia concreta de testing, integración y policy enforcement queda definida en ADR-0026.

## Razonamiento técnico y arquitectónico

La separación explícita relay/auth elimina heurísticas implícitas y reduce ambigüedad operativa.

Siguiendo el principio de mínimo privilegio definido en ADR-0024, los procesos que no requieren autenticación SMTP no deben acceder a credenciales SMTP ni depender de ellas.

Evitar side-effects durante import-time elimina una fuente importante de fragilidad:
- imports impredecibles,
- contaminación de tests,
- problemas de reutilización,
- inicializaciones ocultas.

La estrategia fail-fast en auth mejora observabilidad y evita estados parcialmente inicializados.

La declaración explícita de SMTP_MODE en Compose traslada la política SMTP a la infraestructura declarativa (IaC), facilitando auditoría y revisión operativa.

## Alternativas descartadas
Mantener heurísticas implícitas
   Rechazada por:
   - complejidad creciente,
   - falta de auditabilidad,
   - riesgo de exposición,
   - comportamiento impredecible.

Configuración global única
   Rechazada por:
   - mayor acoplamiento,
   - complejidad operativa,
   - dificultad de despliegue,
   - no resolver la separación relay/auth.
Inicialización automática durante import
   Rechazada por:
   - side-effects,
   - fragilidad en tests,
   - dependencia implícita del entorno,
   - problemas de reutilización.

## Consecuencias

Positivas
- Menor superficie de exposición de secrets.
- Mejor separación de responsabilidades.
- Mayor coherencia operativa entre runtime, CI y testing.
- Mejor reproducibilidad en entornos de validación y despliegue.
- Diagnósticos más claros.
- Mejor auditabilidad de infraestructura.

Operativas
- Todos los stacks deben declarar SMTP_MODE.
- Los operadores deben provisionar secrets únicamente donde corresponda.
- Los entrypoints deben inicializar explícitamente configuración sensible.
- Los procedimientos de despliegue deben documentar la política SMTP.

Compatibilidad

Para mantener compatibilidad conservadora:
   SMTP_MODE=relay
se considera el comportamiento por defecto.

No obstante, se recomienda definirlo explícitamente en todos los stacks.

## Riesgos residuales
- Un operador puede montar secrets innecesariamente en stacks relay.
- El modo auth puede provocar abortos tempranos si los secrets no fueron provisionados.
- Cambios futuros en paths o mecanismos de secrets requerirán coordinación con infraestructura.

## Plan futuro y recomendaciones
- Publicar runbook de aprovisionamiento de secrets.
- Ampliar policy checks de CI para validar:
   SMTP_MODE,
   mounts autorizados,
   permisos esperados.
- Definir estrategia de rotación de secrets.
- Evaluar integración futura con gestores centralizados de secretos.
- Añadir tests E2E SMTP en entorno controlado.

## Referencias
- ADR-0024 — Container Privilege Exception Policy
- ADR-0026 — Estrategia de validación y testing del modelo SMTP
- src/monitoring/common/config.py
- ops/stacks/*/compose.yml
- ops/services/smtp_relay/compose.yml

## Estado

Propuesta consolidada basada en la implementación actual.
