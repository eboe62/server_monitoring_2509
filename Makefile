# ==========================================
# Makefile Global - Monitoring Platform
# Compatible con Docker Compose V2
# Ubicación: /opt/monitoring/Makefile
# ==========================================
# ------------------------------------------
# Configuración base
# ------------------------------------------

BASE_DIR ?= ops/services
COMPOSE = docker compose
PROJECT = monitoring

# Micro-stacks disponibles
STACKS = smtp_relay cron postgres python observability

# Validación de STACK si se usa en targets stack-*
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

.PHONY: help all build build-base build-python build-cron \
        monitoring-net phase4-init \
        stack-up stack-down stack-restart stack-status stack-logs \
        deploy rebuild rebuild-all \
        logs clean-logs check-cron doctor

# ------------------------------------------
# 📌 Ayuda
# ------------------------------------------

help:
	@echo ""
	@echo "=== Monitoring Platform ==="
	@echo ""
	@echo "Inicialización:"
	@echo "  make phase4-init        → prepara entorno base (red + builds)"
	@echo ""
	@echo "Builds:"
	@echo "  make build              → construye todas las imágenes"
	@echo "  make rebuild            → rebuild completo"
	@echo ""
	@echo "Gestión de stacks:"
	@echo "  make stack-up STACK=x"
	@echo "  make stack-down STACK=x"
	@echo "  make stack-restart STACK=x"
	@echo "  make stack-status STACK=x"
	@echo "  make stack-logs STACK=x"
	@echo ""
	@echo "Stacks disponibles:"
	@echo "  $(STACKS)"
	@echo ""
	@echo "Operaciones globales:"
	@echo "  make deploy"
	@echo "  make logs"
	@echo "  make doctor"
	@echo ""

# ------------------------------------------
# Infraestructura base (FASE 4)
# ------------------------------------------

monitoring-net:  ## Crea la red Docker si no existe
	@docker network inspect monitoring-net >/dev/null 2>&1 || \
	docker network create --driver bridge monitoring-net
	@echo "[OK] network monitoring-net ready"

# ------------------------------------------
# Builds
# ------------------------------------------

build-base:  ## Construye imagen base
	docker build --no-cache -f ops/docker/Dockerfile.base -t monitoring-base .

build-python:  ## Construye imagen python runtime
	docker build --no-cache -f ops/docker/Dockerfile.python -t monitoring-python .

build-cron:  ## Construye imagen cron runtime
	docker build --no-cache -f ops/docker/Dockerfile.cron -t monitoring-cron .

build: build-base build-python build-cron  ## Construye todas las imágenes
	@echo "[OK] imágenes construidas"

phase4-init: monitoring-net build  ## Inicialización completa FASE 4
	@echo "[OK] FASE 4 inicializada"

# ------------------------------------------
# Gestión genérica de micro-stacks
# ------------------------------------------

stack-up:  ## Levanta un stack (STACK=nombre)
	$(call validate_stack)
	@echo "=== 🚀 Levantando stack $(STACK) ==="
	cd $(BASE_DIR)/$(STACK) && $(COMPOSE) up -d --build

stack-down:  ## Detiene un stack
	$(call validate_stack)
	@echo "=== ⛔ Parando stack $(STACK) ==="
	cd $(BASE_DIR)/$(STACK) && $(COMPOSE) down -v

stack-restart:  ## Reinicia un stack
	$(call validate_stack)
	@echo "=== 🔁 Reiniciando stack $(STACK) ==="
	cd $(BASE_DIR)/$(STACK) && $(COMPOSE) restart

stack-status:  ## Estado de un stack
	$(call validate_stack)
	cd $(BASE_DIR)/$(STACK) && $(COMPOSE) ps

stack-logs:  ## Logs de un stack
	$(call validate_stack)
	cd $(BASE_DIR)/$(STACK) && $(COMPOSE) logs -f

# ------------------------------------------
# Despliegue completo
# ------------------------------------------

deploy: build
	@echo "=== 🚀 Despliegue completo ==="
	@for s in $(STACKS); do \
		if [ -d "$(BASE_DIR)/$$s" ]; then \
			echo "→ desplegando $$s"; \
			cd $(BASE_DIR)/$$s && $(COMPOSE) up -d --build; \
		fi; \
	done
	@echo "[OK] despliegue finalizado"

rebuild: build
	@echo "[OK] rebuild realizado"

rebuild-all:
	make build
	make deploy

# ------------------------------------------
# Logs
# ------------------------------------------

logs:  ## Muestra logs recientes del sistema y contenedores
	@echo "=== Logs del sistema ==="
	@tail -n 20 /var/log/*.log 2>/dev/null || true
	@echo ""
	@echo "=== Logs contenedores ==="
	@for c in $$(docker ps --format '{{.Names}}'); do \
		echo "\n===== $$c ====="; \
		docker logs $$c --tail=20 2>/dev/null || true; \
	done

# ------------------------------------------
# Utilidades
# ------------------------------------------

clean-logs:  ## Limpia logs del host
	rm -f /var/log/*.log
	@echo "[OK] logs eliminados"

check-cron:  ## Lista tareas cron del sistema
	crontab -l

# ------------------------------------------
# Diagnóstico del sistema
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
	@echo "=== Fin diagnóstico ==="
