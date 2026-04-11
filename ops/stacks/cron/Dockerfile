# Imagen autónoma para ejecución de cronjobs
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/opt/monitoring/src

WORKDIR /opt/monitoring

# Instalar utilidades necesarias, supercronic y limpiar cache
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    curl \
    bc \
    docker-cli \
    bash \
 && curl -L --retry 5 --retry-delay 5 --retry-connrefused \
    https://github.com/aptible/supercronic/releases/download/v0.2.29/supercronic-linux-amd64 \
    -o /usr/local/bin/supercronic \
 && chmod +x /usr/local/bin/supercronic \
 && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir --no-compile -r requirements.txt

# Copiar SOLO lo necesario para el servicio
COPY src/ src/
COPY scripts/ scripts/

# Copiar entrypoint
COPY ops/stacks/cron/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Healthcheck para detectar fallo de cron
HEALTHCHECK CMD pgrep supercronic || exit 1

ENTRYPOINT ["docker-entrypoint.sh"]
