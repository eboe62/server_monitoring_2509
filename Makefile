# Makefile global para /opt/monitoring
# Uso: make <target>
# Ej: make symlinks

.PHONY: help all symlinks audit check-cron logs clean-logs

## 📌 Ayuda: lista de comandos disponibles
help:
	@echo "=== Makefile Global - Monitoring ==="
	@grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

## Ejecuta todas las tareas críticas de despliegue
all: symlinks audit  ## Configura symlinks y ejecuta auditoría

## Configura symlinks en /usr/local/bin (usando setup_symlinks.sh)
symlinks:
	bash deployment/setup_symlinks.sh

## Ejecuta auditoría de binarios y guarda log en /var/log/auditoria_binarios.log
audit:
	bash scripts/auditoria_binarios.sh >> /var/log/auditoria_binarios.log 2>&1
	@echo "[OK] Auditoría ejecutada, ver /var/log/auditoria_binarios.log"

## Muestra las entradas de cron actuales
check-cron:
	crontab -l

## Muestra logs recientes
logs:
	tail -n 20 /var/log/*.log

## Limpia todos los logs en /var/log (⚠️ cuidado en producción)
clean-logs:
	rm -f /var/log/*.log
	@echo "[OK] Logs limpiados"

