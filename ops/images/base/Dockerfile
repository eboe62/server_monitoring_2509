# Imagen base con Python y dependencias comunes
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/opt/monitoring/src

WORKDIR /opt/monitoring

# Instalar dependencias del sistema y limpiar cache
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    docker-cli \
    bash \
 && rm -rf /var/lib/apt/lists/*

# Copiar primero requirements para aprovechar cache de Docker
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir --no-compile -r requirements.txt

# ---- Copiar estructura del proyecto de forma explícita ----
COPY README.md .
COPY __init__.py .

COPY src/ src/
COPY scripts/ scripts/
COPY ops/ ops/
