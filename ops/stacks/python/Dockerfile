# Imagen autónoma para ejecución de scripts Python
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/opt/monitoring/src

WORKDIR /opt/monitoring

# Paquetes con dependencias mínimas del sistema
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    bash \
    netcat-openbsd \
 && rm -rf /var/lib/apt/lists/*

# Usuario estándar (no-root, pero simple con UID fijo)
RUN groupadd -g 10001 appuser \
 && useradd -u 10001 -g appuser -ms /bin/bash appuser

# Copiar requirements primero con las dependencias Python (cache)
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir --no-compile -r requirements.txt

# Copiar SOLO el código necesario para el servicio
COPY src/ src/
COPY scripts/ scripts/

# Copiar entrypoint específico para la imagen Python
COPY ops/stacks/python/docker-entrypoint.sh \
    /usr/local/bin/docker-entrypoint.sh

# Permisos: crear dir para logs y asegurar ejecutables (build-time)
RUN chmod +x /usr/local/bin/docker-entrypoint.sh \
 && chmod +x scripts/*.py || true \
 && mkdir -p /opt/monitoring/logs \
 && chown appuser:appuser /opt/monitoring/logs \
 && chown appuser:appuser /usr/local/bin/docker-entrypoint.sh || true

# Usuario runtime no root
 USER appuser

ENTRYPOINT ["docker-entrypoint.sh"]
