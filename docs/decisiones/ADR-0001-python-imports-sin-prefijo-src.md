# ADR-0001 — Eliminación del prefijo "src." en imports Python

Fecha: 2025-12-09
Estado: Aprobado
Contexto: Migración IaC server_monitoring_2509

## Contexto

Durante la migración de la base de código Python a una estructura bajo `src/`,
se detectaron múltiples imports con el prefijo `src.` (por ejemplo `src.log_ingestor.alert_risk`).

Este patrón impedía una ejecución limpia mediante `python3 -m <paquete>`
y generaba una ambigüedad entre layout de proyecto y namespaces reales de Python.

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
- Necesita validación con `python3 -m compileall`

## Decisión

Se adopta la **Opción B**.

Se elimina el prefijo `src.` de los imports Python y se adaptan los módulos
para que funcionen como paquetes reales ejecutables mediante `python3 -m`.

## Consecuencias

- Se realizará un refactor controlado de imports en los archivos afectados
- No se creará `src/__init__.py`
- Se validará la corrección mediante `python3 -m compileall src/`
- Esta decisión reduce deuda técnica y alinea el proyecto con prácticas estándar

## Estado

Aprobado.

## Validación

La validación del refactor de imports se realizó ejecutando:

python3 -m compileall src/

en un entorno Linux (WSL), equivalente al entorno objetivo de producción.

El resultado fue satisfactorio, sin errores de compilación en los módulos
bajo src/log_ingestor, src/monitoring y src/resource_monitor.

La validación no pudo ejecutarse en entorno Windows PowerShell por ausencia
de intérprete Python, lo cual se considera fuera de alcance del proyecto.
