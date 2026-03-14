COMPOSE=docker compose
SERVICE=smtp-relay

SECRETS_DIR=ops/services/smtp_relay/secrets
TEST_SCRIPT=ops/services/smtp_relay/scripts/test_mail.py


up:
	@echo "[INFO] levantando servicio $(SERVICE)"
	$(COMPOSE) up -d --build
	@echo "[OK] servicio iniciado"


down:
	@echo "[INFO] deteniendo servicio $(SERVICE)"
	$(COMPOSE) down
	@echo "[OK] servicio detenido"


restart:
	@echo "[INFO] reiniciando servicio $(SERVICE)"
	$(COMPOSE) restart $(SERVICE)
	@echo "[OK] servicio reiniciado"


status:
	@echo "[INFO] estado del servicio"
	$(COMPOSE) ps $(SERVICE)


logs:
	@echo "[INFO] mostrando logs del servicio"
	$(COMPOSE) logs -f $(SERVICE)


health:
	@echo "[INFO] comprobando estado de salud"
	@docker inspect --format='Health: {{.State.Health.Status}}' $(SERVICE) 2>/dev/null || \
	echo "[WARN] contenedor no encontrado o sin healthcheck"


test:
	@echo "[INFO] ejecutando test de envío de correo"
	python3 $(TEST_SCRIPT)
	@echo "[OK] test ejecutado"


update-credentials:
	@echo "[INFO] actualización de credenciales SMTP"
	@read -p "Nuevo EMAIL_USER: " USER; \
	read -s -p "Nuevo EMAIL_PASS: " PASS; echo ""; \
	echo $$USER > $(SECRETS_DIR)/smtp_user; \
	echo $$PASS > $(SECRETS_DIR)/smtp_pass; \
	chmod 600 $(SECRETS_DIR)/smtp_*; \
	echo "[OK] credenciales actualizadas"; \
	$(COMPOSE) restart $(SERVICE)
