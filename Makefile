# Makefile global para /opt/monitoring
# Uso: make <target>
# P.e.: make deploy

.PHONY: help all symlinks audit check-cron clean-logs snapshot up-services status logs build-base build-python build-cron deploy-cron deploy rebuild rebuild-all monitoring-net phase4-init

# Ruta base
BASE_DIR ?= ops/services

## 📌 Ayuda: lista de comandos disponibles
help:
	@echo "=== Makefile Global - Monitoring ==="
	@grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

## Ejecuta todas las tareas críticas de despliegue
all: symlinks audit  ## Configura symlinks y ejecuta auditoría

## Configura symlinks en /usr/local/bin (usando setup_symlinks.sh)
symlinks:  ## Crea symlinks en /usr/local/bin
	bash deployment/setup_symlinks.sh

## Ejecuta auditoría de binarios y guarda log en /var/log/auditoria_binarios.log
audit:  ## Ejecuta auditoría de binarios
	bash scripts/auditoria_binarios.sh >> /var/log/auditoria_binarios.log 2>&1
	@echo "[OK] Auditoría ejecutada, ver /var/log/auditoria_binarios.log"

## Muestra las entradas de cron actuales
check-cron:  ## Lista las tareas cron del sistema
	crontab -l

## Limpia todos los logs en /var/log (⚠️ cuidado en producción)
clean-logs:  ## Elimina logs del sistema
	rm -f /var/log/*.log
	@echo "[OK] Logs limpiados"

# --- Snapshots ---
snapshot:  ## Crea snapshot previo al despliegue. ATENCION: Esta acción mejor la ejecutamos manualmente en DigitalOcean
	@echo "Creando snapshot previo con fecha..."
	snap_name="predeploy-$$(date +%Y%m%d%H%M%S)" && \
	doctl compute snapshot create "$$snap_name" --droplet-id <DROPLET_ID>

# --- Servicios principales ---
up-services:
	cd $(BASE_DIR)/smtp_relay && make up

status:
	cd $(BASE_DIR)/smtp_relay && make status

# --- Logs ---
logs:  ## Muestra últimos registros y genera logs_summary.txt
	@echo "=== Mostrando últimos 20 registros ==="
	@sleep 40  # latencia para dar tiempo a que arranquen los contenedores
	@tail -n 20 /var/log/*.log
	@echo "=== Logs de todos los contenedores activos ==="
	@for c in $$(docker ps --format '{{.Names}}'); do \
		echo "\n===== 📦 $$c ====="; \
		docker logs $$c --tail=20 2>/dev/null || echo "⚠️  No se pudo obtener logs de $$c"; \
	done
#	@tail -n 20 /var/log/*.log | tee logs_summary.txt
#	@echo "Resumen generado en logs_summary.txt"
#	git add logs_summary.txt
#	git commit -m "logs latest $$(date +%Y%m%d%H%M%S)"
#	git push origin develop

# --- Builds (siempre con no-cache) ---
# --- FASE 4: Builds base y artefactos (no despliega contenedores) ---
# build-base: Construye la imagen base usando los Dockerfile ubicados en ops/docker

build-base:  ## FASE 4 - Construye imagen base sin cache (incluye requirements)
	# Usa Dockerfile en ops/docker pero contexto raíz porque Dockerfile.base
	# realiza "COPY requirements.txt" y "COPY . ." que requieren el repo root
	docker build --no-cache -f ops/docker/Dockerfile.base -t monitoring-base .

# build-python: usa el Dockerfile.python en ops/docker y el contexto del servicio python

build-python:  ## FASE 4 - Construye imagen Python sin cache (no despliega)
	# Usa Dockerfile en ops/docker; contexto raíz para evitar romper COPY que
	# puedan depender de rutas fuera de ops/docker (ver reporte de inconsistencias)
	docker build --no-cache -f ops/docker/Dockerfile.python -t monitoring-python .

# build-cron: usa el Dockerfile.cron en ops/docker y el contexto del servicio cron

build-cron:  ## FASE 4 - Construye imagen Cron sin cache (no despliega)
	# Usa Dockerfile en ops/docker; contexto raíz por las mismas razones que arriba
	docker build --no-cache -f ops/docker/Dockerfile.cron -t monitoring-cron .

# --- Red Docker idempotente requerida para la FASE 4 ---
monitoring-net:  ## FASE 4 - Crea la red Docker del proyecto de forma idempotente
	@docker network inspect monitoring-net >/dev/null 2>&1 || docker network create --driver bridge monitoring-net
	@echo "[OK] network monitoring-net ready"

# --- Target de inicialización de entorno base (FASE 4) ---
phase4-init: monitoring-net build-base build-python build-cron  ## FASE 4 - Prepara entorno base (no despliega contenedores)
	@echo "[OK] FASE 4 completa: red creada y builds realizados (sin despliegue)"

# --- Atajos de rebuild ---
rebuild: build-base build-python build-cron  ## Reconstruye todas las imágenes sin cache
rebuild-all: rebuild deploy-cron ## Reconstruye e inmediatamente redepliega cron

# --- Despliegue completo ---
deploy: up-services rebuild-all logs  ## Despliegue completo con rebuild y logs al final

# --- Cron ---
deploy-cron: build-base build-cron ## Despliega contenedor de cron jobs
	cd $(BASE_DIR)/cron && \
	docker-compose down -v && \
	docker-compose build --no-cache && \
	docker-compose up -d

# --- Python ---
deploy-python: build-base build-python ## Despliega contenedor python
	cd $(BASE_DIR)/python && \
	docker-compose down -v && \
#	docker-compose build --no-cache && \
	docker-compose up -d

# --- Observability Stack ---
deploy-observability:  ## Despliega el stack centralizado de Observability (Grafana, Loki, Promtail)
	@echo "=== [🚀] Desplegando Observability Stack ==="
	docker-compose -f $(BASE_DIR)/observability/docker-compose.yaml down -v
	docker-compose -f $(BASE_DIR)/observability/docker-compose.yaml build --no-cache
	docker-compose -f $(BASE_DIR)/observability/docker-compose.yaml up -d
	@echo "=== [✅] Observability Stack desplegado correctamente ==="

# --- Restauración de Backups ---
restore-backup:  ## Restaura la última copia de seguridad de la BBDD y muestra el log
	@echo "=== [🧩] Iniciando restauración de backup ==="
	bash $(BASE_DIR)/scripts/backup_restore.sh
	@echo "=== [📄] Log de restauración (/var/log/backup_restore.log): ==="
	@tail -n 20 /var/log/backup_restore.log
