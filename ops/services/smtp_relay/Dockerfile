# Dockerfile for smtp-relay
ARG BASE_IMAGE="boky/postfix:3.6.0@sha256:aafc772384232497bed875e1eb66b4d3e54ba1ebc86e2e185a6dc1dbc48182ef"
FROM ${BASE_IMAGE}

ARG IMAGE_VERSION="v1.0.0"
ARG BUILD_DATE=""

LABEL org.opencontainers.image.title="monitoring-smtp-relay"
LABEL org.opencontainers.image.version="${IMAGE_VERSION}"
LABEL org.opencontainers.image.created="${BUILD_DATE}"

# Scripts
COPY config/patch-postfix.sh \
    /patch-postfix.sh

# ⚠️ Asegurar directorios necesarios
RUN chmod +x /patch-postfix.sh \
 && mkdir -p /var/log \
 && mkdir -p /run/secrets-copy

# Entry
ENTRYPOINT ["/patch-postfix.sh"]
