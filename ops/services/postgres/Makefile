COMPOSE=docker compose
SERVICE=postgres


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


psql:
	@echo "[INFO] abriendo consola psql"
	$(COMPOSE) exec $(SERVICE) psql -U $$POSTGRES_USER $$POSTGRES_DB


backup:
	@echo "[INFO] realizando backup de la base de datos"
	mkdir -p backups
	$(COMPOSE) exec -T $(SERVICE) pg_dump -U $$POSTGRES_USER $$POSTGRES_DB > backups/postgres_backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "[OK] backup generado en ./backups"


restore:
	@echo "[INFO] restaurando backup"
	@read -p "Ruta del backup (.sql): " FILE; \
	cat $$FILE | $(COMPOSE) exec -T $(SERVICE) psql -U $$POSTGRES_USER $$POSTGRES_DB
	@echo "[OK] restauración finalizada"


test:
	@echo "[INFO] comprobando conectividad a postgres"
	$(COMPOSE) exec $(SERVICE) pg_isready -U $$POSTGRES_USER


size:
	@echo "[INFO] tamaño de la base de datos"
	$(COMPOSE) exec $(SERVICE) psql -U $$POSTGRES_USER -d $$POSTGRES_DB -c \
	"SELECT pg_size_pretty(pg_database_size(current_database()));"
