# Imagen autónoma para ejecución de scripts Python
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/opt/monitoring/src

WORKDIR /opt/monitoring

# Dependencias del sistema
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    docker-cli \
    bash \
    netcat-openbsd \
 && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero (cache)
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir --no-compile -r requirements.txt

# Copiar SOLO lo necesario para el servicio
COPY src/ src/
COPY scripts/ scripts/

# Copiar entrypoint específico para la imagen Python
COPY ops/stacks/python/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

RUN chmod +x /usr/local/bin/docker-entrypoint.sh \
 && chmod +x scripts/healthcheck.py

ENTRYPOINT ["docker-entrypoint.sh"]
