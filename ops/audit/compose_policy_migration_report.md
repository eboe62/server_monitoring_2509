# Informe de migración — compose_policy_checks

Fecha: 2026-05-19

Resumen
- Se ha reubicado el módulo de comprobaciones estructuradas a `ops/audit/compose_policy_checks.py`.
- Las comprobaciones se ejecutan preferiblemente dentro del contenedor `monitoring-python`.
- Salida machine-readable `--json` añadida y modo `--self-test` para validar runtime.
- El script devuelve código de salida no cero cuando existen violaciones `FAIL` críticas (`privileged`).

Validaciones migradas a parsing estructurado
- Detección de puertos publicados (`ports`) — migrado a parsing YAML/Compose.
- Detección de `docker.sock` en short y long syntax (`docker_sock`) — migrado.
- Detección de imágenes sin digest y con `:latest` (`images_no_digest`, `images_latest`).
- Detección de `privileged=true` (`privileged`) con severidad `FAIL`.
- Detección de mounts sensibles en RW (`sensitive_mounts`).
- Detección de `cap_add` y `read_only=false`.
- Añadido chequeo runtime (`runtime_checks`) que valida disponibilidad de `docker`/`docker compose`/`docker.sock`.

Validaciones aún heurísticas / pendientes
- Detección de secrets versionados y estructuras más específicas siguen en shell scripts y validaciones existentes.
- Algunas búsquedas de archivos (p.ej. `find ops -name ...`) se mantienen; pueden estructurarse más tarde.

Cambios en `ops/audit/audit_repo_host.sh`
- La ejecución del chequeador estructurado se realiza una sola vez dentro del contenedor y su salida JSON se parsea con Python inline (sin usar `awk` sobre salida humana).
- Se evita ejecutar el módulo Python desde el host; solo se ejecuta dentro de `monitoring-python`.

Severidad y exit codes
- Mapa de severidad central: `POLICY_SEVERITY` en el módulo.
- Violaciones con severidad `FAIL` devuelven rc=1 (actualmente `privileged`).
- Otras violaciones devuelven WARN en salida humana y aparecen en JSON.

Compatibilidad ADR
- Cumple con ADR-0028 (política pragmática): el chequeo informa sobre imágenes sin digest como WARN.
- No modifica arquitectura Docker ni redes; mantiene single-node compose standalone.

Limitaciones y riesgos residuales
- Si `monitoring-python` no tiene acceso a `docker.sock`, algunas comprobaciones runtime no podrán resolverse y se degradarán a WARN con mensaje explícito.
- Dependencia en Python para parsing JSON en el host (uso mínimo en `audit_repo_host.sh`) — se asume Python disponible para audit.
- Si el contenedor `monitoring-python` no está levantado, las validaciones estructuradas se omiten (WARN) y se mantienen heurísticas alternativas.

Siguientes pasos recomendados
1. En CI: añadir un job que ejecute `docker compose run --rm monitoring-python python -m ops.audit.compose_policy_checks --json` para validar en entorno controlado.
2. Considerar añadir `jq` al contenedor de auditoría si se prefiere usar `jq` en vez de Python inline.
3. Extender `POLICY_SEVERITY` para incluir más políticas críticas según madurez de enforcement.

Archivos modificados
- `ops/audit/compose_policy_checks.py` (nuevo/hardened)
- `ops/audit/audit_repo_host.sh` (usa JSON + parsing python)
- `Makefile` (target `test-policy-structured` ejecuta dentro de `monitoring-python`)
