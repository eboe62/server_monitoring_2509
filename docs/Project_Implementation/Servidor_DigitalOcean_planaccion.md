
Yo:
Haz una revisión completa del estado del proyecto y presenta un informe de situación

Respuesta:
2026/10/29 20:37:44

# Informe de situación: server_monitoring_2509

**Alcance:** solo análisis. No he modificado nada. He leído el protocolo de gobernanza, el ledger de implementación, el plan de corrección (PRIORIDADES 1–15), el StatusQuo 260817, el Makefile, los compose y los scripts de auditoría.
**Limitación:** no tengo acceso al servidor de producción. Todo lo que digo sobre producción sale del log StatusQuo del 17/08/2026, que tiene más de dos meses.

## 1. Contexto

- Rama `certificacion_sre_hardening`, sincronizada con `origin`. Va **424 commits por delante de `master`**.
- El trabajo actual es el cierre de la FASE 5 (hardening). Los tres últimos commits arreglan el test de red, el healthcheck de Promtail y la dependencia `pytz` que faltaba.
- Cambios sin commit:
  - Ledger de implementación: dos notas de verificación nuevas.
  - `.gitignore`: ahora solo ignora `docs/Project_Corrections/*.txt`, así que los `.md` de esa carpeta pasan a poder versionarse.

## 2. Estado por fase

| Fase | Estado | Evidencia |
|---|---|---|
| 1–4 (SO, Docker, UFW, repositorio, micro-stacks) | Cerradas | Ledger y StatusQuo |
| 5 – Hardening | Avanzada, sin cerrar | PRIORIDADES 3, 5, 6 y 10 parciales; 11–15 sin estado formal |
| 6 – Postgres | Abierta a propósito | `monitoring_db` sin tablas; la migración de datos espera a que cierre la FASE 5 |
| 7 – Runtime PRO | Operativa | Segmentación de redes y SMTP sin puertos expuestos, verificados |
| 8 – Cron | Sin cerrar en el documento | El fallo de `pytz` está corregido y verificado (diff pendiente), pero la sección dice "NO puede darse por cerrada" |
| 9–10 | Sin evidencia formal de cierre | — |
| 11 – Validación PRO | Bloqueada en el documento por la FASE 8 | El reinicio controlado salió bien: todo volvió en unos 38 s |

Tests que pasaron en producción el 17/08: `test-resilience-completo`, `test-SRE-completo`, `test-smtp-all`, `test-observability-core`, `test-cron-execution`, `test-python-health` y `verify-security`.

## 3. Hallazgos nuevos (no están en el ledger)

**H1 – `test-reproducibilidad` borra todos los datos de producción y no pide confirmación.** Confirmado.
- En [Makefile:1284-1295](Makefile#L1284-L1295) hace `down -v` en todos los stacks y luego `docker system prune -af --volumes`.
- El log del 17/08 muestra `postgres_postgres-data` y `postgres_postgres-backups` con estado `Removed`.
- Ahora no hay pérdida real porque la base está vacía. Pero si se lanza `make test-SRE-completo` en producción después de migrar los datos, se borran la base de datos y sus backups.
- **Esto bloquea la FASE 6.**

**H2 – El volumen de backups no es compartido, aunque el comentario del código diga que sí.** Confirmado.
- [ops/stacks/cron/compose.yml:51-53](ops/stacks/cron/compose.yml#L51-L53) y [ops/services/postgres/compose.yml:39](ops/services/postgres/compose.yml#L39) declaran el volumen sin `name:`. Docker Compose le añade el nombre de cada proyecto delante, así que se crean dos volúmenes distintos: `cron_postgres-backups` y `postgres_postgres-backups`. El log lo confirma.
- `backup_postgres.py` lanza `pg_dump` desde `monitoring-cron`, así que los backups acaban en el volumen de cron.
- La nota del ledger que dice "volumen compartido" es incorrecta.
- Hipótesis: el backup del 27/03 se encontró en otro volumen, y eso explica en parte por qué "no había backups recientes".

**H3 – La auditoría dice que todos los contenedores están parados cuando están en ejecución.** Confirmado.
- En [ops/audit/audit_repo_host.sh:297](ops/audit/audit_repo_host.sh#L297) se usa `grep -q "^$c$$"`. `$$` es una forma de escapar `$` propia de Makefile, pero este fichero es un script bash, donde `$$` es el PID del proceso. La expresión nunca coincide.
- Consecuencia: la sección A7.1 de `make audit` (visibilidad de HostConfig) no audita nada.

**H4 – El ajuste automático de límites de recursos no actúa sobre ningún contenedor.** Confirmado.
- `configure_docker_limits.sh` filtra por la etiqueta `monitoring.managed=true`, y ningún compose la declara. El log muestra "No hay contenedores con label…".
- Los límites declarados en los compose sí se aplican (Postgres y observabilidad). Este script, en cambio, no tiene ningún efecto.

**H5 – El contenedor de debug se queda en ejecución en producción.** Confirmado.
- `make test-smtp-all` arranca `monitoring-debug` (`nicolaka/netshoot`, con tag `latest`) en `restricted-net` y no lo elimina al terminar.
- Esto contradice la PRIORIDAD 15 y la regla de no usar `:latest`.

**H6 – Más falsos positivos de auditoría, aparte del de `secrets.py`.**
- La comprobación de `docker.sock` busca el texto en todo el repositorio y salta con el README, los ADR y `ci.yml`.

**H7 – La ingesta de fail2ban sigue sin funcionar aunque el fallo de `pytz` esté corregido.**
- `ALLOW_HOST_LOGS` no vale `true`. Tu propio diff ya lo recoge. Hay que decidir si es lo que se quiere o si falta configurarlo.

## 4. Incoherencias en la documentación

- **Ledger, FASE 8, 10 y 11:** el diff sin commit dice que `pytz` está corregido y verificado en producción. Sin embargo, 8.0, "Estado actual" de la FASE 8 y la FASE 11 siguen diciendo que el defecto está activo. La nota de 10.1 sigue diciendo que Promtail no tiene healthcheck, cuando 5.1 dice que está resuelto. Además, el último párrafo de 8.0 está cortado ("…solo por el defecto ya corregido").
- **Plan de corrección:**
  - La PRIORIDAD 11 aún habla de `monitoring-net`, una red que ADR-0021 prohíbe, y de "test no determinista". Esto ya se arregló en c28bb3d.
  - La PRIORIDAD 12 habla de "Postgres unhealthy", pero en las evidencias recientes aparece healthy.
  - Las PRIORIDADES 11–15 no tienen estado.
- **El healthcheck de Promtail no tiene evidencia en ejecución en el StatusQuo 260817.** Ese log se hizo en c28bb3d, antes del commit 3a97150, y Promtail sale sin "(healthy)". El ledger dice que se verificó, pero no hay log que lo respalde.
- **El plan de corrección autoritativo (`Correccion_260712.txt`) no está en git**, porque lo excluye `.gitignore`. Por tanto, la condición para desbloquear la FASE 6 depende de un documento sin historial de cambios.
- **Hay muchas copias de documentos autoritativos** (`* copy*.txt`, `StatusQuo_260816 copy 2`, `*_BORRAR`). Esto va contra la regla de AI_ENTRYPOINT de no tener varios candidatos para el mismo documento.
- **El servidor arrastra una confusión de ramas.** Se hizo `git reset --hard origin/certificacion_sre_hardening` sobre la rama local `migracion`, así que el nombre de la rama ya no corresponde a su contenido.

## 5. Riesgos (de mayor a menor)

1. **Crítico, si se migra:** H1 (borrado de datos) unido a H2 (backups en otro volumen) y a que nunca se ha probado un restore. Hoy no hay ningún mecanismo de recuperación probado.
2. **Alto:** la auditoría parece más fiable de lo que es (H3, H6). Hay WARN y FAIL que no significan nada y otros que nunca aparecerían.
3. **Medio:** una herramienta de red con tag `latest` sigue en ejecución en producción (H5).
4. **Bajo:** el ledger y el plan se van desfasando del estado real, y eso dificulta decidir cuándo cerrar la FASE 5.

## 6. Recomendaciones (requieren tu aprobación)

1. Proteger `test-reproducibilidad`: que se niegue a ejecutarse en producción salvo con `CONFIRM=yes` o una variable de entorno, o que no borre los volúmenes de datos. Es un cambio en la infraestructura, así que hay que revisarlo con ADR-0019 y ADR-0028.
2. Hacer que el volumen de backups sea realmente uno solo, con `name:` explícito o `external: true`. Después, probar un restore contra un Postgres temporal (ya lo exige 5.3).
3. Corregir `$$` → `$` en `audit_repo_host.sh:297`, hacer que la comprobación de `docker.sock` mire solo en `ops/**/compose.yml` y decidir qué hacer con la etiqueta `monitoring.managed`.
4. Añadir `debug-toolbox-down` al final de `test-smtp-all` y fijar la versión de `netshoot`.
5. Actualizar la documentación:
   - Ledger: FASE 8, 10 y 11, y la nota de 5.3 sobre el volumen.
   - Plan: dar estado a las PRIORIDADES 11–15.
   - Decidir si `Correccion_260712.txt` se versiona.
   - Hacer limpieza de las copias.
6. Hacer commit de los cambios pendientes y generar un StatusQuo nuevo en HEAD (954164f), que sirva de prueba para cerrar las FASES 8, 10 y 11.

## 7. Validación propuesta

- En el servidor:
  - `docker volume ls | grep backups` y `docker run --rm -v cron_postgres-backups:/b alpine ls -la /b`, para ver si se están generando backups diarios.
  - `docker ps` para comprobar si Promtail sale como healthy y si `monitoring-debug` sigue en ejecución.
  - `git log -1` para saber qué commit está desplegado.
- En local: `pytest` no está instalado en WSL, así que no he podido ejecutar los tests unitarios. Hacen falta un venv y `pip install pytest`.

No puedo decir con seguridad que el entorno PRO esté hoy en el estado descrito, porque la evidencia de producción más reciente es del 17/08/2026. Necesito un StatusQuo actualizado para confirmarlo.

Si quieres compartir este informe, puedo publicarlo como página.

==========================================

Yo:
Revisa .gitignore y .claudecodeignore ambos excluyen los archivos * copy* son simples herramientas de trabajo que me son útiles
La BBDD es simplemente de prueba, los datos son irrelevantes cuando llegue el momento construiremos las tablas con este contenido pero de momento no nos preocupan.
Dime que comandos tengo que ejecutar en PRO para poder tener un informe completo. Todos los contenedores están levantados y funcionando pero verificamos.
Hazme una valoración crítica del proyecto de acuerdo con las necesidades.
Habría que eliminar/añadir algo?
Podríamos decir que una vez concluido el proyecto los riesgos estarán controlados sin necesidad de darle demasiada rigidez al sistema?

Respuesta:
2026/10/29 20:52:10

# Respuesta a tus seis puntos

## 1. Copias de trabajo y BBDD: corrijo lo que dije

**Copias (`* copy*`, `*_BORRAR*`).** Tenías razón. Las dos reglas están en `.gitignore` y en `.claudecodeignore`, y `git ls-files` no devuelve ninguna copia. Retiro ese hallazgo.

**BBDD de prueba.** Cambio la valoración de H1 y H2:
- **H1** (`test-reproducibilidad` borra los volúmenes): baja de crítico a riesgo latente. Borrar volúmenes es justo lo que debe hacer un test de reproducibilidad. Solo será un problema cuando los datos importen.
- **H2** (dos volúmenes de backup distintos): sigue siendo un defecto real, pero hoy no es prioritario.

**Un aviso para cuando construyas las tablas.** El `.gitignore` excluye `*.sql`. Además, `ops/services/postgres/init/` no existe en el repositorio, aunque el compose lo monta. Cuando crees los scripts de inicialización, git los ignorará sin avisar si no añades una excepción, por ejemplo `!ops/services/postgres/init/*.sql`.

## 2. Comandos para un informe completo en PRO

Todo lo que propongo es de solo lectura o reversible. **No ejecutes `make test-SRE-completo` ni `make test-reproducibilidad`**: borran los volúmenes y las imágenes.

```bash
cd /opt/monitoring
OUT=~/StatusQuo_$(date +%y%m%d).txt
{
echo "=== CONTEXTO ==="; date; hostname; uptime
git status; git log -1 --oneline; git branch -vv

echo "=== CONTENEDORES / RECURSOS ==="
docker ps -a --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'
docker stats --no-stream
docker volume ls; docker network ls; docker images
df -h /; free -h

echo "=== BACKUPS (H2) ==="
for v in cron_postgres-backups postgres_postgres-backups; do
  echo "--- $v"; docker run --rm -v $v:/b:ro alpine ls -la /b 2>&1
done

echo "=== CRON: errores y jobs ==="
docker logs --since 48h monitoring-cron 2>&1 | grep -E "Traceback|Error|ERROR|WARN" | sort | uniq -c | sort -rn | head -40
docker logs --since 24h monitoring-cron 2>&1 | grep -E "\[CRON\]|START|backup" | tail -40

echo "=== BBDD ==="
docker exec monitoring-postgres psql -U postgres -l
docker exec monitoring-postgres psql -U postgres -d monitoring_db -c '\dt'

echo "=== LOKI: qué está ingiriendo realmente ==="
curl -s 127.0.0.1:3100/ready; echo
curl -s 127.0.0.1:3100/loki/api/v1/labels; echo
curl -s 127.0.0.1:3100/loki/api/v1/label/job/values; echo

echo "=== HEALTH ==="
for c in $(docker ps --format '{{.Names}}'); do
  echo "$c: $(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}sin-healthcheck{{end}} restarts={{.RestartCount}}' $c)"
done

echo "=== MAKE (no destructivos) ==="
make status
make audit
make test-policy-structured
make test-security-runtime
make verify-security
make audit-runtime-ci
make test-observability-core
make test-cron-execution
make test-python-health
make test-smtp-ci
make test-aislamiento-red
make test-dependencias-host
make test-permisos
make test-aislamiento-fs
} 2>&1 | tee "$OUT"
```

**Bloque con sudo (host).** Esta parte faltó en el informe anterior:

```bash
{
echo "=== HOST (root) ==="
sudo ufw status verbose
sudo ss -tulpn
sudo crontab -l
sudo fail2ban-client status; sudo fail2ban-client status sshd
sudo grep -E "^(PermitRootLogin|PasswordAuthentication|Port)" /etc/ssh/sshd_config /etc/ssh/sshd_config.d/* 2>/dev/null
systemctl is-enabled unattended-upgrades 2>&1; apt list --upgradable 2>/dev/null | wc -l
sudo last -n 15; sudo lastb -n 15 2>/dev/null | head -15
} 2>&1 | tee -a "$OUT"
```

**Opcionales (molestan al servicio unos minutos, pero se recuperan solos):**

```bash
make test-resilience-completo 2>&1 | tee -a "$OUT"
make test-smtp-all 2>&1 | tee -a "$OUT"; make debug-toolbox-down   # test-smtp-all deja monitoring-debug arrancado
```

Cuando termine, pásame el fichero `~/StatusQuo_aammdd.txt`.

## 3. Valoración crítica frente a las necesidades

La Visión define cinco objetivos: detectar eventos de seguridad, centralizar la observabilidad, auditar la actividad, analizar logs de forma estructurada y evaluar la exposición a ataques (honeypot). Comparo con lo que hay.

**La infraestructura está madura.** Esto está confirmado:
- UFW con deny-by-default.
- Ningún puerto publicado, salvo Grafana y Loki en loopback.
- Redes segmentadas.
- Contenedores propios sin root.
- Imágenes de terceros fijadas por digest.
- Límites de recursos.
- Tests de resiliencia reales.
- Recuperación tras reinicio sin intervención.

Para un droplet de un solo nodo, es un nivel de endurecimiento superior al habitual.

**La parte funcional está casi parada.** También confirmado en el código:
- Las tres ingestas Python de logs del host (`log_ingest_batch` para auth, `log_fail2ban_batch` y `log_kern_batch`) salen sin hacer nada porque `ALLOW_HOST_LOGS` no está a `true`. Además, `/var/log` está comentado en los compose de cron y python, así que aunque se activara la variable, no encontrarían los ficheros.
- `monitoring_db` no tiene tablas.
- Por tanto, `alert_risk` (que se ejecuta a las 10:00 y a las 22:00) no tiene datos sobre los que alertar.
- **El único camino que procesa logs de seguridad es Promtail → Loki**, que monta `/var/log:ro`.
- No hay ningún contenedor honeypot en los compose. Solo existe un job de Promtail que lo espera.

Esto significa:
- La observabilidad centralizada existe: los logs llegan a Loki.
- La detección y las alertas de seguridad, que son el propósito principal, hoy no funcionan. Si alguien intentara atacar el servidor, nadie recibiría un aviso.
- No sé si tienes reglas de alerta configuradas en Grafana. No puedo confirmarlo con lo que veo; los comandos de Loki del punto 2 ayudarán.

**El peso de la gobernanza es desproporcionado para el tamaño del producto:**

| Gobernanza | Producto |
|---|---|
| 51 ADR | 7 contenedores |
| 383 ficheros en `ai/` | 7 scripts Python funcionales |
| 83 targets en el Makefile | |
| Ledger de 2.200 líneas | |
| Documento de corrección de 7.200 líneas | |

- Varios ADR parecen de otros proyectos: 06xx (API gateway, RBAC), 08xx (front-back) y 11xx (knowledge repository). Lo deduzco solo por el nombre del fichero; no los he leído.
- El coste se nota en el drift. La Visión pone "eliminar el drift" como capacidad crítica, y la mayoría de mis hallazgos son justamente desfases entre documentos.

**Hay contradicciones en los propios documentos de referencia:**
- La Visión dice "en caso de conflicto, el documento de implementación prevalece". AI_ENTRYPOINT dice que la Visión es el documento de mayor prioridad.
- La Visión cita nombres antiguos: `server_monitoring_2602` y `Implementacion_260227.txt`.
- La Visión sigue describiendo una única red `monitoring-network` (apartados 2.4 y 6.3). ADR-0021 la prohíbe.

## 4. ¿Habría que eliminar o añadir algo?

**Eliminar o simplificar:**
- Las comprobaciones de auditoría basadas en grep que repiten lo que ya hace el motor estructurado: `docker.sock` buscado como texto y secretos detectados por el nombre del fichero. La propia Visión dice "el fin del grep", y hoy solo generan falsos positivos.
- `monitoring-debug` como contenedor permanente. Que se cree y se borre dentro del propio test.
- El target `test-smtp-all`, que está definido dos veces (Makefile:759 y 763).
- Los ADR que no son de este proyecto: moverlos a `ai/` o a su propio repositorio, si confirmas que son ajenos.
- Las PRIORIDADES 11–15: cerrarlas o reclasificarlas como mejoras futuras en lugar de dejarlas abiertas sin estado.
- **Una decisión pendiente:** hay dos caminos para procesar logs del host (Python → PostgreSQL y Promtail → Loki), y hoy solo funciona el segundo. Mi recomendación es usar Loki como única fuente de logs del host y dejar Python para enriquecerlos (geolocalización, puntuación de riesgo). Es una decisión de arquitectura y te corresponde a ti.

**Añadir lo mínimo:**
1. **Alertas que funcionen:** 3–5 reglas en Grafana sobre Loki (fuerza bruta en SSH, baneos de fail2ban, contenedor caído o reiniciándose, disco por encima del 85 %), enviadas por smtp-relay. Es lo que más distancia hay entre lo que pide la Visión y lo que existe.
2. **Alerta de silencio:** un aviso si un job no se ejecuta o si Loki deja de recibir logs durante X horas. Ya está en la FASE 12. Sin esto, un fallo silencioso como el de `pytz` puede durar meses sin que nadie lo vea.
3. **Plan de parches:** `unattended-upgrades` en el host y una revisión periódica, por ejemplo trimestral, de los digests fijados. Fijar por digest da reproducibilidad, pero las imágenes no reciben parches de seguridad hasta que actualizas el digest.
4. **Cuando los datos importen:** backup fuera del droplet (DigitalOcean Spaces), una prueba de restore y una protección en los targets destructivos.

## 5. ¿Quedarán los riesgos controlados sin dar demasiada rigidez al sistema?

**Sí, pero con una condición.** Hoy los riesgos están **reducidos**, no **controlados**. Controlar un riesgo exige tres cosas: prevenir, detectar y responder.
- **Prevenir:** está bien resuelto.
- **Detectar y responder:** hoy no existen en la práctica, porque no hay alertas funcionando ni aviso de silencio.

**La rigidez está en los documentos, no en el sistema en ejecución.** El runtime es razonablemente sencillo: compose por stacks, sin orquestador. Lo que pesa es mantener el ledger, el plan, los ADR y la gobernanza de IA alineados entre sí. Mi propuesta es cerrar el proyecto con un criterio de "terminado" corto que puedas verificar:

```
TERMINADO =
  [1] Perímetro: tests de seguridad y aislamiento en verde      (ya casi)
  [2] Detección: 1 alerta real verificada de principio a fin    (falta)
  [3] Silencio: alerta si no hay logs o no corren los jobs      (falta)
  [4] Parches: unattended-upgrades + revisar digests            (sin verificar)
  [5] Datos: backup fuera + restore probado (cuando importen)   (aplazado a propósito)

RIESGOS QUE SE ACEPTAN (dejarlo escrito una vez):
  - un solo nodo, sin alta disponibilidad
  - promtail, postgres y smtp-relay como root (excepciones ya justificadas)
  - el droplet como punto único de fallo
```

Con eso cumplido, sí puedes decir que los riesgos están controlados en proporción a un proyecto formativo de un solo nodo. A partir de ahí, lo que añada más gobernanza reducirá poco riesgo y aumentará el drift.

**Advertencia:** sin los puntos [2] y [3], diría que el sistema está bien protegido, pero nadie lo vigila.

Cuando me pases el StatusQuo nuevo, puedo convertir esto en un plan de cierre concreto.

==========================================

Yo:
En docs/Project_Implementation/Servidor_DigitalOcean_StatusQuo_261029.md tienes la situación del servidor.
Por otra parte prefiero conservar la Gobernanza tal y como está (sobredimensionada) debido a que se trata de un proyecto formativo al que tratamos de darle utilidad en otro proyecto y versatilidad.
Dime si tienes más dudas o podemos definir el plan de cierre

Respuesta:
2026/10/29 22:58:47

# StatusQuo 261029: qué nos dice

Tomo nota de la gobernanza: queda como está y la he guardado como decisión permanente.

## A. Lo que va bien (confirmado)

- **Los 7 contenedores están healthy, sin reinicios, tras el reboot.** Promtail ya sale healthy, así que el commit 3a97150 está desplegado y verificado.
- **Tests en verde:** resiliencia completo, aislamiento de red y de FS, permisos, dependencias de host, observabilidad, `security-runtime`, `verify-security`, `audit-runtime-ci` y SMTP local.
- **Host:**
  - UFW deny-by-default.
  - SSH solo con clave y `PermitRootLogin prohibit-password`.
  - `ss` muestra solo el 22 abierto al exterior; 3001 y 3100 escuchan en loopback.
  - `unattended-upgrades` activo; el kernel ha pasado de 6.8.0-94 a 6.8.0-147.
- **Loki está recibiendo logs** de `auth_logs`, `container_logs` y `honeypot`.

## B. Lo que falla: el cron funcional está prácticamente roto

He localizado la causa de cada fallo en el código:

| Job | Error | Causa |
|---|---|---|
| `backup_postgres` | `Permission denied` en `/backups` | El volumen pertenece a root y cron corre como UID 10001. **No se ha hecho ni un backup desde el 17/08.** |
| `backup_postgres`, aviso del fallo | `email_to` no definido | `EMAIL_TO` no llega a monitoring-cron, así que **ningún correo sale desde cron, `alert_risk` incluido** |
| `log_ip_geolocation` | `no password supplied` | Cron no monta el secreto de Postgres ni define `POSTGRES_PASSWORD_FILE` |
| `log_honeypot_geolocation` | no resuelve `loki` | Cron solo está en `backend-net`; Loki está en `observability-net` (efecto de ADR-0021) |
| `docker_resources` | no existe el binario `docker` | Necesita la CLI y `docker.sock`, que ADR-0018 prohíbe. **Con el diseño actual no puede funcionar.** |
| ingestas de auth, fail2ban y kern | salen sin hacer nada | `ALLOW_HOST_LOGS` no es `true` y `/var/log` no está montado |

**Inferencia:** no he visto la traza de `alert_risk` porque el grep se cortó en 40 líneas. Pero necesita la base de datos y `EMAIL_TO`, y le faltan las dos, así que casi seguro falla.

## C. Otros hallazgos

1. **Envío SMTP real roto.** El relay acepta `MAIL FROM` y se queda colgado en `RCPT TO` (timeout). En agosto funcionaba. La causa no se puede saber sin `docker logs monitoring-smtp-relay`. Posibilidades: salida hacia Postmark bloqueada, problema de DNS o credenciales caducadas.
2. **fail2ban no está bloqueando a nadie.** La IP 103.159.2.113 hizo unos 12 intentos en 45 minutos, uno cada 3–4 minutos, y lleva 0 bloqueos. Ese ritmo queda por debajo del umbral por defecto (5 intentos en 10 minutos). El riesgo real es bajo porque el acceso por contraseña está desactivado, pero el control no hace su función.
3. **UFW tiene abiertos el 80 y el 443 sin nada detrás.** El job `honeypot` de Promtail tampoco tiene ningún contenedor honeypot al que leer.
4. **Cron monta `/var/lib/docker/containers:ro`.** Así puede leer los logs de todos los contenedores. El comentario lo justifica por el honeypot, pero ese job ya consulta Loki, así que el montaje sobra. Además, la ALLOWLIST de ADR-0031 solo permite ese montaje a Promtail, y la auditoría no lo detecta.
5. **El inventario no coincide con el nombre real del contenedor.** `runtime_containers.yml` dice `smtp-relay` y el contenedor se llama `monitoring-smtp-relay`. Por eso aparece "smtp-relay not running; skipping": los chequeos por inventario se saltan el relay.
6. **Hay 68 paquetes pendientes de actualizar** a pesar de `unattended-upgrades`. Lo normal es que esa herramienta solo aplique los parches de seguridad.
7. **Git en el servidor:** la rama `migracion` ha divergido de `origin/migracion` (6 commits por delante y 3 por detrás) y hay un directorio `artifacts/` sin seguimiento.

**Conclusión:** el sistema está bien protegido, pero hoy no avisa de nada. No hay backups, no sale correo desde cron y no hay alertas.

Me quedan cuatro decisiones de alcance que son tuyas y que cambian el plan de cierre:

==========================================

Yo:
Logs de seguridad del host (auth, fail2ban, kern): hoy solo funciona Promtail→Loki; las ingestas Python→PostgreSQL están desactivadas (ALLOW_HOST_LOGS=false, sin /var/log montado). ¿Qué modelo cerramos?
Loki como fuente (Recomendado)
Host logs solo vía Promtail→Loki. Los jobs Python leen de Loki (cron se une a observability-net) para geolocalizar/puntuar riesgo. Sin /var/log en cron.
Python→PostgreSQL
Activar ALLOW_HOST_LOGS y montar /var/log:ro en cron; requiere crear tablas ya y ampliar ADR/ALLOWLIST. Duplica la vía Promtail.
Aplazar pipeline BBDD
El cierre cubre solo Loki+alertas Grafana; los jobs de ingesta/geolocalización se desactivan en monitoring.cron hasta construir las tablas.
Alertas (el objetivo 'detección temprana' de la Visión): hoy no sale ningún correo desde cron (sin EMAIL_TO) y el envío E2E vía relay falla. ¿Qué canal de alertas debe quedar verificado para cerrar?
Grafana Alerting (Recomendado)
3-5 reglas sobre Loki (fuerza bruta SSH, contenedor caído/reinicios, silencio de logs, fallo de backup) enviadas por smtp-relay. alert_risk queda como complemento.
Solo alert_risk Python
Arreglar EMAIL_TO, credenciales DB y relay; las alertas dependen de datos en PostgreSQL (hoy vacía).
Ambos
Grafana para infraestructura/seguridad en tiempo real; alert_risk para informes de riesgo periódicos.
Honeypot: no existe contenedor honeypot, pero UFW abre 80/443, Promtail tiene job 'honeypot' y cron tiene un job de geolocalización del honeypot. ¿Entra en el alcance del cierre?
Fuera del cierre (Recomendado)
Cerrar 80/443 en UFW, desactivar job honeypot y quitar mount /var/lib/docker/containers de cron. Se retoma después como micro-stack aislado con ADR propio.
Implementarlo ahora
Añadir micro-stack honeypot aislado (red propia, sin acceso a Postgres) según Visión 6.2. Amplía bastante el cierre.
docker_resources (monitorización CPU/RAM de contenedores) necesita docker.sock, prohibido por ADR-0018, así que en cron nunca podrá funcionar. ¿Cómo lo resolvemos?
Tooling host-side (Recomendado)
La Visión permite tooling operacional en host: ejecutarlo vía systemd timer en host y enviar el resultado a log (Promtail lo recoge). Se retira de monitoring.cron.
Eliminar el job
Cubrir saturación con alertas Grafana (reinicios/OOM vía logs) y límites ya declarados en compose. Menos funcionalidad.
Exportador dedicado
Añadir cAdvisor/node-exporter (requiere mounts de host y probablemente Prometheus: nuevo stack + ADR). Lo más completo y lo más pesado.
Other
monitoring-cron es el responsable de gestionar cualquier cron. Revisa la documentación, el objetivo es que esta infraestructura se pueda implementar en cualquier otro servidor. Priorizamos la versatilidad.

Respuesta
2026/10/29 23:06:12

# Propuesta de plan de cierre (borrador pendiente de aprobación)

Tus respuestas quedan así:
- Logs del host: Loki como fuente única.
- Alertas: solo `alert_risk` en Python.
- Honeypot: fuera del cierre.
- Todo en monitoring-cron, y que se pueda desplegar en cualquier servidor.

Dos de estas respuestas chocan con el código actual y hay que resolverlo antes de cerrar el plan:

1. **`alert_risk` consulta la tabla `public.attacking_logs` de PostgreSQL**, que está vacía y no tiene esquema. Con Loki como fuente única y sin tablas, `alert_risk` nunca tendrá nada que enviar. Hace falta un puente entre Loki y la alerta.
2. **`docker_resources` ejecuta `docker stats`** y escribe en `/var/log/...`. Ninguna de las dos cosas existe dentro de cron. Para que funcione en cron y sea portable, cron tiene que leer métricas de Docker de alguna forma, y cualquier forma toca ADR-0018 o ADR-0024.

## Plan (bloques ordenados por dependencia)

```
B0  Higiene del despliegue
    - Servidor: dejar la rama migracion sincronizada con certificacion_sre_hardening
      (decidir qué hacer con los 6 commits locales y con artifacts/)
    - Commit de los cambios pendientes (ledger + .gitignore)

B1  Cron operativo (desbloquea FASE 8) - solo configuración
    - Secreto Postgres en cron: montar el secret + POSTGRES_PASSWORD_FILE
    - EMAIL_TO (y FROM/CC) en el entorno de cron, desde .env y sin valores en git
    - Volumen de backups: name: explícito y compartido + /backups propiedad de appuser
    - Cron se une a observability-net (para leer de Loki), revisando ADR-0021
    - Quitar el mount /var/lib/docker/containers de cron (no lo cubre ADR-0031)
    - Desactivar los jobs del honeypot y las ingestas desde /var/log (Loki los sustituye)
    - Criterio: 24 h de docker logs monitoring-cron sin ningún Traceback

B2  SMTP de extremo a extremo
    - Diagnosticar el timeout en RCPT TO (logs del relay, salida hacia Postmark, credenciales)
    - Criterio: make test-smtp-all en verde + correo recibido

B3  Cadena de detección Loki → alert_risk          [DECISIÓN 1]
    - Criterio: un intento SSH real provoca un correo de alert_risk

B4  Monitorización de recursos dentro de cron      [DECISIÓN 2]
    - Criterio: docker_resources registra métricas y avisa por encima del umbral

B5  Perímetro
    - UFW: cerrar 80/443 (honeypot fuera de alcance)
    - fail2ban: findtime=1h, maxretry=3-5, bantime.increment
      (hoy no frena el ataque lento de 103.159.2.113)
    - Revisar los 68 paquetes pendientes

B6  Coherencia de auditoría (bajo coste)
    - runtime_containers.yml: smtp-relay → monitoring-smtp-relay
    - audit_repo_host.sh:297 ($$ → $), quitar los greps de docker.sock y secrets.py
    - Duplicado de test-smtp-all; el contenedor debug sale con digest fijado
    - Protección CONFIRM en test-reproducibilidad (datos futuros)

B7  Cierre documental
    - Ledger: FASE 5, 8, 10 y 11 con evidencias del nuevo StatusQuo
    - Plan de corrección: estado de las PRIORIDADES 11-15
    - Visión: contradicción de precedencia con AI_ENTRYPOINT, nombres 2602/260227,
      red monitoring-network
    - ADR para las decisiones 1 y 2 (y para el cambio de red de cron si cambia ADR-0021)
    - StatusQuo final = evidencia de cierre de las FASES 8, 10 y 11
```

Quedan fuera del cierre: el honeypot, la migración de datos reales, un backup fuera del servidor y la alta disponibilidad.

==========================================

Yo:
DECISIÓN 1 — alert_risk lee de la tabla PostgreSQL public.attacking_logs (hoy sin esquema). Con Loki como fuente, ¿cómo le llegan los datos?
Loki→PG→alert_risk (Recomendado)
Nuevo job en cron que consulta Loki (LogQL, fallos SSH por IP) y escribe en attacking_logs. Requiere crear ya el esquema mínimo vía init/ declarativo. alert_risk no cambia; PostgreSQL queda como almacén de análisis.
alert_risk lee de Loki
Refactorizar alert_risk para consultar Loki directamente. Sin tablas ni esquema por ahora; PostgreSQL sigue sin uso hasta la migración.
Other
Me da la sensacion de que he respondido mal a la pregunta:
"Logs de seguridad del host (auth, fail2ban, kern): hoy solo funciona Promtail→Loki; las ingestas Python→PostgreSQL están desactivadas (ALLOW_HOST_LOGS=false, sin /var/log montado). ¿Qué modelo cerramos?"
Creo que la respuesta adecuada sería:
"Python→PostgreSQL"
Tiene más sentido?

DECISIÓN 2 — docker_resources debe correr en monitoring-cron y ser portable, pero ADR-0018 prohíbe docker.sock en cron. ¿Qué vía de acceso a métricas de contenedores aceptamos (requiere ADR)?
docker-socket-proxy RO (Recomendado)
Contenedor proxy (tecnativa/docker-socket-proxy) en red interna propia, solo GET containers/stats. Cron consume la API sin tener docker.sock. Patrón estándar y portable; excepción ADR-0024 acotada al proxy.
cgroups montados RO
Montar /sys/fs/cgroup:ro en cron y leer CPU/memoria de cgroup v2. Sin socket, pero depende de la estructura del host (cgroup v2, driver systemd) y cuesta mapear nombres.
Retirar docker_resources
Aceptar como riesgo residual: límites ya declarados en compose + reinicios visibles en Loki. Sin informes de recursos.

Respuesta:
2026/10/29 23:14:40

# Sí, con tu elección de alertas tiene más sentido Python → PostgreSQL

**Por qué encaja mejor.** Al elegir "solo `alert_risk` en Python" decidiste, sin decirlo, que PostgreSQL es el almacén de detección. El código ya está hecho para ese modelo:
- `log_ingest_batch` lee `auth.log` y escribe en `attacking_logs`, que es justo la tabla que consulta `alert_risk`.
- `log_fail2ban_batch` escribe en `fail2ban_logs` y `log_kern_batch` en `kern_logs`.
- Los tres leen solo lo nuevo, usando el último timestamp guardado en la base de datos. Así no duplican filas aunque se ejecuten cada 10 minutos.

Esto significa que el cierre se hace casi solo con configuración, sin reescribir código. Con Loki → PostgreSQL habría que reescribir los tres ingestores.

**Lo que cuesta.** No lo descarta, pero hay que asumirlo:

1. **Permisos.** En Ubuntu, `auth.log`, `kern.log` y `fail2ban.log` suelen pertenecer a `syslog:adm` (o `root:adm`) con permisos 640. Cron corre como UID 10001, así que no podrá leerlos si no se le añade el grupo `adm` con `group_add`. **Pendiente de verificar en el servidor:**
   ```
   stat -c '%n %U:%G %a' /var/log/auth.log /var/log/kern.log /var/log/fail2ban.log; getent group adm
   ```
2. **Montar el directorio entero (`/var/log:ro`), no los ficheros sueltos.** Logrotate sustituye el fichero por uno nuevo, y un bind mount de un solo fichero seguiría apuntando al antiguo después de la rotación.
3. **Gobernanza.** La ALLOWLIST de ADR-0031 solo permite a Promtail leer logs del host. Para cron hace falta una excepción formal, sea ampliando ADR-0031 o con un ADR nuevo. Además, el propio código avisa de que `ALLOW_HOST_LOGS=true` está "no recomendado". Ese texto habrá que cambiarlo, o el código y la decisión se contradirán.
4. **Portabilidad.** La solución queda ligada a hosts Debian/Ubuntu con rsyslog, que son los que generan `auth.log` y `kern.log`. En RHEL el fichero es `/var/log/secure`. Si se documenta como requisito del host, es aceptable para cualquier droplet Ubuntu.
5. **Esquema de base de datos ahora.** Esto adelanta parte de la FASE 6: el esquema, no la migración de datos. Implica crear `ops/services/postgres/init/*.sql` con las tablas y la función `update_attacking_no` (hoy solo descritas en el procedimiento manual de 6.5) y añadir una excepción a `*.sql` en `.gitignore`. Los scripts de `init/` solo se ejecutan con el volumen vacío. Como `postgres_postgres-data` ya está inicializado, habrá que recrearlo; como los datos no importan, no es problema.
6. **Promtail y cron leerán los mismos ficheros.** Es redundante pero inofensivo, porque los dos los leen en modo solo lectura.

**Mi opinión:** recomiendo Python → PostgreSQL para este cierre. Te da la cadena de detección completa con el menor cambio de código. El coste son los puntos 1 y 3, y los dos se resuelven con un ADR. Loki → PostgreSQL sería mejor en seguridad, porque habría un solo lector de logs del host, pero exige reescribir código. Puede quedar como evolución futura.

## Plan de cierre revisado

```
B0  Higiene: sincronizar la rama del servidor, decidir sobre artifacts/,
    commit de lo pendiente

B1  Esquema declarativo (FASE 6 parcial)
    - init/*.sql: attacking_logs, fail2ban_logs, kern_logs + update_attacking_no
      (honeypot_logs fuera)
    - .gitignore: !ops/services/postgres/init/*.sql
    - Recrear postgres-data → \dt muestra las tablas

B2  Cron operativo (FASE 8)
    - Secreto Postgres + POSTGRES_PASSWORD_FILE en cron
    - EMAIL_TO/FROM/CC en el entorno de cron
    - Volumen de backups: name: explícito, compartido y escribible por appuser
    - /var/log:ro + group_add adm + ALLOW_HOST_LOGS=true
    - Quitar /var/lib/docker/containers y desactivar los jobs del honeypot
    - Criterio: 24 h sin Traceback y backup diario generado

B3  SMTP de extremo a extremo: diagnosticar el timeout en RCPT TO → test-smtp-all en verde

B4  Detección: un intento SSH real → fila en attacking_logs → correo de alert_risk

B5  docker_resources mediante docker-socket-proxy en solo lectura
    - Proxy en una red interna propia, solo GET containers/stats
    - DOCKER_HOST en cron; escribir el log en /opt/monitoring/logs, no en /var/log

B6  Perímetro: cerrar 80/443 en UFW, endurecer fail2ban (findtime/maxretry/increment),
    revisar los paquetes pendientes

B7  Coherencia de auditoría: nombre smtp-relay en el inventario, $$ en
    audit_repo_host.sh, greps heurísticos, test-smtp-all duplicado,
    digest del contenedor debug, protección CONFIRM en test-reproducibilidad

B8  Documentación
    - ADR: lectura de logs del host por cron (amplía ADR-0031) y docker-socket-proxy
      (excepción ADR-0018/0024), más el cambio de red si aplica

    - Ledger: FASES 5, 6, 8, 10 y 11; PRIORIDADES 11-15
    - Visión: precedencia, nombres antiguos y red monitoring-network
    - StatusQuo final = evidencia de cierre
```

Siguiendo el protocolo, no toco nada sin tu aprobación. Para empezar necesito dos cosas:
- La salida del `stat` del punto 1.
- Tu aprobación del plan, o los cambios que quieras.

¿Quieres que también lo deje escrito en [Servidor_DigitalOcean_planaccion.md](docs/Project_Implementation/Servidor_DigitalOcean_planaccion.md)?

==========================================

Yo:
Promtail - Loki - Grafana están en este proyecto con un caracter meramente didáctico. Simplemente quiero familiarizarme con ellos y una vez que entienda como funciona el procedimiento básico de alertas y análisis quizas lo acabemos implementando. De momento sólo acompaña.

Antes de dar el siguiente paso dime si necesitas que ejecute algún comando más o si ya tienes suficiente perspectiva del proyecto.

A continuación y en base a la información que hemos recabado vamos a reconstruir el documento
docs/Project_Implementation/Servidor_DigitalOcean_Implementacion.txt
con el fin de simplificarlo (sin sacrificar su caracter didáctico).
Si no precisas aclarar más dudas, devuelve el documento completo corregido.

Respuesta:
2026/10/29 23:47:13

He reconstruido [Servidor_DigitalOcean_Implementacion.txt](docs/Project_Implementation/Servidor_DigitalOcean_Implementacion.txt) en el propio fichero. Pasa de 2.208 a 1.041 líneas y no he hecho commit. No necesité más comandos: lo que falta comprobar (permisos de `/var/log` y logs del relay SMTP) aparece en el documento como pendiente, con el comando exacto para hacerlo.

**Copia del original.** Antes de sobrescribir guardé una copia que incluye tus dos notas sin commit del 18/08:
`/tmp/claude-1000/-mnt-d-WorkSpace-Proyectos-VPS-DigitalOcean-2410-server-monitoring-2509/066e791f-0e0c-480b-8ec6-db0e2c6fc3eb/scratchpad/Servidor_DigitalOcean_Implementacion_ORIGINAL_261029.txt`
La versión anterior a esas notas sigue en git.

## Cómo queda organizado

- **Secciones 0–4: el modelo.**
  - Cadena funcional: logs del host → cron → PostgreSQL → `alert_risk` → correo.
  - Promtail/Loki/Grafana descritos como acompañamiento didáctico, sin formar parte de esa cadena.
  - Tablas de contenedores, redes, puertos, secretos, volúmenes y healthchecks.
- **Sección 5: estado de todas las fases en una tabla.**
- **Fases 1–12:** cada una sigue el mismo esquema: Objetivo → Acciones → Validación → Criterio de cierre → Estado.
- **Apéndice A:** las explicaciones largas de diagnóstico, resumidas como hallazgo → causa → resolución → lección. Ahí va lo didáctico: el `exit` dentro de un subshell, `$$` en bash, volúmenes con prefijo, logrotate y bind mounts, el ataque SSH lento.
- **Apéndice B:** el procedimiento de StatusQuo con los comandos para producción.

## Correcciones respecto a la versión anterior

- Rutas actualizadas: `ops/stacks/` y `compose.yml` en lugar de `ops/docker/` y `docker-compose.*.yaml`.
- Imágenes fijadas por digest en lugar de `:latest`.
- Las tres redes segmentadas en lugar de "monitoring-network".
- Secretos en ficheros `*_FILE` según ADR-0032, en lugar de "solo `.env`, sin `secrets/`".
- Backups en volúmenes Docker en lugar de `/opt/backups`.
- Se elimina el permiso de los infra-stacks para usar `docker.sock`, que contradecía ADR-0018.

## Contenido nuevo que conviene que revises

1. **FASE 3: la rama canónica de producción no la he fijado.** La dejo como pendiente porque la decisión es tuya.
2. **5.3: automatismos del host.** El servidor no tiene crontab de root, así que no están instalados.
   - `configure_docker_limits.sh` no tendría efecto aunque se instalara: ningún contenedor lleva la etiqueta que busca.
   - `apply_ssh_ratelimit.sh` hace `iptables-restore` desde un fichero no versionado, algo que el propio modelo prohíbe.
   - Propongo retirar los dos y los marco como pendientes, no como decididos.
3. **5.4: valores de fail2ban** (`findtime 1h`, `maxretry 3-5`, `bantime.increment`). Son una propuesta mía.
4. **Hallazgo nuevo: cron no está en `restricted-net` y no puede llegar a `smtp-relay`.** Aunque se defina `EMAIL_TO`, ningún job de cron puede enviar correo todavía. Cambiarlo implica revisar ADR-0021 (3.3 y 8.1).

Tus decisiones del 29/10 (Python → PostgreSQL, solo `alert_risk`, honeypot fuera, docker-socket-proxy, todo el cron en monitoring-cron) están marcadas como [DECISIÓN]: pendientes de ADR.

No he tocado la Visión ni el plan de corrección. Siguen sus incoherencias (precedencia frente a AI_ENTRYPOINT, nombres 2602/260227, red única, PRIORIDADES 11–15 sin estado) y quedan para el bloque documental del plan de cierre.

==========================================

Yo:
Ahora vamos a revisar la utilidad de los documentos contenidos en docs/Project_Corrections y que están pendientes de commit.
Son realmente necesarios? Presenta una tabla con enlace y razón de existir de cada uno de ellos.

Respuesta:
2026/10/30 00:03:47

# Documentos de docs/Project_Corrections

**Contexto:** antes, `.gitignore` excluía la carpeta entera (`docs/Project_Corrections/*`). Tu cambio sin commit solo excluye los `.txt`, así que los 8 `.md` aparecen ahora como pendientes de añadir. Ningún documento del repositorio los cita; solo aparecen en el árbol generado `estructura_server_monitoring.txt`. Además, los cinco ADR_* y TRUTH_SOURCE describen un trabajo ya terminado: los 50 ADR de `docs/decisiones/` usan hoy la cabecera normalizada `Status:`/`Date:`.

## Pendientes de commit (.md)

| Documento | Para qué existe | ¿Sigue siendo útil? |
|---|---|---|
| [ADR_HEADER_NORMALIZATION_ANALYSIS.md](docs/Project_Corrections/ADR_HEADER_NORMALIZATION_ANALYSIS.md) | Diagnóstico del 14/06/2026 sobre cómo de homogéneas eran las cabeceras de 41 ADR | No. El trabajo está hecho. Además, sus cifras no cuadran con las del plan siguiente: 31 conformes aquí, 0 en el plan |
| [ADR_HEADER_MIGRATION_CONSERVATIVE_PLAN.md](docs/Project_Corrections/ADR_HEADER_MIGRATION_CONSERVATIVE_PLAN.md) | Plan del 15/06 para normalizar las cabeceras sin tocar el contenido | No. Ya se ejecutó |
| [ADR_PILOT_EXECUTION_ANALYSIS.md](docs/Project_Corrections/ADR_PILOT_EXECUTION_ANALYSIS.md) | Análisis previo del piloto sobre ADR-0014, 0018 y 0021 | No. Era un paso intermedio |
| [ADR_PILOT_DIFFS_FOR_REVIEW.md](docs/Project_Corrections/ADR_PILOT_DIFFS_FOR_REVIEW.md) | Diffs del piloto, propuestos para revisión | No. Ya se aplicaron |
| [ADR_PILOT_FINAL_AUDIT.md](docs/Project_Corrections/ADR_PILOT_FINAL_AUDIT.md) | Auditoría final del piloto antes de ejecutarlo | No. Además cita `adr_template.md`, que hoy se llama `04_adr_template.md` |
| [TRUTH_SOURCE_VERIFICATION.md](docs/Project_Corrections/TRUTH_SOURCE_VERIFICATION.md) | Resolvió qué fuente mandaba en las cabeceras ADR (plantilla o índice) cuando se contradecían | Poco. La decisión ya está aplicada en la plantilla y en 14_ADR_INDEX |
| [SWOT_260613_GOVERNANCE_COHERENCE_ANALYSIS.md](docs/Project_Corrections/SWOT_260613_GOVERNANCE_COHERENCE_ANALYSIS.md) | Análisis SWOT de la coherencia de la gobernanza de IA, con puntos críticos P0–P3 | Parcialmente. Hipótesis, sin verificar punto por punto: buena parte ya está incorporada (existen 17_SKILL_LIFECYCLE y 22_USER_PREFERENCES). Trata de gobernanza, no del servidor |
| [Servidor_Migracion_Monitoring_correcciones_251203.md](docs/Project_Corrections/Servidor_Migracion_Monitoring_correcciones_251203.md) | Diseño de diciembre de 2025 para pasar a IaC: estado de entonces, objetivo y plan | No como referencia actual. Describe `monitoring-base` y `COPY . .`, ambos ya descartados. Solo tiene valor histórico |

## Ya excluidos por .gitignore (.txt), para completar la foto

| Documento | Para qué existe | ¿Sigue siendo útil? |
|---|---|---|
| [Servidor_DigitalOcean_Correccion_260712.txt](docs/Project_Corrections/Servidor_DigitalOcean_Correccion_260712.txt) | Plan priorizado de hardening (PRIORIDADES 1–15) | **Sí. Es autoritativo:** de él depende el cierre de la FASE 5. Hoy no tiene historial de versiones |
| [PreDigest_IA_monitoring_server_2607.txt](docs/Project_Corrections/PreDigest_IA_monitoring_server_2607.txt) | Contexto resumido para asistentes de IA (v260712) | Dudosa. Se solapa con AI_ENTRYPOINT y con el grafo `.ua` |
| [Servidor_Migracion_Monitoring_260125.txt](docs/Project_Corrections/Servidor_Migracion_Monitoring_260125.txt) | Registro de la migración de imports (`common` → `monitoring.common`) | Histórico. Ya lo cubre ADR-0001 |

## Valoración

No es necesario versionar ninguno de los 8 `.md` en este repositorio. Son material de trabajo de tareas ya cerradas, casi todas sobre gobernanza. Tu `.gitignore` excluye `ai/` porque la gobernanza "se versiona aparte", y ADR-1102 separa la gobernanza del contenido. Subir aquí análisis de gobernanza contradice esa separación.

## Recomendación (pendiente de tu aprobación)

1. **Deshacer el cambio de `.gitignore`** (volver a `docs/Project_Corrections/*`). Los `.md` siguen en local como notas de trabajo y no acaban en el repositorio por accidente.
2. **SWOT y TRUTH_SOURCE:** si quieres conservarlos con historial, llévalos a la rama o al repositorio de gobernanza (`gobernanza_ia*`), no a este.
3. **Excepción para `Servidor_DigitalOcean_Correccion_260712.txt`.** Es el único autoritativo. Recomiendo versionarlo con `!docs/Project_Corrections/Servidor_DigitalOcean_Correccion_260712.txt`, porque el cierre de la FASE 5 depende de él. Si prefieres no subirlo por su tamaño (397 KB, 7.200 líneas, gran parte logs de terminal), la alternativa es extraer el plan de PRIORIDADES a un documento corto que sí se versione.

¿Aplico el punto 1 y alguna de las opciones del 3?


==========================================

Yo:
Creo que no tiene sentido mantenerlos y parece que eliminarlos no genera ningún problema. Podríamos extraer alguna conclusión que nos sirva para corregir/ampliar los ADRs canonicos (docs/decisiones)?

Respuesta:
2026/10/30 00:24:19

# Qué se puede aprovechar de docs/Project_Corrections

He comparado lo que dicen los documentos con el estado actual de `docs/decisiones/`, `04_adr_template.md` y `14_ADR_INDEX.md`.

**Resultado general:** casi todo lo que proponían ya está aplicado.
- Los 50 ADR usan la cabecera normalizada.
- El conflicto APPROVED/ACCEPTED está resuelto: hay 47 APPROVED, 2 PROPOSED (0802 y 0803) y 1 DEPRECATED (0006).
- `Decision Type` se sustituyó por `Category`.
- `correcciones_251203` no aporta nada que no esté ya en ADR-0002, 0006, 0011 y 0012.

Aun así, quedan **cuatro conclusiones vigentes** y una idea de herramienta.

## Conclusiones aplicables a los ADR canónicos

| # | Conclusión | Origen | Evidencia actual | Acción propuesta |
|---|---|---|---|---|
| C1 | La plantilla no tiene el campo `Validation Reference`, aunque los ADR sí lo usan | TRUTH_SOURCE, punto 3 (sigue abierto) | 43 de 50 ADR lo usan; faltan 0605 y 1100–1105 | Añadir `Validation Reference: [make <target>] \| NONE` a [04_adr_template.md](docs/decisiones/04_adr_template.md) y completarlo en los 7 que no lo tienen. Es un cambio de plantilla, no un ADR nuevo |
| C2 | Hay ADR con validación real que declaran `NONE` | Amplía C1 con lo visto en esta sesión | ADR-0020: `NONE`, pero AI_ENTRYPOINT le asigna `make test-reproducibilidad`. ADR-0014: `NONE`, pero `test-policy-structured` valida los puertos. ADR-0009 (backups): `NONE`, y los backups llevan fallando desde el 17/08 sin que nadie lo detectara | Rellenar las referencias. En ADR-0009, la validación debería comprobar que existe un backup reciente; hoy ningún target lo hace |
| C3 | El índice no está sincronizado con los ADR | SWOT P0-1, hecho solo en parte | ADR-1100–1105 son APPROVED pero no aparecen en `14_ADR_INDEX.md` | Añadirlos al índice. Va en el repositorio o rama de gobernanza, porque `ai/` se versiona aparte |
| C4 | ADR-0023 dice APPROVED, pero su texto sigue siendo una propuesta | TRUTH_SOURCE (estado frente a contenido) + esta sesión | El índice lo titula "(Propuesto)" y el texto dice "Se propone…". Exige reglas iptables/nftables, cosa que el ledger prohíbe gestionar a mano. smtp-relay está en `restricted-net` y **necesita** salida hacia Postmark. No hay evidencia de que se haya implementado (`Internal: false`, sin proxy) | Pasarlo a PROPOSED o reescribirlo con la decisión real (por ejemplo, salida permitida solo al proveedor SMTP). Hoy aparenta un control que no existe |

**La herramienta (SWOT P1-3): validar la gobernanza automáticamente.** C1–C4 son desfases que una comprobación automática detectaría:
- campos obligatorios en la cabecera,
- estado del fichero igual al del índice,
- que el `make` de `Validation Reference` exista.

Según AI_ENTRYPOINT ("Architectural Precision"), las reglas de lint **no deben ser ADR**. Lo adecuado sería un target como `make verify-adr`, documentado en el ADR-0029 existente o en el README.

**Detalle menor:** tres ADR tienen espacios en el nombre del fichero (0008, 0012 y 0015). Rompen los scripts que no entrecomillan rutas; de hecho, mi propia comprobación falló con ellos. Conviene renombrarlos usando `git mv`.

Del SWOT descarto el resto: el registro de decisiones de IA, la traducción de documentos y los dashboards son cosas de gobernanza, no de los ADR de este proyecto.

## Todos los cambios de ADR pendientes en un solo sitio

Sumando lo de esta sesión:

| ADR | Cambio | Motivo |
|---|---|---|
| 04_adr_template | Añadir `Validation Reference` | C1 |
| 0009, 0014, 0020 (+7 sin campo) | Completar `Validation Reference` | C2 |
| 0009 | Volumen de backups con `name:` explícito; validar que hay un backup reciente | Plan de cierre, FASE 5.5 |
| 0021 | monitoring-cron entra en `restricted-net` para llegar a smtp-relay | Plan de cierre, FASE 8 |
| 0023 | Reclasificarlo o reescribirlo | C4 |
| 0031 | ALLOWLIST: `/var/log:ro` + grupo `adm` para cron | Decisión 29/10 (Python → PostgreSQL) |
| Nuevo (excepción a 0018/0024) | docker-socket-proxy de solo lectura | Decisión 29/10 |
| 14_ADR_INDEX (gobernanza) | Añadir 1100–1105 | C3 |

## Próximo paso (pendiente de tu confirmación)

Los 8 `.md` **no están en git**: si los borro, no hay forma de recuperarlos. Te propongo:

1. Borrar los 8 `.md` de [docs/Project_Corrections/](docs/Project_Corrections/).
2. Deshacer el cambio de `.gitignore` para volver a `docs/Project_Corrections/*`. Queda pendiente tu decisión sobre versionar `Servidor_DigitalOcean_Correccion_260712.txt`.
3. Incorporar C1–C4 y la tabla de cambios a [Servidor_DigitalOcean_planaccion.md](docs/Project_Implementation/Servidor_DigitalOcean_planaccion.md) como bloque documental del plan de cierre, para que no se pierdan al borrar los documentos.

¿Procedo con los tres pasos, o prefieres guardar antes una copia comprimida de los `.md` en el scratchpad?

==========================================

Yo:
Adelante con los tres pasos

Respuesta:

2026/10/30 00:41:05

He hecho los tres pasos:

1. **Borrado:** eliminé los 8 `.md` de [docs/Project_Corrections/](docs/Project_Corrections/). No estaban en git y no hice copia, así que no se pueden recuperar. En la carpeta quedan los tres `.txt`.
2. **`.gitignore`:** vuelve a tener `docs/Project_Corrections/*`. `git diff .gitignore` sale vacío, es decir, coincide con el último commit.
3. **Plan consolidado:** lo he escrito en [Servidor_DigitalOcean_planaccion.md](docs/Project_Implementation/Servidor_DigitalOcean_planaccion.md), en el hueco "Respuesta:" de tu último mensaje. Reúne:
   - tus decisiones del 29/10,
   - los bloques B0–B8 con sus criterios,
   - en B8, las conclusiones C1–C5 extraídas de los documentos borrados y la tabla de cambios en ADR.

   He añadido dos cosas que antes solo estaban sueltas en la conversación:
   - En B0, la decisión de si se versiona `Correccion_260712.txt`.
   - En B7, la herramienta tipo `make verify-adr`, marcada como no-ADR.

No he hecho commit. Quedan pendientes en el árbol de trabajo:
- el ledger modificado (`Implementacion.txt`),
- el StatusQuo 261029,
- el plan de acción.

Los tres forman parte de B0. Si me apruebas B0, empiezo por ahí. Antes necesito que me digas cuál es la rama canónica de producción.


2026/10/30

Ejecutado:
1. Borrados los 8 `.md` de docs/Project_Corrections/ (no estaban en git; sus conclusiones vigentes quedan en este bloque).
2. `.gitignore` restaurado a `docs/Project_Corrections/*`.
3. Plan de cierre consolidado a continuación (sustituye a los borradores anteriores de este fichero).

# PLAN DE CIERRE CONSOLIDADO (v261030)

Estado: pendiente de aprobación bloque a bloque antes de ejecutar.
Ledger de referencia: docs/Project_Implementation/Servidor_DigitalOcean_Implementacion.txt (v261029).

Decisiones del usuario (29/10/2026), pendientes de formalizar en ADR:
- Cadena de detección: Python → PostgreSQL → alert_risk (alertas solo vía alert_risk).
- Promtail/Loki/Grafana: carácter didáctico, sin papel en la cadena funcional.
- Honeypot: fuera del cierre.
- Toda tarea programada en monitoring-cron; portabilidad como prioridad.
- docker_resources: acceso a métricas mediante docker-socket-proxy de solo lectura.
- Gobernanza: se mantiene tal como está (sobredimensionada a propósito).

```
B0  Higiene del despliegue
    - Definir la rama canónica de PRO y alinear la rama del servidor (hoy: migracion
      divergente, 6/3) + decidir el destino de artifacts/
    - Commit de lo pendiente (ledger v261029, StatusQuo 261029, este plan)
    - Decidir si se versiona Servidor_DigitalOcean_Correccion_260712.txt
      (única fuente de las PRIORIDADES 1-15)

B1  Esquema declarativo de Postgres (FASE 6)
    - ops/services/postgres/init/*.sql: attacking_logs, fail2ban_logs, kern_logs
      + update_attacking_no()
    - .gitignore: !ops/services/postgres/init/*.sql
    - Recrear postgres_postgres-data → \dt muestra las tablas

B2  Cron operativo (FASE 8)
    - Secreto Postgres + POSTGRES_PASSWORD_FILE en cron
    - EMAIL_TO/FROM/CC en el entorno de cron + acceso a smtp-relay (restricted-net)
    - Volumen de backups único (name: explícito), escribible por appuser
    - /var/log:ro + group_add adm + ALLOW_HOST_LOGS=true
      (verificar antes: stat de auth.log, kern.log, fail2ban.log y getent group adm)
    - Quitar /var/lib/docker/containers de cron; desactivar log_honeypot_geolocation
    - Criterio: 24 h sin Traceback + backup del día generado

B3  SMTP de extremo a extremo (FASE 9)
    - Diagnosticar el timeout en RCPT TO: docker logs --tail 200 monitoring-smtp-relay
    - Criterio: make test-smtp-all en verde + correo recibido

B4  Cadena de detección (FASE 11.3)
    - Intento SSH real → fila en attacking_logs → correo de alert_risk recibido

B5  docker_resources mediante docker-socket-proxy de solo lectura
    - Red interna propia, solo GET containers/stats; DOCKER_HOST en cron
    - Log en /opt/monitoring/logs (no en /var/log)

B6  Perímetro (FASES 2, 2B y 5)
    - UFW: cerrar 80/443
    - fail2ban: jail.local versionado (findtime 1h, maxretry 3-5, bantime.increment)
    - Retirar configure_docker_limits.sh y apply_ssh_ratelimit.sh del modelo
    - Instalar docker-buildx; revisar los 68 paquetes pendientes
    - Probar un restore contra un Postgres efímero

B7  Coherencia de auditoría
    - runtime_containers.yml: smtp-relay → monitoring-smtp-relay
    - audit_repo_host.sh:297 ($$ → $); quitar los greps heurísticos (docker.sock, secrets.py)
    - test-smtp-all duplicado; netshoot con digest fijado; debug-toolbox-down automático
    - Protección CONFIRM=yes en test-reproducibilidad
    - Herramienta de validación de gobernanza (target tipo make verify-adr): campos
      obligatorios, estado fichero = índice, Validation Reference → target existente.
      No es ADR (AI_ENTRYPOINT, "Architectural Precision"); documentarlo en ADR-0029 o en el README

B8  Documentación y ADR
    a) Conclusiones extraídas de docs/Project_Corrections (documentos ya eliminados):
       C1  04_adr_template.md no tiene el campo "Validation Reference", que usan
           43 de 50 ADR. Añadirlo y completarlo en 0605 y 1100-1105.
           (Origen: TRUTH_SOURCE_VERIFICATION, punto 3)
       C2  Validation Reference = NONE en ADR con validación real:
           0020 (make test-reproducibilidad, según AI_ENTRYPOINT), 0014 (make
           test-policy-structured), 0009 (backups: falta un target que compruebe que
           hay un backup reciente; los backups fallan desde el 17/08 sin que nadie lo detectara)
       C3  14_ADR_INDEX.md no incluye ADR-1100..1105 (APPROVED).
           Corregir en el repositorio o rama de gobernanza (ai/ se versiona aparte).
           (Origen: SWOT_260613, P0-1)
       C4  ADR-0023 marcado APPROVED con texto de propuesta ("Se propone..."), sin
           implementar, dependiente de iptables (prohibido en el ledger) e incompatible
           con smtp-relay en restricted-net (necesita salir hacia Postmark).
           Reclasificar a PROPOSED o reescribirlo con la decisión real (p. ej. salida
           solo hacia el proveedor SMTP)
       C5  Renombrar con git mv los ADR con espacios en el nombre (0008, 0012, 0015)

    b) Tabla consolidada de cambios en ADR:
       ADR                          CAMBIO                                          ORIGEN
       04_adr_template              añadir Validation Reference                     C1
       0009, 0014, 0020 (+7)        completar Validation Reference                  C2
       0009                         volumen de backups con name:; validar backup    FASE 5.5
       0021                         monitoring-cron en restricted-net (SMTP)        FASE 8
       0023                         reclasificar o reescribir                       C4
       0031                         ALLOWLIST: /var/log:ro + grupo adm para cron    Decisión 29/10
       nuevo (exc. 0018/0024)       docker-socket-proxy de solo lectura             Decisión 29/10
       14_ADR_INDEX (gobernanza)    añadir 1100-1105                                C3

    c) Ledger y documentos de referencia
       - Implementacion.txt: actualizar estados con la evidencia del StatusQuo final
       - Plan de corrección: estado de las PRIORIDADES 11-15
       - Visión: contradicción de precedencia con AI_ENTRYPOINT, nombres antiguos
         (2602 / 260227), red monitoring-network
       - StatusQuo final archivado = evidencia de cierre de las FASES 5, 6, 8, 9, 10 y 11
```

Fuera del cierre: honeypot, migración de datos reales, backup fuera del droplet,
alertas en Grafana (línea didáctica), alta disponibilidad.



==========================================
==========================================
==========================================
==========================================
==========================================
==========================================
==========================================
==========================================
