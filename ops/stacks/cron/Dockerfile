# Imagen autónoma para ejecución de cronjobs
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/opt/monitoring/src

WORKDIR /opt/monitoring

# Paquetes mínimos necesarios
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    curl \
    bc \
    bash \
    coreutils \
 && rm -rf /var/lib/apt/lists/*

# Crear usuario no root (UID fijo)
RUN groupadd -g 10001 appuser \
 && useradd -u 10001 -g appuser -ms /bin/bash appuser

# Copiar requirements primero (cache)
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir --no-compile -r requirements.txt

# Copiar código del servicio
COPY src/ src/
COPY scripts/ scripts/

 # Supercronic (vendor + checksum)
COPY ops/vendor/supercronic /tmp/supercronic

RUN cd /tmp/supercronic \
 && sha256sum -c SHA256SUMS \
 && mv supercronic-linux-amd64 /usr/local/bin/supercronic \
 && chmod 755 /usr/local/bin/supercronic \
 && /usr/local/bin/supercronic -test /dev/null \
 && rm -rf /tmp/supercronic

# Copiar Cron + entrypoint
COPY ops/stacks/cron/monitoring.cron /opt/monitoring/ops/stacks/cron/monitoring.cron
COPY ops/stacks/cron/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
# Logs internos y Permisos  explícitos fuera de /opt
RUN chmod 755 /usr/local/bin/docker-entrypoint.sh \
 && chown appuser:appuser /usr/local/bin/docker-entrypoint.sh \
 && mkdir -p /opt/monitoring/logs \
 && chown -R appuser:appuser /opt/monitoring \
 && chmod -R 755 /opt/monitoring

# Usuario no root
USER appuser

# Healthcheck para detectar fallos de cron
HEALTHCHECK CMD pgrep supercronic || exit 1

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
