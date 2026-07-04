# ADR-0001 — Verificación de imports durante la fase de migración

Status: APPROVED
Date: 2025-12-09
Scope: Runtime
Category: ARCHITECTURE
Tags: REVIEW_REQUIRED
Related ADRs: ADR-0002
Supersedes: NONE
Superseded By: NONE
Validation Reference: NONE

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
