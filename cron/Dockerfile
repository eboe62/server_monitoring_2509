# Imagen para cronjobs basada en la base
FROM monitoring-base

# Instalar supercronic y utilidades necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        bash \
        bc \
    && curl -L https://github.com/aptible/supercronic/releases/download/v0.2.29/supercronic-linux-amd64 \
         -o /usr/local/bin/supercronic \
    && chmod +x /usr/local/bin/supercronic \
    && rm -rf /var/lib/apt/lists/*

# Copiar cronfile y entrypoint
# COPY monitoring.cron /opt/monitoring/cronjobs/monitoring.cron
COPY docker-entrypoint.sh /usr/local/bin/

ENTRYPOINT ["docker-entrypoint.sh"]

