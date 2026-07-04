# ADR-0017 — Resilience model at docker single-node

Status: APPROVED
Date: 2026-04-01
Scope: Runtime
Category: RUNTIME
Tags: REVIEW_REQUIRED
Related ADRs: ADR-0018, ADR-0019
Supersedes: NONE
Superseded By: NONE
Validation Reference: NONE

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
