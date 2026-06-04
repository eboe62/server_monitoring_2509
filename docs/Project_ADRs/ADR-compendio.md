# ADR-0000 – Trabajo paralelo fuera de Git durante refactor estructural

Fecha: 2026-01-24
Estado: Aprobado
Contexto: Migración IaC server_monitoring_2509

## Contexto

Durante la refactorización mayor del proyecto Monitoring Stack,
se decidió desarrollar la nueva estructura (`server_monitoring_2511`)
fuera del repositorio Git principal para evitar:

- Riesgo de corrupción del histórico
- Commits intermedios incoherentes
- Mezcla de código legacy y refactorizado

## Decisión

El trabajo se realizó en un directorio externo sin `.git`,
y posteriormente se migró manualmente al repositorio original
mediante una copia controlada de estructura y ficheros.

## Consecuencias

- Mayor control del estado final
- Menor ruido en el histórico Git
- Necesidad de validación manual previa al primer commit

## Estado

Aceptado – migración única

# ADR-0001 — Verificación de imports durante la fase de migración

Fecha: 2025-12-09
Estado: Aprobado
Contexto: Migración IaC server_monitoring_2509

## Contexto

Durante la migración de la base de código Python a una estructura bajo `src/`,
se detectaron múltiples imports con el prefijo `src.` (por ejemplo `src.log_ingestor.alert_risk`).

Este patrón impedía una ejecución limpia mediante `python3 -m <paquete>`
y generaba una ambigüedad entre el layout del proyecto y los namespaces reales
de Python.

Se identificaron 7 archivos afectados, principalmente bajo:
- src/log_ingestor/
- src/resource_monitor/

## Opciones consideradas

### Opción A — Mantener `src/__init__.py` (solución temporal)

Crear `src/__init__.py` para convertir `src/` en un paquete Python y permitir
la resolución de imports con prefijo `src.`.

**Ventajas:**
- Impacto mínimo inmediato
- No requiere modificar imports existentes
- Permite ejecutar módulos como `python3 -m src.<paquete>`

**Inconvenientes:**
- Introduce un anti-patrón (layout como namespace)
- Oculta la estructura real de paquetes
- Genera deuda técnica futura
- Puede causar confusión en CI/CD, empaquetado o instalación

### Opción B — Eliminar prefijo `src.` y adaptar imports a paquetes reales

Modificar los imports para referenciar directamente los paquetes reales
(`monitoring`, `log_ingestor`, `resource_monitor`, etc.)
y ejecutar módulos mediante `python3 -m <paquete>.<modulo>`.

**Ventajas:**
- Arquitectura Python limpia y estándar
- Facilita empaquetado y reutilización
- Alineado con buenas prácticas y el objetivo IaC
- Evita deuda técnica futura

**Inconvenientes:**
- Requiere modificar aproximadamente 7 archivos
- Necesita validación mediante compilación y ejecución controlada

## Decisión

Se adopta la **Opción B**.

Se elimina el prefijo `src.` de los imports Python y se adaptan los módulos
para que funcionen como paquetes reales ejecutables mediante `python3 -m`.

## Consecuencias

- Se realizará un refactor controlado de imports en los archivos afectados
- No se crea `src/__init__.py`
- Se validará la corrección mediante `python3 -m compileall src/`
- Esta decisión reduce deuda técnica y alinea el proyecto con prácticas estándar

## Estado

Aprobado.

## Validación

La verificación del refactor de imports se realizó en dos niveles:

1. Verificación estructural:
   - Revisión manual de todos los imports afectados
   - Refactor controlado y consistente en los 7 archivos identificados

2. Verificación por compilación:
   - Ejecución de:
     docker run --rm -v $(pwd)/src:/app/src -w /app python:3.12-slim python3 -m compileall src/
   - Realizada mediante un contenedor de usar y tirar (ephemeral container) aislado, asegurando que el host de producción jamás ejecute ni compile módulos de Python del proyecto de forma nativa, quedando en estricto cumplimiento con la gobernanza runtime.

El resultado fue satisfactorio, sin errores de compilación ni resolución
de imports en:
- src/log_ingestor
- src/monitoring
- src/resource_monitor

La validación no pudo ejecutarse en entorno Windows PowerShell por ausencia
de intérprete Python configurado, lo cual se considera fuera de alcance
del proyecto y no afecta al entorno objetivo.

No se realizaron ejecuciones completas de los scripts ni carga de variables
de entorno (.env), ya que dichas comprobaciones dependen de configuración
externa y pertenecen a una fase posterior del plan de migración.

## Consecuencias

- La fase de refactor de imports Python se considera cerrada
- Se reduce deuda técnica futura
- El proyecto queda alineado con prácticas estándar de empaquetado Python
- La validación de ejecución queda explícitamente pospuesta a fases posteriores
  (normalización de ejecución y despliegue)


# ADR-0002 – Scripts como wrappers operativos

Fecha: 2026-01-25
Estado: Aprobado
Contexto: Migración IaC server_monitoring_2509

## Contexto

Durante la migración y normalización IaC del proyecto de monitoring,
se identificó la coexistencia de dos tipos de código ejecutable:

- Lógica Python estructurada bajo `src/`, organizada como paquetes importables.
- Scripts operativos bajo `scripts/` y otros directorios de infraestructura,
  utilizados históricamente como puntos de entrada (cron, shell, Makefile).

Asimismo, se estableció como objetivo que la infraestructura pueda desplegarse
de forma autónoma en distintos servidores sin depender de configuraciones
específicas del entorno (PYTHONPATH, instalaciones manuales, etc.).

## Decisión

Se adopta la siguiente separación explícita:

- **El directorio `src/` contiene toda la lógica Python ejecutable como módulo**.
  El código bajo `src/` se ejecuta exclusivamente mediante:

python3 -m <paquete>.<modulo>


- **El directorio `scripts/` se considera infraestructura operativa**.
No se trata como paquete Python ni se hace importable como módulo.

- Los scripts Python ubicados en `scripts/` actúan, cuando sea necesario,
como **wrappers mínimos**, cuya única responsabilidad es invocar
el código correspondiente bajo `src/` mediante `python3 -m`.

- No se asume el uso de `PYTHONPATH` ni la instalación del paquete en editable
como requisito para la ejecución operativa.

## Consecuencias

- Se elimina la ambigüedad entre “script” y “módulo”.
- Se facilita la portabilidad de la infraestructura entre servidores.
- Se evita acoplar la ejecución a configuraciones implícitas del entorno.
- Los wrappers pueden mantenerse estables mientras la lógica evoluciona en `src/`.

## Estado

Aceptado.

# ADR-004 - Eliminación del atributo version en docker-compose (Docker Compose v2)

Fecha: 2026-01-27
Estado: Aprobado
Contexto: Migración IaC server_monitoring_2509

## Contexto

El proyecto server_monitoring utiliza múltiples ficheros docker-compose
distribuidos en distintos subdirectorios (ops/docker, ops/services, etc.).

Al ejecutar comandos como `docker-compose ps` o `make status` en entornos
actuales, se detecta el uso de Docker Compose v2 (plugin `docker compose`),
que emite warnings cuando los ficheros docker-compose incluyen el atributo
`version`.

Ejemplo de warning observado:

  "the attribute `version` is obsolete, it will be ignored"

Aunque este warning no impide la ejecución, introduce ruido operativo,
confusión durante la validación y dificulta la lectura de logs y salidas
automatizadas.

Los ficheros afectados identificados actualmente son:

- ops/stacks/cron/compose.yml
- ops/stacks/observability/compose.yml
- ops/stacks/python/compose.yml
- ops/services/smtp_relay/compose.yml
- ops/services/postgres/compose.yml

## Decisión

Se decide eliminar el atributo `version` de todos los ficheros docker-compose
del proyecto.

A partir de este ADR:
- No se incluirá `version:` en nuevos docker-compose
- Los docker-compose existentes deberán migrarse eliminando dicho atributo
- El esquema será detectado automáticamente por Docker Compose v2

Esta decisión asume explícitamente Docker Compose v2 como estándar del proyecto.

## Consecuencias

Positivas:
- Eliminación de warnings en tiempo de ejecución
- Configuración alineada con el estándar actual de Docker
- Ficheros docker-compose más simples y claros
- Mejor experiencia en CI/CD y automatizaciones (Makefile)

Negativas:
- Pérdida de compatibilidad explícita con Docker Compose v1 (asumido como aceptable)

# Alternativas consideradas

1. Mantener `version` y aceptar los warnings
   - Rechazada por introducir ruido y deuda técnica

2. Forzar uso de Docker Compose v1
   - Rechazada por ir en contra de la evolución natural del stack

# Notas

Tras aplicar esta decisión, se ha validado que comandos como:
  make status
  docker-compose ps

funcionan correctamente sin warnings ni errores.

Esta decisión afecta a múltiples docker-compose y debe aplicarse de forma consistente en todo el repositorio.

## Estado

Aceptado.

# ADR-0005 – Desacoplamiento runtime y lazy imports en config (Runtime desacoplado)

Fecha: 2026-01-27
Estado: Aprobado
Contexto: Migración IaC server_monitoring_2509

## Contexto

Durante FASE 3 se identificó acoplamiento crítico en import-time:
- Lectura de .env y secrets al importar módulos.
- Imports pesados (psycopg2, requests) que provocaban fallos tempranos.
FASE 8 inicia implementación incremental limitada a config.py.

## Decisión

- La carga de configuración sensible y credenciales se realiza exclusivamente en runtime mediante init_config().
- config.py debe poder importarse sin efectos secundarios ni dependencias operativas completas.
- psycopg2 y requests se importan de forma lazy únicamente en las funciones que los requieren.
- Se mantienen valores por defecto mediante variables de entorno para compatibilidad.

Este ADR define la política general de desacoplamiento runtime e import-time utilizada posteriormente por ADR especializados de runtime, secrets y configuración SMTP.

## Consecuencias

- init_config() pasa a ser obligatoria en los entrypoints funcionales.
- Los errores por falta de dependencias aparecen únicamente cuando se utilizan las funciones afectadas.
- Se mejora la portabilidad a CI/CD, cronjobs y contenedores mínimos.
- Se reduce el acoplamiento entre importación de módulos y configuración operativa.

## Fuera de alcance:
- No se modifican docker-compose, Makefiles ni entrypoints en este ADR.
- No se introducen validaciones de precondiciones automáticas (pendiente de fases futuras).

## Estado

Aceptado.

ADR-0006 – Gobernanza de imagen base monitoring-base (Rechazado)

Fecha: 2026-05-04
Estado: Rechazado
Contexto: Migración PRO server_monitoring_2602 – Modelo micro-stack autónomo

## Contexto
Durante la definición del entorno PRO 260214 se adopta el modelo: “micro-stack autónomo con red compartida”.
Cada servicio debe poder:
- Construirse de forma independiente
- Desplegarse sin dependencias implícitas
- Ser trasladado a otro repositorio si fuera necesario
- Evaluación de alternativa descartada

Se evaluó la posibilidad de mantener una imagen base común denominada monitoring-base con los siguientes objetivos:
- Reducir duplicación de dependencias
- Estandarizar runtime Python
- Optimizar tiempos de build
- Garantizar coherencia de entorno
Sin embargo, esta aproximación introduce un riesgo estructural de acoplamiento, especialmente en ausencia de un sistema de gobernanza estricta y verificable.

Condiciones teóricas de implementación (no adoptadas)

En caso de haberse implementado, la imagen base debería haber cumplido:
- Uso de versiones explícitas (prohibido :latest)
- Superficie de ataque mínima (paquetes estrictamente necesarios)
- Ausencia de herramientas de debug en producción
- Separación total de configuración y secrets

## Decisión
Se rechaza completamente el uso de una imagen base compartida (monitoring-base), incluso en el caso de cumplir condiciones estrictas de diseño.

El rechazo aplica aunque la imagen:
- Contenga únicamente runtime común (Python y librerías compartidas)
- Incluya código fuente versionado del proyecto
- Se limite a dependencias declaradas en requirements.txt
- Mantenga configuración genérica no específica de servicio

También se rechaza aunque cumpla las siguientes garantías:
- Restricciones teóricas (no suficientes para su adopción)
- Ausencia de secrets y archivos .env
- No inclusión de configuración específica de servicios
- No ejecución de lógica dependiente de entorno en build-time
- Cumplimiento del principio de reemplazabilidad

Aunque cada servicio pudiera:
- Extender directamente una imagen oficial (python:slim, etc.)
- Sustituir monitoring-base sin romper la arquitectura

Se considera que esto no elimina el riesgo de acoplamiento estructural en la práctica.

Centralización de estado

Se rechaza incluso aunque no tenga centralización de estado:
- Ningún volumen ni dato persistente depende de la imagen base.
- El estado siempre reside en volúmenes declarados por servicio.
La existencia de una imagen base común seguiría introduciendo dependencia en fase de build.

## Consecuencias
Se acepta explícitamente la pérdida de las siguientes ventajas:
- Mayor duplicación de dependencias entre servicios
- Menor eficiencia en tiempos de build
- Menor reutilización de capas Docker
- Posible incremento del tamaño total de imágenes

Estas desventajas se consideran asumibles en favor de:

aislamiento, reproducibilidad y coherencia con el modelo IaC PRO

## Riesgos
Se identifican como riesgos estructurales:
- Crecimiento progresivo de responsabilidad de la imagen base
- Introducción de configuración específica (acoplamiento oculto)
- Dependencia implícita entre servicios en fase de build
- Dificultad de validación independiente en CI/CD
- Riesgo de convertir la imagen en dependencia no reemplazable

Estos riesgos se consideran críticos y suficientes para justificar su no adopción.

## Fuera de alcance:
- No se redefine la estructura de servicios.
- No se introduce pipeline de build automatizado.
- No se modifica el modelo de red compartida.
- No se altera la política de secrets.

## Estado
Rechazado.


# ADR-0007 – Política oficial de entorno VS Code + WSL para proyectos Linux/DevOps

Fecha: 2026-02-16
Estado: Aprobado
Contexto: Estandarización del entorno de desarrollo PRO – Modelo híbrido Windows UI / WSL Runtime

## Contexto
Durante la evolución del entorno PRO se detectaron inconsistencias derivadas de:
- Instalaciones duplicadas de extensiones (Windows vs WSL).
- Uso ocasional de Git desde Windows.
- Problemas de detección automática de repositorios en workspaces ubicados en /mnt.
- Comportamientos inconsistentes de line endings.
- Confusión operativa al abrir proyectos sin Remote-WSL activo.
Inicialmente se consideró instalar VS Code también dentro de WSL, pero esto generaba:
- Duplicidad innecesaria.
- Mayor complejidad de mantenimiento.
- Falta de separación clara entre UI y runtime.
Se decide formalizar un modelo híbrido controlado.

## Decisión
Se adopta el siguiente modelo oficial:

## Arquitectura
VS Code se instala exclusivamente en Windows.
Windows actúa únicamente como UI Host.
Ubuntu WSL2 es el entorno oficial de:
- Ejecución
- Compilación
- Git
- Tooling backend

## Apertura obligatoria
Todo proyecto Linux/DevOps deberá abrirse mediante:
  Remote – WSL → Ubuntu
La barra inferior izquierda debe indicar:
  WSL: Ubuntu
Si no aparece, el entorno se considera inválido.

## Git oficial
El Git oficial del proyecto es el instalado en WSL.
Queda prohibido:
- Ejecutar Git desde Windows para proyectos Linux/DevOps.
- Realizar commits desde entorno no WSL.
No se modifica el comportamiento estándar de Git
(core.discoverAcrossFilesystems permanece en false).

## Ubicación del código
Los proyectos se almacenan en:
  D:\WorkSpace
  Accesible en WSL como:
  /mnt/d/WorkSpace

Decisión consciente:
- Se prioriza organización centralizada.
- Se facilita backup desde Windows.
- Se acepta ligera penalización en file watchers NTFS.

## Modelo de WorkSpace
Se adopta modelo multi-root controlado cuando:
- El workspace raíz es superior al repositorio Git.
- VS Code no detecta automáticamente repositorios hijos en filesystem montado.

Ejemplo oficial:
{
    "folders": [
        {
        "name": "WorkSpace",
        "path": "WorkSpace"
        },
        {
        "name": "server_monitoring_2509",
        "path": "WorkSpace/Proyectos/VPS_DigitalOcean_2410/server_monitoring_2509"
        }
    ],
    "settings": {
        "git.autoRepositoryDetection": "subFolders",
        "git.openRepositoryInParentFolders": "never",
        "git.detectSubmodules": true,
        "files.eol": "\n",
        "search.exclude": {
        "**/node_modules": true,
        "**/__pycache__": true,
        "**/.git": false
        }
    }
}

Justificación:
- Git no cruza límites de filesystem por defecto.
- VS Code no detecta automáticamente subrepositorios bajo /mnt.
- Se prioriza estabilidad frente a automatismo.

## Clasificación de extensiones
Extensiones técnicas (Git, Docker, Python, etc.)
→ Se instalan exclusivamente en WSL.
Extensiones de interfaz (themes, iconos, UI)
→ Se instalan en Windows.

Se prohíbe la duplicación innecesaria.

## Consecuencias
Positivas:
- Separación clara UI / runtime.
- Coherencia total entre entorno local y servidor Linux.
- Eliminación de ambigüedad Git.
- Entorno reproducible.
- Control explícito de workspace.

Limitaciones aceptadas:
- Refresco menos ágil en NTFS frente a ext4.
- Necesidad de workspace multi-root en algunos casos.
- Mayor disciplina operativa.

## Riesgos controlado
- Uso accidental de Git Windows.
- Apertura del proyecto sin Remote-WSL.
- Duplicación de extensiones.
- Inconsistencias de line endings.
La política mitiga estos riesgos mediante reglas explícitas.

## Fuera de alcance:
- No afecta arquitectura Docker.
- No redefine modelo micro-stack.
- No altera política de secrets.
- No introduce pipeline CI/CD.
- No regula configuración específica de Copilot.

## Estado
Aceptado.

# ADR-0008 – Clasificación de servicios: Micro-stack vs Infraestructura Operativa

Fecha: 2026-02-17
Estado: Propuesto
Contexto: server_monitoring_2509
## Contexto
Durante la FASE 4 se adopta el modelo “micro-stack autónomo con red compartida”.
Sin embargo, en la implementación actual coexisten dos tipos de despliegue:
- Servicios ubicados en:
    ops/services/<servicio>/
    (ej. smtp_relay)
- Infra-stacks (infraestructura operativa): Stacks agregados definidos en:
    ops/docker/
    (cron, python runner, postgres, observability)
La documentación inicial de FASE 4 no distingue formalmente ambas categorías, generando ambigüedad sobre qué componentes deben cumplir estrictamente el modelo micro-stack autónomo.
Se requiere una clasificación explícita para mantener coherencia arquitectónica.

## Decisión
Se definen dos categorías formales de despliegue:

1️⃣ Micro-stack Autónomo
Ubicación:
  ops/services/<servicio>/

Debe cumplir obligatoriamente:
- Dockerfile propio
- docker-compose.yml propio
- build independiente (contexto acotado al servicio)
- no depender de archivos fuera del directorio del servicio
- no depender de imágenes base internas del repositorio
- solo se permite el uso de imágenes base oficiales externas versionadas (ej. python:3.12-slim)
- no montar rutas absolutas del host como dependencia estructural
- no versionar secrets
- no incluir secrets ni .env en la imagen
- declarar la red apropiada como external: true (p. ej. `backend-net` para micro-stacks)

Objetivo:
Permitir que el servicio pueda copiarse a otro repositorio y desplegarse de forma independiente.

2️⃣ Stack de Infraestructura Operativa
Ubicación:
  ops/docker/

Incluye:
- cron
- python runner
- postgres (si se mantiene agregado)
- observability

Puede:
- usar build context superior (solo para acceso a código del repositorio)
- montar exclusivamente volúmenes del host explícitamente justificados
- acceder a /var/run/docker.sock únicamente bajo justificación explícita
- acceder a logs del host en modo read-only cuando exista motivo operativo documentado

Restricciones:
- no se permiten bind mounts de código fuente en runtime productivo
- el código ejecutable debe formar parte de la imagen Docker construida
- el runtime debe ser reproducible desde un host limpio mediante reconstrucción declarativa

Debe:
 - declarar la red apropiada como external: true (p. ej. `backend-net` para micro-stacks)
- no versionar secrets
- no incluir secrets dentro de la imagen
- no introducir dependencias implícitas no documentadas

- documentar explícitamente:
  - uso de docker.sock (si aplica)
  - montajes de rutas del host
  - dependencias del host necesarias

- ser auditable mediante scripts automatizados (FASE 4/5)

Objetivo:
  Proveer capacidades operativas del entorno, no servicios exportables.

Importante:
Los Infra-Stacks NO se consideran autónomos a nivel de repositorio ni de arquitectura exportable.
Sin embargo, sí deben ser autónomos a nivel de ejecución (runtime), lo que implica:
  - ausencia de bind mounts estructurales del código fuente
  - capacidad de reconstrucción completa desde imágenes Docker
  - funcionamiento tras:
      docker system prune -af --volumes
  - ausencia de dependencia implícita del filesystem del host

Esto diferencia explícitamente:
  - autonomía arquitectónica/exportable
de:
  - autonomía operativa/runtime

3️⃣ Uso de docker.sock
Los infra-stacks pueden montar:
  /var/run/docker.sock:/var/run/docker.sock

Únicamente cuando sea estrictamente necesario para capacidades de infraestructura (inspección, control del runtime o automatización declarativa).

RIESGO:
El acceso a docker.sock concede privilegios equivalentes a root sobre el host Docker, permitiendo:
- creación/eliminación de contenedores
- acceso a volúmenes
- ejecución arbitraria en el host

MITIGACIONES OBLIGATORIAS:

1) Alcance
- Exclusivo de infra-stacks (ops/docker/)
- Prohibido en micro-stacks (ops/services/)

2) Aislamiento
- Contenedor sin exposición de puertos
- No accesible desde el exterior (solo red interna Docker)

3) Control de ejecución
- No ejecutar código dinámico o no auditado dentro del contenedor
- Scripts versionados y revisados en repositorio

4) Principio de mínimo privilegio (reforzado)
- user != root cuando sea posible
- read_only: true cuando sea viable
- cap_drop: ALL (añadir solo las necesarias si aplica)

5) Trazabilidad
- Toda operación que use docker.sock debe quedar registrada en logs

6) Auditoría
- Debe existir comprobación automática (audit script) que detecte:
  - uso de docker.sock
  - contenedores que lo montan

## Justificación
- No todos los contenedores tienen naturaleza exportable.
- Forzar infraestructura operativa a modelo micro-stack incrementa complejidad sin beneficio claro.
- La separación explícita evita ambigüedades futuras.
- Permite mantener rigor arquitectónico sin sobredimensionar el sistema.

## Consecuencias
- FASE 4 aplica estrictamente solo a micro-stacks autónomos.
- Los stacks operativos quedan formalmente fuera del requisito de portabilidad.
- Se mejora la coherencia documental.
- Se evita refactorización innecesaria.

## Riesgos controlados
- Crecimiento de infra-stacks con privilegios elevados (docker.sock, mounts host)
- Compromiso del host si un contenedor con docker.sock es vulnerado
- Mezcla de responsabilidades entre micro-stack e infra-stack
- Dependencias implícitas del host no documentadas

Controles:
- Auditoría automática (FASE 4/5)
- Restricción de exposición de red
- Revisión obligatoria de ADR para cualquier excepción

## Fuera de alcance:
- No se obliga a migrar postgres a micro-stack.
- No se reestructura el repositorio.
- No se modifica ADR-0006.
- No se introduce nuevo orquestador.

## Estado
Aprobado.

# ADR-0009 – Estrategia de Backups PostgreSQL

Estado: Aprobado
Fecha: 2026-03-05
Contexto: server_monitoring_2509

## Contexto
El sistema de monitorización utiliza PostgreSQL como micro-stack autónomo para persistencia de datos.

Inicialmente el sistema utilizaba wrappers en el host que ejecutaban scripts Python mediante cron para realizar backups.

Este enfoque introducía problemas arquitectónicos:
  - Violación parcial del modelo IaC
  - Dependencia de scripts host-level
  - Dificultad para reproducir el entorno

## Decisión
Se adopta la siguiente estrategia:
1. Los backups lógicos de PostgreSQL se gestionan dentro del runtime contenerizado del proyecto.
2. La lógica de backup se ubica dentro del micro-stack postgres:
     ops/services/postgres/scripts/
3. El scheduler oficial continúa siendo el contenedor monitoring-cron.
4. El proceso de backup se ejecuta mediante pg_dump contra el servicio postgres dentro de la red Docker backend-net.
      Ejemplo conceptual:
          monitoring-cron
            └ pg_dump -h postgres
5. Los backups se almacenan en:
      /ops/backups

montado desde el host.

## Consecuencias

Ventajas
  - Coherencia total con modelo IaC
  - Eliminación de dependencias del host
  - Backups reproducibles
  - Lógica de persistencia cercana al micro-stack de datos

Limitaciones
  - Dependencia del runtime Docker para ejecución del backup
  - No sustituye snapshots del droplet como mecanismo de contingencia

Alternativas consideradas
  A) Backups ejecutados desde host
    Rechazado por violar modelo IaC.
  B) Cron interno dentro del contenedor PostgreSQL
    Rechazado por mezclar responsabilidades en el micro-stack.
  C) Scheduler externo
    Considerado innecesario para el alcance del proyecto.

## Estado
Aprobado.


# ADR-0010 - Arquitectura de runtime cron

Fecha: 2026-03-05
Estado: Propuesto
Contexto: server_monitoring_2509
## Contexto
El sistema server_monitoring requiere ejecutar tareas periódicas para:
- mantenimiento del sistema
- generación de backups
- operaciones de housekeeping
- ejecución de verificaciones de salud

En la arquitectura inicial se contemplaban:
- wrappers bash
- ejecución directa desde el host
- cronjobs distribuidos entre stacks

Durante la evolución del proyecto se detectaron varios problemas:
- Acoplamiento host ↔ contenedores
- Dificultad para versionar la lógica de cron
- Duplicación de scripts wrapper
- Falta de trazabilidad operacional

Adicionalmente, la gestión de backups PostgreSQL se trasladó al micro-stack postgres, eliminando la lógica externa de backup que anteriormente dependía de wrappers.

Esto obliga a definir una arquitectura clara del runtime de cron dentro del sistema.

## Decisión
Se adopta una arquitectura basada en contenedores dedicados para la ejecución de cronjobs.
Principios adoptados:
  - monitoring-cron es un contenedor del plano 2 (Infra-Stack)
    Su función es ejecutar tareas periódicas de infraestructura.
  - Los cronjobs se ejecutan directamente contra servicios Docker
      Ejemplo:
      monitoring-cron
        └ pg_dump -h postgres
    La resolución del servicio se realiza mediante DNS interno de Docker.
  - Eliminación de wrappers
    Los scripts wrapper intermedios quedan eliminados.
    Los cronjobs deben invocar directamente:
      - comandos del sistema
      - utilidades estándar
      - clientes de servicio (ej. pg_dump)
  - Separación de responsabilidades por stack
    Arquitectura resultante:
      Plano 2 — Infra-Stack
      monitoring-cron
        ├ tareas mantenimiento
        ├ housekeeping
        └ operaciones programadas infra

      Plano 1 — Micro-Stacks
      postgres
        ├ runtime base de datos
        └ lógica interna de backup
  - El runtime cron no contiene lógica de negocio
    Las tareas cron:
    - orquestan
    - invocan utilidades
    pero no implementan lógica compleja.

## Opciones consideradas
Opción A — Cron en el host

  host cron
    └ docker exec ...

  Ventajas
  - simplicidad inicial
  Inconvenientes
  - fuerte acoplamiento host
  - difícil versionado
  - menor reproducibilidad
  Resultado: rechazada

Opción B — Cron distribuido por contenedor

  container A
  container B
  container C
    └ cron propio

  Ventajas
  - encapsulación
  Inconvenientes
  - múltiples runtimes cron
  - difícil trazabilidad
  - mayor complejidad operativa
  Resultado: rechazada

Opción C — Contenedor cron dedicado (seleccionada)

  monitoring-cron
    ├ cron daemon
    ├ jobs definidos en repo
    └ acceso a servicios docker

  Ventajas
  - centralización
  - versionado en Git
  - observabilidad
  - arquitectura reproducible
  Resultado: aceptada

## Consecuencias
Positivas
  - arquitectura más predecible
  - cronjobs versionados en IaC
  - menor dependencia del host
  - eliminación de wrappers innecesarios
  - alineación con arquitectura por stacks

Negativas
  - necesidad de mantener un contenedor adicional
  - dependencia del networking docker interno
  - algunos comandos requieren clientes instalados en el contenedor cron

## Estado
Propuesto — pendiente de incorporación al compendio ADR.

# ADR-0011 - Python Runtime Execution Model (Determinismo)

Fecha: 2026-03-05
Estado: Propuesto
Ámbito: server_monitoring_2509

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

# ADR-0012 — Separation of Host Cron vs Monitoring Cron (Runtime reproducible)

Fecha: 2026-03-12
Estado: Propuesto
Ámbito: server_monitoring_2509

## Contexto
El sistema server_monitoring se despliega en un servidor VPS bajo una arquitectura basada en Infrastructure as Code y contenedores Docker.

Durante la fase de diseño surgió ambigüedad sobre dónde deben ejecutarse las tareas programadas del sistema.

Existen dos tipos distintos de automatismos:
  - Automatismos del sistema operativo (mantenimiento del host)
  - Automatismos propios del runtime del proyecto

Sin una separación explícita, las auditorías pueden interpretar incorrectamente que el host ejecuta lógica de aplicación o asumir dependencias indebidas entre host y runtime Docker.

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

# ADR-0013 – Credential Management Policy

Fecha: 2026-03-14
Estado: Aprobado
Contexto: server_monitoring_2509

## Contexto
Durante FASE 4 del proceso de implementación se evaluó el modelo de gestión de credenciales definido inicialmente en la arquitectura del proyecto.

La documentación contemplaba el uso de un directorio `secrets/` por micro-stack para almacenar credenciales no versionadas.

Este modelo introducía varias complejidades operativas:
- Necesidad de crear y mantener múltiples directorios `secrets/`.
- Ambigüedad sobre el mecanismo real de inyección de secretos en contenedores.
- Riesgo de divergencia entre micro-stacks.
- Sobrecarga innecesaria en un entorno **single-host sin orquestador**.

El proyecto utiliza **Docker Compose v2 en un único host** y no emplea Docker Swarm ni otros orquestadores que proporcionen gestión nativa de secretos.

En este contexto, el uso de directorios `secrets/` aporta escaso valor operativo y complica la arquitectura.

Por este motivo se decide simplificar el modelo. La carpeta secrets se crea únicamente cuando un servicio requiere credenciales externas o material sensible.
Si un servicio no requiere credenciales, la carpeta secrets no es necesaria.
Las credenciales nunca deben almacenarse en el repositorio.

## Decisión
El proyecto adopta la siguiente política oficial de gestión de credenciales:

### Mecanismo oficial
Las credenciales del sistema se gestionan **exclusivamente mediante variables de entorno** definidas en archivos `.env` locales no versionados.

Por cada micro-stack:
- Debe existir un archivo `.env.template` versionado.
- El archivo `.env` real se genera manualmente a partir de dicha plantilla.
- El archivo `.env` debe estar incluido en `.gitignore`.

Ejemplo:
```
  ops/services/postgres/
  ├ compose.yml
  ├ Dockerfile
  ├ .env.template
  ├ config/
  └ scripts/
```

El archivo `.env.template` contiene únicamente nombres de variables y valores de ejemplo.

El archivo `.env` contiene las credenciales reales y **no forma parte del repositorio**.

## Gestión de credenciales

El proyecto utiliza actualmente variables de entorno (.env) para la inyección de credenciales en tiempo de ejecución.

Estas credenciales:
- no deben versionarse en el repositorio
- deben mantenerse únicamente en el servidor
- deben cargarse mediante la directiva env_file de Docker Compose

No se utilizan actualmente:
- Docker Secrets
- gestores externos de secretos (Vault, SSM, etc.)

Por tanto no se mantienen carpetas secrets dentro del repositorio ni estructuras asociadas a Docker secrets.

Si en el futuro se adopta un gestor de secretos se introducirá mediante un ADR específico.

### Restricciones obligatorias
No se permite:
- Versionar archivos `.env` con credenciales reales.
- Incluir credenciales dentro de Dockerfiles.
- Copiar archivos `.env` dentro de imágenes Docker.
- Incluir credenciales en scripts versionados.

### Alcance
Esta política aplica a:
- Micro-Stacks (`ops/services/*`)
- Infra-Stacks (`ops/docker/*`)

### Exclusiones explícitas
No se utilizan los siguientes mecanismos:
- Docker Swarm secrets
- Kubernetes secrets
- Directorios `secrets/` dentro de micro-stacks
- Sistemas externos de gestión de secretos

Si en el futuro se adopta un orquestador o gestor de secretos dedicado, deberá formalizarse mediante un nuevo ADR.

## Consecuencias
Positivas:
- Arquitectura significativamente más simple.
- Menor fricción operativa en despliegues manuales.
- Reducción de estructura innecesaria en micro-stacks.
- Mayor claridad en el flujo de configuración.

Limitaciones aceptadas:
- Las credenciales se almacenan en archivos `.env` locales.
- No existe cifrado nativo de credenciales en repositorio.
- La seguridad depende del control de acceso al host.

Estas limitaciones se consideran aceptables en el contexto actual del proyecto:
- servidor único
- acceso SSH controlado
- repositorio privado
- entorno de aprendizaje/prototipado avanzado.

## Alternativas consideradas
### 1. Uso de directorios `secrets/` por micro-stack
Ventajas:
- Separación explícita de credenciales.

Problemas detectados:
- No existe integración nativa con Docker Compose.
- Requiere mecanismos adicionales de montaje y lectura.
- Aumenta la complejidad sin aportar beneficios claros.

Decisión: Rechazada.

### 2. Uso de Docker Swarm secrets
Ventajas:
- Gestión de secretos nativa del orquestador.
- Inyección segura en contenedores.

Problemas detectados:
- Requiere habilitar Docker Swarm.
- Introduce complejidad innecesaria para un entorno single-node.

Decisión: Rechazada.

### 3. Uso de gestor externo de secretos (Vault, SOPS, etc.)
Ventajas:
- Seguridad avanzada.
- Rotación y auditoría de credenciales.

Problemas detectados:
- Sobrecoste operativo elevado.
- Infraestructura adicional fuera del alcance actual.

Decisión: Rechazada.

## Notas
Esta decisión implica la eliminación del directorio `secrets/` de la estructura mínima obligatoria de los micro-stacks definida en el documento de implementación.

Los documentos afectados deberán actualizarse para reflejar el nuevo modelo de credenciales.

Esta política es coherente con el modelo actual del proyecto:
- Docker Compose v2
- despliegue single-host
- arquitectura IaC reproducible.

## Estado
Aceptado.

# ADR-0014 — Docker Port Exposure Policy

Fecha: 2026-03-14
Estado: Aprobado
Ámbito: server_monitoring_2509

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

# ADR-0015 — Docker Network Exposure Model

Fecha: 2026-03-14
Estado: Aprobado
Ámbito: server_monitoring_2509

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

# ADR-0016 — Política de aislamiento y segmentación de redes Docker

Fecha: 2026-05-06
Estado: Aprobado
Ámbito: server_monitoring_2509

## Contexto

La plataforma está basada en múltiples stacks Docker desacoplados mediante Compose e infraestructura declarativa.

Durante la evolución del sistema aparecieron varios riesgos:
- comunicación excesivamente permisiva entre servicios,
- exposición innecesaria de puertos,
- acoplamiento entre stacks,
- dificultad para delimitar dominios funcionales,
- y propagación potencial de incidentes entre contenedores.

Además, algunos servicios externos requieren exposición parcial controlada mientras que otros deben permanecer únicamente accesibles desde redes internas.

## Problema

El uso de redes Docker compartidas sin segmentación explícita:
- dificulta aplicar el principio de mínimo privilegio,
- incrementa superficie de ataque,
- reduce trazabilidad de comunicaciones,
- y complica la evolución segura de la arquitectura.

Era necesario definir una política homogénea de segmentación de redes y exposición de servicios.

## Decisión

Se adopta una estrategia de segmentación explícita mediante redes Docker diferenciadas por dominio funcional.

Principios generales:

- Cada stack debe conectarse únicamente a las redes estrictamente necesarias.
- La exposición de puertos debe minimizarse.
- Los servicios internos no deben exponerse directamente al host salvo necesidad justificada.
- Las comunicaciones entre dominios deben ser explícitas y auditables.

Clasificación de redes:

- Redes internas de aplicación
  Uso:
  - comunicación privada entre servicios del mismo dominio funcional.

- Redes compartidas controladas
  Uso:
  - integración explícita entre stacks relacionados.

- Redes restringidas
  Uso:
  - servicios sensibles,
  - relay SMTP,
  - observabilidad,
  - componentes con requisitos especiales de endurecimiento.

## Reglas operativas

- Evitar el uso indiscriminado de:
  network_mode: host

- Evitar contenedores conectados a múltiples redes sin justificación funcional.

- Priorizar:
  internal: true
  cuando el servicio no requiera acceso externo.

- La pertenencia de un servicio a una red debe reflejar una necesidad funcional explícita.

- La infraestructura declarativa (Compose) debe representar de forma visible la política de segmentación.
## Ejemplos en el proyecto
Scripts actuales que entran en esta categoría:
configure_docker_limits.sh
  - aplica límites de CPU y memoria a contenedores
  - evita saturación del host

apply_ssh_ratelimit.sh
  - configura limitación de conexiones SSH
  - protege frente a ataques masivos

## Razonamiento

La segmentación reduce superficie de ataque y limita propagación lateral entre servicios.

Separar dominios funcionales mejora:
- auditabilidad,
- aislamiento operativo,
- trazabilidad de comunicaciones,
- y capacidad de endurecimiento progresivo.

La infraestructura declarativa permite revisar y validar la política de conectividad sin depender exclusivamente del runtime.

Esta política complementa:
- ADR-0005 para desacoplamiento runtime,
- y ADR-0024 para endurecimiento contextual y principio de mínimo privilegio aplicado a contenedores.

## Consecuencias

Positivas:
- menor exposición innecesaria,
- mejor aislamiento entre stacks,
- mayor claridad arquitectónica,
- reducción de acoplamiento,
- mejora de auditabilidad.

Operativas:
- nuevos servicios deben declarar explícitamente sus redes,
- cambios de conectividad requieren actualización de Compose,
- redes compartidas deben justificarse arquitectónicamente.

Negativas:
- incremento moderado de complejidad declarativa,
- necesidad de mantenimiento explícito de topología de red.

## Validación

La validación debe realizarse mediante:
- revisión de Compose,
- inspección de redes Docker,
- validaciones CI sobre exposición de puertos y redes compartidas,
- revisión arquitectónica de nuevos stacks.

## Referencias

- ADR-0005 — Política de inicialización runtime e import-time.
- ADR-0024 — Política de excepciones de privilegios en contenedores.

## Estado

Aprobado.

# ADR-0017 — Resilience model at docker single-node

Fecha: 2026-04-01
Estado: Aprobado
Ámbito: server_monitoring_2509

## Contexto
El sistema de monitorización se despliega en un entorno basado en Docker Compose sobre un único nodo (single-node), sin uso de orquestadores como Kubernetes o Docker Swarm.

Durante la validación de resiliencia (tests test-resilience), se detectó un comportamiento aparentemente inconsistente:
- El contenedor monitoring-python no se recrea automáticamente tras ejecutar docker kill
- Sin embargo, sí se reinicia correctamente cuando el proceso principal (PID 1) termina dentro del contenedor

Esto generó dudas sobre el correcto funcionamiento de la política:

  restart: always

Tras el análisis, se concluye que el comportamiento observado es consistente con el modelo de ejecución de Docker Compose.

## Decisión
Se adopta explícitamente el modelo: Single-node Docker Compose sin orquestador

Con las siguientes implicaciones:

- restart: always
  ✔ Reinicia el contenedor cuando el proceso interno (PID 1) termina
  ❌ NO recrea el contenedor si este es eliminado manualmente (docker kill, docker rm)

- Docker Compose:
  ✔ Gestiona el estado inicial (declarativo)
  ❌ NO mantiene un loop de reconciliación continuo
  ❌ NO proporciona self-healing a nivel de contenedor

- Los tests de resiliencia deben:
  ✔ Simular fallos internos (crash de proceso)
  ❌ NO asumir comportamiento de orquestador

## Propuesta de mejora
Corto plazo (recomendado):
- Ajustar tests de resiliencia:
    Usar kill -9 1 en lugar de docker kill:
      docker exec monitoring-python sh -c "kill -9 1"
    en vez de:
      docker kill monitoring-python
- Documentar explícitamente el modelo en todos los ADR relacionados
- Añadir validación de RestartCount > 0 en tests

Medio plazo:
Añadir mecanismo externo de supervisión
    Opciones:
    - systemd → relanzar docker compose up
    - watchdog script
    - cron de verificación de estado

    Objetivo:
    - Recuperar contenedores eliminados accidentalmente

Largo plazo (evolución arquitectónica):
Evaluar migración a un orquestador
    Opciones:
    - Docker Swarm (baja complejidad)
    - Kubernetes (alta robustez)

    Beneficios:
    - Self-healing real (reconciliación continua)
    - Gestión avanzada de estado
    - Escalabilidad horizontal

## Consecuencias
Positivas
- Simplicidad operativa (sin orquestador)
- Menor consumo de recursos
- Comportamiento predecible y alineado con Docker estándar
- Facilidad de depuración
Negativas
- No existe self-healing completo: Eliminación de contenedores no se corrige automáticamente
- Dependencia de mecanismos externos para recuperación completa
- Tests de resiliencia deben adaptarse al modelo real (no Kubernetes-like)

## Alternativas consideradas
- Asumir comportamiento tipo Kubernetes (rechazada)
  ❌ Incorrecto en Docker Compose
  ❌ Genera tests inválidos
  ❌ Produce falsas expectativas de resiliencia

- Implementar orquestador desde el inicio (rechazada por ahora)
  ❌ Sobrecoste operativo
  ❌ Complejidad innecesaria para el alcance actual

- Mantener Compose + documentar limitaciones (aceptada)
  ✔ Coherente con el contexto del proyecto
  ✔ Control total sobre comportamiento
  ✔ Evolución progresiva posible

## Relación con otros ADR
Este ADR impacta directamente en:
- Estrategia de despliegue
- Diseño de tests de resiliencia
- Observabilidad y validación del sistema

Debe ser tenido en cuenta en todos los ADR que impliquen:
- Alta disponibilidad
- Gestión de fallos
- Automatización operativa

## Validación
Se considera comportamiento correcto cuando:

Caso 1: kill proceso interno (PID 1)
  → contenedor se reinicia automáticamente

Caso 2: docker kill contenedor
  → contenedor NO se recrea automáticamente

El test-resilience deben validar exclusivamente:
- Reinicio tras fallo interno
- Degradación controlada ante caída de dependencias (DB)
- Recuperación tras restauración de servicios

## Estado
Aprobado.

# ADR-0018 – Modelo de Seguridad Runtime Docker y Requisitos de Resiliencia

Fecha: 2026-04-05
Estado: Aprobado
Contexto: server_monitoring_2509

## Contexto
Durante la FASE 5 se valida el comportamiento del sistema bajo condiciones reales de operación:
- Fallos de contenedores (crash)
- Fallos de base de datos
- Fallos de red (parcialmente controlables en entorno Docker)
- Recuperación automática
- Observabilidad activa durante incidencias

Adicionalmente, se formaliza un modelo explícito de:
- Seguridad en runtime de contenedores Docker
- Uso controlado de privilegios (docker.sock, capabilities, usuario)
- Reglas de exposición de red
- Requisitos mínimos de resiliencia verificables mediante tests automatizados

---

## Decisión
Se establecen dos bloques normativos obligatorios:

# 1️⃣ Modelo de Seguridad Runtime Docker

## 1.1 Principios generales
- El host NO ejecuta lógica funcional de aplicación
- La ejecución funcional se realiza dentro de contenedores
- El host puede ejecutar tooling operacional asociado a:
    - Docker Compose
    - validaciones runtime
    - auditoría estructural
    - automatización declarativa
    - verificaciones CI/IaC
- Se aplica principio de mínimo privilegio
- Toda excepción debe estar documentada en ADR

Cada contenedor funcional:
- define su propio entorno de ejecución
- evita dependencias implícitas con otros stacks

El control-plane operacional host-side:
- no debe introducir acoplamiento funcional
- debe permanecer declarativo y auditado

## 1.2 Usuarios en contenedores
Regla:
- Los contenedores deben ejecutarse como usuario no root siempre que sea viable

Excepción:
- Infra-stacks pueden usar root si es necesario (ej: postfix, docker tooling)

Control:
- docker inspect <container> | grep User

---

## 1.3 Capacidades Linux (capabilities)
Regla:
- cap_drop: ALL por defecto
- Añadir únicamente capacidades necesarias

---

## 1.4 Sistema de archivos

Regla:
- read_only: true cuando sea compatible con el servicio

Objetivo:
- Reducir superficie de ataque en runtime

---

## 1.5 Exposición de puertos
Reglas:
Micro-stacks:
- NO deben usar ports

Servicios internos accesibles localmente:
- Bind a loopback:
  127.0.0.1:<host_port>:<container_port>

Servicios públicos:
- Solo 80 y 443 expuestos en host

Control:
- docker ps --format "{{.Ports}}"
  ss -tulpn

---

## 1.6 Uso de docker.sock
Regla:
- Permitido SOLO bajo excepción ADR explícita y documentada
- El uso de docker.sock debe considerarse privilegio equivalente a root host

Prohibido:
- En micro-stacks (ops/services/)
- En TOOLBOX_RUNTIME
- En runtimes operativos persistentes utilizados únicamente para tooling
- Como dependencia implícita de validaciones CI/runtime

El acceso a docker.sock:
- no puede asumirse como capacidad base del sistema
- debe minimizarse progresivamente
- debe sustituirse por validaciones host-side estructuradas cuando sea viable

Riesgo:
- Equivalente a acceso root sobre el host Docker

Mitigaciones obligatorias:
- No exposición de puertos del contenedor
- Acceso únicamente desde red interna Docker
- No ejecución de código dinámico o no auditado
- Scripts versionados en repositorio
- Registro de actividad en logs
- Justificación explícita en ADR o README

Control:
- grep -R "docker.sock" ops/

---

## 1.7 Imágenes Docker

Reglas:
- Prohibido uso de :latest
- Versionado explícito
- Imágenes minimalistas

Objetivo:
- Reproducibilidad y reducción de superficie de ataque

---

## 1.8 Secrets
Reglas:
- No versionar secrets
- No incluir secrets en imágenes
---

## 1.9 Validación automática de seguridad

La seguridad runtime debe validarse mediante:

  make test-security-runtime

Este test debe verificar:
- usuario (root vs no root)
- exposición de puertos
- uso de docker.sock
- coherencia básica de runtime

---

2️⃣ Requisitos de Resiliencia

## 2.1 Definición
El sistema debe ser capaz de:
- Detectar fallos
- Degradarse de forma controlada cuando sea posible
- Recuperarse automáticamente
- Mantener observabilidad durante incidencias

La resiliencia se garantiza a nivel de contenedor individual.
Cada servicio debe:
- poder reiniciarse de forma independiente
- no depender de runtime compartido
- mantener funcionamiento degradado si otros servicios fallan

Nota:
La degradación de red puede no ser completamente determinista en Docker.

---

## 2.2 Requisitos obligatorios
R1 – Reinicio automático
Todos los contenedores deben tener política de restart tras un fallo

  Control:
    docker inspect <container> | grep RestartPolicy

Validación:
  make test-resilience-restart

---

R2 – Healthchecks
Servicios críticos deben exponer estado

  Estados esperados:
    healthy
    unhealthy

  Control:
    docker inspect <container> | grep Health

Validación:
  make test-python-health

---

R3 – Recuperación ante crash
El sistema debe reiniciarse y volver a healthy:
  - Reiniciar contenedores automáticamente
  - Recuperar estado healthy

  Validación:
    make test-resilience-restart

---

R4 – Resiliencia ante fallo de base de datos
 El sistema debe:
  - Detectar caida DB
  - Recuperarse automáticamente

  Validación:
    make test-resilience-db

---

R5 – Resiliencia de red
El sistema debe:
  - Tolerar pérdida de conectividad
  - Recuperarse tras restauración


Nota:
La detección de degradación puede depender del healthcheck del servicio.

  Validación:
    make test-resilience-network

---

R6 – Observabilidad
El stack de observabilidad debe:
  - Permanecer operativo durante incidencias
  - Permitir consulta de logs

  Validación:
    make test-observability

---

R7 – Procesamiento asíncrono (cron)
Debe ejecutarse dentro de contenedor

  Validación:
    make test-cron-execution

---

R8 – SMTP resiliente (infraestructura)
El sistema debe:
  - Aceptar mensajes (Postfix OK)
  - Mantener cola operativa
  - Permitir trazabilidad vía logs

Validación:
  make test-smtp-all

  Nota:
  La entrega final depende de proveedor externo (ej. Postmark)
---

## 2.3 Validación obligatoria
La resiliencia se valida mediante:
  make test-resilience-completo

Este test debe cubrir:
- crash
- DB failure
- network (best-effort)
- observability

---

## Justificación
- Alinea documentación con comportamiento real
- Permite validación automática en CI
- Reduce ambigüedad
- Refleja límites reales de Docker

---

## Consecuencias
- Seguridad verificable automáticamente
- Resiliencia basada en tests reales
- Mayor coherencia CI ↔ ADR

---

## Riesgos controlados
- Privilegios excesivos
- Exposición accidental de servicios
- Uso indebido de docker.sock
- Fallos no detectados en runtime
- Pérdida de observabilidad durante incidencias

---

## Fuera de alcance
- Orquestación avanzada (Kubernetes, Swarm)
- Gestión externa de secretos (Vault, etc.)
- Autoescalado

---

## Relación con otros ADR
ADR-0008 — Clasificación de servicios - Micro-stack vs Infraestructura Operativa
ADR-0014 — Docker Port Exposure Policy
ADR-0015 — Docker Network Exposure Model

## Estado
Aprobado.

# ADR-0019 — Resilience Testing Strategy

Fecha: 2026-04-25
Estado: Aprobado
Contexto: server_monitoring_2509

## Contexto

Durante la implementación de tests de resiliencia en CI se han observado comportamientos no deterministas al simular fallos reales de red mediante:

docker network disconnect

Problemas detectados:
- conexiones TCP persistentes (keep-alive)
- caché DNS interna de Docker
- latencias del runtime en CI
- diferencias entre entorno local y CI

Esto provocó múltiples falsos negativos en pipeline.

Adicionalmente, se detectó acoplamiento indebido entre:
- bind mounts del host
- permisos de contenedores (USER no root)
- rutas de logs dependientes del host (/var/log montado desde host)

Esto rompía el principio de separación entre:
- runtime funcional containerizado
- control-plane operacional host-side

definido por el modelo IaC actual.

## Decisión
Se separa la estrategia de testing en dos niveles:

### 1. CI (determinista)
Se implementa:
    test-resilience-network-ci

Basado en:
- desconexión controlada de red Docker
- validación mediante healthchecks internos

NO se valida conectividad TCP real.

Objetivo:
- determinismo
- estabilidad en pipeline

### 2. Local / Staging (real)
Se implementa:
    test-resilience-network-real

Basado en:
- aislamiento real de red
- validación TCP (nc)
- simulación de fallos reales

Uso limitado a entornos controlados.

### Principio clave

Los tests de resiliencia NO deben depender de:
- bind mounts del host
- rutas del sistema (/var/log)
- comportamiento no determinista del runtime Docker

### Logs
Se elimina dependencia de:
    /var/log (host)

Se adopta:
    /opt/monitoring/logs

Motivo:
- coherencia con el modelo IaC híbrido actual
- separación funcional host/runtime
- reducción de dependencias host-side funcionales
- reproducibilidad operacional razonable

## Consecuencias
- CI más estable y determinista
- coherencia con modelo IaC
- aislamiento completo
- independencia del host
- reproducibilidad total

## Estado
Adoptado


# ADR-0020 — Container Execution Model & Privilege Strategy

Fecha: 2026-05-04
Estado: Aprobado
Contexto: server_monitoring_2509

## Contexto

Durante la evolución del sistema se han identificado inconsistencias en el modelo de ejecución de contenedores:
- uso mixto de root y no-root sin criterio explícito
- dependencia histórica de bind mounts del host
- contenedores con propósitos distintos (runtime vs debug) tratados de forma homogénea

Estas inconsistencias generan:
- ambigüedad en el modelo de seguridad
- pérdida de reproducibilidad
- acoplamiento innecesario al host
- dificultad para escalar el sistema a otros entornos

Adicionalmente, el sistema debe servir como base portable para:
- despliegue de servicios (DB, web services)
- análisis forense
- evaluación de vulnerabilidades
- recuperación de sistemas

Esto exige un modelo de ejecución claro, consistente y replicable.

## Decisión

Se define un modelo explícito de ejecución de contenedores basado en su propósito:

### 1. Contenedores de runtime (infra-stacks)

Ejemplos:
- monitoring-cron
- monitoring-python
- observability stack

Características obligatorias:
- autocontenidos (sin dependencia del host)
- reproducibles (build determinista)
- sin bind mounts de código
- un proceso principal definido

Regla de privilegios:
Estos contenedores DEBEN ejecutarse como usuario no-root.

Motivo:
- principio de mínimo privilegio
- reducción de superficie de ataque
- coherencia con modelo IaC

El runtime:
    monitoring-python

NO debe considerarse un toolbox Docker completo.

Por defecto:
- no incorpora docker CLI
- no incorpora docker compose
- no monta docker.sock

Las operaciones Docker host-level deben ejecutarse desde:
- host control-plane
- scripts operacionales externos
- pipelines CI/CD autorizados

Cualquier excepción deberá documentarse explícitamente mediante ADR adicional.

### 2. Contenedores de servicio (micro-stacks)

Ejemplos:
- postgres
- smtp-relay
- servicios externos

Características:
- pueden depender de imágenes oficiales
- pueden requerir root internamente
- responsabilidad delegada al proveedor de la imagen

Regla de privilegios:
No se fuerza USER no-root si rompe compatibilidad.

Motivo:
- evitar desviaciones de imágenes oficiales
- mantener estabilidad y soporte upstream

### 3. Contenedores operativos / debug

Ejemplos:
- contenedores de diagnóstico
- tooling interactivo

Características:
- ejecución manual
- uso puntual
- no forman parte del runtime crítico

Regla de privilegios:

Pueden ejecutarse como root, de forma explícita y controlada.

Motivo:
- facilitar debugging
- permitir operaciones de bajo nivel

## Principios derivados

1. Separación por propósito
Cada contenedor debe tener un único rol claro:
- runtime
- servicio
- operativo

No se permite mezclar roles.

2. Eliminación de dependencias del host
- prohibido uso de bind mounts de código en producción
- el código debe integrarse en la imagen Docker durante el build
- permitido solo:
    logs específicos (controlados)
    datos persistentes definidos explícitamente
    sockets o recursos del host justificados documentalmente

Validación obligatoria:
    make test-reproducibilidad

El test debe validar:
- eliminación completa de contenedores
- eliminación de imágenes
- eliminación de volúmenes
 - recreación de las redes de monitoring (backend-net / observability-net / restricted-net)
- reconstrucción íntegra desde cero
- ausencia de dependencias implícitas del host

3. Coherencia con IaC

El comportamiento del sistema debe mantener:
- reproducibilidad operativa,
- independencia del host,
- coherencia entre build y runtime.

4. Seguridad contextual (no dogmática)

El uso de no-root:
- es obligatorio en runtime propio
- es opcional en servicios externos
- es irrelevante en contenedores de debug controlado

## Consecuencias

Positivas:
- modelo de seguridad claro y consistente
- reducción de ambigüedad en decisiones técnicas
- mejora de portabilidad del sistema
- base sólida para hardening futuro
- alineación con principios IaC

Negativas:
- necesidad de clasificar correctamente los contenedores
- posible refactor de imágenes existentes
- incremento inicial de complejidad conceptual

## Relación con otros ADR
- ADR-0008 (micro-stack vs infra-stack)
  → Este ADR refuerza la separación de roles
- ADR-0014 / ADR-0015 (exposición de servicios)
  → Complementa el aislamiento mediante privilegios
- ADR-0018 (seguridad runtime)
  → Define el criterio concreto de aplicación de no-root
- ADR-0019 (resilience testing)
  → Garantiza coherencia entre runtime y testing

## Estado
Adoptado

# ADR-0021 — Network Segmentation Strategy

Fecha: 2026-05-04
Estado: Aprobado
Contexto: server_monitoring_2509

Nota: Durante la migración de la plataforma la red histórica `monitoring-net` se ha sustituido por un conjunto de redes segmentadas: `backend-net`, `observability-net` y `restricted-net`. Este documento refleja la estrategia y la transición.

## Contexto

Historicamente todos los contenedores del sistema compartían una única red Docker:
  monitoring-net

Este enfoque simplifica la conectividad pero introduce problemas críticos:
- comunicación lateral no restringida entre servicios
- imposibilidad de aislar dominios funcionales
- incremento de superficie de ataque
- inviabilidad de escenarios de análisis forense controlado
- dificultad para reutilizar la infraestructura en otros contextos

Este modelo entra en conflicto con:
- ADR-0008 (separación micro-stack vs infra-stack)
- ADR-0020 (separación por propósito y privilegios)
- objetivos del sistema:
  - despliegue de servicios
  - análisis de vulnerabilidades
  - entornos controlados y reproducibles

## Decisión
Se adopta un modelo de segmentación de red basado en dominios funcionales (ver monitoring-network en Makefile)
Se reemplaza el uso de una única red global por múltiples redes especializadas.

## Modelo de redes

Se definen las siguientes redes:

### 1. backend-net
Uso:
- comunicación entre servicios internos de negocio

Ejemplos:
- monitoring-cron → postgres
- monitoring-python → postgres

Características:
- acceso restringido a servicios backend
- no exposición externa
- no accesible desde contenedores de observabilidad

### 2. observability-net
Uso:
- ingestión y visualización de logs

Ejemplos:
- promtail → loki
- grafana → loki

Características:
- acceso limitado a stack de observabilidad
- no acceso directo a bases de datos
- desacoplado del backend

### 3. restricted-net
Uso:
- contenedores sensibles o entornos controlados

Ejemplos:
- análisis forense
- sandbox de vulnerabilidades
- servicios potencialmente comprometidos

Características:
- aislamiento fuerte
- sin acceso a otras redes salvo configuración explícita
- ideal para ejecución de cargas no confiables

### 4. edge-net (opcional)
Uso:
- exposición controlada hacia el exterior

Ejemplos:
- grafana (si se expone)
- reverse proxy

Características:
- único punto de entrada/salida
- control de puertos
- puede estar limitado a 127.0.0.1 o VPN

## Reglas de conexión
1. Principio de mínimo acceso
Un contenedor solo puede estar conectado a las redes estrictamente necesarias.

2. Prohibición de red global
No se permite el uso de una red única compartida por todos los servicios.

3. Conexiones explícitas
Toda comunicación entre servicios debe estar definida explícitamente mediante redes compartidas.

4. Aislamiento por defecto

Los nuevos servicios deben:
- empezar sin acceso a otras redes
- añadir conectividad solo si es necesario

## Ejemplo de aplicación

monitoring-cron → backend-net
postgres        → backend-net

promtail        → observability-net
loki            → observability-net
grafana         → observability-net + edge-net (opcional)

## Validación
Se deben implementar tests específicos:
- test-aislamiento-red
- test-arranque-desordenado
- test-dependencias-host

Validaciones esperadas:
- un contenedor no puede resolver ni conectar a servicios fuera de su red
- fallos de red no afectan a dominios no relacionados
- la observabilidad sigue funcionando sin acceso al backend

## Consecuencias
Positivas:
- reducción significativa de superficie de ataque
- eliminación de movimiento lateral entre servicios
- mejora de aislamiento para análisis forense
- mayor reutilización de la infraestructura
- alineación con arquitectura por dominios

Negativas:
- incremento de complejidad en docker-compose
- necesidad de definir correctamente dependencias
- posible refactor de configuraciones existentes

## Relación con otros ADR
- ADR-0008 (micro-stack vs infra-stack)
  → se refuerza el aislamiento entre dominios
- ADR-0014 / ADR-0015 (exposición de servicios)
  → edge-net centraliza exposición
- ADR-0018 (seguridad runtime)
  → segmentación reduce superficie de ataque
- ADR-0019 (resilience testing)
  → permite tests más realistas de fallo de red
- ADR-0020 (container execution model)
  → separación por propósito se refleja en red

## Estado
Adoptado

# ADR-0022 — Promtail Privilege Approval

Fecha: 2026-05-08
Estado: Aprobado
Contexto: server_monitoring_2509

## Contexto

Promtail (Grafana Labs) se usa para la ingestión de logs desde el host y contenedores. En la configuración actual Promtail requiere acceso a:

- `/var/log` del host
- `/var/lib/docker/containers` (para leer logs de contenedores)

Estos mounts permiten a Promtail leer ficheros del host y de otros contenedores, lo que implica un nivel de confianza elevado en el componente que ejecuta Promtail.

## Problema

Montar paths host en un contenedor concede la capacidad de leer información sensible del host y hace que el contenedor de Promtail sea un punto de confianza crítica. Negar este acceso impediría la recopilación de logs en la forma actual.

## Decisión

Se aprueba (estado: Aprobado) permitir que Promtail monte los directorios necesarios para la captura de logs en la configuración de observabilidad, atendiendo la Recomendación 1. Esto implica aceptar el componente como parte del plano de infraestructura de confianza y gestionarlo con controles operativos más estrictos.

Recomendación aplicada (alcance limitado a Recomendación 1):

- Mantener exclusivamente los mounts necesarios para observabilidad defensiva:
  `/var/log` en modo solo lectura (`:ro`) para observación de eventos críticos del host
  `/var/lib/docker/containers` en modo solo lectura (`:ro`) para ingestión de logs Docker
El estado interno de Promtail (positions file) no debe persistirse sobre rutas del host y se almacena mediante volumen Docker explícito dedicado (`promtail-data`).
La arquitectura adopta un modelo híbrido:
  - observabilidad container-centric para servicios Docker
  - observabilidad host-centric para eventos de seguridad del sistema anfitrión
- Ejecutar Promtail en el stack de observabilidad (`observability-net`) como servicio de infraestructura (no como servicio de aplicación).
- Garantizar imagen firmada/consistente y usar versiones fijas (no `:latest`).
- Limitar recursos (CPU/mem) y ejecutar bajo cuentas kernel-namespaced y políticas de seccomp/APPArmor lo más restrictivas posibles.

## Consecuencias

Pros:

- Conservamos la capacidad de ingestión de logs completos y la correlación necesaria para observabilidad.
- Evita reescrituras grandes en la arquitectura de logging a corto plazo.

Contras:

- Promtail se considera un componente de alta confianza; cualquier vulnerabilidad en Promtail o en su configuración de mounts puede comprometer información host.
- Requiere controles operativos (actualizaciones, hardening) y revisiones periódicas.

## Mitigaciones operativas (resumen)

- Marcar Promtail como componente infra-trusted en inventario y playbooks.
- Aplicar mounts `:ro` siempre que sea posible (actual configuración ya usa `:ro` en contenedores de logs).
- Mantener una política de actualización y escaneo de vulnerabilidades para la imagen Promtail.
- Registrar y auditar cambios en la configuración de Promtail.

## Relación con otros ADR

- ADR-0021 — Network Segmentation Strategy: Promtail queda en `observability-net` (coherente con la segmentación).
- ADR-0020 — Container Execution Model Privilege Strategy: refuerza la necesidad de delimitar componentes privilegiados.
- ADR-0018 — Docker security runtime and resilience requirements: se complementa con mitigaciones runtime.

## Estado

Aprobado

# ADR-0023 — Egress Control for restricted-net (Propuesto)

Fecha: 2026-05-08
Estado: Propuesto
Contexto: server_monitoring_2509

## Contexto

El objetivo de `restricted-net` es alojar contenedores o cargas con confianza reducida o entornos de análisis forense/sandbox. Por defecto Docker permite egress (salida) desde contenedores a Internet, lo que deja una vía de exfiltración y comunicación no controlada.

## Problema

Sin controles de egress, un contenedor comprometido en `restricted-net` puede establecer conexiones salientes hacia Internet u otras redes, exponiendo datos o recibiendo instrucciones de control remoto.

## Propuesta / Decisión (Propuesto)

Se propone aplicar un modelo de egress-control basado en defensa en profundidad con las siguientes medidas recomendadas:

1) Default-deny a egress para `restricted-net` a nivel host
- Implementar reglas de firewall (iptables/nftables) que bloqueen todo tráfico saliente desde las interfaces Docker asociadas a `restricted-net`, salvo excepciones explícitas.

2) Egress proxy centralizado (recomendado)
- Provisionar un `egress-proxy` (HTTP/HTTPS/TCP) en `edge-net` o en un host dedicado.
- Todos los contenedores de `restricted-net` con permiso de salida deben usar el proxy para acceder a recursos externos (configurar variables `HTTP_PROXY/HTTPS_PROXY` y reglas transparentes si procede).
- El proxy permite inspección, filtrado de dominios y registro de solicitudes salientes.

3) Reglas de excepción (white-list)
- Mantener una lista mínima de destinos autorizados (IPs, FQDN) y puertos para usos operativos (actualizaciones controladas, DNS, servicios internos).
- Registrar y revisar cambios en la lista.

4) Telemetría y bloqueo granulado
- Integrar logs del proxy con la plataforma de observabilidad (Loki) para auditoría.
- Rechazar o saturar conexiones no autorizadas y generar alertas.

5) Controles de mitigación local
- Usar userland proxies ligeros (p. ej. `squid`, `tinyproxy`, `envoy`) para casos específicos.
- En entornos donde no sea posible un proxy, aplicar reglas eBPF/iptables que limiten IPs y puertos.

## Argumentos a favor

- Reduce vector de exfiltración y comando-control.
- Facilita auditoría de tráfico saliente y detección temprana.
- Centraliza la política de salida y permite aplicar controles de seguridad (filtrado, autenticación, TLS inspection si procede).

## Costes y consecuencias

- Aumento de complejidad operativa (gestión del proxy y de listas de permisos).
- Latencia potencial y puntos únicos de fallo (mitigable con alta disponibilidad para el proxy).
- Requiere planificación para actualizaciones de contenedores y repositorios de imágenes (excluyendo hosts de actualización autorizados).

## Recomendación operativa

- Implementar primero un proxy de egress en modo observabilidad (registro/log-only) para monitorizar el impacto.
- Tras un periodo de validación, aplicar default-deny y promover excepciones justificadas.
- Automatizar la gestión de reglas (infra-as-code) y documentar el runbook de emergencia.

## Pruebas sugeridas (alta nivel)

- Test de conectividad controlada: levantar un contenedor en `restricted-net` y validar que sólo puede acceder a destinos permitidos a través del proxy.
- Test de bypass: intentar conexiones directas (no-proxy) y comprobar bloqueo y registros.

## Relación con otros ADR

- ADR-0021: segmentación de redes — `restricted-net` forma parte de la estrategia.
- ADR-0020 / ADR-0018: ejecución y hardening — complementa políticas de runtime.

## Estado

Propuesto

# ADR-0024 — Container Privilege Exception Policy (Mínimo privilegio contextual)

Fecha: 2026-05-09
Estado: Aprobado
Implementación: Completa
Ámbito: server_monitoring_2509

## Contexto

La plataforma utiliza una arquitectura Docker IaC organizada en:
- micro-stacks autónomos,
- infra-stacks internos,
- controles de seguridad host.

Durante el endurecimiento del runtime se aplicó inicialmente una política homogénea basada en:
- ejecución obligatoria con UID != 0,
- eliminación generalizada de privilegios.

La experiencia operativa demostró que este enfoque generaba incompatibilidades funcionales y falsos positivos de seguridad en imágenes oficiales externas.

Se detectó especialmente en:
- postgres,
- promtail,
- smtp-relay.

## Problema

El modelo anterior asumía que ejecutar contenedores como non-root era un requisito universal.

Consecuencias:
- incompatibilidad con imágenes oficiales,
- hardening artificial sobre componentes externos,
- falsos positivos en CI,
- confusión entre seguridad del código propio y comportamiento upstream.

La plataforma necesitaba diferenciar:
- contenedores desarrollados y controlados por el proyecto,
- dependencias externas consideradas infra-trusted.

## Decisión

Se establece una clasificación explícita de contenedores.

### 1. Contenedores propios

Ejemplos:
- monitoring-python
- monitoring-cron

Reglas obligatorias:
- ejecución con UID != 0,
- uso de usuario non-root,
- prohibido root en runtime,
- prohibido:
  - sudo,
  - su,
  - escaladas de privilegio,
  - chown runtime innecesarios,
- ejecución reproducible mediante:
  python3 -m <modulo>

La ausencia de:
- docker.sock
- docker CLI
- docker compose

en:
    monitoring-python

se considera medida de hardening válida y alineada con minimización de privilegios.

Las validaciones estructuradas deberán soportar degradación explícita cuando el runtime no disponga de capacidades Docker host-level.

### 2. Contenedores externos / infra-trusted

Ejemplos:
- postgres,
- smtp-relay,
- promtail.

Reglas:
- se permite UID = 0 si la imagen lo requiere,
- no se fuerza modificación del usuario interno,
- deben tratarse como dependencias infra-trusted,
- las excepciones deben quedar documentadas y auditables.

## Principio

El principio de mínimo privilegio debe aplicarse de forma contextual y proporcional al nivel de control sobre cada contenedor.

La política de endurecimiento se aplica prioritariamente al código controlado por el proyecto.

Las dependencias externas deben mantener compatibilidad funcional con sus imágenes oficiales, utilizando controles compensatorios cuando sea necesario.

## Controles compensatorios

Para contenedores externos ejecutados como root:
- redes Docker aisladas,
- exposición mínima de puertos,
- mounts preferentemente read-only,
- volúmenes explícitos,
- acceso restringido a credenciales SMTP y otros secretos operativos,
- separación funcional entre stacks.

## Validación

La validación de privilegios debe realizarse en runtime mediante:

  docker exec <container> id -u

Reglas CI:
- contenedores propios:
  FAIL si UID == 0
- contenedores externos:
  WARN permitido con excepción documentada

No se considera suficiente:
- docker inspect .Config.User

## Consecuencias

Positivas:
- reducción de falsos positivos,
- compatibilidad con imágenes oficiales,
- separación clara de responsabilidades,
- CI más fiable,
- modelo de seguridad más coherente.

Operativas:
- las excepciones deben documentarse,
- nuevos contenedores privilegiados requieren revisión explícita.

## Acciones obligatorias

- test-security-runtime debe validar UID efectivo mediante docker exec,
- los Dockerfiles propios deben evitar cambios de permisos innecesarios,
- los scripts host-only no deben usar sudo embebido y deben validar EUID.

## Excepciones aprobadas

postgres:
- imagen oficial postgres,
- excepción permitida,
- control mediante compose y volúmenes explícitos.

smtp-relay:
- postfix upstream,
- excepción permitida,
- exposición restringida y mounts controlados.

promtail:
- imagen oficial grafana/promtail,
- excepción permitida,
- mounts read-only para logs y runtime Docker.

## Seguimiento

Este ADR debe revisarse cuando:
- se añadan nuevos contenedores privilegiados,
- cambien las políticas runtime,
- se incorporen nuevos controles compensatorios.

## Referencias

- ADR-0005 — Runtime desacoplado y lazy imports
- ADR-0020 — Container Execution Model & Privilege Strategy
- ADR-0025 — Modelo SMTP explícito y endurecimiento de configuración

# ADR-0025 — Modelo SMTP explícito y endurecimiento de configuración (Endurecimiento SMTP)

Fecha: 2026-05-13
Estado: Aprobado
Ámbito: server_monitoring_2509

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

# ADR-0026 — Estrategia de validación y testing del modelo SMTP (Estrategia de validación multinivel)

Fecha: 2026-05-13
Estado: Propuesta
Implementación: Parcial
Ámbito: server_monitoring_2509

## Contexto

ADR-0025 define el modelo SMTP explícito y las reglas operativas asociadas. Este ADR define exclusivamente su estrategia de validación y testing.

Históricamente existían problemas relacionados con:
- lectura de credenciales SMTP durante import-time,
- heurísticas implícitas de autenticación,
- contaminación de CI por secrets presentes en runners,
- diferencias entre entornos locales, CI y contenedores,
- ausencia de validaciones automáticas sobre Compose y entrypoints.

Para reducir estos riesgos se adopta una estrategia de testing multinivel.

## Problema

La validación manual no permite detectar de forma fiable:
- regresiones entre modos relay/auth,
- lectura indebida de credenciales SMTP,
- side-effects durante importación,
- configuraciones inconsistentes en Compose,
- incumplimientos arquitectónicos.

Además, una conexión SMTP satisfactoria no garantiza cumplimiento arquitectónico ni coherencia operativa.

## Decisión

Se adopta una estrategia de validación basada en:
- unit tests,
- integration tests,
- policy tests,
- runtime smoke checks en CI.

### 1. Unit tests

Validan comportamiento aislado de:
- SMTP_MODE,
- init_config(),
- send_email(),
- fail-fast en auth.

Características:
- sin tráfico SMTP real,
- sin dependencia DNS,
- sin uso de credenciales reales,
- uso de mocking y monkeypatching.

### 2. Integration tests

Validan interacción entre librería y entorno controlado:
- carga de credenciales SMTP,
- comportamiento relay/auth,
- validación de errores por ausencia de credenciales.

Características:
- uso de tmp_path,
- filesystem temporal,
- sin infraestructura SMTP externa.

### 3. Policy tests

Validan cumplimiento arquitectónico y declarativo:
- presencia explícita de SMTP_MODE,
- consistencia entre auth y montaje de credenciales,
- placement correcto de init_config().

Se realizan mediante análisis estático sobre:
- Compose YAML,
- AST Python.

Objetivo:
detectar errores estructurales sin ejecutar código.

### 4. Runtime smoke checks en CI

CI debe validar:
- instalación correcta de dependencias,
- ejecución de tests,
- aislamiento de credenciales temporales,
- funcionamiento básico relay/auth.

Requisitos:
- PYTHONPATH=src,
- entorno aislado,
- dependencias instaladas desde requirements.txt.

## Razonamiento

La validación multinivel permite separar responsabilidades y reducir falsos diagnósticos.

Unit tests
    Permiten validar semántica interna y lógica de control:
    - autenticación,
    - validación de modos,
    - fail-fast,
    - decisiones runtime.

    El uso de mocks evita:
    - tráfico SMTP real,
    - dependencia de DNS,
    - flakiness,
    - latencia externa.

Integration tests
    Validan integración entre librería y filesystem controlado sin necesidad de infraestructura completa.

    Esto permite detectar:
    - errores de carga de secrets,
    - problemas de fallback,
    - incompatibilidades entre runtime y tests.

Policy tests
    El comportamiento esperado no depende únicamente del código Python, sino también de la infraestructura declarativa.

    La validación estática sobre Compose y AST permite detectar:
    - mounts inconsistentes,
    - uso incorrecto de SMTP_MODE,
    - llamadas a init_config() fuera de __main__,
    - side-effects en import-time.

    El análisis AST se adopta porque permite validar estructura sintáctica sin ejecutar módulos ni disparar efectos secundarios.

CI reproducible
    El aislamiento explícito de credenciales SMTP y dependencias reduce:
    - contaminación desde runners,
    - falsos negativos,
    - diferencias entre entornos.

    Esto mejora la auditabilidad y estabilidad del pipeline.

## Alcance actual

La estrategia actual valida:
- comportamiento relay/auth,
- fail-fast en auth,
- login SMTP condicional,
- ausencia de autenticación en relay,
- placement correcto de init_config(),
- consistencia básica de Compose,
- aislamiento de runtime durante CI.

## Limitaciones

La estrategia actual no valida:
- entrega SMTP real extremo a extremo,
- negociación TLS contra proveedores reales,
- permisos efectivos host,
- rotación dinámica de credenciales,
- enforcement runtime de mounts read-only,
- escenarios reales de timeout o latencia.

Los policy tests tampoco cubren:
- templating complejo de Compose,
- mounts dinámicos externos,
- llamadas indirectas a init_config().

## Consecuencias

Positivas:
- reducción de regresiones,
- detección temprana de errores,
- mayor estabilidad de validación en CI,
- reducción de side-effects durante importación,
- mayor coherencia entre infraestructura declarativa y runtime.

Operativas:
- nuevos entrypoints deben respetar la política de inicialización,
- nuevos stacks deben declarar SMTP_MODE,
- los tests deben mantenerse alineados con Compose y runtime real.

## Guía operativa

Cada nuevo servicio debe:
- declarar SMTP_MODE explícitamente,
- invocar init_config() únicamente dentro de:
  if __name__ == "__main__":
- evitar lectura de credenciales durante import-time.

Los tests deben:
- evitar dependencias externas,
- aislar filesystem y entorno,
- no reutilizar credenciales reales.

## Evolución futura

Líneas recomendadas:
- tests E2E SMTP en entorno controlado,
- validación automática de mounts read-only,
- tests de resiliencia y timeouts,
- consolidación de fixtures comunes,
- policy checks automáticos en pull requests,
- validación de rotación de credenciales.

## Referencias

- ADR-0005 — Runtime desacoplado y lazy imports
- ADR-0019 — Resilience Testing Strategy
- ADR-0024 — Container Privilege Exception Policy
- ADR-0025 — Modelo SMTP explícito y endurecimiento de configuración

Archivos relacionados:
- src/monitoring/common/config.py
- tests/unit/*
- tests/integration/*
- ops/stacks/*/compose.yml
- .github/workflows/ci.yml
- Makefile



# ADR-0027 — Tipología oficial de contenedores y política de healthchecks

Fecha: 2026-05-17
Estado: Aprobado
Contexto: server_monitoring_2509 — Hardening runtime, validación CI/CD y normalización de healthchecks

## Contexto

Durante la evolución del entorno server_monitoring se detectaron inconsistencias en:
- validación de healthchecks
- clasificación semántica de contenedores
- criterios CI/CD
- auditoría runtime
- separación entre readiness y liveness

La validación original utilizaba:
- grep textual sobre compose
- detección heurística de healthchecks
- correlación parcial entre service_name y container_name

Esto provocaba:
- falsos positivos
- falsos negativos
- ambigüedad arquitectónica
- drift entre ADR y runtime real
- enforcement inconsistente

Especialmente en:
- monitoring-python
- promtail
- smtp-relay
- monitoring-cron

Adicionalmente se detectó que algunos contenedores eran tratados como microservicios HTTP tradicionales cuando realmente representaban:

- runtimes operativos
- supervisores
- tooling persistente
- componentes infraestructurales

La validación anterior asumía implícitamente:
    “todo contenedor debe tener un healthcheck homogéneo”

Esta premisa resultó incorrecta.

No todos los contenedores:
- exponen APIs
- representan servicios funcionales
- requieren readiness HTTP
- participan en tráfico de negocio

## Problema identificado

Los healthchecks estaban siendo utilizados con semánticas distintas según la naturaleza real del contenedor.

Esto generaba:
- checks artificiales
- validaciones incorrectas
- gates CI poco fiables
- confusión operacional
- auditorías ambiguas

Se identificaron además limitaciones técnicas en:
- parsing YAML manual
- detección basada en grep
- resolución indirecta de compose
- correlación runtime ↔ compose

## Decisión

Se adopta una clasificación oficial de contenedores y una política explícita de healthchecks.

Cada contenedor debe clasificarse según su función arquitectónica real.

La validación runtime debe utilizar:
- docker compose config ejecutado exclusivamente desde el host
- parsing estructurado
- correlación determinista service/container

La validación NO debe asumir:
- acceso a docker.sock desde contenedores
- disponibilidad de Docker CLI dentro de runtimes operativos
- capacidades de control plane en TOOLBOX_RUNTIME o INFRA_TRUSTED

Toda validación relacionada con:
- docker compose
- docker inspect
- docker ps
- docker.sock

debe ejecutarse explícitamente desde el host o CI runner autorizado.

Los contenedores operativos:
- no constituyen tooling Docker implícito
- no deben montar docker.sock salvo excepción ADR explícita
- no deben utilizarse como punto de ejecución de auditoría runtime

Se establece además un archivo centralizado:
    ops/runtime_containers.yml

como fuente única de verdad para:
- clasificación runtime
- política de healthchecks
- enforcement CI
- auditoría operacional

## Tipología oficial de contenedores

### 1. SERVICE_RUNTIME

Contenedores que exponen funcionalidad activa consumible.

Ejemplos:
- postgres
- grafana
- loki

Requisitos:
- readiness checks reales
- validación funcional explícita
- detección determinista de disponibilidad

Checks válidos:
- pg_isready
- HTTP /ready
- HTTP /health

No se permiten:
- exit 0 artificiales
- keepalive falsos
- checks semánticamente vacíos

---

### 2. SUPERVISOR_RUNTIME

Contenedores cuyo objetivo principal es mantener un scheduler o supervisor operativo.

Ejemplo:
- monitoring-cron

Requisitos:
- liveness checks
- validación del proceso supervisor

Checks válidos:
- pidof
- pgrep

Objetivo:
- detectar caída del scheduler
- detectar corrupción runtime

---

### 3. TOOLBOX_RUNTIME

Contenedores persistentes utilizados como:
- entorno operador
- runtime controlado
- tooling operacional
- punto de entrada IaC

Ejemplo:
- monitoring-python

Características:
- pueden utilizar keepalive explícito
- pueden ejecutarse mediante docker exec
- no representan servicios funcionales externos

No requieren:
- readiness HTTP
- validación semántica de API

Los healthchecks triviales son aceptables únicamente si:
- están documentados
- la clasificación TOOLBOX_RUNTIME es explícita

---

### 4. INFRA_TRUSTED

Contenedores upstream o infraestructurales considerados dependencias confiables.

Ejemplos:
- promtail
- smtp-relay

Deben utilizar:
- el mecanismo más apropiado según capacidades reales del upstream
- minimizando modificaciones sobre imágenes oficiales

Puede aceptarse ausencia de healthcheck cuando:
- la imagen upstream no proporcione tooling adecuado
- el coste de introducir tooling adicional no esté justificado
- existan mecanismos alternativos de validación operacional

Debe evitarse:
- hardening artificial
- wrappers innecesarios
- sidecars no justificados
- modificación innecesaria de imágenes oficiales

## Política oficial de healthchecks

Los healthchecks deben alinearse con:
- semántica runtime
- comportamiento real del contenedor
- función arquitectónica

No se asume un modelo homogéneo basado exclusivamente en microservicios HTTP.

## Implementación adoptada

Se introduce:
- ops/runtime_containers.yml
- ops/runtime_containers.sh
- validación CI estructurada
- enforcement runtime por clasificación
- auditoría basada en docker compose config

La validación ya no depende exclusivamente de:
- grep textual
- coincidencias heurísticas
- comentarios YAML

## Modelo de validación runtime

El script:
ops/runtime_containers.sh

implementa:
- parseo estructurado de runtime_containers.yml
- resolución determinista compose
- correlación entre:
    service_name
    container_name
- detección explícita de healthchecks

Se incorpora:
    check-health <container>

como mecanismo oficial de validación.

Formato de salida:
    container|FOUND|compose|service|healthcheck

Estados soportados:
    FOUND
    NOT_FOUND
    COMPOSE_INVALID
    WARN

Donde:
- WARN representa configuraciones explícitamente aceptadas por política runtime
especialmente en contenedores:
    INFRA_TRUSTED
    TOOLBOX_RUNTIME

## Decisión específica sobre promtail

promtail queda clasificado como:

INFRA_TRUSTED

Se elimina el healthcheck runtime del contenedor.

Motivación:
- la imagen oficial upstream no incorpora:
    wget
    curl
    utilidades equivalentes de validación HTTP
introducir tooling adicional únicamente para healthchecks:
- rompería alineación upstream
- aumentaría drift operacional
- introduciría hardening artificial

La validación operacional de promtail pasa a realizarse mediante:
- validación CI estructural
- verificación runtime con:
- docker ps
- docker logs
- docker inspect

El enforcement asociado queda configurado como:
    enforcement_level: warn

Objetivo:
- evitar falsos negativos
- respetar capacidades reales del upstream
- mantener coherencia IaC y reproducibilidad runtime

## Decisión específica sobre monitoring-python

monitoring-python queda clasificado oficialmente como:

TOOLBOX_RUNTIME

Su función es:
- runtime persistente
- tooling operacional
- ejecución controlada mediante docker exec
- entorno operador

No representa:
- API
- microservicio HTTP
- daemon funcional expuesto

Por tanto:
- no requiere readiness HTTP
- puede utilizar keepalive documentado
- puede tener enforcement warn

Esto NO constituye:
- anti-pattern
- workaround
- desviación arquitectónica

## Consecuencias

Positivas:
- reducción de falsos positivos
- validación CI más determinista
- coherencia ADR ↔ runtime
- mejor auditabilidad
- separación formal readiness/liveness
- enforcement centralizado

Operativas:
- nuevos contenedores deben declararse en runtime_containers.yml
- CI y Makefile dependen de la clasificación runtime
- los tests deben respetar la semántica del contenedor

## Limitaciones conocidas

La presencia de un healthcheck declarado NO garantiza por sí sola operatividad real.

Durante la validación se detectó que:
- algunos contenedores upstream minimalistas
- pueden no incluir tooling HTTP básico
- necesario para implementar healthchecks tradicionales

Caso identificado:
    promtail

La imagen oficial upstream carece de:
    wget
    curl
    herramientas equivalentes

Por tanto:
- la validación CI distingue entre:
    ausencia legítima de healthcheck
    incumplimiento arquitectónico
- algunos contenedores INFRA_TRUSTED pueden operar sin healthcheck runtime
- la validación operacional real debe complementarse mediante:
    docker ps
    docker inspect
    docker logs

## Restricciones

No se permitirá:
- readiness artificial
- endpoints fake
- sidecars innecesarios
- checks semánticamente vacíos
- degradar reproducibilidad IaC

Los healthchecks:
- deben ejecutarse dentro del contenedor
- deben ser deterministas
- deben devolver exit codes reales
- no deben depender del host

## Riesgos identificados

Persisten riesgos asociados a:
- parsing YAML manual mediante awk
- dependencia de docker compose config
- divergencias entre compose renderizado y runtime real
- validación parcial de healthchecks upstream

# ==========================================

## Validación futura

Las siguientes herramientas deben alinearse con esta decisión:
- CI
- Makefile
- audit_repo_host.sh
- runtime tests
- resiliency tests
- policy checks

Las futuras validaciones deberán distinguir explícitamente:
- smoke tests
- policy checks
- certification checks
- runtime enforcement

## Relación con otros ADR

Este ADR complementa:
- ADR-0008 — Servicios micro-stack vs infra-stack
- ADR-0010 — Arquitectura runtime cron
- ADR-0014 — Docker Port Exposure Policy
- ADR-0015 — Docker Network Exposure Model
- ADR-0017 — Resilience model at docker single-node
- ADR-0018 — Docker security runtime and resilience requirements
- ADR-0019 — Resilience Testing Strategy
- ADR-0020 — Container Execution Model & Privilege Strategy

## Estado

Aprobado.
Arquitectura runtime normalizada.
Clasificación de contenedores formalizada.
Política de healthchecks alineada con semántica operacional real.

ADR-0028 – Política de reproducibilidad Docker y endurecimiento de validaciones IaC

Fecha: 2026-05-18
Estado: Aprobado
Contexto: Hardening moderado de reproducibilidad Docker – server_monitoring_2509

## Contexto

Durante la evolución de las validaciones de infraestructura del proyecto server_monitoring_2509 se detectaron varios problemas relacionados con:
- uso implícito de tags mutables en imágenes Docker
- ausencia de validaciones de reproducibilidad
- falsos positivos en auditorías de Dockerfiles
- bloqueo excesivo de auditorías por estados runtime transitorios
- incoherencia entre hardening teórico y operativa real del entorno

Las validaciones iniciales introducidas en:
- ops/audit/validate_reproducibility.sh
- ops/audit/validate_dockerfiles.sh

permitían detectar:
- uso de :latest
- imágenes upstream sin digest
- requirements Python no fijados
- apt-get install sin versiones explícitas
- imágenes dangling

Sin embargo, durante validaciones reales sobre el servidor se observaron problemas operativos relevantes:

- falsas detecciones de latest implícito en:
    FROM ${BASE_IMAGE}

- bloqueo innecesario de auditorías debido a imágenes dangling temporales
  generadas por Docker BuildKit

- incompatibilidad entre ciertas imágenes upstream y tags inexistentes
  (caso boky/postfix:3.6.0)

- endurecimiento excesivo para un entorno no orientado a supply-chain
  crítica

Además, se detectó necesidad de mejorar reproducibilidad mínima de runtime sin introducir complejidad excesiva ni drift operacional.

## Decisión

Se adopta una política pragmática de reproducibilidad Docker basada en:

### 1. Digest obligatorio en imágenes upstream runtime

Las imágenes upstream utilizadas directamente en compose.yml deberán fijarse mediante digest SHA256.

Ejemplos adoptados:
- postgres:14.3@sha256:...
- grafana/promtail:2.9.3@sha256:...
- grafana/loki:2.9.3@sha256:...
- grafana/grafana:10.4.2@sha256:...

Objetivo:
- evitar mutabilidad silenciosa de tags
- mejorar reproducibilidad de despliegue
- mantener trazabilidad de imágenes

### 2. Prohibición de :latest explícito

Se mantiene prohibición explícita de:
    :latest

tanto en:
- compose.yml
- Dockerfiles

La validación permanece bloqueante (FAIL).

### 3. Excepción explícita para FROM parametrizado

Se acepta el patrón:
    FROM ${BASE_IMAGE}

cuando:
- BASE_IMAGE esté definido mediante ARG
- exista resolución explícita de versión o digest

Motivación:
- evitar falsos positivos
- permitir reutilización controlada
- mantener flexibilidad CI/CD

La validación pasa a:
- WARN informativo
- no FAIL

### 4. Política pragmática sobre dangling images

Las imágenes dangling pasan a considerarse:
- condición operacional temporal
- no incumplimiento arquitectónico

Motivación:
- Docker BuildKit puede generar dangling legítimos
- bloquear auditorías por este motivo introduce ruido operacional

Nueva política:
- WARN operativo
- nunca FAIL bloqueante

Se añade recomendación explícita:
    make clean-dangling
como limpieza posterior a builds o despliegues.

### 5. Requirements Python no fijados

Las dependencias Python no completamente fijadas:
    >=
    PyYAML sin versión
    etc.

pasan a clasificarse como:
- WARN
- recomendación de mejora futura

y no como:
- FAIL bloqueante

Motivación:
- evitar sobre-endurecimiento prematuro
- mantener compatibilidad operativa
- priorizar estabilidad del pipeline actual

### 6. apt-get install sin versiones explícitas

Las instalaciones apt sin pinning:
- permanecen permitidas
- generan únicamente WARN informativo

Motivación:
- Debian slim introduce complejidad alta para pinning estricto
- el beneficio operacional actual no justifica el coste

## Consecuencias

Positivas:
- mejora moderada de reproducibilidad runtime
- reducción de falsos positivos
- auditorías más alineadas con operativa real
- pipeline CI más estable
- menor drift respecto a upstream

Negativas / trade-offs:
- reproducibilidad aún no completamente hermética
- requirements Python siguen parcialmente mutables
- apt packages continúan dependiendo de repositorios Debian runtime

Riesgos aceptados:
- cambios menores futuros en dependencias Python
- variabilidad limitada en paquetes apt
- dependencia de disponibilidad de digests upstream

## Validaciones realizadas

Se validó satisfactoriamente:

### validate_reproducibility.sh
- detección correcta de imágenes sin digest
- aceptación de imágenes locales con tag explícito
- dangling images degradadas a WARN

### validate_dockerfiles.sh
- detección correcta de :latest explícito
- exclusión correcta de:
    FROM ${BASE_IMAGE}

- requirements no fijados degradados a WARN
- apt-get install sin pinning degradado a WARN

### Runtime validado

Servicios operativos correctamente:
- postgres
- promtail
- loki
- grafana
- monitoring-python
- monitoring-cron
- smtp-relay

## Alternativas consideradas

### Opción A — Reproducibilidad estricta total

Incluyendo:
- pinning completo apt
- requirements totalmente fijados
- builds herméticos
- bloqueo por dangling images

Rechazada por:
- complejidad excesiva
- alto coste operacional
- sobreingeniería para el alcance actual

### Opción B — Mantener validaciones mínimas anteriores

Rechazada por:
- insuficiente control de mutabilidad
- ausencia de trazabilidad runtime
- riesgo de drift silencioso

## Estado

Aceptado.

## Notas

Esta decisión representa:
- endurecimiento moderado
- no hardening extremo

El objetivo explícito es:
- mejorar reproducibilidad práctica
- minimizar falsos positivos
- preservar mantenibilidad operacional

Las validaciones actuales deben entenderse como:
- guardrails operativos
- no como framework completo de supply-chain security


# ADR-0029 — Structured Compose Policy Audit

Fecha: 2026-05-20
Estado: Aprobado
Contexto: server_monitoring_2509 — Hardening de auditoría Compose y validación estructurada runtime

## Contexto

Durante la evolución del entorno server_monitoring se detectaron limitaciones importantes en las validaciones de seguridad y compliance aplicadas sobre Docker Compose.

La validación original utilizaba principalmente:
- grep
- awk
- búsquedas textuales
- parsing shell heurístico
- correlación parcial entre runtime y compose

Especialmente en:
- ops/audit/audit_repo_host.sh
- Makefile
- validaciones runtime
- policy checks

Este enfoque provocaba:
- falsos positivos
- falsos negativos
- dependencia excesiva del formato YAML
- fragilidad ante cambios de indentación o estructura
- dificultad para evolucionar políticas
- baja mantenibilidad
- difícil integración CI/CD
- auditorías parcialmente no deterministas

Adicionalmente se identificaron inconsistencias arquitectónicas:
- parte del tooling operacional Python debía ejecutarse desde host-side
- algunas validaciones parseaban salida humana
- las severidades no estaban centralizadas
- no existía salida machine-readable estable
- la correlación runtime ↔ compose no era determinista

El proyecto mantiene actualmente:
- Docker Compose standalone
- arquitectura single-node
- modelo híbrido Host-Controlled Docker Compose IaC
- runtime operacional basado en infra-stacks
- validaciones pragmáticas alineadas con ADR-0017
- separación explícita entre:
    - runtime funcional containerizado
    - control-plane operacional host-side
  definida en ADR-0011

Durante la implantación también se detectó una limitación operacional adicional:
    docker compose config

requiere contexto Compose válido.

Cuando el comando se ejecuta dentro del contenedor:
    monitoring-python

puede producir:
    no configuration file provided: not found

si el runtime no dispone del directorio Compose correcto o no existe:
- COMPOSE_FILE
- working directory válido
- bind mount consistente

Posteriormente se verificó además que el runtime actual:
- no incorpora docker CLI
- no incorpora docker compose
- no expone docker.sock
- no actúa como toolbox Docker host-level

Por tanto:
- la validación runtime debe degradar correctamente
- los fallos de resolución Compose no deben romper auditorías completas
- el sistema debe soportar fallback explícito
- el fallback YAML estático debe considerarse comportamiento operativo válido

## Problema identificado

Las validaciones heurísticas basadas en shell no proporcionaban suficiente robustez para:
- auditoría reproducible
- enforcement progresivo
- validación estructurada real
- integración CI/CD
- los runtimes funcionales containerizados no deben asumir capacidades Docker host-level

## Decisión

Se adopta un modelo de auditoría estructurada basado en parsing Compose mediante Python.

Se establece como motor oficial:
    ops/audit/compose_policy_checks.py

La validación estructurada se ejecuta preferiblemente desde el host mediante:
    python3 -m ops.audit.compose_policy_checks

sin depender del runtime containerizado monitoring-python.

El contenedor:
    monitoring-python

actúa como runtime Python aislado y NO se considera un toolbox Docker completo.

El runtime actual NO garantiza:
- disponibilidad docker CLI
- disponibilidad docker compose
- acceso operativo a docker.sock
- resolución compose runtime-resolved

Por tanto:
- docker compose config puede no estar disponible dentro del runtime
- el fallback YAML estático debe considerarse comportamiento operativo válido
- las validaciones deben degradar explícitamente sin romper auditorías

Cuando exista tooling Docker operativo dentro del runtime, podrá utilizarse:
    docker compose config

como representación runtime-resolved del estado Compose efectivo.

En ausencia de dichas capacidades:
- el sistema degradará explícitamente
- el fallback YAML estático será comportamiento válido
- las auditorías no deberán fallar completamente

La salida soporta:
- modo humano
- salida JSON machine-readable
- checks parciales mediante --check
- runtime validation mediante --self-test

La severidad se centraliza mediante:
POLICY_SEVERITY

El host:
- coordina ejecución
- recopila resultados
- consume JSON estructurado
- evita parsear salida humana
- mantiene las operaciones Docker host-level

## Fallback estructurado

Cuando:
    docker compose config

no puede resolverse correctamente dentro del runtime, el sistema degrada explícitamente a:
- parsing YAML estático
- merge best-effort
- validación parcial

mediante:
    load_compose_from_files()

sobre archivos detectados bajo:
    ops/

El sistema debe emitir warning explícito cuando ocurra degradación runtime.

Ejemplo esperado:
    [WARN] Usando parseo estático de archivos Compose

Este fallback:
- NO garantiza resolución completa Compose
- NO resuelve merges complejos de forma idéntica
- NO reproduce profiles avanzados
- NO sustituye completamente docker compose config

Sin embargo:
- preserva auditabilidad mínima
- evita fallo completo del pipeline
- mantiene comportamiento determinista suficiente para auditoría defensiva
- reduce dependencia operacional del control-plane Docker

## Runtime Model

La lógica principal de validación se ejecuta dentro del runtime containerizado del proyecto.

Principios adoptados:

1 — El host no ejecuta lógica core de validación
El host:
- orquesta
- invoca runtime
- consume JSON
- presenta resultados
- mantiene control-plane Docker

No debe ejecutar:
- validaciones principales
- lógica policy core
- parsing Compose complejo

2 — Runtime operacional centralizado
El runtime principal válido es:
    monitoring-python

Este runtime:
- ejecuta lógica Python versionada
- realiza validaciones estructuradas best-effort
- consume configuraciones runtime del proyecto
- opera como runtime operacional de aplicación

El runtime NO garantiza:
- acceso Docker CLI
- acceso docker compose
- acceso docker.sock
- capacidades completas de toolbox Docker

Las operaciones Docker host-level permanecen fuera del contenedor.

3 — Parsing estructurado
Las validaciones utilizan:
- parsing YAML real
- estructuras Python
- JSON machine-readable

No se considera válido:
- parsear salida humana con awk
- correlación basada únicamente en grep
- enforcement basado exclusivamente en texto plano

## Validaciones estructuradas implementadas

Se implementan validaciones estructuradas para:
- puertos publicados
- docker.sock
- imágenes con :latest
- imágenes sin digest
- privileged=true
- mounts sensibles RW
- cap_add
- read_only=false

Las validaciones operan sobre:

services:
    resueltos mediante Compose.

Cuando la resolución runtime no esté disponible:
- se utilizará fallback YAML
- se emitirá warning explícito
- la validación continuará en modo best-effort

## Runtime checks

Se añade:
    --self-test

para validar:
- disponibilidad opcional docker CLI
- disponibilidad opcional docker compose
- operatividad opcional docker compose config
- acceso opcional docker.sock
- degradación fallback correctamente gestionada

La ausencia de capacidades Docker dentro del runtime NO constituye necesariamente fallo arquitectónico.

Objetivo:
- detectar degradaciones runtime
- validar capacidad operacional disponible
- identificar problemas de control-plane
- mejorar observabilidad de auditoría

## Severidades

Las severidades se centralizan mediante:
POLICY_SEVERITY

Clasificación inicial:
- privileged=true → FAIL
- resto → WARN

El exit code queda alineado con la severidad.

Consecuencia:
- violaciones FAIL devuelven rc != 0
- warnings permanecen auditables sin romper ejecución

## Herramientas auxiliares

Se introduce:
    ops/audit/parse_compose_json.py

como helper ligero para:
- parse JSON desde shell
- evitar Python inline en bash
- simplificar mantenimiento operacional

El host puede utilizar prioritariamente:
- jq
- parse_compose_json.py

para consumir JSON estructurado.

## Restricciones

No se permitirá:
- enforcement basado exclusivamente en grep
- parsear salida humana como fuente principal
- ejecutar lógica policy core desde host
- introducir dependencias Kubernetes
- introducir OPA/Rego
- introducir policy-as-code complejo
- degradar reproducibilidad runtime

Las validaciones:
- deben ser deterministas
- deben soportar salida machine-readable
- deben degradar explícitamente cuando el runtime Compose no pueda resolverse
- no deben asumir capacidades Docker dentro del runtime Python

## Tradeoffs

### Ventajas
- reducción significativa de falsos positivos
- reducción significativa de falsos negativos
- validación estructurada real
- mejor mantenibilidad
- integración CI/CD más fiable
- enforcement progresivo
- menor deuda técnica shell-based
- mejor correlación YAML ↔ auditoría
- alineación con arquitectura container-first
- reducción de superficie de ataque del runtime Python

### Inconvenientes
- mayor complejidad respecto a shell puro
- dependencia parcial del fallback YAML
- pérdida parcial de correlación runtime ↔ compose
- necesidad de contexto Compose detectable
- mayor complejidad de degradación operacional

## Riesgos identificados

Persisten riesgos asociados a:
- divergencias entre runtime y YAML estático
- degradación best-effort del fallback
- resolución Compose parcial
- dependencia de rutas Compose detectables
- pérdida de correlación runtime ↔ compose cuando docker compose config no está disponible

En el runtime actual:
    monitoring-python

NO dispone de:
- docker CLI
- compose plugin
- acceso docker.sock

Esto reduce superficie de ataque respecto al diseño inicial, pero incrementa dependencia del fallback YAML estático.

Históricamente se contempló que:
    monitoring-python

pudiese requerir acceso parcial a:
    docker.sock

Sin embargo, el runtime actual en producción NO expone:
- docker.sock
- docker CLI
- docker compose

Las validaciones estructuradas operan actualmente mediante:
- parsing YAML estático
- degradación explícita
- validación best-effort

La resolución Compose runtime-resolved queda limitada a entornos donde el tooling Docker exista explícitamente.

Esto incrementa superficie de ataque respecto a un contenedor completamente aislado.

Actualmente se considera aceptable debido a:
- arquitectura single-node
- entorno controlado
- ausencia de multitenancy
- modelo infra-stack documentado
- mitigaciones existentes en ADR-0008 y ADR-0018

## Mitigaciones operativas

Mitigaciones obligatorias:

1 — Restricción de exposición
- monitoring-python no debe exponer puertos públicos
- acceso exclusivamente interno
- no montar docker.sock salvo excepción explícitamente documentada
- no introducir docker CLI dentro del runtime salvo necesidad operacional justificada

2 — Auditoría
- uso de docker.sock auditado automáticamente
- policy checks obligatorios
- degradación runtime auditada mediante warnings explícitos

3 — Runtime controlado
- scripts versionados
- ejecución auditada
- tooling conocido
- fallback deterministicamente gestionado

4 — Fallback explícito
- degradación controlada
- warnings visibles
- no ocultar fallo de docker compose config
- continuidad operacional best-effort

## Compatibilidad

La decisión mantiene compatibilidad con:
- Docker Compose standalone
- arquitectura single-node
- runtime actual
- Makefile existente
- audit_repo_host.sh
- CI actual
- ADR previos
- modelo IaC actual

No se introduce:
- Kubernetes
- Docker Swarm
- OPA/Rego
- policy engines externos
- reconciliación distribuida

## Consecuencias

Positivas
- auditoría estructurada reproducible
- validación machine-readable
- reducción de deuda técnica shell-based
- mejor integración futura con CI/CD
- separación más clara entre:
    - runtime funcional containerizado
    - control-plane operacional host-side
- reducción de superficie de ataque del runtime Python
- eliminación de dependencia estructural de docker.sock en monitoring-python
- alineación entre arquitectura declarada y runtime real observado
- enforcement progresivo viable
- mayor coherencia ADR ↔ runtime real

Negativas
- dependencia operacional del fallback YAML
- necesidad de mantener tooling Python adicional
- posibilidad de degradación fallback parcial
- pérdida parcial de resolución runtime efectiva
- complejidad superior respecto a grep simple

## Validación futura

Las siguientes herramientas deberán alinearse con esta decisión:
- CI
- Makefile
- audit_repo_host.sh
- runtime tests
- resiliency tests
- policy checks

Las futuras validaciones deberán distinguir explícitamente:

- smoke tests
- policy checks
- runtime validation
- certification checks
- enforcement checks
- fallback checks

## Relación con otros ADR

Este ADR complementa:

- ADR-0008 — Servicios micro-stack vs infra-stack
- ADR-0011 — Python Runtime Execution Model
- ADR-0014 — Docker Port Exposure Policy
- ADR-0015 — Docker Network Exposure Model
- ADR-0017 — Resilience model at docker single-node
- ADR-0018 — Docker security runtime and resilience requirements
- ADR-0019 — Resilience Testing Strategy
- ADR-0020 — Container Execution Model & Privilege Strategy
- ADR-0024 — Container Privilege Exception Policy
- ADR-0027 — Tipología oficial de contenedores y política de healthchecks

## Estado
Aprobado.
Auditoría Compose estructurada normalizada.
Modelo runtime-aligned corregido respecto al runtime real.
Fallback Compose explícitamente formalizado.
Validación machine-readable establecida.
Degradación best-effort documentada oficialmente.

# ADR-0030 – Auditoría Runtime HostConfig y Visibilidad de Privilegios Docker

Fecha: 2026-05-23
Estado: Aprobado
Contexto: server_monitoring_2509 - Hardening runtime y auditoría Host-Controlled IaC

## Contexto

Durante la evolución del hardening runtime del proyecto se identificó que las validaciones existentes cubrían únicamente una parte del estado real de privilegios Docker.

La auditoría actual ya verificaba:
- UID runtime efectivo
- uso de docker.sock
- privileged parcial
- mounts sensibles
- aislamiento de red
- validaciones Compose estructuradas

Sin embargo, todavía no existía visibilidad estructurada sobre:
- HostConfig runtime efectivo
- Linux capabilities
- seccomp runtime
- AppArmor runtime
- no-new-privileges
- readonly rootfs efectivo

Asimismo, parte de la auditoría seguía dependiendo de:
- correlaciones shell
- grep heurístico
- parsing textual parcial

El proyecto opera explícitamente bajo:
- Docker Compose standalone
- single-node runtime
- Host-Controlled IaC
- observabilidad híbrida
- diferenciación entre:
  - SERVICE_RUNTIME
  - INFRA_TRUSTED
  - TOOLBOX_RUNTIME

Por tanto, no resultaba coherente adoptar modelos de enforcement complejos inspirados en Kubernetes o plataformas cloud-native enterprise.

## Decisión

Se adopta una nueva fase de auditoría runtime basada en:
- docker inspect host-side
- validación HostConfig real
- runtime visibility estructurada
- parsing determinista

La fase inicial tendrá únicamente objetivos de:
- visibilidad
- baseline runtime
- inventario reproducible

NO de enforcement agresivo.

La auditoría runtime:
- NO dependerá de docker.sock dentro de contenedores
- NO ejecutará lógica Docker desde runtime containers
- NO bloqueará pipelines inicialmente
- NO impondrá hardening masivo automático

La información runtime recopilada incluirá visibilidad estructurada sobre:
- Privileged
- CapAdd
- CapDrop
- SecurityOpt
- ReadonlyRootfs
- AppArmorProfile
- tmpfs
- devices runtime

La fase actual tendrá carácter exclusivamente observacional (runtime visibility baseline), sin interpretar todavía los resultados como enforcement definitivo.

Las validaciones se ejecutarán exclusivamente desde el host mediante tooling estructurado existente.

## Consecuencias

### Positivas
- Mayor visibilidad runtime real
- Reducción parcial de drift Compose ↔ runtime
- Menor dependencia de parsing heurístico
- Auditoría más determinista
- Mejor alineación con ADR-0018 y ADR-0029
- Baseline reproducible de evidencia runtime
- Base futura para hardening incremental

### Negativas
- Incremento moderado de complejidad de auditoría
- Dependencia parcial de docker inspect host-side
- Posible aparición inicial de ruido operacional
- Ausencia todavía de clasificación runtime contextual
- Necesidad futura de baseline de excepciones runtime

## Limitaciones
Esta fase NO garantiza todavía:
- enforcement completo de mínimo privilegio
- diff estructurado Compose ↔ runtime
- clasificación runtime contextual
- baseline formal de excepciones runtime
- seccomp obligatorio
- AppArmor obligatorio
- cap_drop universal
- no-new-privileges universal

Tampoco sustituye:
- revisiones manuales
- excepciones ADR documentadas
- validación operacional progresiva

## Estado futuro esperado
La auditoría runtime servirá como baseline inicial para futuras fases de:
- diff Compose ↔ runtime estructurado
- clasificación runtime contextual
- baseline de excepciones runtime
- hardening incremental
- enforcement selectivo
- validación CI más precisa

manteniendo siempre compatibilidad con:
- Docker Compose standalone
- arquitectura single-node
- operabilidad del entorno PRO
- observabilidad híbrida existente

# ADR-0031 – Gobernanza Runtime Docker y Clasificación de Dependencias Host

    Fecha: 2026-05-26
    Estado: Aprobado
    Contexto: server_monitoring_2509

## Contexto

    Tras completar las fases de:
    - reproducibilidad
    - segmentación de red
    - endurecimiento runtime inicial
    - normalización de secretos
    - separación host/runtime
    - auditoría HostConfig

    se ejecutó una validación operacional completa del runtime Docker en entorno PRO DigitalOcean.

La auditoría se realizó utilizando:
    - docker inspect
    - HostConfig runtime
    - validación declarativa de capabilities Linux vía HostConfig
    - correlación runtime vs compose labels
    - clasificación runtime de mounts y aislamiento
    - análisis de mounts
    - validación de puertos publicados
    - comprobaciones UFW
    - healthchecks runtime
    - validación compose discovery
    - revisión de usuarios runtime

    La evidencia operacional confirmó:
    Estado actual confirmado
    - Aislamiento y privilegios
        No existe docker.sock montado en ningún contenedor.
        No existe privileged=true.
        No existe network_mode=host.
        monitoring-python y monitoring-cron ejecutan como appuser.
        grafana y loki ejecutan con usuarios no-root explícitos.
        cap_drop: ALL se aplica correctamente en:
            grafana
            loki
            promtail
            monitoring-cron
            monitoring-python

    - Red y exposición
        PostgreSQL NO expone puertos al exterior.
        Loki y Grafana publican únicamente sobre 127.0.0.1.
        UFW aplica:
            deny incoming por defecto
            allow únicamente 22/80/443
        No existen puertos de BBDD expuestos públicamente.

    - Observabilidad
        monitoring-python posee healthcheck operativo.
        promtail utiliza mounts readonly explícitos.
        observability stack permanece desacoplado de backend-net.

    - Persistencia
        PostgreSQL utiliza volúmenes Docker nombrados.
        No se detectó persistencia crítica en bind mounts arbitrarios.

    Hallazgos relevantes

    La auditoría también confirmó:

    - Hardening parcial
        ReadonlyRootfs=false permanece en todos los servicios.
        Esto confirma:
            el entorno NO está aún en modo immutable runtime
            existe compatibilidad operacional priorizada sobre hardening agresivo
            el proyecto adopta un enfoque service-aware incremental

    - Servicios con privilegios superiores al baseline ideal
        monitoring-smtp-relay:
            - ejecuta como root
            - mantiene capabilities Linux activas:
                cap_net_bind_service
                cap_net_raw
                cap_setuid
                cap_setgid
                otras capabilities baseline Docker

    PostgreSQL:
        no define usuario explícito
        mantiene modelo upstream por defecto
        no utiliza cap_drop explícito

    promtail:
        requiere acceso readonly host-centric:
            /var/log
            /var/lib/docker/containers

    - Descubrimiento Compose
    No existe:
        compose raíz unificado

    La arquitectura Compose actual está segmentada:
        ops/stacks/python
        ops/stacks/cron
        ops/stacks/observability
        ops/services/postgres
        ops/services/smtp_relay

    Esto invalida parcialmente:
        tooling legacy que asume compose monolítico

    y obliga a:
        descubrimiento multi-compose
        auditoría runtime federada

# Problema

    La ausencia de una política runtime consolidada generaba:
    - ambigüedad operacional
    - deuda técnica de hardening
    - validaciones inconsistentes
    - falta de taxonomía de excepciones
    - incompatibilidad entre hardening teórico y runtime real
    - tooling legacy incompatible con arquitectura Compose distribuida

    Además:
    - algunos servicios upstream requieren privilegios reales
    - readonly rootfs completo rompe compatibilidad operacional
    - observabilidad host-centric necesita mounts readonly del host
    - SMTP relay requiere capacidades Linux específicas

# Decisión

    Se adopta un modelo oficial de:
    “Gobernanza Runtime Declarativa Basada en Evidencia Operacional”.

    El hardening deja de basarse exclusivamente en:
    - teoría
    - benchmarks genéricos
    - enforcement absoluto

    y pasa a priorizar:
    - compatibilidad operacional
    - auditabilidad
    - reproducibilidad
    - enforcement incremental
    - validación runtime real
    - clasificación explícita de excepciones

# Política Runtime Oficial

## 1. Prohibiciones estructurales

    Queda prohibido:
    - privileged=true
    - network_mode=host
    - docker.sock
    - bind mounts RW sensibles host-side
    - ejecución host-side de Python aplicativo
    - publicación externa de PostgreSQL
    - lógica runtime fuera de contenedores gobernados

    Toda excepción requiere:
    - ADR explícito
    - justificación técnica
    - evidencia operacional
    - validación CI
    - revisión arquitectónica

## 2. Clasificación oficial de mounts
    Permitidos baseline
    - volúmenes Docker nombrados
    - mounts readonly de configuración
    - secrets readonly

    Permitidos por excepción auditada
        /var/log:ro
        /var/lib/docker/containers:ro

    únicamente para:
    - observabilidad
    - log shipping
    - correlación runtime

    Prohibidos
    - docker.sock
    - mounts RW sobre host crítico
    - mounts arbitrarios no documentados
    - bind mounts de código runtime

## 3. Hardening baseline obligatorio

    Obligatorio:
- prohibición privileged
- prohibición host network
- aislamiento de redes
- validación HostConfig automática
- clasificación explícita de excepciones runtime

## 4. Hardening incremental service-aware

    Readonly rootfs:
    - NO será obligatorio globalmente
    - se aplicará únicamente tras validación operacional

    Servicios upstream compatibles podrán migrarse progresivamente a:
    - readonly rootfs
    - tmpfs específicos
    - runtime writable isolation

    La ausencia temporal de readonly rootfs:
    - NO constituye incumplimiento crítico
    - NO invalida la gobernanza runtime incremental
    - sí representa deuda técnica de hardening pendiente

    mientras permanezcan activos:
    - cap_drop
    - no-new-privileges
    - aislamiento runtime
    - validación CI
    - control de mounts

## 5. Servicios con excepciones explícitas

    monitoring-smtp-relay
        Excepción aprobada:
            ejecución como root
            capabilities Linux declaradas específicas

        Justificación:
            compatibilidad upstream SMTP relay
            binding/red/network stack requerido

        Restricciones:
            red restringida
            mounts limitados
            sin docker.sock
            sin privileged
            revisión periódica obligatoria

    PostgreSQL
        Excepción aprobada:
            readonly rootfs deshabilitado
            usuario upstream implícito

        Justificación:
            WAL
            runtime mutable legítimo
            compatibilidad upstream oficial

        Restricciones:
            sin publicación externa
            backend-net únicamente
            persistencia gobernada
            límites CPU/memoria activos

    promtail
        Excepción aprobada:
            acceso readonly host-centric

        Justificación:
            shipping logs Docker
            observabilidad operacional

        Restricciones:
            readonly estricto
            sin control plane Docker
            sin docker.sock

    6. Arquitectura Compose
    La plataforma adopta oficialmente:
        arquitectura Compose distribuida

    No existe obligación de:
        compose raíz único

    El tooling deberá:
        soportar multi-compose discovery
        descubrir stacks automáticamente
        correlacionar runtime federado mediante labels compose oficiales
        evitar heurísticas substring sobre nombres de contenedor

    Quedan prohibidas:
        suposiciones hardcoded sobre compose monolítico

# Consecuencias

    Positivas
    - reducción de ambigüedad operacional
    - hardening compatible con upstream
    - menor riesgo de regresiones
    - enforcement CI realista
    - mayor auditabilidad
    - reducción de drift runtime
    - separación clara entre:
        baseline obligatorio
        excepción válida
        deuda técnica
        hardening diferido

    Negativas
    - mayor complejidad documental
    - necesidad de mantener excepciones explícitas
    - auditorías runtime más sofisticadas
    - necesidad de tooling multi-compose

# Validación

    Las auditorías deberán validar automáticamente:
        Seguridad
            privileged=true
            docker.sock
            network_mode=host
            mounts RW peligrosos
            publicación externa indebida
            capabilities declaradas no justificadas vía HostConfig

        Runtime
            usuarios runtime
            SecurityOpt
            healthchecks
            restart policies
            segmentación de redes
            readonly compatibility

        Arquitectura
            descubrimiento compose distribuido
            coherencia HostConfig
            correlación runtime vs compose
            clasificación de excepciones

# Estado objetivo

    El entorno PRO deberá permanecer:
        gobernado
        auditable
        reproducible
        sin privilegios implícitos
        sin exposición externa indebida
        compatible operacionalmente
        endurecido progresivamente
        validado automáticamente

    La prioridad arquitectónica oficial pasa a ser:
        estabilidad operacional
        enforcement incremental
        auditabilidad
        compatibilidad upstream
        reducción progresiva de superficie de ataque

## Relación con otros ADR

    - ADR-0016 — Segmentación de redes: refuerza el requisito de aislamiento por redes (`backend-net`, `observability-net`, `restricted-net`) y condiciona las excepciones de exposición.
    - ADR-0018 — Seguridad runtime y resiliencia: dicta controles de `privileged`, `capabilities`, `restart` y healthchecks que esta gobernanza materializa en validaciones HostConfig.
    - ADR-0021 — Network Segmentation Strategy: la taxonomía de mounts y excepciones favorece observability-host mounts sin romper segmentación backend.
    - ADR-0028 — Reproducibilidad: la auditoría conserva pragmatismo sobre imágenes y reproducibilidad, relegando bloqueo estricto y priorizando evidencia operativa.
    - ADR-0029 — Structured Compose Policy Audit: obliga a discovery multi-compose y correlación runtime vs compose; este ADR implementa la fase runtime de esa estrategia.
    - ADR-0030 — Auditoría HostConfig y visibilidad: complementa la fase observacional con un enforcement incremental y clasificación de excepciones.

## Estado

    - Estado: Aprobado.
    - Enforcement: Parcial operativo. Las validaciones host-side se ejecutan periódicamente y en CI en modo `audit-runtime-ci`. Violaciones `forbidden` fallan pipelines; `warning` se registran para corrección progresiva.
    - Hardening: Incremental — el enforcement runtime actual prioriza compatibilidad operacional y clasificación explícita de excepciones. Algunas recomendaciones baseline (cap_drop ALL, ReadonlyRootfs, no-new-privileges) permanecen parcialmente desplegadas.
    - Observabilidad: Integrada — la taxonomía de mounts y la allowlist permiten mantener observability funcional sin romper aislamiento de red.

# ADR-0032 – Endurecimiento de gestión de secretos PostgreSQL y validaciones CI

Fecha: 2026-05-31
Estado: Aprobado
Contexto: Proyecto server_monitoring_2509

## Contexto

Durante las auditorías de seguridad y gobernanza runtime se identificaron varias desviaciones relacionadas con la gestión de secretos PostgreSQL y la validación de la aplicación.

Los hallazgos principales fueron:
- Existencia de una contraseña PostgreSQL hardcodeada en el fichero .env.
- Uso incorrecto del recurso postgres_password como directorio en lugar de fichero secreto.
- Ausencia de validación automatizada completa de secretos en producción.
- Riesgo de regresiones por errores de imports o inicialización Python no detectados por CI.
- Dependencia parcial de validaciones manuales para certificar el estado de seguridad del despliegue.

Aunque la plataforma operaba correctamente, la situación introducía deuda técnica y reducía la capacidad de certificación reproducible del entorno.

## Decisión

Se adopta una estrategia de endurecimiento basada en cuatro pilares.

### 1. Gestión de secretos mediante fichero

Se elimina cualquier uso de:
  POSTGRES_PASSWORD=<valor>
en configuración persistente.

La autenticación PostgreSQL pasa a depender exclusivamente de:
  POSTGRES_PASSWORD_FILE=/run/secrets/postgres_password
siguiendo el patrón estándar soportado por la imagen oficial de PostgreSQL.

### 2. Normalización del secreto PostgreSQL

Se establece que:
  ops/services/postgres/secrets/postgres_password
debe ser un fichero real.

Se fijan los siguientes requisitos mínimos:
- fichero secreto con permisos 600
- directorio secrets con permisos 700
- propietario distinto de nobody
- ausencia de secretos hardcodeados

### 3. Auditoría automática de seguridad

Se incorpora:
  ops/services/postgres/scripts/check_postgres_secret.sh
como mecanismo oficial de validación.

La auditoría verifica:
- existencia del secreto
- permisos
- propietario
- ausencia de POSTGRES_PASSWORD hardcodeado
- presencia de POSTGRES_PASSWORD_FILE
- montaje correcto del secreto
- ausencia de wrappers inseguros

El fallo de cualquiera de estas comprobaciones provoca error explícito.

### 4. Refuerzo de validaciones CI

Se añaden nuevas verificaciones automáticas:
- compilación completa mediante python3 -m compileall src
- smoke tests de imports
- smoke tests de init_config
- validación de modos SMTP relay y auth

El objetivo es detectar tempranamente:
- errores de sintaxis
- errores de imports
- regresiones de configuración
- problemas de inicialización

## Consecuencias

Positivas:
- eliminación de secretos hardcodeados
- alineación con buenas prácticas Docker
- reducción de superficie de ataque
- validación reproducible entre CI y producción
- detección temprana de regresiones
- mejora de la trazabilidad operativa
- reducción de deuda técnica

Negativas:
- incremento moderado de controles de validación
- mayor sensibilidad de CI ante errores de configuración

## Validación

Las siguientes evidencias confirman la implantación correcta.

Producción:
  make verify-security

Resultado:
  [OK] Comprobaciones del secreto PostgreSQL superadas

CI:
- pipeline completado correctamente
- compileall ejecutado sin errores
- smoke tests superados
- init_config validado correctamente

Runtime:
- scripts PostgreSQL operativos
- imports Python resueltos correctamente
- localización automática de src implementada

## Compatibilidad

Compatible con:
ADR-0016
ADR-0018
ADR-0029
ADR-0031

Complementa los mecanismos de gobernanza y endurecimiento definidos en dichos ADR sin introducir incompatibilidades arquitectónicas.

## Estado
Aprobado.

Implementado y validado tanto en CI como en producción.
