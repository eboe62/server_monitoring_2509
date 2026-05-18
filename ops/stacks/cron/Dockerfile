# Imagen autónoma para ejecución de cronjobs
FROM python:3.12-slim

ARG IMAGE_VERSION="v1.0.0"
ARG BUILD_DATE=""

LABEL org.opencontainers.image.title="monitoring-cron"
LABEL org.opencontainers.image.version="${IMAGE_VERSION}"
LABEL org.opencontainers.image.created="${BUILD_DATE}"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/opt/monitoring/src \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /opt/monitoring

# Paquetes con dependencias mínimas del sistema
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    curl \
    bc \
    bash \
    coreutils \
 && rm -rf /var/lib/apt/lists/*

# Usuario estándar (no-root, pero simple con UID fijo)
RUN groupadd -g 10001 appuser \
 && useradd -u 10001 -g appuser -ms /bin/bash appuser

# Copiar requirements primero con las dependencias Python (cache)
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir --disable-pip-version-check -r requirements.txt

# Copiar SOLO el código necesario para el servicio
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
COPY ops/stacks/cron/monitoring.cron \
     /opt/monitoring/ops/stacks/cron/monitoring.cron

COPY ops/stacks/cron/docker-entrypoint.sh \
     /usr/local/bin/docker-entrypoint.sh

 # Logs internos y permisos runtime mínimos (build-time) fuera de /opt
 RUN chmod 755 /usr/local/bin/docker-entrypoint.sh \
 && chown appuser:appuser /usr/local/bin/docker-entrypoint.sh \
 && mkdir -p /opt/monitoring/logs \
 && chown appuser:appuser /opt/monitoring/logs \
 \
 # 🔑 CRÍTICO: logs escribibles
 && chmod 775 /opt/monitoring/logs \
 \
 && chmod 755 /opt/monitoring \
 && chmod 755 /opt/monitoring/src \
 && chmod 755 /opt/monitoring/scripts \
 \
 # Cron legible
 && chmod 644 /opt/monitoring/ops/stacks/cron/monitoring.cron \
 \
 # tmp necesario para runtime
 && chmod 1777 /tmp

# Usuario runtime no root
USER appuser

# Healthcheck para detectar fallos de cron
HEALTHCHECK CMD pgrep supercronic || exit 1

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
