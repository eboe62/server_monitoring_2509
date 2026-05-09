# Dockerfile
FROM boky/postfix

# Scripts
COPY config/patch-postfix.sh \
    /patch-postfix.sh

COPY scripts/test_mail.py \
    /scripts/test_mail.py

RUN chmod +x /patch-postfix.sh

# ⚠️ Asegurar directorios necesarios
RUN mkdir -p /var/log \
 && mkdir -p /run/secrets-copy

# Entry
ENTRYPOINT ["/patch-postfix.sh"]
