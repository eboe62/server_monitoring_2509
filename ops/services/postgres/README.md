Postgres micro-stack (ops/services/postgres)
==========================================

Resumen mínimo operativo:

- Crear un fichero `.env` en este directorio a partir de `.env.template` con las credenciales reales.
- Proteger permisos del archivo `.env` (recomendado: `chmod 600 .env`).
- Mantener `backups/` como directorio local para dumps/restore; este directorio se monta en el contenedor en `/backups`.

Coexistencia temporal con Infra-Stack
-------------------------------------
El volumen de datos se declara como `postgres-data` en este compose y NO es `external`. Por defecto Docker Compose crea volumes aislados por `project-name` (p. ej. `<project>_postgres-data`).
Esto permite que este micro-stack coexista con la definición previa de Postgres en el Infra-Stack sin colisiones, salvo que se fuerce el mismo `COMPOSE_PROJECT_NAME` o se use `POSTGRES_CONTAINER_NAME` para forzar `container_name` explícito.

Cumplimiento
-----------
Esta estructura cumple ADR-0008: servicio autónomo, volúmenes propios declarados y conexión a la red compartida `monitoring-net` (externa).

Operaciones básicas
-------------------
- Preparar `.env`: copiar `.env.template` → `.env` y editar valores.
- Permisos: `chmod 600 .env`.
- Backups: colocar/leer dumps en `backups/` (montado como `/backups`).

Notas
-----
- No versionar `.env` ni credenciales. Este README es orientativo y mínimo.
# PostgreSQL micro-stack (ops/services/postgres)

Resumen
-------
Micro-stack autónomo PostgreSQL compatible con `monitoring-net` (external: true).

Operativa mínima
----------------
- Copiar `.env.template` a `.env` en `ops/services/postgres/` y rellenar. NO cometas `.env`.
- Crear `backups/` y `init/` si necesitas backups o scripts de inicialización. Los directorios ya existen como skeleton.
- Para compatibilidad con scripts que esperan nombre de contenedor `monitoring-postgres`, puedes definir `POSTGRES_CONTAINER_NAME` en tu `.env` y usar `docker compose run --name ${POSTGRES_CONTAINER_NAME}` si lo necesitas; por defecto no se fuerza `container_name`.

Notas
-----
- Volúmenes: `postgres-data` es declarado en este stack (driver local). Backups se montan desde `./backups` (relativo).
- Redes: se conecta a `monitoring-net` (external: true). Asegúrate de que esa red existe en el host destino.
- Secretos: no versionar ficheros sensibles. Usa `.env` (ignorado) o un directorio `secrets/` montado fuera del repo.

Migración y checklist
---------------------
Ver la documentación principal del proyecto para pasos de dump/restore y ventana de corte. Mantener backup completo antes de cualquier operación.
