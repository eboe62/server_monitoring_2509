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
Esta estructura cumple ADR-0008: servicio autónomo, volúmenes propios declarados y conexión a la red compartida `backend-net` (externa).

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
Micro-stack autónomo PostgreSQL compatible con `backend-net` (external: true).

Operativa mínima
----------------
- Copiar `.env.template` a `.env` en `ops/services/postgres/` y rellenar. NO cometas `.env`.
- Crear `backups/` y `init/` si necesitas backups o scripts de inicialización. Los directorios ya existen como skeleton.
- Para compatibilidad con scripts que esperan nombre de contenedor `monitoring-postgres`, puedes definir `POSTGRES_CONTAINER_NAME` en tu `.env` y usar `docker compose run --name ${POSTGRES_CONTAINER_NAME}` si lo necesitas; por defecto no se fuerza `container_name`.

Notas
-----
- Volúmenes: `postgres-data` es declarado en este stack (driver local). Backups se montan desde `./backups` (relativo).
- Redes: se conecta a `backend-net` (external: true). Asegúrate de que esa red existe en el host destino.

Nota: Históricamente este proyecto referenciaba una red global `monitoring-net`. Tras la adopción de ADR-0021, la plataforma usa redes segmentadas: `backend-net`, `observability-net` y `restricted-net` según el propósito del servicio.
- Secretos: no versionar ficheros sensibles. Usa `.env` (ignorado) o un directorio `secrets/` montado fuera del repo.

Secretos y flujo recomendado
--------------------------
- El password de Postgres ya debe gestionarse como fichero en `ops/services/postgres/secrets/postgres_password`.
- No ponga `POSTGRES_PASSWORD` en `.env` ni en plantillas. En su lugar, el `compose.yml` monta el fichero en
	`/run/secrets/postgres_password` y exporta `POSTGRES_PASSWORD_FILE=/run/secrets/postgres_password`.
- Ejemplo de creación segura en host:

```sh
mkdir -p ops/services/postgres/secrets
chmod 700 ops/services/postgres/secrets
printf '%s' 'SUPER_PASSWORD' > ops/services/postgres/secrets/postgres_password
chmod 600 ops/services/postgres/secrets/postgres_password
```

Verificaciones rápidas
----------------------
- Ejecutar validación local antes de arrancar el stack:

```sh
bash ops/services/postgres/scripts/check_postgres_secret.sh
```

Esto evita que el contenedor entre en restart loop por credenciales inexistentes. No use wrappers de entrypoint: la imagen oficial de Postgres reconoce `POSTGRES_PASSWORD_FILE`.

Migración y checklist
---------------------
Ver la documentación principal del proyecto para pasos de dump/restore y ventana de corte. Mantener backup completo antes de cualquier operación.
