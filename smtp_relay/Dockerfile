# Dockerfile
FROM boky/postfix

COPY config/patch-postfix.sh /patch-postfix.sh
RUN chmod +x /patch-postfix.sh

ENTRYPOINT ["/patch-postfix.sh"]

