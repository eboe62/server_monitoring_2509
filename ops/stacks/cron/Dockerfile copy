# Imagen para cronjobs basada en la base
FROM monitoring-base:local

# Instalar utilidades necesarias y supercronic
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    curl \
    bc \
 && curl -L https://github.com/aptible/supercronic/releases/download/v0.2.29/supercronic-linux-amd64 \
    -o /usr/local/bin/supercronic \
 && chmod +x /usr/local/bin/supercronic \
 && rm -rf /var/lib/apt/lists/*

# Copiar entrypoint
COPY ops/stacks/cron/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENV PYTHONPATH=/opt/monitoring/src

WORKDIR /opt/monitoring

# Healthcheck para detectar fallo de cron
HEALTHCHECK CMD pgrep supercronic || exit 1

ENTRYPOINT ["docker-entrypoint.sh"]
