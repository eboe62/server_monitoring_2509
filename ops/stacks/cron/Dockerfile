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
    docker-cli \
    bash \
    coreutils \
 && rm -rf /var/lib/apt/lists/*

# Crear usuario no root (UID fijo)
RUN groupadd -g 10001 appuser \
 && useradd -u 10001 -g appuser -ms /bin/bash appuser

# Supercronic (vendor + checksum)
COPY ops/vendor/supercronic /tmp/supercronic

RUN cd /tmp/supercronic \
 && sha256sum -c SHA256SUMS \
 && mv supercronic-linux-amd64 /usr/local/bin/supercronic \
 && chmod +x /usr/local/bin/supercronic \
 && /usr/local/bin/supercronic -test /dev/null \
 && rm -rf /tmp/supercronic

# Dependencias Python
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir --no-compile -r requirements.txt

# Copiar código del servicio
COPY src/ src/
COPY scripts/ scripts/

# Copiar entrypoint
COPY ops/stacks/cron/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Healthcheck para detectar fallos de cron
HEALTHCHECK CMD pgrep supercronic || exit 1

ENTRYPOINT ["docker-entrypoint.sh"]
