# Dockerfile
FROM boky/postfix

COPY config/patch-postfix.sh /patch-postfix.sh
COPY scripts/test_mail.py /scripts/test_mail.py

RUN chmod +x /patch-postfix.sh

ENTRYPOINT ["/patch-postfix.sh"]
