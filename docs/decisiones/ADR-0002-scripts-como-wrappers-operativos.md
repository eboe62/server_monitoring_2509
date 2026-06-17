# ADR-0002 – Scripts como wrappers operativos

Status: APPROVED
Date: 2026-01-25
Scope: Runtime
Category: ARCHITECTURE
Tags: REVIEW_REQUIRED
Related ADRs: ADR-0003, ADR-0011
Supersedes: NONE
Superseded By: NONE
Validation Reference: NONE

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

