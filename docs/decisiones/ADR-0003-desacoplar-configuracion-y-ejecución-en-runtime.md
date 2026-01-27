# ADR-0003 – Desacoplamiento de configuración y ejecución en runtime

Fecha: 2026-01-25
Estado: Aprobado
Contexto: Migración IaC server_monitoring_2509

## Contexto

El sistema de monitoring ejecuta múltiples tareas periódicas (cronjobs) y
scripts operativos que dependen de configuración sensible (credenciales,
secrets, servicios externos). Históricamente, parte de esta configuración se
cargaba en tiempo de importación de los módulos Python, introduciendo
dependencias rígidas al filesystem y provocando fallos inmediatos en entornos
donde dichos recursos no estaban presentes.

Además, la ejecución directa de ficheros .py por ruta absoluta dificultaba la
portabilidad y la ejecución coherente entre entornos (local, contenedor,
servidor limpio).

Problema
- Fallos en import-time por ausencia de .env o secrets
- Código no importable en entornos limpios
- Acoplamiento a rutas absolutas (/opt/monitoring, /var/log)
- Dificultad para validar y desplegar en nuevos servidores
- Falta de separación clara entre código, configuración y entorno

## Decisión

Se adopta un modelo explícito de inicialización en runtime:

1. El código Python debe poder importarse siempre sin efectos secundarios.
2. Toda configuración sensible se carga explícitamente en runtime mediante
   una función de inicialización (init_config()).
3. Los entrypoints (wrappers, cronjobs, contenedores) son responsables de
   invocar init_config() antes de ejecutar funcionalidades dependientes del
   entorno.
4. Toda ejecución Python se realiza mediante python3 -m <paquete>.<módulo>.
5. Los wrappers en scripts/ son mínimos y no contienen lógica de negocio.

## Consecuencias

Positivas:
- Eliminación de fallos en import-time
- Código portable e importable en limpio
- Dependencias explícitas y diagnosticables
- Mejor separación de responsabilidades
- Ejecución reproducible en contenedores

Negativas / trade-offs:
- Los errores de configuración se detectan en runtime y no al importar
- Requiere disciplina: todos los entrypoints deben invocar init_config()
- Mayor responsabilidad documental sobre precondiciones operativas

# Alternativas consideradas

- Mantener carga en import-time: descartado por fragilidad y falta de
  portabilidad.
- Uso de frameworks pesados de configuración: descartado por sobrecoste
  innecesario para el alcance del proyecto.

# Notas

Esta decisión se aplica de forma incremental. Parte del código ya ha sido
adaptado (FASE 7), y el resto se normalizará en fases posteriores siguiendo el
mismo patrón.

## Estado

Aceptado.
