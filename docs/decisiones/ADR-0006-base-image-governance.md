ADR-0006 – Gobernanza de imagen base monitoring-base

Fecha: 2026-02-14
Estado: Aprobado
Contexto: Migración PRO server_monitoring_2602 – Modelo micro-stack autónomo

## Contexto
Durante la definición del entorno PRO 260214 se adopta el modelo: “micro-stack autónomo con red compartida”.
Cada servicio debe poder:
- Construirse de forma independiente
- Desplegarse sin dependencias implícitas
- Ser trasladado a otro repositorio si fuera necesario

Sin embargo, se decide mantener una imagen base común denominada monitoring-base para:
- Reducir duplicación de dependencias
- Estandarizar runtime Python
- Optimizar tiempos de build
- Garantizar coherencia de entorno
Esta decisión introduce un posible riesgo de acoplamiento si no se regula explícitamente su alcance.

## Decisión
Se mantiene la imagen monitoring-base bajo las siguientes reglas estrictas:
Alcance permitido:
- Runtime común (Python, librerías compartidas)
- Código fuente versionado del proyecto
- Dependencias declaradas en requirements.txt
- Configuración genérica no específica de servicio

Prohibiciones explícitas:
- No puede contener secrets
- No puede contener archivos .env
- No puede contener configuración específica de servicios
- No puede incluir lógica de bootstrap específica
- No puede ejecutar código en build-time que dependa de entorno PRO

Principio de reemplazabilidad:
- Cada servicio debe poder:
  Extender directamente una imagen oficial (python:slim, etc.)
  O sustituir monitoring-base sin romper arquitectura
- monitoring-base es una optimización, no una dependencia estructural.

No centralización de estado:
- Ningún volumen ni dato persistente depende de la imagen base.
- El estado siempre reside en volúmenes declarados por servicio.

## Consecuencias
- Se mejora la eficiencia de builds y coherencia de runtime.
- Se reduce duplicación entre servicios.
- Se mantiene compatibilidad con el modelo micro-stack autónomo.

## Riesgos controlado
- Si la imagen crece en responsabilidad, puede generar acoplamiento.
- Si empieza a incluir configuración específica, rompe autonomía.
- Si se convierte en requisito obligatorio no reemplazable, contradice el modelo PRO.
Por tanto:
- La gobernanza de monitoring-base es obligatoria en cada refactor o ampliación.

## Fuera de alcance:
- No se redefine la estructura de servicios.
- No se introduce pipeline de build automatizado.
- No se modifica el modelo de red compartida.
- No se altera la política de secrets.

## Estado
Aceptado.















