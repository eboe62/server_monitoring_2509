# Imagen autónoma para ejecución de cronjobs
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/opt/monitoring/src

WORKDIR /opt/monitoring

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    curl \
    bc \
    docker-cli \
    bash \
 && rm -rf /var/lib/apt/lists/*

COPY ops/vendor/supercronic/supercronic-linux-amd64 /usr/local/bin/supercronic

RUN chmod +x /usr/local/bin/supercronic \
 && test -x /usr/local/bin/supercronic \
 && /usr/local/bin/supercronic -test /dev/null || true

#RUN echo "87625cd179eff21226f0be6f2f47dd357037064598e6c1f9ffcbd0335d402bbd  /tmp/supercronic/supercronic-linux-amd64" | sha256sum -c - \
# && mv /tmp/supercronic/supercronic-linux-amd64 /usr/local/bin/supercronic \
# && chmod +x /usr/local/bin/supercronic \
# && /usr/local/bin/supercronic --version

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
