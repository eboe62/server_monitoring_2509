# ADR-0804: Espacio Justicia como Frontend Alternativo a `GDA/frontend` — Repositorio, Stack y Entorno de Desarrollo

Status: PROPOSED
Date: 2026-08-17
Scope: System
Category: ARCHITECTURE
Tags: architecture, integration, frontend, espacio-justicia
Related ADRs: ADR-0607, ADR-0608, ADR-0801, ADR-0802
Supersedes: NONE
Superseded By: NONE
Validation Reference: NONE

## Contexto

`GDA/frontend` es la SPA de referencia del proyecto: Quasar 2 + Vue 3 + Pinia + vue-i18n + axios, consumiendo los microservicios GDA a través del API Gateway (ver ADR-0802). Toda la guía de arquitectura frontend existente (`ai/governance/04_ARCHITECTURE_GUIDELINES.md`, `CLAUDE.md`) asume implícitamente ese único frontend.

Espacio Justicia introduce un **segundo frontend**, consumidor del mismo API Gateway pero de un dominio funcional distinto: el microservicio `gda-comunicacion` (ADR-0607) para noticias, documentación (ADR-0608) y calendario de eventos del "Encargo de Justicia".

Evidencia recogida al intentar observar su evolución en el navegador:

1. **Stack propio, distinto del de `GDA/frontend`.** El contrato de requisitos funcionales (`Documentacion_BackEnd_EspacioJusticia_2607_requisitos02.2.md`, §8.11 "tecnologías de desarrollo") fija explícitamente Vue.js + Bootstrap, sin exigir Quasar. El propio código en `GDA/espacio-justicia/package.json` lo confirma: Vite + Vue 3 + vue-router + Bootstrap 5, **sin Quasar, sin Pinia, sin axios, sin vue-i18n**. No es una elección de plantilla del asistente IA: es el stack real entregado por el equipo de frontend.
2. **Repositorio y equipo propios.** `GDA/espacio-justicia/` es un repositorio Git independiente, con remoto en el GitLab corporativo (`http://172.16.22.114/espacio-justicia/espacio-justicia.git`, rama `main`), desarrollado por un equipo de frontend distinto al de `GDA/frontend`. La sección "REPOSITORIO DEL PROYECTO" del contrato de requisitos lo confirma como repositorio independiente, a cargo de ese equipo.
3. **Rol de este workspace: observación, no desarrollo.** El seguimiento de Espacio Justicia desde aquí consiste en `git pull` + ejecución local (`npm install` / `npm run dev`) para visualizar el avance en el navegador — no se proponen cambios de código sobre ese repositorio desde este contexto de trabajo, al no ser el equipo propietario.
4. **Bloqueo de entorno al instalar dependencias.** El registry npm privado corporativo configurado (`verdaccio.k8spru21.justicia.es`) presenta un certificado TLS firmado por una CA propia ("AC NP SERVICIOS WEB JUSTICIA", Secretaría de Estado de Justicia) que no está instalada en el almacén de certificados de este equipo de desarrollo (verificado en `Cert:\CurrentUser\Root`, `Cert:\LocalMachine\Root` y `Cert:\LocalMachine\CA`: ausente en los tres). Esto provoca el fallo `npm install` → `SELF_SIGNED_CERT_IN_CHAIN`. El problema es del entorno local, no del código del proyecto, y previsiblemente afectará a cualquier otra persona que instale dependencias de Espacio Justicia (o de cualquier otro paquete servido por ese mismo registry) desde un equipo sin esa CA instalada.

No existe hoy ningún ADR que reconozca la existencia de un segundo frontend con stack propio, ni que deje constancia del caveat de certificado — de no documentarlo, cualquier sesión futura (humana o asistida por IA) puede aplicar por error las convenciones de `GDA/frontend` sobre Espacio Justicia, o "resolver" el bloqueo de certificado desactivando la verificación SSL de forma global y sin registro.

## Decisión

1. **Espacio Justicia se reconoce como un segundo frontend, independiente de `GDA/frontend`**, con stack propio (Vue 3 + Vite + Bootstrap, sin Quasar/Pinia/vue-i18n/axios), repositorio Git propio y equipo de desarrollo propio. Las convenciones de `GDA/frontend` documentadas en `ai/governance/04_ARCHITECTURE_GUIDELINES.md` y en `CLAUDE.md` **no se extienden a Espacio Justicia** salvo que se documente explícitamente lo contrario.
2. **Los lineamientos de integración con el backend son comunes a ambos frontends.** ADR-0802 (API Gateway como único punto de entrada, CORS, manejo de errores) se mantiene como referencia compartida, por tratarse de un patrón de integración con el backend y no de un patrón de UI. Este ADR no sustituye a ADR-0802, lo complementa aclarando que existe más de un consumidor frontend.
3. **El rol de este repositorio/workspace frente a `GDA/espacio-justicia/` es de solo observación.** Se permite clonar/actualizar (`git pull`) y ejecutar localmente (`npm install`, `npm run dev`) para visualizar el avance, pero no se realizan commits ni `push` contra ese repositorio desde este contexto de trabajo.
4. **Se documenta como caveat operativo conocido el requisito de CA corporativa para el registry privado.** Mientras la CA "AC NP SERVICIOS WEB JUSTICIA" no esté instalada en el almacén de certificados del equipo local, la instalación de dependencias de Espacio Justicia (o de cualquier otro paquete de ese mismo registry) puede requerir un workaround temporal — `NPM_CONFIG_STRICT_SSL=false` acotado a la ejecución puntual de un único comando, nunca persistido en `.npmrc` ni aplicado de forma global — hasta que se obtenga el certificado oficial vía IT/DevOps corporativo.

## Deuda técnica / pendiente (no bloqueante)

- Instalar la CA "AC NP SERVICIOS WEB JUSTICIA" de forma oficial en los equipos de desarrollo (o publicarla como parte del onboarding de entorno) para eliminar la necesidad del workaround de `strict-ssl`.
- Confirmar si el equipo de Espacio Justicia documentará sus propias decisiones de arquitectura frontend (equivalente a una serie de ADR de UI propia) o si permanecen fuera del alcance de gobernanza de este repositorio por pertenecer a un equipo/repo externo.

## Consecuencias

### Positivas (+)

- Evita que las convenciones de `GDA/frontend` (Quasar/Pinia/vue-i18n) se apliquen erróneamente sobre Espacio Justicia.
- Deja constancia explícita de que la relación de este repositorio con `GDA/espacio-justicia/` es de observación, reduciendo el riesgo de cambios accidentales sobre código de un equipo externo.
- Documenta el bloqueo de certificado del registry privado para que no se re-descubra en cada sesión, ni se resuelva de forma insegura y sin registro (p. ej. desactivando SSL de forma global y persistente).

### Negativas (-)

- Añade un segundo frontend al inventario de gobernanza a título informativo, sin control directo sobre su evolución (repositorio y equipo externos).
- El workaround de certificado sigue siendo deuda técnica sin resolver de forma definitiva; depende de un tercero (IT/DevOps corporativo) fuera del control de este equipo.

## Referencias

- ADR-0607: Introducción del microservicio `gda-comunicacion` para Noticias y Eventos (Espacio Justicia).
- ADR-0608: Estrategia de almacenamiento de adjuntos de noticia (Espacio Justicia).
- ADR-0801: Estrategia de empaquetado y despliegue con contenedores Docker.
- ADR-0802: Lineamientos de integración frontend con microservicios backend.
- `Documentacion_BackEnd_EspacioJusticia_2607_requisitos02.2.md` — contrato de requisitos, §7 "Repositorio del proyecto", §8.11 "tecnologías de desarrollo".
- `GDA/espacio-justicia/package.json` — evidencia del stack real (Vite + Vue 3 + Bootstrap, sin Quasar).
