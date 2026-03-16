# Imagen para ejecutar scripts Python
FROM monitoring-base

# Copiar entrypoint específico para la imagen Python
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENV PYTHONPATH=/opt/monitoring/src

WORKDIR /opt/monitoring

ENTRYPOINT ["docker-entrypoint.sh"]
