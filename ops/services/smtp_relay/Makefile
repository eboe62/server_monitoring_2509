COMPOSE=docker-compose
SERVICE=smtp-relay

up:
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down

restart: down up

status:
	$(COMPOSE) ps $(SERVICE)

logs:
	$(COMPOSE) logs -f $(SERVICE)

health:
	docker inspect --format='Health: {{.State.Health.Status}}' $(SERVICE)

test:
	python3 ops/services/smtp_relay/scripts/test_mail.py

update-credentials:
	@read -p "Nuevo EMAIL_USER: " USER; \
	read -p "Nuevo EMAIL_PASS: " PASS; \
	echo $$USER > ops/services/smtp_relay/secrets/smtp_user; \
	echo $$PASS > ops/services/smtp_relay/secrets/smtp_pass; \
	chmod 600 ops/services/smtp_relay/secrets/smtp_*; \
	echo "[INFO] Credenciales actualizadas."; \
	$(COMPOSE) restart $(SERVICE)

