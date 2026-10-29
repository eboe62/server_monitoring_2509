=== CONTEXTO ===
Thu Oct 29 21:48:28 UTC 2026
eob-260131
 21:48:28 up 1 min,  1 user,  load average: 1.13, 0.67, 0.26
On branch migracion
Your branch and 'origin/migracion' have diverged,
and have 6 and 3 different commits each, respectively.
  (use "git pull" if you want to integrate the remote branch with yours)

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        artifacts/

nothing added to commit but untracked files present (use "git add" to track)
954164f fix: añade dependencia pytz faltante en monitoring-cron (log_fail2ban_batch)
  copilot_sandbox e8cd0f5 Merge pull request #55 from eboe62/CORRECCION
* migracion       954164f [origin/migracion: ahead 6, behind 3] fix: añade dependencia pytz faltante en monitoring-cron (log_fail2ban_batch)
=== CONTENEDORES / RECURSOS ===
NAMES                   IMAGE                      STATUS                        PORTS
monitoring-cron         monitoring-cron:v1.0.0     Up About a minute (healthy)
promtail                grafana/promtail:2.9.3     Up About a minute (healthy)
monitoring-debug        nicolaka/netshoot          Exited (137) 15 minutes ago
monitoring-smtp-relay   monitoring-smtp-relay      Up About a minute (healthy)   587/tcp
monitoring-python       monitoring-python:v1.0.0   Up About a minute (healthy)
grafana                 grafana/grafana:10.4.2     Up About a minute (healthy)   3000/tcp, 127.0.0.1:3001->3001/tcp
loki                    grafana/loki:2.9.3         Up About a minute (healthy)   127.0.0.1:3100->3100/tcp
monitoring-postgres     postgres:14.3              Up About a minute (healthy)   5432/tcp
CONTAINER ID   NAME                    CPU %     MEM USAGE / LIMIT     MEM %     NET I/O           BLOCK I/O         PIDS
595d999cdcbe   monitoring-cron         0.00%     13.34MiB / 1.922GiB   0.68%     1.27kB / 126B     10.8MB / 0B       7
2b23ad2dae7b   promtail                0.54%     90.7MiB / 250MiB      36.28%    4.47kB / 78.3kB   66MB / 28.7kB     7
f3fe53f36019   monitoring-smtp-relay   0.03%     64.48MiB / 1.922GiB   3.28%     1.1kB / 126B      52.9MB / 2.27MB   12
d3a0a01229a4   monitoring-python       0.00%     8.336MiB / 1.922GiB   0.42%     4.37kB / 378B     9.32MB / 0B       1
1e5e98766f23   grafana                 0.15%     170.3MiB / 300MiB     56.76%    20kB / 3.79kB     129MB / 250kB     14
1502fa2b4de2   loki                    0.35%     87.11MiB / 500MiB     17.42%    79.8kB / 2.85kB   58.2MB / 446kB    7
c7c1d622e9bb   monitoring-postgres     0.03%     51.7MiB / 500MiB      10.34%    1.31kB / 126B     38.2MB / 303kB    7
DRIVER    VOLUME NAME
local     58bd72d1512c3ee57f3e601350db8b5eb859cbe528f231b5d0fa3aa7360178b1
local     60bbfd738c570db94ae39bf8fd048adf4e0c6d80bcadf9f4b72399a9ab54a142
local     738f76a891571af4650247a321db87d0cc2f3c65c425cf419d65968843a43532
local     cron_postgres-backups
local     observability_grafana-data
local     observability_loki-data
local     observability_promtail-data
local     postgres_postgres-backups
local     postgres_postgres-data
local     smtp_relay_smtp_relay_logs
NETWORK ID     NAME                DRIVER    SCOPE
5c7f1ed123be   backend-net         bridge    local
ceee9c6a19c5   bridge              bridge    local
014ae96fb15b   host                host      local
440b7969d128   none                null      local
f09d464e8b7c   observability-net   bridge    local
059f20d37ac5   restricted-net      bridge    local
WARNING: This output is designed for human readability. For machine-readable output, please use --format.
IMAGE                          ID             DISK USAGE   CONTENT SIZE   EXTRA
monitoring-cron:v1.0.0         6b8431b9a5d7        249MB             0B   U
monitoring-python:v1.0.0       7739c57d5598        151MB             0B   U
monitoring-smtp-relay:latest   2cb43eac6aac        306MB             0B   U
nicolaka/netshoot:latest       2298d942ce5f        627MB             0B   U
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda1        48G   12G   36G  25% /
               total        used        free      shared  buff/cache   available
Mem:           1.9Gi       562Mi       682Mi        16Mi       895Mi       1.4Gi
Swap:             0B          0B          0B
=== BACKUPS (H2) ===
--- cron_postgres-backups
Unable to find image 'alpine:latest' locally
latest: Pulling from library/alpine
7b229517ed22: Pulling fs layer
7b229517ed22: Verifying Checksum
7b229517ed22: Download complete
7b229517ed22: Pull complete
Digest: sha256:be2656061b536c1883c4034790e21d0a09c5aaaf51968b89368a3c0371ea2c9a
Status: Downloaded newer image for alpine:latest
total 8
drwxr-xr-x    2 root     root          4096 Aug 17 17:20 .
drwxr-xr-x    1 root     root          4096 Oct 29 21:48 ..
--- postgres_postgres-backups
total 8
drwxr-xr-x    2 root     root          4096 Aug 17 17:18 .
drwxr-xr-x    1 root     root          4096 Oct 29 21:48 ..
=== CRON: errores y jobs ===
      2 time="2026-10-28T22:05:00Z" level=info msg="Traceback (most recent call last):" channel=stderr iteration=72 job.command="python3 scripts/backup_postgres.py" job.position=8 job.schedule="5 22 * * *"
      2 time="2026-10-27T22:05:00Z" level=info msg="Traceback (most recent call last):" channel=stderr iteration=71 job.command="python3 scripts/backup_postgres.py" job.position=8 job.schedule="5 22 * * *"
      1 time="2026-10-29T21:30:05Z" level=info msg="mnt-info: 2026-10-29T21:30:05.124288 - [ERROR] Error consultando Loki: HTTPConnectionPool(host='loki', port=3100): Max retries exceeded with url: /loki/api/v1/query_range?query=%7Bhoneypot%3D%22true%22%7D&start=1793307605114903040&end=1793309405114903040&limit=5000 (Caused by NameResolutionError(\"HTTPConnection(host='loki', port=3100): Failed to resolve 'loki' ([Errno -3] Temporary failure in name resolution)\"))" channel=stdout iteration=10532 job.command="python3 -m log_ingestor.log_honeypot_geolocation" job.position=6 job.schedule="*/10 * * * *"
      1 time="2026-10-29T21:30:05Z" level=info msg="mnt-info: 2026-10-29T21:30:05.114677 - [WARN] .env no encontrado en ops/services/smtp_relay/.env; usando variables de entorno actuales" channel=stdout iteration=10532 job.command="python3 -m log_ingestor.log_honeypot_geolocation" job.position=6 job.schedule="*/10 * * * *"
      1 time="2026-10-29T21:30:04Z" level=info msg="mnt-info: 2026-10-29T21:30:04.655176 - [ERROR] No se pudo establecer conexión a la base de datos." channel=stdout iteration=10532 job.command="python3 -m log_ingestor.log_ip_geolocation" job.position=5 job.schedule="*/10 * * * *"
      1 time="2026-10-29T21:30:04Z" level=info msg="mnt-info: 2026-10-29T21:30:04.655111 - [ERROR] Error conectando a la base de datos: connection to server at \"monitoring-postgres\" (172.18.0.2), port 5432 failed: fe_sendauth: no password supplied" channel=stdout iteration=10532 job.command="python3 -m log_ingestor.log_ip_geolocation" job.position=5 job.schedule="*/10 * * * *"
      1 time="2026-10-29T21:30:04Z" level=info msg="mnt-info: 2026-10-29T21:30:04.600219 - [WARN] Ingestión desactivada en el host. Establece ALLOW_HOST_LOGS=true para activarla (no recomendado)." channel=stdout iteration=10532 job.command="python3 -m log_ingestor.log_ingest_batch" job.position=2 job.schedule="*/10 * * * *"
      1 time="2026-10-29T21:30:04Z" level=info msg="mnt-info: 2026-10-29T21:30:04.599612 - [WARN] Ingestión desactivada en el host. Establece ALLOW_HOST_LOGS=true para activarla (no recomendado)." channel=stdout iteration=10532 job.command="python3 -m log_ingestor.log_fail2ban_batch" job.position=3 job.schedule="*/10 * * * *"
      1 time="2026-10-29T21:30:04Z" level=info msg="mnt-info: 2026-10-29T21:30:04.599446 - [WARN] .env no encontrado en ops/services/smtp_relay/.env; usando variables de entorno actuales" channel=stdout iteration=10532 job.command="python3 -m log_ingestor.log_fail2ban_batch" job.position=3 job.schedule="*/10 * * * *"
      1 time="2026-10-29T21:30:04Z" level=info msg="mnt-info: 2026-10-29T21:30:04.594790 - [WARN] .env no encontrado en ops/services/smtp_relay/.env; usando variables de entorno actuales" channel=stdout iteration=10532 job.command="python3 -m log_ingestor.log_ingest_batch" job.position=2 job.schedule="*/10 * * * *"
      1 time="2026-10-29T21:30:04Z" level=info msg="mnt-info: 2026-10-29T21:30:04.541461 - [WARN] Ingestión desactivada en el host. Establece ALLOW_HOST_LOGS=true para activarla (no recomendado)." channel=stdout iteration=10532 job.command="python3 -m log_ingestor.log_kern_batch" job.position=4 job.schedule="*/10 * * * *"
      1 time="2026-10-29T21:30:04Z" level=info msg="mnt-info: 2026-10-29T21:30:04.541316 - [WARN] .env no encontrado en ops/services/smtp_relay/.env; usando variables de entorno actuales" channel=stdout iteration=10532 job.command="python3 -m log_ingestor.log_kern_batch" job.position=4 job.schedule="*/10 * * * *"
      1 time="2026-10-29T21:30:04Z" level=info msg="mnt-info: 2026-10-29T21:30:04.407783 - [WARN] .env no encontrado en ops/services/smtp_relay/.env; usando variables de entorno actuales" channel=stdout iteration=10532 job.command="python3 -m log_ingestor.log_ip_geolocation" job.position=5 job.schedule="*/10 * * * *"
      1 time="2026-10-29T21:20:05Z" level=info msg="mnt-info: 2026-10-29T21:20:05.185905 - [ERROR] Error consultando Loki: HTTPConnectionPool(host='loki', port=3100): Max retries exceeded with url: /loki/api/v1/query_range?query=%7Bhoneypot%3D%22true%22%7D&start=1793307005167192832&end=1793308805167192832&limit=5000 (Caused by NameResolutionError(\"HTTPConnection(host='loki', port=3100): Failed to resolve 'loki' ([Errno -3] Temporary failure in name resolution)\"))" channel=stdout iteration=10531 job.command="python3 -m log_ingestor.log_honeypot_geolocation" job.position=6 job.schedule="*/10 * * * *"
      1 time="2026-10-29T21:20:05Z" level=info msg="mnt-info: 2026-10-29T21:20:05.164980 - [WARN] .env no encontrado en ops/services/smtp_relay/.env; usando variables de entorno actuales" channel=stdout iteration=10531 job.command="python3 -m log_ingestor.log_honeypot_geolocation" job.position=6 job.schedule="*/10 * * * *"
      1 time="2026-10-29T21:20:04Z" level=info msg="mnt-info: 2026-10-29T21:20:04.676213 - [ERROR] No se pudo establecer conexión a la base de datos." channel=stdout iteration=10531 job.command="python3 -m log_ingestor.log_ip_geolocation" job.position=5 job.schedule="*/10 * * * *"
      1 time="2026-10-29T21:20:04Z" level=info msg="mnt-info: 2026-10-29T21:20:04.676159 - [ERROR] Error conectando a la base de datos: connection to server at \"monitoring-postgres\" (172.18.0.2), port 5432 failed: fe_sendauth: no password supplied" channel=stdout iteration=10531 job.command="python3 -m log_ingestor.log_ip_geolocation" job.position=5 job.schedule="*/10 * * * *"
      1 time="2026-10-29T21:20:04Z" level=info msg="mnt-info: 2026-10-29T21:20:04.590660 - [WARN] Ingestión desactivada en el host. Establece ALLOW_HOST_LOGS=true para activarla (no recomendado)." channel=stdout iteration=10531 job.command="python3 -m log_ingestor.log_ingest_batch" job.position=2 job.schedule="*/10 * * * *"
      1 time="2026-10-29T21:20:04Z" level=info msg="mnt-info: 2026-10-29T21:20:04.590517 - [WARN] .env no encontrado en ops/services/smtp_relay/.env; usando variables de entorno actuales" channel=stdout iteration=10531 job.command="python3 -m log_ingestor.log_ingest_batch" job.position=2 job.schedule="*/10 * * * *"
      1 time="2026-10-29T21:20:04Z" level=info msg="mnt-info: 2026-10-29T21:20:04.564437 - [WARN] Ingestión desactivada en el host. Establece ALLOW_HOST_LOGS=true para activarla (no recomendado)." channel=stdout iteration=10531 job.command="python3 -m log_ingestor.log_kern_batch" job.position=4 job.schedule="*/10 * * * *"
      1 time="2026-10-29T21:20:04Z" level=info msg="mnt-info: 2026-10-29T21:20:04.561268 - [WARN] Ingestión desactivada en el host. Establece ALLOW_HOST_LOGS=true para activarla (no recomendado)." channel=stdout iteration=10531 job.command="python3 -m log_ingestor.log_fail2ban_batch" job.position=3 job.schedule="*/10 * * * *"
      1 time="2026-10-29T21:20:04Z" level=info msg="mnt-info: 2026-10-29T21:20:04.561104 - [WARN] .env no encontrado en ops/services/smtp_relay/.env; usando variables de entorno actuales" channel=stdout iteration=10531 job.command="python3 -m log_ingestor.log_fail2ban_batch" job.position=3 job.schedule="*/10 * * * *"
      1 time="2026-10-29T21:20:04Z" level=info msg="mnt-info: 2026-10-29T21:20:04.558942 - [WARN] .env no encontrado en ops/services/smtp_relay/.env; usando variables de entorno actuales" channel=stdout iteration=10531 job.command="python3 -m log_ingestor.log_kern_batch" job.position=4 job.schedule="*/10 * * * *"
      1 time="2026-10-29T21:20:04Z" level=info msg="mnt-info: 2026-10-29T21:20:04.421579 - [WARN] .env no encontrado en ops/services/smtp_relay/.env; usando variables de entorno actuales" channel=stdout iteration=10531 job.command="python3 -m log_ingestor.log_ip_geolocation" job.position=5 job.schedule="*/10 * * * *"
      1 time="2026-10-29T21:10:05Z" level=info msg="mnt-info: 2026-10-29T21:10:05.247201 - [ERROR] Error consultando Loki: HTTPConnectionPool(host='loki', port=3100): Max retries exceeded with url: /loki/api/v1/query_range?query=%7Bhoneypot%3D%22true%22%7D&start=1793306405238043904&end=1793308205238043904&limit=5000 (Caused by NameResolutionError(\"HTTPConnection(host='loki', port=3100): Failed to resolve 'loki' ([Errno -3] Temporary failure in name resolution)\"))" channel=stdout iteration=10530 job.command="python3 -m log_ingestor.log_honeypot_geolocation" job.position=6 job.schedule="*/10 * * * *"
      1 time="2026-10-29T21:10:05Z" level=info msg="mnt-info: 2026-10-29T21:10:05.237912 - [WARN] .env no encontrado en ops/services/smtp_relay/.env; usando variables de entorno actuales" channel=stdout iteration=10530 job.command="python3 -m log_ingestor.log_honeypot_geolocation" job.position=6 job.schedule="*/10 * * * *"
      1 time="2026-10-29T21:10:04Z" level=info msg="mnt-info: 2026-10-29T21:10:04.933285 - [WARN] Ingestión desactivada en el host. Establece ALLOW_HOST_LOGS=true para activarla (no recomendado)." channel=stdout iteration=10530 job.command="python3 -m log_ingestor.log_ingest_batch" job.position=2 job.schedule="*/10 * * * *"
      1 time="2026-10-29T21:10:04Z" level=info msg="mnt-info: 2026-10-29T21:10:04.931714 - [WARN] .env no encontrado en ops/services/smtp_relay/.env; usando variables de entorno actuales" channel=stdout iteration=10530 job.command="python3 -m log_ingestor.log_ingest_batch" job.position=2 job.schedule="*/10 * * * *"
      1 time="2026-10-29T21:10:04Z" level=info msg="mnt-info: 2026-10-29T21:10:04.677218 - [WARN] Ingestión desactivada en el host. Establece ALLOW_HOST_LOGS=true para activarla (no recomendado)." channel=stdout iteration=10530 job.command="python3 -m log_ingestor.log_kern_batch" job.position=4 job.schedule="*/10 * * * *"
      1 time="2026-10-29T21:10:04Z" level=info msg="mnt-info: 2026-10-29T21:10:04.672786 - [WARN] .env no encontrado en ops/services/smtp_relay/.env; usando variables de entorno actuales" channel=stdout iteration=10530 job.command="python3 -m log_ingestor.log_kern_batch" job.position=4 job.schedule="*/10 * * * *"
      1 time="2026-10-29T21:10:04Z" level=info msg="mnt-info: 2026-10-29T21:10:04.640960 - [WARN] Ingestión desactivada en el host. Establece ALLOW_HOST_LOGS=true para activarla (no recomendado)." channel=stdout iteration=10530 job.command="python3 -m log_ingestor.log_fail2ban_batch" job.position=3 job.schedule="*/10 * * * *"
      1 time="2026-10-29T21:10:04Z" level=info msg="mnt-info: 2026-10-29T21:10:04.640734 - [WARN] .env no encontrado en ops/services/smtp_relay/.env; usando variables de entorno actuales" channel=stdout iteration=10530 job.command="python3 -m log_ingestor.log_fail2ban_batch" job.position=3 job.schedule="*/10 * * * *"
      1 time="2026-10-29T21:10:04Z" level=info msg="mnt-info: 2026-10-29T21:10:04.638144 - [ERROR] No se pudo establecer conexión a la base de datos." channel=stdout iteration=10530 job.command="python3 -m log_ingestor.log_ip_geolocation" job.position=5 job.schedule="*/10 * * * *"
      1 time="2026-10-29T21:10:04Z" level=info msg="mnt-info: 2026-10-29T21:10:04.638091 - [ERROR] Error conectando a la base de datos: connection to server at \"monitoring-postgres\" (172.18.0.2), port 5432 failed: fe_sendauth: no password supplied" channel=stdout iteration=10530 job.command="python3 -m log_ingestor.log_ip_geolocation" job.position=5 job.schedule="*/10 * * * *"
      1 time="2026-10-29T21:10:04Z" level=info msg="mnt-info: 2026-10-29T21:10:04.427656 - [WARN] .env no encontrado en ops/services/smtp_relay/.env; usando variables de entorno actuales" channel=stdout iteration=10530 job.command="python3 -m log_ingestor.log_ip_geolocation" job.position=5 job.schedule="*/10 * * * *"
      1 time="2026-10-29T21:00:05Z" level=info msg="mnt-info: 2026-10-29T21:00:05.777394 - [ERROR] Error consultando Loki: HTTPConnectionPool(host='loki', port=3100): Max retries exceeded with url: /loki/api/v1/query_range?query=%7Bhoneypot%3D%22true%22%7D&start=1793305805767457024&end=1793307605767457024&limit=5000 (Caused by NameResolutionError(\"HTTPConnection(host='loki', port=3100): Failed to resolve 'loki' ([Errno -3] Temporary failure in name resolution)\"))" channel=stdout iteration=10529 job.command="python3 -m log_ingestor.log_honeypot_geolocation" job.position=6 job.schedule="*/10 * * * *"
      1 time="2026-10-29T21:00:05Z" level=info msg="mnt-info: 2026-10-29T21:00:05.765995 - [WARN] .env no encontrado en ops/services/smtp_relay/.env; usando variables de entorno actuales" channel=stdout iteration=10529 job.command="python3 -m log_ingestor.log_honeypot_geolocation" job.position=6 job.schedule="*/10 * * * *"
      1 time="2026-10-29T21:00:05Z" level=info msg="mnt-info: 2026-10-29T21:00:05.129269 - [WARN] Ingestión desactivada en el host. Establece ALLOW_HOST_LOGS=true para activarla (no recomendado)." channel=stdout iteration=10529 job.command="python3 -m log_ingestor.log_fail2ban_batch" job.position=3 job.schedule="*/10 * * * *"
      1 time="2026-10-29T21:00:05Z" level=info msg="mnt-info: 2026-10-29T21:00:05.124973 - [WARN] .env no encontrado en ops/services/smtp_relay/.env; usando variables de entorno actuales" channel=stdout iteration=10529 job.command="python3 -m log_ingestor.log_fail2ban_batch" job.position=3 job.schedule="*/10 * * * *"
      1 time="2026-10-29T21:00:05Z" level=info msg="mnt-info: 2026-10-29T21:00:05.118151 - [ERROR] No se pudo establecer conexión a la base de datos." channel=stdout iteration=10529 job.command="python3 -m log_ingestor.log_ip_geolocation" job.position=5 job.schedule="*/10 * * * *"
time="2026-10-28T22:00:07Z" level=info msg="Traceback (most recent call last):" channel=stderr iteration=72 job.command="echo \"[CRON][docker_resources][START]\" && python3 -m resource_monitor.docker_resources" job.position=1 job.schedule="0 22 * * *"
time="2026-10-28T22:00:07Z" level=info msg="  File \"<frozen runpy>\", line 198, in _run_module_as_main" channel=stderr iteration=72 job.command="echo \"[CRON][docker_resources][START]\" && python3 -m resource_monitor.docker_resources" job.position=1 job.schedule="0 22 * * *"
time="2026-10-28T22:00:07Z" level=info msg="  File \"<frozen runpy>\", line 88, in _run_code" channel=stderr iteration=72 job.command="echo \"[CRON][docker_resources][START]\" && python3 -m resource_monitor.docker_resources" job.position=1 job.schedule="0 22 * * *"
time="2026-10-28T22:00:07Z" level=info msg="  File \"/opt/monitoring/src/resource_monitor/docker_resources.py\", line 173, in <module>" channel=stderr iteration=72 job.command="echo \"[CRON][docker_resources][START]\" && python3 -m resource_monitor.docker_resources" job.position=1 job.schedule="0 22 * * *"
time="2026-10-28T22:00:07Z" level=info msg="    main()" channel=stderr iteration=72 job.command="echo \"[CRON][docker_resources][START]\" && python3 -m resource_monitor.docker_resources" job.position=1 job.schedule="0 22 * * *"
time="2026-10-28T22:00:07Z" level=info msg="  File \"/opt/monitoring/src/resource_monitor/docker_resources.py\", line 119, in main" channel=stderr iteration=72 job.command="echo \"[CRON][docker_resources][START]\" && python3 -m resource_monitor.docker_resources" job.position=1 job.schedule="0 22 * * *"
time="2026-10-28T22:00:07Z" level=info msg="    stats = get_docker_stats()" channel=stderr iteration=72 job.command="echo \"[CRON][docker_resources][START]\" && python3 -m resource_monitor.docker_resources" job.position=1 job.schedule="0 22 * * *"
time="2026-10-28T22:00:07Z" level=info msg="            ^^^^^^^^^^^^^^^^^^" channel=stderr iteration=72 job.command="echo \"[CRON][docker_resources][START]\" && python3 -m resource_monitor.docker_resources" job.position=1 job.schedule="0 22 * * *"
time="2026-10-28T22:00:07Z" level=info msg="  File \"/opt/monitoring/src/resource_monitor/docker_resources.py\", line 19, in get_docker_stats" channel=stderr iteration=72 job.command="echo \"[CRON][docker_resources][START]\" && python3 -m resource_monitor.docker_resources" job.position=1 job.schedule="0 22 * * *"
time="2026-10-28T22:00:07Z" level=info msg="    result = subprocess.run(cmd, capture_output=True, text=True)" channel=stderr iteration=72 job.command="echo \"[CRON][docker_resources][START]\" && python3 -m resource_monitor.docker_resources" job.position=1 job.schedule="0 22 * * *"
time="2026-10-28T22:00:07Z" level=info msg="             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^" channel=stderr iteration=72 job.command="echo \"[CRON][docker_resources][START]\" && python3 -m resource_monitor.docker_resources" job.position=1 job.schedule="0 22 * * *"
time="2026-10-28T22:00:07Z" level=info msg="  File \"/usr/local/lib/python3.12/subprocess.py\", line 548, in run" channel=stderr iteration=72 job.command="echo \"[CRON][docker_resources][START]\" && python3 -m resource_monitor.docker_resources" job.position=1 job.schedule="0 22 * * *"
time="2026-10-28T22:00:07Z" level=info msg="    with Popen(*popenargs, **kwargs) as process:" channel=stderr iteration=72 job.command="echo \"[CRON][docker_resources][START]\" && python3 -m resource_monitor.docker_resources" job.position=1 job.schedule="0 22 * * *"
time="2026-10-28T22:00:07Z" level=info msg="         ^^^^^^^^^^^^^^^^^^^^^^^^^^^" channel=stderr iteration=72 job.command="echo \"[CRON][docker_resources][START]\" && python3 -m resource_monitor.docker_resources" job.position=1 job.schedule="0 22 * * *"
time="2026-10-28T22:00:07Z" level=info msg="  File \"/usr/local/lib/python3.12/subprocess.py\", line 1026, in __init__" channel=stderr iteration=72 job.command="echo \"[CRON][docker_resources][START]\" && python3 -m resource_monitor.docker_resources" job.position=1 job.schedule="0 22 * * *"
time="2026-10-28T22:00:07Z" level=info msg="    self._execute_child(args, executable, preexec_fn, close_fds," channel=stderr iteration=72 job.command="echo \"[CRON][docker_resources][START]\" && python3 -m resource_monitor.docker_resources" job.position=1 job.schedule="0 22 * * *"
time="2026-10-28T22:00:07Z" level=info msg="  File \"/usr/local/lib/python3.12/subprocess.py\", line 1955, in _execute_child" channel=stderr iteration=72 job.command="echo \"[CRON][docker_resources][START]\" && python3 -m resource_monitor.docker_resources" job.position=1 job.schedule="0 22 * * *"
time="2026-10-28T22:00:07Z" level=info msg="    raise child_exception_type(errno_num, err_msg, err_filename)" channel=stderr iteration=72 job.command="echo \"[CRON][docker_resources][START]\" && python3 -m resource_monitor.docker_resources" job.position=1 job.schedule="0 22 * * *"
time="2026-10-28T22:00:07Z" level=info msg="FileNotFoundError: [Errno 2] No such file or directory: 'docker'" channel=stderr iteration=72 job.command="echo \"[CRON][docker_resources][START]\" && python3 -m resource_monitor.docker_resources" job.position=1 job.schedule="0 22 * * *"
time="2026-10-28T22:00:07Z" level=error msg="error running command: exit status 1" iteration=72 job.command="echo \"[CRON][docker_resources][START]\" && python3 -m resource_monitor.docker_resources" job.position=1 job.schedule="0 22 * * *"
time="2026-10-28T22:05:00Z" level=info msg=starting iteration=72 job.command="python3 scripts/backup_postgres.py" job.position=8 job.schedule="5 22 * * *"
time="2026-10-28T22:05:00Z" level=info msg="mnt-info: 2026-10-28T22:05:00.725989 - [INFO] Iniciando backup de monitoring_db (destino: /backups/monitoring_db-202610282205.backup)..." channel=stdout iteration=72 job.command="python3 scripts/backup_postgres.py" job.position=8 job.schedule="5 22 * * *"
time="2026-10-28T22:05:00Z" level=info msg="pg_dump: error: could not open output file \"/backups/monitoring_db-202610282205.backup\": Permission denied" channel=stderr iteration=72 job.command="python3 scripts/backup_postgres.py" job.position=8 job.schedule="5 22 * * *"
time="2026-10-28T22:05:00Z" level=info msg="mnt-info: 2026-10-28T22:05:00.783065 - [ERROR] Error durante el backup de monitoring_db: Command '['pg_dump', '-h', 'monitoring-postgres', '-p', '5432', '-U', 'postgres', '-F', 'c', '-b', '-v', '-f', '/backups/monitoring_db-202610282205.backup', 'monitoring_db']' returned non-zero exit status 1." channel=stdout iteration=72 job.command="python3 scripts/backup_postgres.py" job.position=8 job.schedule="5 22 * * *"
time="2026-10-28T22:05:00Z" level=info msg="Traceback (most recent call last):" channel=stderr iteration=72 job.command="python3 scripts/backup_postgres.py" job.position=8 job.schedule="5 22 * * *"
time="2026-10-28T22:05:00Z" level=info msg="  File \"/opt/monitoring/scripts/backup_postgres.py\", line 73, in <module>" channel=stderr iteration=72 job.command="python3 scripts/backup_postgres.py" job.position=8 job.schedule="5 22 * * *"
time="2026-10-28T22:05:00Z" level=info msg="    subprocess.run(cmd, check=True, env=env)" channel=stderr iteration=72 job.command="python3 scripts/backup_postgres.py" job.position=8 job.schedule="5 22 * * *"
time="2026-10-28T22:05:00Z" level=info msg="  File \"/usr/local/lib/python3.12/subprocess.py\", line 571, in run" channel=stderr iteration=72 job.command="python3 scripts/backup_postgres.py" job.position=8 job.schedule="5 22 * * *"
time="2026-10-28T22:05:00Z" level=info msg="    raise CalledProcessError(retcode, process.args," channel=stderr iteration=72 job.command="python3 scripts/backup_postgres.py" job.position=8 job.schedule="5 22 * * *"
time="2026-10-28T22:05:00Z" level=info msg="subprocess.CalledProcessError: Command '['pg_dump', '-h', 'monitoring-postgres', '-p', '5432', '-U', 'postgres', '-F', 'c', '-b', '-v', '-f', '/backups/monitoring_db-202610282205.backup', 'monitoring_db']' returned non-zero exit status 1." channel=stderr iteration=72 job.command="python3 scripts/backup_postgres.py" job.position=8 job.schedule="5 22 * * *"
time="2026-10-28T22:05:00Z" level=info channel=stderr iteration=72 job.command="python3 scripts/backup_postgres.py" job.position=8 job.schedule="5 22 * * *"
time="2026-10-28T22:05:00Z" level=info msg="During handling of the above exception, another exception occurred:" channel=stderr iteration=72 job.command="python3 scripts/backup_postgres.py" job.position=8 job.schedule="5 22 * * *"
time="2026-10-28T22:05:00Z" level=info channel=stderr iteration=72 job.command="python3 scripts/backup_postgres.py" job.position=8 job.schedule="5 22 * * *"
time="2026-10-28T22:05:00Z" level=info msg="Traceback (most recent call last):" channel=stderr iteration=72 job.command="python3 scripts/backup_postgres.py" job.position=8 job.schedule="5 22 * * *"
time="2026-10-28T22:05:00Z" level=info msg="  File \"/opt/monitoring/scripts/backup_postgres.py\", line 86, in <module>" channel=stderr iteration=72 job.command="python3 scripts/backup_postgres.py" job.position=8 job.schedule="5 22 * * *"
time="2026-10-28T22:05:00Z" level=info msg="    send_email(" channel=stderr iteration=72 job.command="python3 scripts/backup_postgres.py" job.position=8 job.schedule="5 22 * * *"
time="2026-10-28T22:05:00Z" level=info msg="  File \"/opt/monitoring/src/monitoring/common/config.py\", line 266, in send_email" channel=stderr iteration=72 job.command="python3 scripts/backup_postgres.py" job.position=8 job.schedule="5 22 * * *"
time="2026-10-28T22:05:00Z" level=info msg="    raise ValueError(\"No se ha definido destinatario de correo (email_to)\")" channel=stderr iteration=72 job.command="python3 scripts/backup_postgres.py" job.position=8 job.schedule="5 22 * * *"
time="2026-10-28T22:05:00Z" level=info msg="ValueError: No se ha definido destinatario de correo (email_to)" channel=stderr iteration=72 job.command="python3 scripts/backup_postgres.py" job.position=8 job.schedule="5 22 * * *"
time="2026-10-28T22:05:00Z" level=error msg="error running command: exit status 1" iteration=72 job.command="python3 scripts/backup_postgres.py" job.position=8 job.schedule="5 22 * * *"
=== BBDD ===
                                   List of databases
     Name      |  Owner   | Encoding |  Collate   |   Ctype    |   Access privileges
---------------+----------+----------+------------+------------+-----------------------
 monitoring_db | postgres | UTF8     | en_US.utf8 | en_US.utf8 |
 postgres      | postgres | UTF8     | en_US.utf8 | en_US.utf8 |
 template0     | postgres | UTF8     | en_US.utf8 | en_US.utf8 | =c/postgres          +
               |          |          |            |            | postgres=CTc/postgres
 template1     | postgres | UTF8     | en_US.utf8 | en_US.utf8 | =c/postgres          +
               |          |          |            |            | postgres=CTc/postgres
(4 rows)

Did not find any relations.
=== LOKI: qué está ingiriendo realmente ===
ready

{"status":"success","data":["filename","honeypot","job","reason","service_name","stream"]}

{"status":"success","data":["auth_logs","container_logs","honeypot"]}

=== HEALTH ===
monitoring-cron: healthy restarts=0
promtail: healthy restarts=0
monitoring-smtp-relay: healthy restarts=0
monitoring-python: healthy restarts=0
grafana: healthy restarts=0
loki: healthy restarts=0
monitoring-postgres: healthy restarts=0
=== MAKE (no destructivos) ===

=== Diagnóstico del sistema ===

[1] Docker instalado:
Docker version 29.1.3, build 29.1.3-0ubuntu3~24.04.2

[2] Docker Compose:
Docker Compose version 2.37.1+ds1-0ubuntu2~24.04.1

[3] Contenedores activos:
NAMES                   STATUS                        PORTS
monitoring-cron         Up About a minute (healthy)
promtail                Up About a minute (healthy)
monitoring-smtp-relay   Up About a minute (healthy)   587/tcp
monitoring-python       Up About a minute (healthy)
grafana                 Up About a minute (healthy)   3000/tcp, 127.0.0.1:3001->3001/tcp
loki                    Up About a minute (healthy)   127.0.0.1:3100->3100/tcp
monitoring-postgres     Up About a minute (healthy)   5432/tcp

[4] Redes Docker para monitoring (comprobación):
backend-net: OK
observability-net: OK
restricted-net: OK

[5] Espacio en disco:
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda1        48G   12G   36G  25% /

[6] Uso Docker:
TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
Images          10        8         2.429GB   2.292GB (94%)
Containers      8         7         793MB     0B (0%)
Local Volumes   10        10        54.1MB    0B (0%)
Build Cache     56        0         305.3MB   14.39MB

[7] Volúmenes Docker:
DRIVER    VOLUME NAME
local     58bd72d1512c3ee57f3e601350db8b5eb859cbe528f231b5d0fa3aa7360178b1
local     60bbfd738c570db94ae39bf8fd048adf4e0c6d80bcadf9f4b72399a9ab54a142
local     738f76a891571af4650247a321db87d0cc2f3c65c425cf419d65968843a43532
local     cron_postgres-backups
local     observability_grafana-data
local     observability_loki-data
local     observability_promtail-data
local     postgres_postgres-backups
local     postgres_postgres-data
local     smtp_relay_smtp_relay_logs

[8] Redes Docker:

[9] Contenedores de la plataforma:
monitoring-cron
monitoring-smtp-relay
monitoring-python
monitoring-postgres

[10] Stacks disponibles:
postgres smtp_relay python cron observability

=== Fin diagnóstico ===


=== Ejecutando auditoría (estructura / ADR) ===
chmod +x ops/audit/audit_repo_host.sh
./ops/audit/audit_repo_host.sh
==========================================
AUDITORÍA SERVIDOR
Fecha: Thu Oct 29 21:48:43 UTC 2026
Host:  eob-260131
==========================================

------------------------------------------
A.- AUDITORÍA REPOSITORIO
------------------------------------------

A1 Git

[INFO] Verificando repositorio Git
[OK] Repositorio Git válido
[INFO] Rama actual: migracion
[INFO] Commit actual: 954164f423a3a8a38d84f3013f636ace3bc4050b
[WARN] Repositorio con cambios locales

A2 Estructura

[INFO] Verificando estructura del proyecto
[OK] Directorio presente: src
[OK] Directorio presente: ops/stacks
[OK] Directorio presente: ops/services
[OK] Directorio presente: scripts
[OK] Directorio presente: docs/decisiones

A3 docker compose

[INFO] Buscando docker-compose
[OK] docker-compose detectados
[INFO] Validando ops/stacks/cron/compose.yml
[OK] ops/stacks/cron/compose.yml válido
[INFO] Validando ops/stacks/python/compose.yml
[OK] ops/stacks/python/compose.yml válido
[INFO] Validando ops/stacks/observability/compose.yml
[OK] ops/stacks/observability/compose.yml válido
[INFO] Validando ops/services/smtp_relay/compose.yml
[OK] ops/services/smtp_relay/compose.yml válido
[INFO] Validando ops/services/postgres/compose.yml
[OK] ops/services/postgres/compose.yml válido

[INFO] Validando presencia de healthchecks según ops/runtime_containers.yml (host-side enforcement)
[OK] monitoring-python: healthcheck present for service monitoring-python in ops/stacks/python/compose.yml
[OK] monitoring-cron: healthcheck present for service monitoring-cron in ops/stacks/cron/compose.yml
[OK] monitoring-postgres: healthcheck present for service postgres in ops/services/postgres/compose.yml
[OK] smtp-relay: healthcheck present for service smtp-relay in ops/services/smtp_relay/compose.yml
[OK] promtail: healthcheck present for service promtail in ops/stacks/observability/compose.yml
[OK] loki: healthcheck present for service loki in ops/stacks/observability/compose.yml
[OK] grafana: healthcheck present for service grafana in ops/stacks/observability/compose.yml

A4 Puertos declarados

[INFO] Buscando puertos publicados en compose

A5 Cronfile

[WARN] Cronfile no encontrado
[OK] Stack cron declarado

A6 Ejecución Python

[INFO] Buscando ejecuciones Python
grep: ./CLAUDE.md: No such file or directory
grep: ./AI_ENTRYPOINT.md: No such file or directory
[WARN] Posible ejecución python incorrecta:
./ops/audit/audit_repo_host.sh:252:BAD=$(grep -R "python3 src/" -n . \
grep: ./CLAUDE.md: No such file or directory
grep: ./AI_ENTRYPOINT.md: No such file or directory
grep: ./ops/audit/__pycache__/compose_policy_checks.cpython-312.pyc: binary file matches
[OK] Uso de python3 -m detectado

A7 Docker socket

[INFO] Buscando uso de docker.sock
grep: ./CLAUDE.md: No such file or directory
grep: ./AI_ENTRYPOINT.md: No such file or directory
grep: ./ops/audit/__pycache__/compose_policy_checks.cpython-312.pyc: binary file matches
grep: ./ops/audit/__pycache__/runtime_governance_audit.cpython-312.pyc: binary file matches
[WARN] docker.sock montado en contenedor:
./README.md:382:- uso de docker.sock
./.github/workflows/ci.yml:293:      - name: Check docker.sock usage
./.github/workflows/ci.yml:295:          if grep -R "docker.sock" ops; then
./.github/workflows/ci.yml:296:            echo "⚠ docker.sock detectado (ver ADR-0008)"
./.github/workflows/ci.yml:298:            echo "✔ docker.sock no usado"
./ops/audit/audit_repo_host.sh:8:#     Es el auditor principal que ejecuta comprobaciones de estructura, Compose, docker.sock y reproducibilidad.
./ops/audit/audit_repo_host.sh:136:# - TOOLBOX_RUNTIME e INFRA_TRUSTED NO implican acceso a docker.sock.
./ops/audit/audit_repo_host.sh:142:# - eliminar dependencia implícita de docker.sock
./ops/audit/audit_repo_host.sh:202:#   docker/compose/docker.sock. Cualquier chequeo sobre docker/compose se
./ops/audit/audit_repo_host.sh:279:info "Buscando uso de docker.sock"
./ops/audit/audit_repo_host.sh:281:SOCK=$(grep -R "docker.sock" -n . || true)
./ops/audit/audit_repo_host.sh:284:    ok "docker.sock no usado"
./ops/audit/audit_repo_host.sh:286:    warn "docker.sock montado en contenedor:"
./ops/audit/audit_repo_host.sh:535:echo "C3 docker.sock"
./ops/audit/audit_repo_host.sh:539:info "Verificando montaje docker.sock (superficie de ataque)"
./ops/audit/audit_repo_host.sh:543:        SOCK_OUTPUT=$(jq -r '.docker_sock // [] | if (.|length)==0 then empty else .[] | "  - " + (.[0]) + ": " + (.[1]) end' "$STRUCTURED_FILE" || true)
./ops/audit/audit_repo_host.sh:545:            ok "docker.sock no montado en contenedores (estructura detectada)"
./ops/audit/audit_repo_host.sh:547:            warn "docker.sock detectado (structured):"
./ops/audit/audit_repo_host.sh:553:            SOCK_OUTPUT=$("$PARSER" "$STRUCTURED_FILE" docker_sock 2>/dev/null || true)
./ops/audit/audit_repo_host.sh:556:                ok "docker.sock no montado en contenedores (estructura detectada)"
./ops/audit/audit_repo_host.sh:560:                warn "docker.sock detectado (structured):"
./ops/audit/audit_repo_host.sh:568:    SOCK=$(grep -R "docker.sock" -n ops 2>/dev/null || true)
./ops/audit/audit_repo_host.sh:570:        ok "docker.sock no montado en contenedores"
./ops/audit/audit_repo_host.sh:572:        warn "docker.sock detectado:"
./ops/audit/runtime_governance_audit.py:173:    # docker.sock mounts
./ops/audit/runtime_governance_audit.py:176:        if "docker.sock" in src:
./ops/audit/runtime_governance_audit.py:177:            add_finding("docker_sock", "forbidden", f"Mounts docker.sock: {src}", {"mount_type": "socket", "source": src, "destination": m.get("Destination")})
./ops/audit/runtime_governance_audit.py:203:            # RW bind mounts: forbidden only for high-risk paths or docker.sock; otherwise warning
./ops/audit/runtime_governance_audit.py:205:                if is_high or "docker.sock" in src_norm:
./ops/audit/check_hostconfig.sh:178:        # docker.sock forbidden
./ops/audit/check_hostconfig.sh:181:        if echo "${src}" | grep -q "docker.sock"; then
./ops/audit/check_hostconfig.sh:182:          fail "${c} mounts docker.sock from host (${src})"
./ops/audit/compose_policy_checks.py:35:    contenedores proporcionan Docker/compose/docker.sock. Cualquier comprobación de
./ops/audit/compose_policy_checks.py:120:    # Verifica la accesibilidad de docker.sock intentando listar los contenedores
./ops/audit/compose_policy_checks.py:152:    - sin dependencia docker.sock
./ops/audit/compose_policy_checks.py:185:    - no requiere docker.sock
./ops/audit/compose_policy_checks.py:203:            "(fallback host-side sin docker.sock)"
./ops/audit/compose_policy_checks.py:231:def detect_docker_sock(compose: Dict[str, Any]) -> List[Tuple[str, str]]:
./ops/audit/compose_policy_checks.py:240:                if any("docker.sock" in part for part in parts):
./ops/audit/compose_policy_checks.py:245:                if isinstance(src, str) and "docker.sock" in src:
./ops/audit/compose_policy_checks.py:247:                elif isinstance(target, str) and "docker.sock" in target:
./ops/audit/compose_policy_checks.py:295:    sensitive_paths = ("/etc/passwd", "/etc/shadow", "/var/run/docker.sock", "/root", "/var/lib/docker")
./ops/audit/compose_policy_checks.py:409:    "docker_sock": "WARN",
./ops/audit/compose_policy_checks.py:439:    if selected is None or "docker_sock" in selected:
./ops/audit/compose_policy_checks.py:440:        ds = detect_docker_sock(compose)
./ops/audit/compose_policy_checks.py:441:        out["docker_sock"] = ds
./ops/audit/compose_policy_checks.py:472:    # docker.sock
./ops/audit/compose_policy_checks.py:473:    if not results.get("docker_sock"):
./ops/audit/compose_policy_checks.py:474:        ok("docker.sock no usado (estructura detectada)")
./ops/audit/compose_policy_checks.py:476:        warn("docker.sock montado en contenedor (structured):")
./ops/audit/compose_policy_checks.py:477:        for svc, v in results.get("docker_sock", []):
./ops/audit/compose_policy_checks.py:545:            ok("Acceso a docker.sock operativo")
./ops/audit/compose_policy_checks.py:547:            warn("Acceso a docker.sock NO operativo (el contenedor puede no tener acceso al control plane)")
./ops/audit/compose_policy_checks.py:590:    parser.add_argument("--check", dest="check", action="append", help="Ejecutar solo comprobaciónes específicas (ports,docker_sock,images,privileged,sensitive_mounts,cap_add,read_only_false)")
./ops/audit/compose_policy_checks.py:591:    parser.add_argument("--self-test", dest="self_test", action="store_true", help="Ejecutar autotest runtime (docker CLI/compose/compose config/docker.sock)")
./ops/audit/compose_policy_checks.py:616:        if rt.get("docker_sock"):
./ops/audit/compose_policy_checks.py:617:            ok("Acceso a docker.sock operativo")
./ops/audit/compose_policy_checks.py:619:            warn("Acceso a docker.sock NO operativo (el contenedor puede no tener acceso al control plane)")
./ops/audit/parse_compose_json.py:30:Keys supported: ports, docker_sock
./ops/stacks/cron/compose.yml:27:      # - /var/run/docker.sock:/var/run/docker.sock
./ops/stacks/python/compose.yml:26:      # - /var/run/docker.sock:/var/run/docker.sock
./.ua/knowledge-graph.json:1742:      "id": "function:ops/audit/compose_policy_checks.py:detect_docker_sock",
./.ua/knowledge-graph.json:1744:      "name": "detect_docker_sock",
./.ua/knowledge-graph.json:1746:      "summary": "Function detect_docker_sock in ops/audit/compose_policy_checks.py",
./.ua/knowledge-graph.json:2914:      "target": "function:ops/audit/compose_policy_checks.py:detect_docker_sock",
./Makefile:625:## - docker.sock indebido
./Makefile:688: # [3] docker.sock
./Makefile:689: @echo "[3] Verificando uso de docker.sock"
./Makefile:691: @if grep -R "docker.sock" ops/services 2>/dev/null; then \
./Makefile:692:         echo "[FAIL] docker.sock usado en micro-stacks"; \
./Makefile:695:         echo "[OK] docker.sock no usado en servicios"; \
./docs/arquitectura/.ua/knowledge-graph.json:1742:      "id": "function:ops/audit/compose_policy_checks.py:detect_docker_sock",
./docs/arquitectura/.ua/knowledge-graph.json:1744:      "name": "detect_docker_sock",
./docs/arquitectura/.ua/knowledge-graph.json:1746:      "summary": "Function detect_docker_sock in ops/audit/compose_policy_checks.py",
./docs/arquitectura/.ua/knowledge-graph.json:2914:      "target": "function:ops/audit/compose_policy_checks.py:detect_docker_sock",
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1670:[INFO] Buscando uso de docker.sock
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1674:[WARN] docker.sock montado en contenedor:
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1675:./README.md:382:- uso de docker.sock
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1676:./.github/workflows/ci.yml:293:      - name: Check docker.sock usage
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1677:./.github/workflows/ci.yml:295:          if grep -R "docker.sock" ops; then
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1678:./.github/workflows/ci.yml:296:            echo "⚠ docker.sock detectado (ver ADR-0008)"
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1679:./.github/workflows/ci.yml:298:            echo "✔ docker.sock no usado"
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1680:./ops/audit/audit_repo_host.sh:8:#     Es el auditor principal que ejecuta comprobaciones de estructura, Compose, docker.sock y reproducibilidad.
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1681:./ops/audit/audit_repo_host.sh:136:# - TOOLBOX_RUNTIME e INFRA_TRUSTED NO implican acceso a docker.sock.
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1682:./ops/audit/audit_repo_host.sh:142:# - eliminar dependencia implícita de docker.sock
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1683:./ops/audit/audit_repo_host.sh:202:#   docker/compose/docker.sock. Cualquier chequeo sobre docker/compose se
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1684:./ops/audit/audit_repo_host.sh:279:info "Buscando uso de docker.sock"
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1685:./ops/audit/audit_repo_host.sh:281:SOCK=$(grep -R "docker.sock" -n . || true)
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1686:./ops/audit/audit_repo_host.sh:284:    ok "docker.sock no usado"
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1687:./ops/audit/audit_repo_host.sh:286:    warn "docker.sock montado en contenedor:"
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1688:./ops/audit/audit_repo_host.sh:535:echo "C3 docker.sock"
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1689:./ops/audit/audit_repo_host.sh:539:info "Verificando montaje docker.sock (superficie de ataque)"
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1690:./ops/audit/audit_repo_host.sh:543:        SOCK_OUTPUT=$(jq -r '.docker_sock // [] | if (.|length)==0 then empty else .[] | "  - " + (.[0]) + ": " + (.[1]) end' "$STRUCTURED_FILE" || true)
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1691:./ops/audit/audit_repo_host.sh:545:            ok "docker.sock no montado en contenedores (estructura detectada)"
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1692:./ops/audit/audit_repo_host.sh:547:            warn "docker.sock detectado (structured):"
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1693:./ops/audit/audit_repo_host.sh:553:            SOCK_OUTPUT=$("$PARSER" "$STRUCTURED_FILE" docker_sock 2>/dev/null || true)
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1694:./ops/audit/audit_repo_host.sh:556:                ok "docker.sock no montado en contenedores (estructura detectada)"
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1695:./ops/audit/audit_repo_host.sh:560:                warn "docker.sock detectado (structured):"
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1696:./ops/audit/audit_repo_host.sh:568:    SOCK=$(grep -R "docker.sock" -n ops 2>/dev/null || true)
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1697:./ops/audit/audit_repo_host.sh:570:        ok "docker.sock no montado en contenedores"
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1698:./ops/audit/audit_repo_host.sh:572:        warn "docker.sock detectado:"
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1699:./ops/audit/runtime_governance_audit.py:173:    # docker.sock mounts
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1700:./ops/audit/runtime_governance_audit.py:176:        if "docker.sock" in src:
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1701:./ops/audit/runtime_governance_audit.py:177:            add_finding("docker_sock", "forbidden", f"Mounts docker.sock: {src}", {"mount_type": "socket", "source": src, "destination": m.get("Destination")})
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1702:./ops/audit/runtime_governance_audit.py:203:            # RW bind mounts: forbidden only for high-risk paths or docker.sock; otherwise warning
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1703:./ops/audit/runtime_governance_audit.py:205:                if is_high or "docker.sock" in src_norm:
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1704:./ops/audit/check_hostconfig.sh:178:        # docker.sock forbidden
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1705:./ops/audit/check_hostconfig.sh:181:        if echo "${src}" | grep -q "docker.sock"; then
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1706:./ops/audit/check_hostconfig.sh:182:          fail "${c} mounts docker.sock from host (${src})"
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1707:./ops/audit/compose_policy_checks.py:35:    contenedores proporcionan Docker/compose/docker.sock. Cualquier comprobación de
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1708:./ops/audit/compose_policy_checks.py:120:    # Verifica la accesibilidad de docker.sock intentando listar los contenedores
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1709:./ops/audit/compose_policy_checks.py:152:    - sin dependencia docker.sock
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1710:./ops/audit/compose_policy_checks.py:185:    - no requiere docker.sock
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1711:./ops/audit/compose_policy_checks.py:203:            "(fallback host-side sin docker.sock)"
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1712:./ops/audit/compose_policy_checks.py:231:def detect_docker_sock(compose: Dict[str, Any]) -> List[Tuple[str, str]]:
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1713:./ops/audit/compose_policy_checks.py:240:                if any("docker.sock" in part for part in parts):
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1714:./ops/audit/compose_policy_checks.py:245:                if isinstance(src, str) and "docker.sock" in src:
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1715:./ops/audit/compose_policy_checks.py:247:                elif isinstance(target, str) and "docker.sock" in target:
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1716:./ops/audit/compose_policy_checks.py:295:    sensitive_paths = ("/etc/passwd", "/etc/shadow", "/var/run/docker.sock", "/root", "/var/lib/docker")
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1717:./ops/audit/compose_policy_checks.py:409:    "docker_sock": "WARN",
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1718:./ops/audit/compose_policy_checks.py:439:    if selected is None or "docker_sock" in selected:
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1719:./ops/audit/compose_policy_checks.py:440:        ds = detect_docker_sock(compose)
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1720:./ops/audit/compose_policy_checks.py:441:        out["docker_sock"] = ds
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1721:./ops/audit/compose_policy_checks.py:472:    # docker.sock
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1722:./ops/audit/compose_policy_checks.py:473:    if not results.get("docker_sock"):
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1723:./ops/audit/compose_policy_checks.py:474:        ok("docker.sock no usado (estructura detectada)")
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1724:./ops/audit/compose_policy_checks.py:476:        warn("docker.sock montado en contenedor (structured):")
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1725:./ops/audit/compose_policy_checks.py:477:        for svc, v in results.get("docker_sock", []):
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1726:./ops/audit/compose_policy_checks.py:545:            ok("Acceso a docker.sock operativo")
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1727:./ops/audit/compose_policy_checks.py:547:            warn("Acceso a docker.sock NO operativo (el contenedor puede no tener acceso al control plane)")
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1728:./ops/audit/compose_policy_checks.py:590:    parser.add_argument("--check", dest="check", action="append", help="Ejecutar solo comprobaciónes específicas (ports,docker_sock,images,privileged,sensitive_mounts,cap_add,read_only_false)")
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1729:./ops/audit/compose_policy_checks.py:591:    parser.add_argument("--self-test", dest="self_test", action="store_true", help="Ejecutar autotest runtime (docker CLI/compose/compose config/docker.sock)")
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1730:./ops/audit/compose_policy_checks.py:616:        if rt.get("docker_sock"):
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1731:./ops/audit/compose_policy_checks.py:617:            ok("Acceso a docker.sock operativo")
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1732:./ops/audit/compose_policy_checks.py:619:            warn("Acceso a docker.sock NO operativo (el contenedor puede no tener acceso al control plane)")
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1733:./ops/audit/parse_compose_json.py:30:Keys supported: ports, docker_sock
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1734:./ops/stacks/cron/compose.yml:27:      # - /var/run/docker.sock:/var/run/docker.sock
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1735:./ops/stacks/python/compose.yml:26:      # - /var/run/docker.sock:/var/run/docker.sock
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1736:./.ua/knowledge-graph.json:1742:      "id": "function:ops/audit/compose_policy_checks.py:detect_docker_sock",
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1737:./.ua/knowledge-graph.json:1744:      "name": "detect_docker_sock",
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1738:./.ua/knowledge-graph.json:1746:      "summary": "Function detect_docker_sock in ops/audit/compose_policy_checks.py",
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1739:./.ua/knowledge-graph.json:2914:      "target": "function:ops/audit/compose_policy_checks.py:detect_docker_sock",
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1740:./Makefile:625:## - docker.sock indebido
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1741:./Makefile:688: # [3] docker.sock
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1742:./Makefile:689: @echo "[3] Verificando uso de docker.sock"
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1743:./Makefile:691: @if grep -R "docker.sock" ops/services 2>/dev/null; then \
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1744:./Makefile:692:         echo "[FAIL] docker.sock usado en micro-stacks"; \
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1745:./Makefile:695:         echo "[OK] docker.sock no usado en servicios"; \
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1746:./docs/arquitectura/.ua/knowledge-graph.json:1742:      "id": "function:ops/audit/compose_policy_checks.py:detect_docker_sock",
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1747:./docs/arquitectura/.ua/knowledge-graph.json:1744:      "name": "detect_docker_sock",
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1748:./docs/arquitectura/.ua/knowledge-graph.json:1746:      "summary": "Function detect_docker_sock in ops/audit/compose_policy_checks.py",
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1749:./docs/arquitectura/.ua/knowledge-graph.json:2914:      "target": "function:ops/audit/compose_policy_checks.py:detect_docker_sock",
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1750:./docs/Project_Definition/00_PROJECT_VISION_DigitalOcean_Definicion_Proyecto.txt:302:Estas excepciones se ejecutan de manera nativa en el host para garantizar el acceso al control-plane de Docker sin comprometer la seguridad de los contenedores ni requerir la exposición de docker.sock. Ninguna de estas excepciones del host debe contener lógica funcional de negocio.
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1751:./docs/Project_Definition/00_PROJECT_VISION_DigitalOcean_Definicion_Proyecto.txt:398:    - Mínimo Privilegio: Comprueba en los bloques de servicios que las configuraciones no expongan el socket de Docker (docker.sock) de manera innecesaria ni activen flags de privilegios peligrosos (privileged=true).
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1752:./docs/Project_Definition/00_PROJECT_VISION_DigitalOcean_Definicion_Proyecto.txt:531:    - Auditoría automática de seguridad runtime (puertos, docker.sock, uso de latest)
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1753:./docs/Project_Implementation/Servidor_DigitalOcean_Implementacion.txt:1014:Algunos contenedores de infraestructura requieren acceso al socket Docker del host (/var/run/docker.sock). Este acceso debe limitarse exclusivamente a infra-stacks y considerarse equivalente a privilegios administrativos sobre el host Docker.
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1754:./docs/Project_Implementation/Servidor_DigitalOcean_Implementacion.txt:1238:    - Prohibición de uso de docker.sock en micro-stacks
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1755:./docs/Project_Implementation/Servidor_DigitalOcean_Implementacion.txt:1242:    - Detección de uso de docker.sock
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1756:./docs/Project_Implementation/Servidor_DigitalOcean_Implementacion.txt:1346:    1. Bloqueo Activo Punitivo: Cualquier hallazgo crítico calificado como prohibido ('forbidden') —tales como la presencia de 'privileged=true', 'network_mode=host', montajes mutables en rutas sensibles o fugas del plano de control mediante 'docker.sock'— provocará de forma determinista la caída del pipeline y el fallo del despliegue.
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1757:./docs/Project_Implementation/Servidor_DigitalOcean_Implementacion.txt:1508:    - uso controlado de docker.sock (solo infra-stacks según ADR)
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1758:./docs/decisiones/ADR-0031-gobernanza_runtime_y_clasificacion_dependencias_host.md:41:        No existe docker.sock montado en ningún contenedor.
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1759:./docs/decisiones/ADR-0031-gobernanza_runtime_y_clasificacion_dependencias_host.md:160:    - docker.sock
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1760:./docs/decisiones/ADR-0031-gobernanza_runtime_y_clasificacion_dependencias_host.md:189:    - docker.sock
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1761:./docs/decisiones/ADR-0031-gobernanza_runtime_y_clasificacion_dependencias_host.md:240:            sin docker.sock
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1762:./docs/decisiones/ADR-0031-gobernanza_runtime_y_clasificacion_dependencias_host.md:271:            sin docker.sock
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1763:./docs/decisiones/ADR-0031-gobernanza_runtime_y_clasificacion_dependencias_host.md:315:            docker.sock
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1764:./docs/decisiones/ADR-0011-python_runtime_execution_model.md:191:- no exista acceso a docker.sock
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1765:./docs/decisiones/ADR-0018-docker_security_runtime_and_resilience_requirements.md:23:- Uso controlado de privilegios (docker.sock, capabilities, usuario)
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1766:./docs/decisiones/ADR-0018-docker_security_runtime_and_resilience_requirements.md:91:## 1.6 Uso de docker.sock
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1767:./docs/decisiones/ADR-0018-docker_security_runtime_and_resilience_requirements.md:94:- El uso de docker.sock debe considerarse privilegio equivalente a root host
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1768:./docs/decisiones/ADR-0018-docker_security_runtime_and_resilience_requirements.md:102:El acceso a docker.sock:
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1769:./docs/decisiones/ADR-0018-docker_security_runtime_and_resilience_requirements.md:119:- grep -R "docker.sock" ops/
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1770:./docs/decisiones/ADR-0018-docker_security_runtime_and_resilience_requirements.md:145:- uso de docker.sock
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1771:./docs/decisiones/ADR-0018-docker_security_runtime_and_resilience_requirements.md:267:- Uso indebido de docker.sock
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1772:./docs/decisiones/ADR-0020-Container_Execution_Model_Privilege_Strategy.md:67:- no monta docker.sock
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1773:./docs/decisiones/ADR-0030-auditoría_runtime_HostConfig_y_visibilidad_privilegios.md:19:- uso de docker.sock
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1774:./docs/decisiones/ADR-0030-auditoría_runtime_HostConfig_y_visibilidad_privilegios.md:66:- NO dependerá de docker.sock dentro de contenedores
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1775:./docs/decisiones/ADR-0024-Container_Privilege_Exception_Policy.md:68:- docker.sock
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1776:./docs/decisiones/ADR-0027-tipologia_contenedores_politica_healthchecks.md:87:- acceso a docker.sock desde contenedores
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1777:./docs/decisiones/ADR-0027-tipologia_contenedores_politica_healthchecks.md:95:- docker.sock
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1778:./docs/decisiones/ADR-0027-tipologia_contenedores_politica_healthchecks.md:101:- no deben montar docker.sock salvo excepción ADR explícita
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1779:./docs/decisiones/ADR-0029-structured_compose_policy_audit.md:77:- no expone docker.sock
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1780:./docs/decisiones/ADR-0029-structured_compose_policy_audit.md:115:- acceso operativo a docker.sock
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1781:./docs/decisiones/ADR-0029-structured_compose_policy_audit.md:214:- acceso docker.sock
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1782:./docs/decisiones/ADR-0029-structured_compose_policy_audit.md:234:- docker.sock
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1783:./docs/decisiones/ADR-0029-structured_compose_policy_audit.md:261:- acceso opcional docker.sock
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1784:./docs/decisiones/ADR-0029-structured_compose_policy_audit.md:336:- eliminación de dependencia de docker.sock dentro de runtimes funcionales
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1785:./docs/decisiones/ADR-0029-structured_compose_policy_audit.md:360:- acceso docker.sock
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1786:./docs/decisiones/ADR-0029-structured_compose_policy_audit.md:368:    docker.sock
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1787:./docs/decisiones/ADR-0029-structured_compose_policy_audit.md:371:- docker.sock
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1788:./docs/decisiones/ADR-0029-structured_compose_policy_audit.md:398:- no montar docker.sock salvo excepción explícitamente documentada
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1789:./docs/decisiones/ADR-0029-structured_compose_policy_audit.md:402:- uso de docker.sock auditado automáticamente
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1790:./docs/decisiones/ADR-0029-structured_compose_policy_audit.md:448:- eliminación de dependencia estructural de docker.sock en monitoring-python
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1791:./docs/decisiones/ADR-0008-servicios_micro-stack _vs_infra-stack.md:60:- acceder a /var/run/docker.sock únicamente bajo justificación explícita
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1792:./docs/decisiones/ADR-0008-servicios_micro-stack _vs_infra-stack.md:75:  - uso de docker.sock (si aplica)
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1793:./docs/decisiones/ADR-0008-servicios_micro-stack _vs_infra-stack.md:98:3️⃣ Uso de docker.sock
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1794:./docs/decisiones/ADR-0008-servicios_micro-stack _vs_infra-stack.md:100:  /var/run/docker.sock:/var/run/docker.sock
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1795:./docs/decisiones/ADR-0008-servicios_micro-stack _vs_infra-stack.md:105:El acceso a docker.sock concede privilegios equivalentes a root sobre el host Docker, permitiendo:
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1796:./docs/decisiones/ADR-0008-servicios_micro-stack _vs_infra-stack.md:130:- Toda operación que use docker.sock debe quedar registrada en logs
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1797:./docs/decisiones/ADR-0008-servicios_micro-stack _vs_infra-stack.md:134:  - uso de docker.sock
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1798:./docs/decisiones/ADR-0008-servicios_micro-stack _vs_infra-stack.md:150:- Crecimiento de infra-stacks con privilegios elevados (docker.sock, mounts host)
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1799:./docs/decisiones/ADR-0008-servicios_micro-stack _vs_infra-stack.md:151:- Compromiso del host si un contenedor con docker.sock es vulnerado
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1950:C3 docker.sock
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1952:[INFO] Verificando montaje docker.sock (superficie de ataque)
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1953:[OK] docker.sock no montado en contenedores (estructura detectada)
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:1986:[WARN] Usando parseo estático de archivos Compose (fallback host-side sin docker.sock)
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:2111:  "docker_sock": [],
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:2140:# [3] docker.sock
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:2141:[3] Verificando uso de docker.sock
./docs/Project_Definition/Servidor_DigitalOcean_StatusQuo_260817:2142:[OK] docker.sock no usado en servicios
./docs/Project_Definition/00_PROJECT_VISION_DigitalOcean_Definicion_Proyecto.txt:302:Estas excepciones se ejecutan de manera nativa en el host para garantizar el acceso al control-plane de Docker sin comprometer la seguridad de los contenedores ni requerir la exposición de docker.sock. Ninguna de estas excepciones del host debe contener lógica funcional de negocio.
./docs/Project_Definition/00_PROJECT_VISION_DigitalOcean_Definicion_Proyecto.txt:398:    - Mínimo Privilegio: Comprueba en los bloques de servicios que las configuraciones no expongan el socket de Docker (docker.sock) de manera innecesaria ni activen flags de privilegios peligrosos (privileged=true).
./docs/Project_Definition/00_PROJECT_VISION_DigitalOcean_Definicion_Proyecto.txt:531:    - Auditoría automática de seguridad runtime (puertos, docker.sock, uso de latest)
./docs/Project_Implementation/Servidor_DigitalOcean_Implementacion.txt:1014:Algunos contenedores de infraestructura requieren acceso al socket Docker del host (/var/run/docker.sock). Este acceso debe limitarse exclusivamente a infra-stacks y considerarse equivalente a privilegios administrativos sobre el host Docker.
./docs/Project_Implementation/Servidor_DigitalOcean_Implementacion.txt:1238:    - Prohibición de uso de docker.sock en micro-stacks
./docs/Project_Implementation/Servidor_DigitalOcean_Implementacion.txt:1242:    - Detección de uso de docker.sock
./docs/Project_Implementation/Servidor_DigitalOcean_Implementacion.txt:1356:    1. Bloqueo Activo Punitivo: Cualquier hallazgo crítico calificado como prohibido ('forbidden') —tales como la presencia de 'privileged=true', 'network_mode=host', montajes mutables en rutas sensibles o fugas del plano de control mediante 'docker.sock'— provocará de forma determinista la caída del pipeline y el fallo del despliegue.
./docs/Project_Implementation/Servidor_DigitalOcean_Implementacion.txt:1518:    - uso controlado de docker.sock (solo infra-stacks según ADR)
./docs/decisiones/ADR-0031-gobernanza_runtime_y_clasificacion_dependencias_host.md:41:        No existe docker.sock montado en ningún contenedor.
./docs/decisiones/ADR-0031-gobernanza_runtime_y_clasificacion_dependencias_host.md:160:    - docker.sock
./docs/decisiones/ADR-0031-gobernanza_runtime_y_clasificacion_dependencias_host.md:189:    - docker.sock
./docs/decisiones/ADR-0031-gobernanza_runtime_y_clasificacion_dependencias_host.md:240:            sin docker.sock
./docs/decisiones/ADR-0031-gobernanza_runtime_y_clasificacion_dependencias_host.md:271:            sin docker.sock
./docs/decisiones/ADR-0031-gobernanza_runtime_y_clasificacion_dependencias_host.md:315:            docker.sock
./docs/decisiones/ADR-0011-python_runtime_execution_model.md:191:- no exista acceso a docker.sock
./docs/decisiones/ADR-0018-docker_security_runtime_and_resilience_requirements.md:23:- Uso controlado de privilegios (docker.sock, capabilities, usuario)
./docs/decisiones/ADR-0018-docker_security_runtime_and_resilience_requirements.md:91:## 1.6 Uso de docker.sock
./docs/decisiones/ADR-0018-docker_security_runtime_and_resilience_requirements.md:94:- El uso de docker.sock debe considerarse privilegio equivalente a root host
./docs/decisiones/ADR-0018-docker_security_runtime_and_resilience_requirements.md:102:El acceso a docker.sock:
./docs/decisiones/ADR-0018-docker_security_runtime_and_resilience_requirements.md:119:- grep -R "docker.sock" ops/
./docs/decisiones/ADR-0018-docker_security_runtime_and_resilience_requirements.md:145:- uso de docker.sock
./docs/decisiones/ADR-0018-docker_security_runtime_and_resilience_requirements.md:267:- Uso indebido de docker.sock
./docs/decisiones/ADR-0020-Container_Execution_Model_Privilege_Strategy.md:67:- no monta docker.sock
./docs/decisiones/ADR-0030-auditoría_runtime_HostConfig_y_visibilidad_privilegios.md:19:- uso de docker.sock
./docs/decisiones/ADR-0030-auditoría_runtime_HostConfig_y_visibilidad_privilegios.md:66:- NO dependerá de docker.sock dentro de contenedores
./docs/decisiones/ADR-0024-Container_Privilege_Exception_Policy.md:68:- docker.sock
./docs/decisiones/ADR-0027-tipologia_contenedores_politica_healthchecks.md:87:- acceso a docker.sock desde contenedores
./docs/decisiones/ADR-0027-tipologia_contenedores_politica_healthchecks.md:95:- docker.sock
./docs/decisiones/ADR-0027-tipologia_contenedores_politica_healthchecks.md:101:- no deben montar docker.sock salvo excepción ADR explícita
./docs/decisiones/ADR-0029-structured_compose_policy_audit.md:77:- no expone docker.sock
./docs/decisiones/ADR-0029-structured_compose_policy_audit.md:115:- acceso operativo a docker.sock
./docs/decisiones/ADR-0029-structured_compose_policy_audit.md:214:- acceso docker.sock
./docs/decisiones/ADR-0029-structured_compose_policy_audit.md:234:- docker.sock
./docs/decisiones/ADR-0029-structured_compose_policy_audit.md:261:- acceso opcional docker.sock
./docs/decisiones/ADR-0029-structured_compose_policy_audit.md:336:- eliminación de dependencia de docker.sock dentro de runtimes funcionales
./docs/decisiones/ADR-0029-structured_compose_policy_audit.md:360:- acceso docker.sock
./docs/decisiones/ADR-0029-structured_compose_policy_audit.md:368:    docker.sock
./docs/decisiones/ADR-0029-structured_compose_policy_audit.md:371:- docker.sock
./docs/decisiones/ADR-0029-structured_compose_policy_audit.md:398:- no montar docker.sock salvo excepción explícitamente documentada
./docs/decisiones/ADR-0029-structured_compose_policy_audit.md:402:- uso de docker.sock auditado automáticamente
./docs/decisiones/ADR-0029-structured_compose_policy_audit.md:448:- eliminación de dependencia estructural de docker.sock en monitoring-python
./docs/decisiones/ADR-0008-servicios_micro-stack _vs_infra-stack.md:60:- acceder a /var/run/docker.sock únicamente bajo justificación explícita
./docs/decisiones/ADR-0008-servicios_micro-stack _vs_infra-stack.md:75:  - uso de docker.sock (si aplica)
./docs/decisiones/ADR-0008-servicios_micro-stack _vs_infra-stack.md:98:3️⃣ Uso de docker.sock
./docs/decisiones/ADR-0008-servicios_micro-stack _vs_infra-stack.md:100:  /var/run/docker.sock:/var/run/docker.sock
./docs/decisiones/ADR-0008-servicios_micro-stack _vs_infra-stack.md:105:El acceso a docker.sock concede privilegios equivalentes a root sobre el host Docker, permitiendo:
./docs/decisiones/ADR-0008-servicios_micro-stack _vs_infra-stack.md:130:- Toda operación que use docker.sock debe quedar registrada en logs
./docs/decisiones/ADR-0008-servicios_micro-stack _vs_infra-stack.md:134:  - uso de docker.sock
./docs/decisiones/ADR-0008-servicios_micro-stack _vs_infra-stack.md:150:- Crecimiento de infra-stacks con privilegios elevados (docker.sock, mounts host)
./docs/decisiones/ADR-0008-servicios_micro-stack _vs_infra-stack.md:151:- Compromiso del host si un contenedor con docker.sock es vulnerado

[INFO] Resumiendo HostConfig/runtime (solo visibilidad, no modifica nada)
[WARN] monitoring-python no está en ejecución; omitiendo inspección host-side
[WARN] monitoring-cron no está en ejecución; omitiendo inspección host-side
[WARN] monitoring-postgres no está en ejecución; omitiendo inspección host-side
[WARN] smtp-relay no está en ejecución; omitiendo inspección host-side
[WARN] promtail no está en ejecución; omitiendo inspección host-side
[WARN] loki no está en ejecución; omitiendo inspección host-side
[WARN] grafana no está en ejecución; omitiendo inspección host-side

A8 Secrets

[INFO] Buscando directorios secrets
[OK] Directorios secrets detectados:
ops/services/smtp_relay/secrets
ops/services/postgres/secrets

A9 Secrets versionados

[INFO] Verificando secrets versionados
[FAIL] Secrets versionados en Git:
src/monitoring/common/secrets.py

------------------------------------------
B.- AUDITORÍA HOST
------------------------------------------

B1 Sistema

[INFO] Sistema
Linux eob-260131 6.8.0-147-generic #147-Ubuntu SMP PREEMPT_DYNAMIC Thu Sep 24 11:33:16 UTC 2026 x86_64 x86_64 x86_64 GNU/Linux

B2 UFW

[INFO] Estado UFW
[WARN] UFW instalado — se requiere ejecutar como root para mostrar estado (omitido)

B3 fail2ban

[INFO] Estado fail2ban
[OK] fail2ban activo

B4 Cron host

[INFO] Cron del usuario
Sin crontab
[INFO] Cron root
[WARN] Comprobación de crontab root requiere privilegios de root (omitido)

B5 Docker

[INFO] Docker runtime
29.1.3
[OK] Docker instalado

B6 Contenedores

[INFO] Contenedores activos
NAMES                   STATUS                        PORTS
monitoring-cron         Up About a minute (healthy)
promtail                Up About a minute (healthy)
monitoring-smtp-relay   Up About a minute (healthy)   587/tcp
monitoring-python       Up About a minute (healthy)
grafana                 Up About a minute (healthy)   3000/tcp, 127.0.0.1:3001->3001/tcp
loki                    Up About a minute (healthy)   127.0.0.1:3100->3100/tcp
monitoring-postgres     Up About a minute (healthy)   5432/tcp

B7 Puertos host

[INFO] Puertos abiertos en host
Netid State  Recv-Q Send-Q Local Address:Port  Peer Address:PortProcess
udp   UNCONN 0      0         127.0.0.54:53         0.0.0.0:*
udp   UNCONN 0      0      127.0.0.53%lo:53         0.0.0.0:*
tcp   LISTEN 0      4096         0.0.0.0:22         0.0.0.0:*
tcp   LISTEN 0      4096       127.0.0.1:3100       0.0.0.0:*
tcp   LISTEN 0      4096   127.0.0.53%lo:53         0.0.0.0:*
tcp   LISTEN 0      4096       127.0.0.1:44565      0.0.0.0:*
tcp   LISTEN 0      4096      127.0.0.54:53         0.0.0.0:*
tcp   LISTEN 0      4096       127.0.0.1:3001       0.0.0.0:*
tcp   LISTEN 0      4096            [::]:22            [::]:*

B8 Redes Docker

[INFO] Redes Docker
NETWORK ID     NAME                DRIVER    SCOPE
5c7f1ed123be   backend-net         bridge    local
ceee9c6a19c5   bridge              bridge    local
014ae96fb15b   host                host      local
440b7969d128   none                null      local
f09d464e8b7c   observability-net   bridge    local
059f20d37ac5   restricted-net      bridge    local
[OK] Redes de monitoring (backend-net/observability-net/restricted-net) detectadas

B9 Volúmenes

[INFO] Volúmenes Docker
DRIVER    VOLUME NAME
local     58bd72d1512c3ee57f3e601350db8b5eb859cbe528f231b5d0fa3aa7360178b1
local     60bbfd738c570db94ae39bf8fd048adf4e0c6d80bcadf9f4b72399a9ab54a142
local     738f76a891571af4650247a321db87d0cc2f3c65c425cf419d65968843a43532
local     cron_postgres-backups
local     observability_grafana-data
local     observability_loki-data
local     observability_promtail-data
local     postgres_postgres-backups
local     postgres_postgres-data
local     smtp_relay_smtp_relay_logs

------------------------------------------
C.- CUMPLIMIENTO ADR
------------------------------------------

C1 ADR-0014 / ADR-0015

[INFO] Verificando exposición de puertos Docker (ADR-0014 / ADR-0015)
[WARN] Puertos potencialmente expuestos (structured):
  - loki: 127.0.0.1:${LOKI_PORT}:3100
  - grafana: 127.0.0.1:${GRAFANA_PORT}:3001

C2 Validación reproducibilidad de imágenes

[INFO] Ejecutando validaciones de reproducibilidad: ops/audit/validate_reproducibility.sh
[INFO] Validando ops/services/postgres/compose.yml
[OK] ops/services/postgres/compose.yml: compose válido
[OK] ops/services/postgres/compose.yml: sin :latest
[INFO] Validando ops/services/smtp_relay/compose.yml
[OK] ops/services/smtp_relay/compose.yml: compose válido
[OK] ops/services/smtp_relay/compose.yml: sin :latest
[OK] ops/services/smtp_relay/compose.yml:7: imagen local con tag explícito
[INFO] Validando ops/stacks/cron/compose.yml
[OK] ops/stacks/cron/compose.yml: compose válido
[OK] ops/stacks/cron/compose.yml: sin :latest
[OK] ops/stacks/cron/compose.yml:7: imagen local con tag explícito
[INFO] Validando ops/stacks/observability/compose.yml
[OK] ops/stacks/observability/compose.yml: compose válido
[OK] ops/stacks/observability/compose.yml: sin :latest
[INFO] Validando ops/stacks/python/compose.yml
[OK] ops/stacks/python/compose.yml: compose válido
[OK] ops/stacks/python/compose.yml: sin :latest
[OK] ops/stacks/python/compose.yml:7: imagen local con tag explícito
[WARN] Imágenes dangling detectadas (IDs):\n82efbf9c0fa1
679e4be9f918
6a8de175ce0d
6860eccd9725
5b21e2e86aab
[WARN] Sugerencia: ejecutar 'make clean-dangling' tras despliegues o builds

VALIDACIÓN OK: reproducibilidad básica verificada
[OK] Validación reproducibilidad pasada

C3 docker.sock

[INFO] Verificando montaje docker.sock (superficie de ataque)
[OK] docker.sock no montado en contenedores (estructura detectada)

C4 servicios fuera de backend-net / observability-net / restricted-net

[INFO] Verificando uso de redes backend-net / observability-net / restricted-net
[OK] Red backend-net disponible

C5 ADR-0016 cron del host para lógica de aplicación

[INFO] Buscando ejecución de scripts del proyecto en cron del host
[WARN] Comprobación de cron root requiere privilegios de root (omitido)
[OK] Cron del host no ejecuta lógica del proyecto

C6 ejecución python fuera de contenedor

[INFO] Buscando ejecución directa de Python del proyecto
[OK] No se detectó Python del proyecto ejecutándose en host

C7 permisos scripts host hardening

[INFO] Verificando scripts de hardening del host
[OK] Script presente: /opt/monitoring/ops/deployment/configure_docker_limits.sh
[OK] Script presente: /opt/monitoring/scripts/apply_ssh_ratelimit.sh

------------------------------------------
FIN AUDITORÍA
------------------------------------------

=== TEST POLICY STRUCTURED (compose checks / host-side) ===
make test-policy-structured
make[1]: Entering directory '/opt/monitoring'
=== TEST POLICY STRUCTURED (compose checks / host-side) ===
[WARN] docker compose config no disponible; activando fallback estructural estático ADR-0029
[WARN] Usando parseo estático de archivos Compose (fallback host-side sin docker.sock)
{
  "runtime_checks": {
    "docker_cli": true,
    "docker_compose": true,
    "compose_config": false,
    "docker_host_access": true
  },
  "runtime_hostconfig": [
    [
      "postgres",
      "NOT_RUNNING",
      {}
    ],
    [
      "smtp-relay",
      "NOT_RUNNING",
      {}
    ],
    [
      "monitoring-cron",
      "monitoring-cron",
      {
        "Privileged": false,
        "CapAdd": [],
        "CapDrop": [
          "ALL"
        ],
        "SecurityOpt": [
          "no-new-privileges:true"
        ],
        "ReadonlyRootfs": false,
        "Tmpfs": {},
        "Devices": [],
        "AppArmorProfile": "docker-default",
        "NoNewPrivileges": true
      }
    ],
    [
      "promtail",
      "promtail",
      {
        "Privileged": false,
        "CapAdd": [],
        "CapDrop": [
          "ALL"
        ],
        "SecurityOpt": [
          "no-new-privileges:true"
        ],
        "ReadonlyRootfs": false,
        "Tmpfs": {},
        "Devices": [],
        "AppArmorProfile": "docker-default",
        "NoNewPrivileges": true
      }
    ],
    [
      "loki",
      "loki",
      {
        "Privileged": false,
        "CapAdd": [],
        "CapDrop": [
          "ALL"
        ],
        "SecurityOpt": [
          "no-new-privileges:true"
        ],
        "ReadonlyRootfs": false,
        "Tmpfs": {},
        "Devices": [],
        "AppArmorProfile": "docker-default",
        "NoNewPrivileges": true
      }
    ],
    [
      "grafana",
      "grafana",
      {
        "Privileged": false,
        "CapAdd": [],
        "CapDrop": [
          "ALL"
        ],
        "SecurityOpt": [
          "no-new-privileges:true"
        ],
        "ReadonlyRootfs": false,
        "Tmpfs": {},
        "Devices": [],
        "AppArmorProfile": "docker-default",
        "NoNewPrivileges": true
      }
    ],
    [
      "monitoring-python",
      "monitoring-python",
      {
        "Privileged": false,
        "CapAdd": [],
        "CapDrop": [
          "ALL"
        ],
        "SecurityOpt": [
          "no-new-privileges:true"
        ],
        "ReadonlyRootfs": false,
        "Tmpfs": {},
        "Devices": [],
        "AppArmorProfile": "docker-default",
        "NoNewPrivileges": true
      }
    ]
  ],
  "ports": [
    [
      "loki",
      "127.0.0.1:${LOKI_PORT}:3100"
    ],
    [
      "grafana",
      "127.0.0.1:${GRAFANA_PORT}:3001"
    ]
  ],
  "docker_sock": [],
  "images_latest": [],
  "images_no_digest": [],
  "privileged": [],
  "sensitive_mounts": [],
  "cap_add": [],
  "read_only_false": []
}
make[1]: Leaving directory '/opt/monitoring'

=== TEST SECURITY RUNTIME  (ADR-0018 / ADR-0023) ===
make test-security-runtime
make[1]: Entering directory '/opt/monitoring'
# ----------------------------------------
# Test security runtime (ADR-0018 / ADR-0023)
# ----------------------------------------
=== TEST SECURITY RUNTIME ===

# [1] Usuario runtime
[1] Verificando usuario en contenedores
[OK] monitoring-python usa usuario non-root (UID=10001)
[OK] monitoring-cron usa usuario non-root (UID=10001)

[2] Verificando contenedores infra-trusted
[WARN] monitoring-postgres ejecuta como root (UID=0) — excepción infra-trusted permitida
[WARN] monitoring-smtp-relay ejecuta como root (UID=0) — excepción infra-trusted permitida
[WARN] promtail ejecuta como root (UID=0) — excepción infra-trusted permitida

[OK] test-security-runtime completado
# [3] docker.sock
[3] Verificando uso de docker.sock
[OK] docker.sock no usado en servicios

# [4] Restart policy
[4] Verificando restart policy
[OK] monitoring-python restart=always
[OK] monitoring-cron restart=always
[OK] monitoring-postgres restart=always
[OK] smtp-relay restart=
none
[OK] promtail restart=always
[OK] loki restart=always
[OK] grafana restart=always

# [5] Healthchecks
[5] Verificando healthchecks
[OK] monitoring-python health=healthy
[OK] monitoring-cron health=healthy
[OK] monitoring-postgres health=healthy
[OK] smtp-relay health=
none
[OK] promtail health=healthy
[OK] loki health=healthy
[OK] grafana health=healthy

[6] Runtime HostConfig summary (visibility only)
for c in $(bash ops/runtime_containers.sh list); do \
        if docker ps --format '{{.Names}}' | grep -q "^$c$"; then \
                echo "[INFO] Inspecting container: $c"; \
                docker inspect --format 'Name={{.Name}} Privileged={{.HostConfig.Privileged}} CapAdd={{json .HostConfig.CapAdd}} CapDrop={{json .HostConfig.CapDrop}} SecurityOpt={{json .HostConfig.SecurityOpt}} ReadonlyRootfs={{.HostConfig.ReadonlyRootfs}} AppArmor={{.AppArmorProfile}}' $c 2>/dev/null || echo "  -> inspect failed for $c"; \
        else \
                echo "[WARN] $c not running; skipping"; \
        fi; \
done
[INFO] Inspecting container: monitoring-python
Name=/monitoring-python Privileged=false CapAdd=null CapDrop=["ALL"] SecurityOpt=["no-new-privileges:true"] ReadonlyRootfs=false AppArmor=docker-default
[INFO] Inspecting container: monitoring-cron
Name=/monitoring-cron Privileged=false CapAdd=null CapDrop=["ALL"] SecurityOpt=["no-new-privileges:true"] ReadonlyRootfs=false AppArmor=docker-default
[INFO] Inspecting container: monitoring-postgres
Name=/monitoring-postgres Privileged=false CapAdd=null CapDrop=null SecurityOpt=null ReadonlyRootfs=false AppArmor=docker-default
[WARN] smtp-relay not running; skipping
[INFO] Inspecting container: promtail
Name=/promtail Privileged=false CapAdd=null CapDrop=["ALL"] SecurityOpt=["no-new-privileges:true"] ReadonlyRootfs=false AppArmor=docker-default
[INFO] Inspecting container: loki
Name=/loki Privileged=false CapAdd=null CapDrop=["ALL"] SecurityOpt=["no-new-privileges:true"] ReadonlyRootfs=false AppArmor=docker-default
[INFO] Inspecting container: grafana
Name=/grafana Privileged=false CapAdd=null CapDrop=["ALL"] SecurityOpt=["no-new-privileges:true"] ReadonlyRootfs=false AppArmor=docker-default

[7] Ejecutando checks estructurales HostConfig (ops/audit/check_hostconfig.sh)
[INFO] Checking container monitoring-python
[WARN] monitoring-python has ReadonlyRootfs=false
[INFO] monitoring-python approved readonly bind mount: /var/lib/docker/containers
[INFO] monitoring-python configured user=appuser
[INFO] Checking container monitoring-cron
[WARN] monitoring-cron has ReadonlyRootfs=false
[INFO] monitoring-cron approved readonly bind mount: /var/lib/docker/containers
[INFO] monitoring-cron configured user=appuser
[INFO] Checking container monitoring-postgres
[WARN] monitoring-postgres has ReadonlyRootfs=false
[WARN] monitoring-postgres missing no-new-privileges
[WARN] monitoring-postgres does not define CapDrop
[WARN] monitoring-postgres mounts host path readonly: /opt/monitoring/ops/services/postgres/init
[WARN] monitoring-postgres mounts host path readonly: /opt/monitoring/ops/services/postgres/secrets/postgres_password
[WARN] monitoring-postgres has no explicit runtime user
[INFO] smtp-relay not running; skipping
[INFO] Checking container promtail
[WARN] promtail has ReadonlyRootfs=false
[WARN] promtail mounts host path readonly: /opt/monitoring/ops/stacks/observability/config/promtail-config.yml
[INFO] promtail approved readonly bind mount: /var/lib/docker/containers
[INFO] promtail approved readonly bind mount: /var/log
[INFO] promtail is infra_trusted and may run as root
[INFO] Checking container loki
[WARN] loki has ReadonlyRootfs=false
[WARN] loki mounts host path readonly: /opt/monitoring/ops/stacks/observability/config/loki-config.yml
[INFO] loki configured user=10001
[INFO] Checking container grafana
[WARN] grafana has ReadonlyRootfs=false
[WARN] grafana mounts host path readonly: /opt/monitoring/ops/stacks/observability/config/datasource.yml
[INFO] grafana configured user=472

=== FIN TEST SECURITY RUNTIME ===
make[1]: Leaving directory '/opt/monitoring'

=== RUNTIME GOVERNANCE AUDITS ===
make audit-runtime
make[1]: Entering directory '/opt/monitoring'
=== RUNTIME GOVERNANCE AUDIT (human) ===
python3 -m ops.audit.runtime_governance_audit --output-md artifacts/runtime_audit.md ; RC=$? ; \
if [ $RC -ne 0 ]; then \
        echo "[WARNING] Runtime governance audit returned RC=$RC"; \
fi
No forbidden findings detected (summary written)
make[1]: Leaving directory '/opt/monitoring'

make audit-runtime-json
make[1]: Entering directory '/opt/monitoring'
=== RUNTIME GOVERNANCE AUDIT (json) ===
python3 -m ops.audit.runtime_governance_audit --output-json artifacts/runtime_audit.json --output-md artifacts/runtime_audit.md ; RC=$? ; \
if [ $RC -ne 0 ]; then \
        echo "[WARNING] Runtime governance audit (json) returned RC=$RC"; \
fi
No forbidden findings detected (summary written)
make[1]: Leaving directory '/opt/monitoring'

make audit-runtime-ci
make[1]: Entering directory '/opt/monitoring'
=== RUNTIME GOVERNANCE AUDIT (CI mode - fail on forbidden) ===
python3 -m ops.audit.runtime_governance_audit --output-json artifacts/runtime_audit.json --output-md artifacts/runtime_audit.md --ci ; RC=$? ; \
if [ $RC -ne 0 ]; then echo "[ERROR] Runtime governance audit FAILED (forbidden findings)" ; exit $RC ; fi
No forbidden findings detected (summary written)
make[1]: Leaving directory '/opt/monitoring'

=== VERIFY SECURITY CHECKS ===
make verify-security
make[1]: Entering directory '/opt/monitoring'
=== VERIFY SECURITY CHECKS ===
[INFO] Comprobando secreto Postgres: ops/services/postgres/secrets/postgres_password
[OK] Permisos del fichero secreto: 600
[OK] Permisos del directorio de secrets: 700
[OK] Propietario del fichero secreto: eboe62
[OK] No se ha encontrado POSTGRES_PASSWORD hardcodeado en ops/services/postgres/.env
[OK] No se ha encontrado POSTGRES_PASSWORD hardcodeado en ops/services/postgres/.env.template
[OK] No se ha encontrado POSTGRES_PASSWORD hardcodeado en ops/services/postgres/compose.yml
[OK] compose contiene POSTGRES_PASSWORD_FILE
[OK] compose monta el secreto en /run/secrets/postgres_password
[OK] No se ha detectado entrypoint wrapper en compose
[OK] Comprobaciones del secreto PostgreSQL superadas
make[1]: Leaving directory '/opt/monitoring'

=== TEST POLICY STRUCTURED (compose checks / host-side) ===
[WARN] docker compose config no disponible; activando fallback estructural estático ADR-0029
[WARN] Usando parseo estático de archivos Compose (fallback host-side sin docker.sock)
{
  "runtime_checks": {
    "docker_cli": true,
    "docker_compose": true,
    "compose_config": false,
    "docker_host_access": true
  },
  "runtime_hostconfig": [
    [
      "postgres",
      "NOT_RUNNING",
      {}
    ],
    [
      "smtp-relay",
      "NOT_RUNNING",
      {}
    ],
    [
      "monitoring-cron",
      "monitoring-cron",
      {
        "Privileged": false,
        "CapAdd": [],
        "CapDrop": [
          "ALL"
        ],
        "SecurityOpt": [
          "no-new-privileges:true"
        ],
        "ReadonlyRootfs": false,
        "Tmpfs": {},
        "Devices": [],
        "AppArmorProfile": "docker-default",
        "NoNewPrivileges": true
      }
    ],
    [
      "promtail",
      "promtail",
      {
        "Privileged": false,
        "CapAdd": [],
        "CapDrop": [
          "ALL"
        ],
        "SecurityOpt": [
          "no-new-privileges:true"
        ],
        "ReadonlyRootfs": false,
        "Tmpfs": {},
        "Devices": [],
        "AppArmorProfile": "docker-default",
        "NoNewPrivileges": true
      }
    ],
    [
      "loki",
      "loki",
      {
        "Privileged": false,
        "CapAdd": [],
        "CapDrop": [
          "ALL"
        ],
        "SecurityOpt": [
          "no-new-privileges:true"
        ],
        "ReadonlyRootfs": false,
        "Tmpfs": {},
        "Devices": [],
        "AppArmorProfile": "docker-default",
        "NoNewPrivileges": true
      }
    ],
    [
      "grafana",
      "grafana",
      {
        "Privileged": false,
        "CapAdd": [],
        "CapDrop": [
          "ALL"
        ],
        "SecurityOpt": [
          "no-new-privileges:true"
        ],
        "ReadonlyRootfs": false,
        "Tmpfs": {},
        "Devices": [],
        "AppArmorProfile": "docker-default",
        "NoNewPrivileges": true
      }
    ],
    [
      "monitoring-python",
      "monitoring-python",
      {
        "Privileged": false,
        "CapAdd": [],
        "CapDrop": [
          "ALL"
        ],
        "SecurityOpt": [
          "no-new-privileges:true"
        ],
        "ReadonlyRootfs": false,
        "Tmpfs": {},
        "Devices": [],
        "AppArmorProfile": "docker-default",
        "NoNewPrivileges": true
      }
    ]
  ],
  "ports": [
    [
      "loki",
      "127.0.0.1:${LOKI_PORT}:3100"
    ],
    [
      "grafana",
      "127.0.0.1:${GRAFANA_PORT}:3001"
    ]
  ],
  "docker_sock": [],
  "images_latest": [],
  "images_no_digest": [],
  "privileged": [],
  "sensitive_mounts": [],
  "cap_add": [],
  "read_only_false": []
}
# ----------------------------------------
# Test security runtime (ADR-0018 / ADR-0023)
# ----------------------------------------
=== TEST SECURITY RUNTIME ===

# [1] Usuario runtime
[1] Verificando usuario en contenedores
[OK] monitoring-python usa usuario non-root (UID=10001)
[OK] monitoring-cron usa usuario non-root (UID=10001)

[2] Verificando contenedores infra-trusted
[WARN] monitoring-postgres ejecuta como root (UID=0) — excepción infra-trusted permitida
[WARN] monitoring-smtp-relay ejecuta como root (UID=0) — excepción infra-trusted permitida
[WARN] promtail ejecuta como root (UID=0) — excepción infra-trusted permitida

[OK] test-security-runtime completado
# [3] docker.sock
[3] Verificando uso de docker.sock
[OK] docker.sock no usado en servicios

# [4] Restart policy
[4] Verificando restart policy
[OK] monitoring-python restart=always
[OK] monitoring-cron restart=always
[OK] monitoring-postgres restart=always
[OK] smtp-relay restart=
none
[OK] promtail restart=always
[OK] loki restart=always
[OK] grafana restart=always

# [5] Healthchecks
[5] Verificando healthchecks
[OK] monitoring-python health=healthy
[OK] monitoring-cron health=healthy
[OK] monitoring-postgres health=healthy
[OK] smtp-relay health=
none
[OK] promtail health=healthy
[OK] loki health=healthy
[OK] grafana health=healthy

[6] Runtime HostConfig summary (visibility only)
for c in $(bash ops/runtime_containers.sh list); do \
        if docker ps --format '{{.Names}}' | grep -q "^$c$"; then \
                echo "[INFO] Inspecting container: $c"; \
                docker inspect --format 'Name={{.Name}} Privileged={{.HostConfig.Privileged}} CapAdd={{json .HostConfig.CapAdd}} CapDrop={{json .HostConfig.CapDrop}} SecurityOpt={{json .HostConfig.SecurityOpt}} ReadonlyRootfs={{.HostConfig.ReadonlyRootfs}} AppArmor={{.AppArmorProfile}}' $c 2>/dev/null || echo "  -> inspect failed for $c"; \
        else \
                echo "[WARN] $c not running; skipping"; \
        fi; \
done
[INFO] Inspecting container: monitoring-python
Name=/monitoring-python Privileged=false CapAdd=null CapDrop=["ALL"] SecurityOpt=["no-new-privileges:true"] ReadonlyRootfs=false AppArmor=docker-default
[INFO] Inspecting container: monitoring-cron
Name=/monitoring-cron Privileged=false CapAdd=null CapDrop=["ALL"] SecurityOpt=["no-new-privileges:true"] ReadonlyRootfs=false AppArmor=docker-default
[INFO] Inspecting container: monitoring-postgres
Name=/monitoring-postgres Privileged=false CapAdd=null CapDrop=null SecurityOpt=null ReadonlyRootfs=false AppArmor=docker-default
[WARN] smtp-relay not running; skipping
[INFO] Inspecting container: promtail
Name=/promtail Privileged=false CapAdd=null CapDrop=["ALL"] SecurityOpt=["no-new-privileges:true"] ReadonlyRootfs=false AppArmor=docker-default
[INFO] Inspecting container: loki
Name=/loki Privileged=false CapAdd=null CapDrop=["ALL"] SecurityOpt=["no-new-privileges:true"] ReadonlyRootfs=false AppArmor=docker-default
[INFO] Inspecting container: grafana
Name=/grafana Privileged=false CapAdd=null CapDrop=["ALL"] SecurityOpt=["no-new-privileges:true"] ReadonlyRootfs=false AppArmor=docker-default

[7] Ejecutando checks estructurales HostConfig (ops/audit/check_hostconfig.sh)
[INFO] Checking container monitoring-python
[WARN] monitoring-python has ReadonlyRootfs=false
[INFO] monitoring-python approved readonly bind mount: /var/lib/docker/containers
[INFO] monitoring-python configured user=appuser
[INFO] Checking container monitoring-cron
[WARN] monitoring-cron has ReadonlyRootfs=false
[INFO] monitoring-cron approved readonly bind mount: /var/lib/docker/containers
[INFO] monitoring-cron configured user=appuser
[INFO] Checking container monitoring-postgres
[WARN] monitoring-postgres has ReadonlyRootfs=false
[WARN] monitoring-postgres missing no-new-privileges
[WARN] monitoring-postgres does not define CapDrop
[WARN] monitoring-postgres mounts host path readonly: /opt/monitoring/ops/services/postgres/init
[WARN] monitoring-postgres mounts host path readonly: /opt/monitoring/ops/services/postgres/secrets/postgres_password
[WARN] monitoring-postgres has no explicit runtime user
[INFO] smtp-relay not running; skipping
[INFO] Checking container promtail
[WARN] promtail has ReadonlyRootfs=false
[INFO] promtail approved readonly bind mount: /var/log
[WARN] promtail mounts host path readonly: /opt/monitoring/ops/stacks/observability/config/promtail-config.yml
[INFO] promtail approved readonly bind mount: /var/lib/docker/containers
[INFO] promtail is infra_trusted and may run as root
[INFO] Checking container loki
[WARN] loki has ReadonlyRootfs=false
[WARN] loki mounts host path readonly: /opt/monitoring/ops/stacks/observability/config/loki-config.yml
[INFO] loki configured user=10001
[INFO] Checking container grafana
[WARN] grafana has ReadonlyRootfs=false
[WARN] grafana mounts host path readonly: /opt/monitoring/ops/stacks/observability/config/datasource.yml
[INFO] grafana configured user=472

=== FIN TEST SECURITY RUNTIME ===
=== VERIFY SECURITY CHECKS ===
[INFO] Comprobando secreto Postgres: ops/services/postgres/secrets/postgres_password
[OK] Permisos del fichero secreto: 600
[OK] Permisos del directorio de secrets: 700
[OK] Propietario del fichero secreto: eboe62
[OK] No se ha encontrado POSTGRES_PASSWORD hardcodeado en ops/services/postgres/.env
[OK] No se ha encontrado POSTGRES_PASSWORD hardcodeado en ops/services/postgres/.env.template
[OK] No se ha encontrado POSTGRES_PASSWORD hardcodeado en ops/services/postgres/compose.yml
[OK] compose contiene POSTGRES_PASSWORD_FILE
[OK] compose monta el secreto en /run/secrets/postgres_password
[OK] No se ha detectado entrypoint wrapper en compose
[OK] Comprobaciones del secreto PostgreSQL superadas
=== RUNTIME GOVERNANCE AUDIT (CI mode - fail on forbidden) ===
python3 -m ops.audit.runtime_governance_audit --output-json artifacts/runtime_audit.json --output-md artifacts/runtime_audit.md --ci ; RC=$? ; \
if [ $RC -ne 0 ]; then echo "[ERROR] Runtime governance audit FAILED (forbidden findings)" ; exit $RC ; fi
No forbidden findings detected (summary written)
=== TEST OBSERVABILITY CORE ===

[1] Esperando Loki...
ready

[OK] Loki accesible

[2] Generando log REAL en contenedor

[3] Query Loki...
[OK] logs ingeridos

=== FIN TEST OBSERVABILITY ===

=== TEST CRON EXECUTION ===
[1] Preparando entorno logs
[2] Generando marca temporal
[3] Verificando ejecución...
[OK] cron ejecutando correctamente
# ----------------------------------------
# [6] Python health
# ----------------------------------------
=== TEST PYTHON HEALTH ===
[1] Estado contenedor
State=running Health=healthy

[2] Esperando healthy...
[INFO] container=monitoring-python mode=strict timeout=90s
[DEBUG] status=healthy elapsed=0s
[OK] estado healthy
[OK] python healthy


=== TEST SMTP CONNECT ===
Asegurando debug toolbox...
make[1]: Entering directory '/opt/monitoring'
=== Iniciando contenedor debug (network=restricted-net) ===
9591bac8f2afcd0b0220bc5d3b762739929182328ed6c8d3ecaec6d926ae510d
[OK] contenedor debug activo

make[1]: Leaving directory '/opt/monitoring'
Test conexión SMTP
Connection to smtp-relay (172.20.0.3) 587 port [tcp/submission] succeeded!
[OK] conexión TCP correcta

=== TEST SMTP BANNER ===
[OK] banner SMTP correcto

=== TEST SMTP PROTOCOL ===
[OK] SMTP handshake válido

=== TEST SMTP AUTH ===
[OK] SASL activo

=== TEST SMTP RELAY LOCAL (SIN POSTMARK) ===
[OK] relay acepta MAIL FROM / RCPT / DATA

=== TEST SMTP QUEUE ===
[OK] cola vacía

=== TEST SMTP LOG CLEAN ===
[OK] logs limpios


=== TEST AISLAMIENTO RED ===
[1] Intentando conexión indebida (desde restricted-net)
[OK] acceso restringido (esperado)
[2] Validando redes internas
        "Containers": {
        "Containers": {
        "Containers": {
[OK] test aislamiento completado

=== TEST DEPENDENCIAS HOST ===
[1] Buscando bind mounts peligrosos
        "Mounts": [
[2] Verificando /opt/monitoring interno
[OK] código disponible dentro del contenedor
[OK] test dependencias finalizado

=== TEST PERMISOS ===
[1] UID en contenedores
uid=10001(appuser) gid=10001(appuser) groups=10001(appuser)
uid=10001(appuser) gid=10001(appuser) groups=10001(appuser)
[2] escritura en logs
[OK] escritura válida
[OK] test permisos completado

=== TEST AISLAMIENTO FS ===
[1] escribiendo en contenedor A
docker exec monitoring-python sh -c "echo test > /tmp/testfile"
[2] comprobando en contenedor B
[OK] aislamiento correcto
eboe62@eob-260131:/opt/monitoring$
==========================================

echo "=== HOST (root) ==="
sudo ufw status verbose
sudo ss -tulpn
sudo crontab -l
sudo fail2ban-client status; sudo fail2ban-client status sshd
sudo grep -E "^(PermitRootLogin|PasswordAuthentication|Port)" /etc/ssh/sshd_config /etc/ssh/sshd_config.d/* 2>/dev/null
systemctl is-enabled unattended-upgrades 2>&1; apt list --upgradable 2>/dev/null | wc -l
sudo last -n 15; sudo lastb -n 15 2>/dev/null | head -15
} 2>&1 | tee -a "$OUT"
=== HOST (root) ===
[sudo] password for eboe62:
Sorry, try again.
[sudo] password for eboe62:
Status: active
Logging: on (low)
Default: deny (incoming), allow (outgoing), deny (routed)
New profiles: skip

To                         Action      From
--                         ------      ----
22/tcp (OpenSSH)           ALLOW IN    Anywhere
80/tcp                     ALLOW IN    Anywhere
443/tcp                    ALLOW IN    Anywhere
22/tcp (OpenSSH (v6))      ALLOW IN    Anywhere (v6)
80/tcp (v6)                ALLOW IN    Anywhere (v6)
443/tcp (v6)               ALLOW IN    Anywhere (v6)

Netid State  Recv-Q Send-Q Local Address:Port  Peer Address:PortProcess
udp   UNCONN 0      0         127.0.0.54:53         0.0.0.0:*    users:(("systemd-resolve",pid=459,fd=16))
udp   UNCONN 0      0      127.0.0.53%lo:53         0.0.0.0:*    users:(("systemd-resolve",pid=459,fd=14))
tcp   LISTEN 0      4096         0.0.0.0:22         0.0.0.0:*    users:(("sshd",pid=1255,fd=3),("systemd",pid=1,fd=94))
tcp   LISTEN 0      4096       127.0.0.1:3100       0.0.0.0:*    users:(("docker-proxy",pid=1953,fd=7))
tcp   LISTEN 0      4096   127.0.0.53%lo:53         0.0.0.0:*    users:(("systemd-resolve",pid=459,fd=15))
tcp   LISTEN 0      4096       127.0.0.1:44565      0.0.0.0:*    users:(("containerd",pid=851,fd=14))
tcp   LISTEN 0      4096      127.0.0.54:53         0.0.0.0:*    users:(("systemd-resolve",pid=459,fd=17))
tcp   LISTEN 0      4096       127.0.0.1:3001       0.0.0.0:*    users:(("docker-proxy",pid=1991,fd=7))
tcp   LISTEN 0      4096            [::]:22            [::]:*    users:(("sshd",pid=1255,fd=4),("systemd",pid=1,fd=95))
no crontab for root
Status
|- Number of jail:      1
`- Jail list:   sshd
Status for the jail: sshd
|- Filter
|  |- Currently failed: 1
|  |- Total failed:     2
|  `- Journal matches:  _SYSTEMD_UNIT=sshd.service + _COMM=sshd
`- Actions
   |- Currently banned: 0
   |- Total banned:     0
   `- Banned IP list:
/etc/ssh/sshd_config:PermitRootLogin prohibit-password
/etc/ssh/sshd_config:PasswordAuthentication no
/etc/ssh/sshd_config.d/50-cloud-init.conf:PasswordAuthentication no
/etc/ssh/sshd_config.d/60-cloudimg-settings.conf:PasswordAuthentication no
enabled
68
eboe62   pts/0        150.244.160.215  Thu Oct 29 21:47   still logged in
reboot   system boot  6.8.0-147-generi Thu Oct 29 21:46   still running
eboe62   pts/1        150.244.160.215  Thu Oct 29 21:31 - 21:32  (00:01)
eboe62   pts/0        150.244.160.215  Thu Oct 29 19:30 - 21:32  (02:01)
eboe62   pts/0        213.94.50.17     Thu Aug 20 19:02 - 21:17  (02:14)
eboe62   pts/0        213.94.50.17     Mon Aug 17 17:08 - 20:32  (03:24)
reboot   system boot  6.8.0-94-generic Mon Aug 17 17:07 - 21:32 (73+04:25)
eboe62   pts/0        213.94.50.17     Sun Aug 16 12:22 - 12:24  (00:01)
reboot   system boot  6.8.0-94-generic Sun Aug 16 12:18 - 21:32 (74+09:14)
eboe62   pts/0        213.94.55.139    Sun May 31 23:54 - 00:03  (00:09)
reboot   system boot  6.8.0-94-generic Sun May 31 23:53 - 00:03  (00:09)
eboe62   pts/0        213.94.55.139    Sun May 31 11:53 - 11:54  (00:00)
reboot   system boot  6.8.0-94-generic Sun May 31 11:53 - 11:54  (00:01)
eboe62   pts/0        213.94.55.139    Sun May 31 11:24 - 11:42  (00:18)
reboot   system boot  6.8.0-94-generic Sun May 31 11:23 - 11:42  (00:19)

wtmp begins Sat Jan 31 22:45:55 2026
admin-12 ssh:notty    103.159.2.113    Thu Oct 29 21:50 - 21:50  (00:00)
test123  ssh:notty    103.159.2.113    Thu Oct 29 21:47 - 21:47  (00:00)
shaquill ssh:notty    2.57.121.112     Thu Oct 29 21:32 - 21:32  (00:00)
superuse ssh:notty    202.51.214.99    Thu Oct 29 21:31 - 21:31  (00:00)
admin    ssh:notty    139.19.117.130   Thu Oct 29 21:30 - 21:30  (00:00)
admin    ssh:notty    103.159.2.113    Thu Oct 29 21:29 - 21:29  (00:00)
admin    ssh:notty    103.159.2.113    Thu Oct 29 21:25 - 21:25  (00:00)
sabrine  ssh:notty    93.152.221.37    Thu Oct 29 21:22 - 21:22  (00:00)
admin    ssh:notty    103.159.2.113    Thu Oct 29 21:22 - 21:22  (00:00)
apache   ssh:notty    103.159.2.113    Thu Oct 29 21:18 - 21:18  (00:00)
app      ssh:notty    103.159.2.113    Thu Oct 29 21:15 - 21:15  (00:00)
app      ssh:notty    103.159.2.113    Thu Oct 29 21:11 - 21:11  (00:00)
app      ssh:notty    103.159.2.113    Thu Oct 29 21:08 - 21:08  (00:00)
centos   ssh:notty    103.159.2.113    Thu Oct 29 21:04 - 21:04  (00:00)
admin1   ssh:notty    2.57.122.209     Thu Oct 29 21:02 - 21:02  (00:00)

==========================================

=== TEST RESILIENCIA SRE (Site Reliability Engineering) ===

# ----------------------------------------
# [0] Estado inicial
# ----------------------------------------
[0] Estado inicial
CONTAINER ID   IMAGE                      COMMAND                  CREATED         STATUS                   PORTS                                NAMES
9591bac8f2af   nicolaka/netshoot          "sleep infinity"         3 minutes ago   Up 3 minutes                                                  monitoring-debug
595d999cdcbe   monitoring-cron:v1.0.0     "/usr/local/bin/dock…"   2 months ago    Up 4 minutes (healthy)                                        monitoring-cron
2b23ad2dae7b   grafana/promtail:2.9.3     "/usr/bin/promtail -…"   2 months ago    Up 4 minutes (healthy)                                        promtail
f3fe53f36019   monitoring-smtp-relay      "/patch-postfix.sh /…"   2 months ago    Up 4 minutes (healthy)   587/tcp                              monitoring-smtp-relay
d3a0a01229a4   monitoring-python:v1.0.0   "docker-entrypoint.sh"   2 months ago    Up 4 minutes (healthy)                                        monitoring-python
1e5e98766f23   grafana/grafana:10.4.2     "/run.sh"                2 months ago    Up 4 minutes (healthy)   3000/tcp, 127.0.0.1:3001->3001/tcp   grafana
1502fa2b4de2   grafana/loki:2.9.3         "/usr/bin/loki -conf…"   2 months ago    Up 4 minutes (healthy)   127.0.0.1:3100->3100/tcp             loki
c7c1d622e9bb   postgres:14.3              "docker-entrypoint.s…"   2 months ago    Up 4 minutes (healthy)   5432/tcp                             monitoring-postgres

# ----------------------------------------
# [1] CRASH REAL proceso (PID 1)
# ----------------------------------------
[1] CRASH proceso interno (PID 1)
# --- VALIDAR RESTART (no health aún) ---
esperando restart (running)...
[OK] contenedor reiniciado
# --- VALIDAR HEALTH POST-RESTART ---
esperando recuperación health (healthy)...
[OK] restart + recovery OK
# Debug
[INFO] estado tras restart:
State=running Health=healthy

# ----------------------------------------
# [2] FALLO DB
# ----------------------------------------
[2] Simulación fallo DB
monitoring-postgres
[STEP] esperando pérdida real de conectividad...
[OK] degradación detectada (conectividad perdida)
monitoring-postgres
[STEP] esperando recuperación real...
# --- FASE 1: DNS ---
# --- FASE 2: TCP + warmup Postgres ---
[DEBUG] TCP OK (1)
[DEBUG] TCP OK (2)
[DEBUG] TCP OK (3)
[OK] DB recuperada

# ----------------------------------------
# [3] FALLO RED (simulado)
# ----------------------------------------
[3] Simulación fallo red hacia DB
Network=backend-net
[STEP] desconectando red...
[STEP] verificando aislamiento real...
[OK] aislamiento de red confirmado
[STEP] reconectando red...
[STEP] verificando recuperación de conectividad...
[OK] red restaurada

# ----------------------------------------
# [4] OBSERVABILIDAD (Loki)
# ----------------------------------------
[4] Verificando Loki
ready
[OK] Loki accesible
[STEP] generando log REAL en contenedor (PID 1)...
[STEP] verificando ingestión en Loki...
[OK] Loki ingestando logs
# ----------------------------------------
# [5] ESTADO FINAL
# ----------------------------------------
[5] Estado final
CONTAINER ID   IMAGE                      COMMAND                  CREATED         STATUS                    PORTS                                NAMES
9591bac8f2af   nicolaka/netshoot          "sleep infinity"         3 minutes ago   Up 3 minutes                                                   monitoring-debug
595d999cdcbe   monitoring-cron:v1.0.0     "/usr/local/bin/dock…"   2 months ago    Up 5 minutes (healthy)                                         monitoring-cron
2b23ad2dae7b   grafana/promtail:2.9.3     "/usr/bin/promtail -…"   2 months ago    Up 5 minutes (healthy)                                         promtail
f3fe53f36019   monitoring-smtp-relay      "/patch-postfix.sh /…"   2 months ago    Up 5 minutes (healthy)    587/tcp                              monitoring-smtp-relay
d3a0a01229a4   monitoring-python:v1.0.0   "docker-entrypoint.sh"   2 months ago    Up 5 minutes (healthy)                                         monitoring-python
1e5e98766f23   grafana/grafana:10.4.2     "/run.sh"                2 months ago    Up 5 minutes (healthy)    3000/tcp, 127.0.0.1:3001->3001/tcp   grafana
1502fa2b4de2   grafana/loki:2.9.3         "/usr/bin/loki -conf…"   2 months ago    Up 5 minutes (healthy)    127.0.0.1:3100->3100/tcp             loki
c7c1d622e9bb   postgres:14.3              "docker-entrypoint.s…"   2 months ago    Up 12 seconds (healthy)   5432/tcp                             monitoring-postgres

=== FIN TEST RESILIENCIA SRE ===


=== TEST SMTP CONNECT ===
Asegurando debug toolbox...
Test conexión SMTP
Connection to smtp-relay (172.20.0.3) 587 port [tcp/submission] succeeded!
[OK] conexión TCP correcta

=== TEST SMTP BANNER ===
[OK] banner SMTP correcto

=== TEST SMTP PROTOCOL ===
[OK] SMTP handshake válido

=== TEST SMTP AUTH ===
[OK] SASL activo

=== TEST SMTP RELAY FLOW (POSTMARK API) ===
docker exec monitoring-python python3 scripts/test_mail.py || (echo "Fallo Relay Flow" && exit 1)

=== SMTP RELAY E2E TEST ===

[INFO] Conectando a SMTP server : smtp-relay:587...
[INFO] Subject                  : E2E TEST 1793310747
[INFO] Message-ID               : <e2e-1793310747@appvisibility.es>
[INFO] From                     : noreply@appvisibility.es
[INFO] To                       : contacto@appvisibility.es
📤 Enviando email...
send: 'ehlo [172.20.0.2]\r\n'
reply: b'250-smtp-relay.local\r\n'
reply: b'250-PIPELINING\r\n'
reply: b'250-SIZE\r\n'
reply: b'250-VRFY\r\n'
reply: b'250-ETRN\r\n'
reply: b'250-STARTTLS\r\n'
reply: b'250-ENHANCEDSTATUSCODES\r\n'
reply: b'250-8BITMIME\r\n'
reply: b'250-DSN\r\n'
reply: b'250-SMTPUTF8\r\n'
reply: b'250 CHUNKING\r\n'
reply: retcode (250); Msg: b'smtp-relay.local\nPIPELINING\nSIZE\nVRFY\nETRN\nSTARTTLS\nENHANCEDSTATUSCODES\n8BITMIME\nDSN\nSMTPUTF8\nCHUNKING'
send: 'ehlo [172.20.0.2]\r\n'
reply: b'250-smtp-relay.local\r\n'
[OK] EHLO aceptado
reply: b'250-PIPELINING\r\n'
reply: b'250-SIZE\r\n'
reply: b'250-VRFY\r\n'
reply: b'250-ETRN\r\n'
reply: b'250-STARTTLS\r\n'
reply: b'250-ENHANCEDSTATUSCODES\r\n'
reply: b'250-8BITMIME\r\n'
reply: b'250-DSN\r\n'
reply: b'250-SMTPUTF8\r\n'
reply: b'250 CHUNKING\r\n'
reply: retcode (250); Msg: b'smtp-relay.local\nPIPELINING\nSIZE\nVRFY\nETRN\nSTARTTLS\nENHANCEDSTATUSCODES\n8BITMIME\nDSN\nSMTPUTF8\nCHUNKING'
send: 'mail FROM:<noreply@appvisibility.es>\r\n'
reply: b'250 2.1.0 Ok\r\n'
reply: retcode (250); Msg: b'2.1.0 Ok'
send: 'rcpt TO:<contacto@appvisibility.es>\r\n'
[OK] MAIL FROM aceptado
send: 'QUIT\r\n'

[ERROR] Error SMTP: Connection unexpectedly closed: timed out
Fallo Relay Flow
make: *** [Makefile:861: test-smtp-relay-flow] Error 1
monitoring-debug
[OK] contenedor debug eliminado

==========================================
==========================================
==========================================
==========================================
