# Imagen para ejecutar scripts Python
FROM monitoring-base

# Copiar entrypoint específico para la imagen Python
COPY stacks/python/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

RUN chmod +x /usr/local/bin/docker-entrypoint.sh

WORKDIR /opt/monitoring

ENTRYPOINT ["docker-entrypoint.sh"]
