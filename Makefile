# ==========================================
# Makefile Global - Monitoring Platform
# ==========================================

PROJECT = monitoring
COMPOSE = docker compose

SERVICE_DIR = ops/services
STACK_DIR   = ops/stacks

SERVICE_STACKS = postgres smtp_relay
INFRA_STACKS   = python cron observability
STACKS = $(SERVICE_STACKS) $(INFRA_STACKS)

AUDIT_SCRIPT = ops/audit/audit_repo_host.sh
DEV_COMPOSE = compose.dev.yml

# ------------------------------------------
# Validación STACK
# ------------------------------------------

define validate_stack
@if [ -z "$(STACK)" ]; then \
	echo "[ERROR] Debe especificar STACK=<nombre>"; \
	exit 1; \
fi; \
if ! echo "$(STACKS)" | grep -w "$(STACK)" >/dev/null; then \
	echo "[ERROR] STACK inválido: $(STACK)"; \
	echo "Stacks disponibles: $(STACKS)"; \
	exit 1; \
fi
endef

define stack_path
if [ -d "$(SERVICE_DIR)/$(STACK)" ]; then \
	printf "%s" "$(SERVICE_DIR)/$(STACK)"; \
else \
	printf "%s" "$(STACK_DIR)/$(STACK)"; \
fi
endef

.PHONY: help build build-base build-python build-cron \
clean clean-docker monitoring-net phase4-init \
stack-up stack-down stack-restart stack-status stack-logs \
deploy rebuild rebuild-all doctor audit git-log \
dev-up dev-down

# ------------------------------------------
# Help
# ------------------------------------------

help:
	@echo ""
	@echo "=== Monitoring Platform ==="
	@echo ""
	@echo "Stacks disponibles:"
	@echo "  $(STACKS)"
	@echo ""
	@echo "Ejemplos:"
	@echo "  make stack-up STACK=postgres"
	@echo "  make stack-up STACK=observability"
	@echo ""

# ------------------------------------------
# Git utilities
# ------------------------------------------

git-log: ## Historial git resumido
	@echo ""
	@echo "=== Git history (últimos 25 commits) ==="
	sudo git log --oneline --decorate --graph --all -n 25

# ------------------------------------------
# Auditoría
# ------------------------------------------

audit: ## Ejecuta auditoría repositorio + host
	@echo ""
	@echo "=== Ejecutando auditoría ==="
	chmod +x $(AUDIT_SCRIPT)
	./$(AUDIT_SCRIPT)

# ------------------------------------------
# Infraestructura base
# ------------------------------------------

monitoring-net:  ## Crea la red Docker si no existe
	@docker network inspect monitoring-net >/dev/null 2>&1 || \
	docker network create monitoring-net
	@echo "[OK] network monitoring-net ready"

# ------------------------------------------
# Limpieza
# ------------------------------------------

clean:
	@echo "[INFO] limpiando imágenes dangling"
	docker image prune -f

clean-docker:
	@echo "[INFO] limpieza completa Docker"
	docker container prune -f
	docker image prune -f
	docker builder prune -f

# ------------------------------------------
# Builds
# ------------------------------------------

build-base:
	docker build --no-cache -f ops/images/base/Dockerfile -t monitoring-base .

build-python:
	docker build --no-cache -f ops/stacks/python/Dockerfile -t monitoring-python .

build-cron:
	docker build --no-cache -f ops/stacks/cron/Dockerfile -t monitoring-cron .

build: build-base build-python build-cron  ## Construye todas las imágenes
	@echo "[OK] imágenes construidas"

phase4-init: monitoring-net build  ## Inicialización completa
	@echo "[OK] entorno inicializado"

# ------------------------------------------
# Gestión genérica de micro-stacks
# ------------------------------------------

stack-up:  ## Levanta un stack (STACK=nombre)
	$(call validate_stack)
	@DIR=$$( $(call stack_path) ); \
	echo "=== 🚀 Levantando stack $(STACK) ==="; \
	cd $$DIR && $(COMPOSE) up -d --build

stack-down:  ## Detiene un stack
	$(call validate_stack)
	@DIR=$$( $(call stack_path) ); \
	echo "=== ⛔ Parando stack $(STACK) ==="; \
	cd $$DIR && $(COMPOSE) down

stack-restart:  ## Reinicia un stack
	$(call validate_stack)
	@DIR=$$( $(call stack_path) ); \
	echo "=== 🔁 Reiniciando stack $(STACK) ==="; \
	cd $$DIR && $(COMPOSE) restart

stack-status:  ## Estado de un stack
	$(call validate_stack)
	@DIR=$$( $(call stack_path) ); \
	echo "=== Estado stack $(STACK) ==="; \
	cd $$DIR && $(COMPOSE) ps

stack-logs:
	$(call validate_stack)
	@DIR=$$( $(call stack_path) ); \
	cd $$DIR && $(COMPOSE) logs -f

# ------------------------------------------
# Despliegue completo
# ------------------------------------------

deploy: build
	@set -e; \
	echo "=== 🚀 Despliegue completo ==="; \
	for s in $(SERVICE_STACKS); do \
		echo "→ desplegando $$s"; \
		cd $(SERVICE_DIR)/$$s && $(COMPOSE) up -d --build; \
	done; \
	for s in $(INFRA_STACKS); do \
		echo "→ desplegando $$s"; \
		cd $(STACK_DIR)/$$s && $(COMPOSE) up -d --build; \
	done; \
	echo "[OK] despliegue finalizado"

dev-up:
	$(COMPOSE) -f $(DEV_COMPOSE) up -d

dev-down:
	$(COMPOSE) -f $(DEV_COMPOSE) down

# ------------------------------------------
# Rebuild
# ------------------------------------------

rebuild: clean build
	@echo "[OK] rebuild realizado"

rebuild-all:
	make clean-docker
	make build
	make deploy

# ------------------------------------------
# Logs
# ------------------------------------------

logs:  ## Muestra logs recientes del sistema y contenedores
	@echo "=== Logs del sistema ==="
	@echo ""
	@echo "=== Logs contenedores ==="
	@for c in $$(docker ps --format '{{.Names}}'); do \
		echo "===== $$c ====="; \
		docker logs $$c --tail=20; \
	done

# ------------------------------------------
# Diagnóstico
# ------------------------------------------

doctor:  ## Verifica estado del entorno
	@echo ""
	@echo "=== Diagnóstico del sistema ==="
	@echo ""

	@echo "[1] Docker instalado:"
	@docker --version || echo "Docker NO instalado"

	@echo ""
	@echo "[2] Docker Compose:"
	@docker compose version || echo "Docker Compose V2 NO disponible"

	@echo ""
	@echo "[3] Contenedores activos:"
	@docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

	@echo ""
	@echo "[4] Red monitoring-net:"
	@docker network inspect monitoring-net >/dev/null 2>&1 && \
	echo "OK" || echo "No existe"

	@echo ""
	@echo "[5] Espacio en disco:"
	@df -h /

	@echo ""
	@echo "[6] Uso Docker:"
	@docker system df

	@echo ""
	@echo "[7] Volúmenes Docker:"
	@docker volume ls

	@echo ""
	@echo "[8] Redes Docker:"
	@docker network ls | grep monitoring || true

	@echo ""
	@echo "[9] Contenedores de la plataforma:"
	@docker ps --format "{{.Names}}" | grep monitoring || echo "Ninguno activo"

	@echo ""
	@echo "[10] Stacks disponibles:"
	@echo "$(STACKS)"

	@echo ""
	@echo "=== Fin diagnóstico ==="

health:
	@echo "=== HEALTH CHECK ==="
	@docker ps --format "table {{.Names}}\t{{.Status}}"
	@echo ""
	@echo "[CHECK] Containers unhealthy:"
	@docker ps --filter "health=unhealthy"
	@echo ""
	@echo "[CHECK] Restarting containers:"
	@docker ps --filter "status=restarting"

# ------------------------------------------
# Debug / Operabilidad
# ------------------------------------------

debug-shell: ## Acceso shell a contenedor (STACK opcional)
	@STACK_NAME=$${STACK:-python}; \
	if ! echo "$(STACKS)" | grep -w "$$STACK_NAME" >/dev/null; then \
		echo "[ERROR] STACK inválido: $$STACK_NAME"; \
		echo "Stacks disponibles: $(STACKS)"; \
		exit 1; \
	fi; \
	echo "=== Debug shell en $$STACK_NAME ==="; \
	docker exec -it monitoring-$$STACK_NAME sh || \
	echo "[ERROR] contenedor no disponible"

debug-net: ## Verifica resolución DNS entre contenedores
	@echo "=== Test DNS interno ==="
	@docker exec monitoring-python getent hosts monitoring-postgres || echo "[ERROR] DNS fallo"

debug-ports: ## Ver puertos expuestos en host
	@echo "=== Puertos escuchando en host ==="
	ss -tulpn

debug-docker: ## Estado detallado Docker
	@echo "=== Docker inspect resumido ==="
	@docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

debug-logs: ## Logs rápidos de todos los contenedores
	@for c in $$(docker ps --format '{{.Names}}'); do \
		echo "===== $$c ====="; \
		docker logs $$c --tail=50; \
	done

debug-exec: ## Ejecutar comando en contenedor (STACK opcional)
	@STACK_NAME=$${STACK:-python}; \
	if ! echo "$(STACKS)" | grep -w "$$STACK_NAME" >/dev/null; then \
		echo "[ERROR] STACK inválido: $$STACK_NAME"; \
		exit 1; \
	fi; \
	if [ -z "$(CMD)" ]; then \
		echo "[ERROR] Debe especificar CMD='comando'"; \
		exit 1; \
	fi; \
	echo "=== Ejecutando en $$STACK_NAME ==="; \
	docker exec -it monitoring-$$STACK_NAME sh -c "$(CMD)"

# ------------------------------------------
# Debug container (toolbox)
# ------------------------------------------

DEBUG_IMAGE = nicolaka/netshoot
DEBUG_CONTAINER = monitoring-debug

debug-toolbox-up: ## Levanta contenedor de debugging en monitoring-net
	@echo "=== Iniciando contenedor debug ==="
	@docker rm -f $(DEBUG_CONTAINER) >/dev/null 2>&1 || true
	@docker run -d --name $(DEBUG_CONTAINER) \
		--network monitoring-net \
		$(DEBUG_IMAGE) sleep infinity
	@echo "[OK] contenedor debug activo"

debug-toolbox-shell: ## Shell en contenedor debug
	@docker exec -it $(DEBUG_CONTAINER) sh

debug-toolbox-down: ## Elimina contenedor debug
	@docker rm -f $(DEBUG_CONTAINER) || true
	@echo "[OK] contenedor debug eliminado"
