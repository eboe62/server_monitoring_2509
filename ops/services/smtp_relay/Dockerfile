# Dockerfile
FROM boky/postfix

COPY ops/services/smtp_relay/patch-postfix.sh /patch-postfix.sh
RUN chmod +x /patch-postfix.sh

ENTRYPOINT ["/patch-postfix.sh"]

