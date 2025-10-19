# Makefile global para /opt/monitoring
# Uso: make <target>
# P.e.: make deploy

.PHONY: help all symlinks audit check-cron clean-logs snapshot up-services status logs build-base build-python build-cron deploy-cron deploy rebuild rebuild-all

# Ruta base
BASE_DIR := /opt/monitoring

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
#	@tail -n 20 /var/log/*.log | tee logs_summary.txt
#	@echo "Resumen generado en logs_summary.txt"
#	git add logs_summary.txt
#	git commit -m "logs latest $$(date +%Y%m%d%H%M%S)"
#	git push origin develop

# --- Builds (siempre con no-cache) ---
# --- Base ---
build-base:  ## Construye imagen base sin cache (incluye requirements) y se usa como caché para las demás imágenes (cron, python, ...)
	docker build --no-cache -f Dockerfile.base -t monitoring-base .

build-python:  ## Construye imagen Python sin cache
	docker build --no-cache -t monitoring-python $(BASE_DIR)/python

build-cron:  ## Construye imagen Cron sin cache
	docker build --no-cache -t monitoring-cron $(BASE_DIR)/cron

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
