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

# ------------------------------------------
# Help
# ------------------------------------------

.PHONY: help

help:
	@echo ""
	@echo "=== Monitoring Platform ==="
	@echo ""
	@echo "CORE:"
	@echo "  make audit        → Validación estructural (build-time)"
	@echo "  make status       → Snapshot del sistema"
	@echo "  make health       → Estado runtime (healthchecks)"
	@echo "  make test         → Validación funcional"
	@echo "  make debug        → Herramientas de diagnóstico"
	@echo ""
	@echo "STACKS:"
	@echo "  make stack-up STACK=<name>"
	@echo "  make stack-down STACK=<name>"
	@echo "  make stack-restart STACK=<name>"
	@echo "  make stack-status STACK=<name>"
	@echo "  make stack-logs STACK=<name>"
	@echo ""
	@echo "Ejemplos:"
	@echo "  make stack-up STACK=postgres"
	@echo "  make stack-up STACK=observability"
	@echo ""
	@echo "Stacks disponibles: $(STACKS)"
	@echo ""

# ------------------------------------------
# AUDIT (build-time)
# ------------------------------------------
## Ejecuta diagnóstico estructural (offline)
## Momento: build-time
## Proposito: ¿Está bien construido el sistema?
## Tipo: estático
## ✔ Diagnóstico profundo
## ✔ Busca problemas estructurales
## ✔ Evalúa cumplimiento ADR

.PHONY: audit

audit:
	@echo ""
	@echo "=== Ejecutando auditoría (estructura / ADR) ==="
	chmod +x $(AUDIT_SCRIPT)
	./$(AUDIT_SCRIPT)

# ------------------------------------------
# STATUS (snapshot)
# ------------------------------------------
## Verifica estado global
## Momento: runtime snapshot
## Proposito: ¿Que hay ahora mismo?
## Tipo: snapshot
## ✔ Estado del sistema en runtime
## ✔ Snapshot global
## Analiza:
## - docker version
## - disk
## - network
## - containers

.PHONY: status

status:
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
	@echo "[4] Redes Docker para monitoring (comprobación):"
	@for n in backend-net observability-net restricted-net; do \
		docker network inspect $$n >/dev/null 2>&1 && echo "$$n: OK" || echo "$$n: No existe"; \
	done

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
	@echo ""

# ------------------------------------------
# HEALTH (runtime state)
# ------------------------------------------
## Realizachequeo activo + autorepair
## Momento: runtime behavior
## Proposito: ¿Está funcionando correctamente ahora mismo?
## Tipo: dinámico
## ✔ Estado dinámico
## ✔ Problemas operativos
## Analiza:
## - unhealthy
## - restart
## - auto-recovery

.PHONY: health

health:
	@echo "=== HEALTH CHECK ==="

debug-docker: ## Estado detallado Docker
	@echo "=== Docker inspect resumido ==="
	@echo "\n[Containers]"
	@docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
	@echo ""

	@echo "[CHECK] Containers unhealthy:"
	@docker ps --filter "health=unhealthy"
	@echo ""

	@echo "[CHECK] Restarting containers:"
	@docker ps --filter "status=restarting"
	@echo ""

# ------------------------------------------
# TEST (validación funcional)
# test = validación automatizable (CI/CD, reproducible, determinista)
# Características:
# - tiene PASS / FAIL
# - se puede integrar en pipeline
# - no requiere contexto humano
# - objetivo: validar sistema
# Los tests pueden usar herramientas de debug pero siguen siendo tests
# Ejemplo:
# - Kubernetes usa pods debug para tests
# - Chaos engineering usa tooling externo
# ------------------------------------------
.PHONY: test

CI ?= false

WAIT_SCRIPT=./scripts/wait_for_health.sh

test:
	@echo "=== TEST COMMANDS ==="
	@echo "make test-resilience-completo"
	@echo "make test-resilience-restart"
	@echo "make test-resilience-db"
	@echo "make test-resilience-network"
	@echo "make test-resilience-observability"
	@echo "make test-python-health"
	@echo "make test-cron-execution"
	@echo "make test-observability-core"
	@echo "make test-smtp-all"
	@echo "make test-network"
	@echo ""

.PHONY: clean-dangling validate-dockerfiles

clean-dangling:
	@echo "Cleaning dangling images (docker image prune -f)"
	@docker image prune -f || true

validate-dockerfiles:
	@chmod +x ops/audit/validate_dockerfiles.sh
	@./ops/audit/validate_dockerfiles.sh

# --- Resilience

.PHONY: test-resilience-completo

test-resilience-completo: test-resilience-inicio test-resilience-restart test-resilience-db test-resilience-network test-resilience-observability test-resilience-fin

test-resilience-inicio:
	@echo "\n=== TEST RESILIENCIA SRE (Site Reliability Engineering) ==="
	@echo ""
	# ----------------------------------------
	# [0] Estado inicial
	# ----------------------------------------
	@echo "[0] Estado inicial"
	@docker ps
	@echo ""

test-resilience-restart:
	# ----------------------------------------
	# [1] CRASH REAL proceso (PID 1)
	# ----------------------------------------
## Testea:
## - kill -9
## - espera running
## - espera healthy

	@echo "[1] CRASH proceso interno (PID 1)"

	@docker exec monitoring-python sh -c "kill -9 1" || true

	# --- VALIDAR RESTART (no health aún) ---
	@echo "esperando restart (running)..."
	@timeout 30 sh -c '\
	until [ "$$(docker inspect monitoring-python --format="{{.State.Status}}")" = "running" ]; do \
		sleep 2; \
	done' || \
	(echo "[FAIL] contenedor no se ha reiniciado" && \
	docker inspect monitoring-python --format="State={{.State.Status}}" && exit 1)

	@echo "[ OK ] contenedor reiniciado"

	# --- VALIDAR HEALTH POST-RESTART ---
	@echo "esperando recuperación health (healthy)..."

	@timeout 60 sh -c '\
	until [ "$$(docker inspect monitoring-python --format="{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}")" = "healthy" ]; do \
		sleep 2; \
	done' || \
	(echo "[FAIL] contenedor no alcanza healthy tras restart" && \
	docker inspect monitoring-python --format="State={{.State.Status}} Health={{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}" && exit 1)

	@echo "[ OK ] restart + recovery OK"

	# Debug
	@echo "[INFO] estado tras restart:"
	@docker inspect monitoring-python --format='State={{.State.Status}} Health={{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}'
	@echo ""

test-resilience-db:
	# ----------------------------------------
	# [2] FALLO DB
	# ----------------------------------------
## Testea:
## - stop postgres
## - detectar pérdida REAL de conectividad
## - start postgres
## - espera healthy
## - esperar recuperación REAL (DNS + TCP)

	@echo "[2] Simulación fallo DB"

	@docker stop monitoring-postgres || true

	@echo "[STEP] esperando pérdida real de conectividad..."

	@timeout 60 sh -c '\
	until ! docker exec monitoring-python sh -c "getent hosts monitoring-postgres >/dev/null 2>&1 && nc -z monitoring-postgres 5432" >/dev/null 2>&1; do \
		echo "[DEBUG] postgres sigue accesible"; \
		sleep 2; \
	done' || \
	(echo "[FAIL] no se detecta caída real de DB" && exit 1)

	@echo "[ OK ] degradación detectada (conectividad perdida)"

	@docker start monitoring-postgres

	@echo "[STEP] esperando recuperación real..."

	# --- FASE 1: DNS ---
	@timeout 60 sh -c '\
	until docker exec monitoring-python sh -c "getent hosts monitoring-postgres" >/dev/null 2>&1; do \
		echo "[DEBUG] esperando DNS..."; \
		sleep 2; \
	done' || \
	(echo "[FAIL] DNS no recupera" && exit 1)

	# --- FASE 2: TCP + warmup Postgres ---
	@timeout 180 sh -c '\
	ok=0; \
	for i in $$(seq 1 120); do \
		if docker exec monitoring-python sh -c "nc -z monitoring-postgres 5432" >/dev/null 2>&1; then \
			ok=$$((ok+1)); \
			echo "[DEBUG] TCP OK ($$ok)"; \
		else \
			ok=0; \
			echo "[DEBUG] esperando TCP..."; \
		fi; \
		\
		if [ "$$ok" -ge 3 ]; then \
			exit 0; \
		fi; \
		sleep 2; \
	done; \
	exit 1' || \
	(echo "[FAIL] DB no recupera conectividad estable" && exit 1)

	@echo "[ OK ] DB recuperada"
	@echo ""

test-resilience-network:
	# ----------------------------------------
	# [3] FALLO RED (simulado)
	# ----------------------------------------
## Testea:
## - disconnect network
## - espera unhealthy
## - reconnect network
## - espera healthy
## Dependencias:
## [ red ]
##     monitoring-networks conecta TODO

	@echo "[3] Simulación fallo red hacia DB"

	@NETWORK=$$(docker inspect -f '{{range $$k, $$v := .NetworkSettings.Networks}}{{$$k}}{{end}}' monitoring-postgres); \
	if [ -z "$$NETWORK" ]; then \
		echo "[FAIL] no se pudo determinar la red"; \
		exit 1; \
	fi; \
	echo "Network=$$NETWORK"; \
	\
	echo "[STEP] desconectando red..."; \
	if ! docker network disconnect $$NETWORK monitoring-postgres; then \
		echo "[FAIL] error al desconectar red"; \
		exit 1; \
	fi; \
	\
	echo "[STEP] verificando aislamiento real..."; \
	timeout 20 sh -c '\
	until ! docker exec monitoring-python sh -c "nc -z monitoring-postgres 5432" >/dev/null 2>&1; do \
		sleep 2; \
	done' || (echo "[FAIL] el aislamiento de red NO es efectivo" && exit 1); \
	\
	echo "[ OK ] aislamiento de red confirmado"; \
	\
	echo "esperando degradación (health)..."; \
	timeout 60 sh -c '\
	until [ "$$(docker inspect monitoring-python --format="{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}")" = "unhealthy" ]; do \
		sleep 2; \
	done' || (echo "[FAIL] no degrada por red" && exit 1); \
	\
	echo "[ OK ] degradación por red OK"; \
	\
	echo "[STEP] reconectando red..."; \
	if ! docker network connect $$NETWORK monitoring-postgres; then \
		echo "[FAIL] error al reconectar red"; \
		exit 1; \
	fi; \
	\
	echo "[STEP] verificando recuperación de conectividad..."; \
	timeout 60 sh -c '\
	until docker exec monitoring-python sh -c "nc -z monitoring-postgres 5432" >/dev/null 2>&1; do \
		sleep 2; \
	done' || (echo "[FAIL] no recupera conectividad TCP" && exit 1); \
	\
	echo "esperando recuperación (health)..."; \
	timeout 60 sh -c '\
	until [ "$$(docker inspect monitoring-python --format="{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}")" = "healthy" ]; do \
		sleep 2; \
	done' || (echo "[FAIL] no recupera tras red" && exit 1); \
	\
	echo "[ OK ] red restaurada"
	@echo ""

test-resilience-observability:
	# ----------------------------------------
	# [4] OBSERVABILIDAD (Loki)
	# ----------------------------------------
## Testea:
## - generar log
## - comprobar Loki

	@echo "[4] Verificando Loki"

	@timeout 30 sh -c 'until curl -s http://127.0.0.1:3100/ready; do sleep 2; done' || \
		(echo "[FAIL] Loki no responde" && exit 1)

	@echo "[ OK ] Loki accesible"

	@echo "[STEP] generando log REAL en contenedor (PID 1)..."
	@docker exec monitoring-cron sh -c "echo 'SRE_test_$$(date +%s)' >> /proc/1/fd/1" || \
		(echo "[FAIL] no se puede escribir en stdout del contenedor" && exit 1)

	@sleep 7

	@echo "[STEP] verificando ingestión en Loki..."
	@RESULT=$$(curl -s -G http://127.0.0.1:3100/loki/api/v1/query \
		--data-urlencode 'query={job="container_logs"} |= "SRE_test_"' \
		| jq '.data.result | length'); \
	if [ "$$RESULT" -eq 0 ]; then \
		echo "[FAIL] Loki no ingiere logs"; exit 1; \
	else \
		echo "[ OK ] Loki ingestando logs"; \
	fi

test-resilience-fin:
	# ----------------------------------------
	# [5] ESTADO FINAL
	# ----------------------------------------

	@echo "[5] Estado final"
	@docker ps

	@echo "\n=== FIN TEST RESILIENCIA SRE ==="
	@echo ""

# --- test-python-health
## Testea:
## - estado real (no solo "running")
## Dependencias:
## [ monitoring-python ]
##     ├── depende de → monitoring-postgres
##     ├── depende de → smtp-relay
##     └── genera logs → /var/log → promtail → loki

.PHONY: test-python-health

test-python-health:
	# ----------------------------------------
	# [6] Python health
	# ----------------------------------------
	@echo "=== TEST PYTHON HEALTH ==="

	@echo "[1] Estado contenedor"

	@docker inspect monitoring-python --format='State={{.State.Status}} Health={{.State.Health.Status}}'

	@echo ""

	@echo "[2] Esperando healthy..."
	@if [ "$(CI)" = "true" ]; then \
		$(WAIT_SCRIPT) monitoring-python ci 60; \
	else \
		$(WAIT_SCRIPT) monitoring-python strict 90; \
	fi

	@echo "[ OK ] python healthy"

	@echo ""


# --- test-cron-execution
## Testea:
## - problemas de permisos
## - cron muerto
## - path incorrecto
## Dependencias:
## [ monitoring-cron ]
##     ├── depende de → monitoring-python (lógica)
##     ├── escribe → /var/log/test.log
##     └── (indirecto) → promtail → loki

.PHONY: test-cron-execution

test-cron-execution:
	@echo "=== TEST CRON EXECUTION ==="

	@echo "[1] Preparando entorno logs"
	@docker exec monitoring-cron sh -c "mkdir -p /opt/monitoring/logs"

	@echo "[2] Generando marca temporal"
	@docker exec monitoring-cron sh -c "echo test_$$(date +%s) >> /opt/monitoring/logs/test.log" || \
		(echo "[FAIL] no se puede escribir log" && exit 1)

	@sleep 5

	@echo "[3] Verificando ejecución..."
	@docker exec monitoring-cron sh -c "grep test_ /opt/monitoring/logs/test.log" >/dev/null 2>&1 || \
		(echo "[FAIL] cron no ejecuta" && exit 1)

	@echo "[ OK ] cron ejecutando correctamente"

# ------------------------------------------
# TEST OBSERVABILITY CORE (reutilizable)
# ------------------------------------------

.PHONY: test-observability-core

test-observability-core:
	@echo "=== TEST OBSERVABILITY CORE ==="
	@echo ""

	@echo "[1] Esperando Loki..."
	@timeout 30 sh -c 'until curl -s http://127.0.0.1:3100/ready; do sleep 2; done' || \
		(echo "[ERROR] Loki no responde" && exit 1)
	@echo ""

	@echo "[ OK ] Loki accesible"
	@echo ""

	@echo "[2] Generando log REAL en contenedor"
	@docker exec monitoring-cron sh -c "echo 'loki_test_$$(date +%s)' >> /proc/1/fd/1"
	@echo ""

	@sleep 7

	@echo "[3] Query Loki..."
	@RESULT=$$(curl -s -G http://127.0.0.1:3100/loki/api/v1/query \
		--data-urlencode 'query={job="container_logs"} |= "loki_test_"' \
		| jq '.data.result | length'); \
	if [ "$$RESULT" -eq 0 ]; then \
		echo "[FAIL] Loki no ingiere logs"; exit 1; \
	else \
		echo "[ OK ] logs ingeridos"; \
	fi
	@echo ""

	@echo "=== FIN TEST OBSERVABILITY ==="
	@echo ""

.PHONY: test-security-runtime

test-security-runtime:
	# ----------------------------------------
	# Test security runtime (ADR-0018 / ADR-0023)
	# ----------------------------------------
## Testea:
## - ejecución non-root en contenedores propios
## - excepciones infra-trusted documentadas
## - puertos mal expuestos
## - docker.sock indebido
## - restart policy

	@echo "=== TEST SECURITY RUNTIME ==="
	@echo ""

	# [1] Usuario runtime
	@echo "[1] Verificando usuario en contenedores"

	@FAIL=0; \
	\
	for c in monitoring-python monitoring-cron; do \
		if ! docker ps --format '{{.Names}}' | grep -q "^$$c$$"; then \
			echo "[FAIL] $$c no está en ejecución"; \
			FAIL=1; \
			continue; \
		fi; \
		UID=$$(docker exec $$c sh -c 'id -u' 2>/dev/null || true); \
		case "$$UID" in \
			''|*[!0-9]*) \
				echo "[FAIL] no se pudo obtener UID válido en $$c"; \
				FAIL=1; \
				;; \
			0) \
				echo "[FAIL] $$c ejecuta como root (UID=0)"; \
				FAIL=1; \
				;; \
			*) \
				echo "[ OK ] $$c usa usuario non-root (UID=$$UID)"; \
				;; \
		esac; \
	done; \
	\
	echo ""; \
	echo "[2] Verificando contenedores infra-trusted"; \
	\
	for e in monitoring-postgres monitoring-smtp-relay promtail; do \
		if docker ps --format '{{.Names}}' | grep -q "^$$e$$"; then \
			UID=$$(docker exec $$e sh -c 'id -u' 2>/dev/null || true); \
			case "$$UID" in \
				''|*[!0-9]*) \
					echo "[WARN] no se pudo obtener UID válido en $$e"; \
					;; \
				0) \
					echo "[WARN] $$e ejecuta como root (UID=0) — excepción infra-trusted permitida"; \
					;; \
				*) \
					echo "[ OK ] $$e usa UID=$$UID"; \
					;; \
			esac; \
		else \
			echo "[WARN] $$e no está en ejecución"; \
		fi; \
	done; \
	\
	echo ""; \
	if [ "$$FAIL" -ne 0 ]; then \
		echo "[FAIL] test-security-runtime"; \
		exit 1; \
	fi; \
	\
	echo "[ OK ] test-security-runtime completado"

	# [3] docker.sock
	@echo "[3] Verificando uso de docker.sock"

	@if grep -R "docker.sock" ops/services 2>/dev/null; then \
		echo "[FAIL] docker.sock usado en micro-stacks"; \
		exit 1; \
	else \
		echo "[ OK ] docker.sock no usado en servicios"; \
	fi
	@echo ""

	# [4] Restart policy
	@echo "[4] Verificando restart policy"

	@for c in $$(bash ops/runtime_containers.sh list); do \
		POLICY=$$(docker inspect $$c --format='{{.HostConfig.RestartPolicy.Name}}' 2>/dev/null || echo "none"); \
		if [ "$$POLICY" = "no" -o "$$POLICY" = "none" ]; then \
			echo "[WARN] $$c sin restart policy o no presente"; \
		else \
			echo "[ OK ] $$c restart=$$POLICY"; \
		fi; \
	done
	@echo ""

	# [5] Healthchecks
	@echo "[5] Verificando healthchecks"

	@for c in $$(bash ops/runtime_containers.sh list); do \
		HEALTH=$$(docker inspect $$c --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' 2>/dev/null || echo "none"); \
		if [ "$$HEALTH" = "none" ]; then \
			echo "[WARN] $$c sin healthcheck"; \
		else \
			echo "[ OK ] $$c health=$$HEALTH"; \
		fi; \
	done
	@echo ""

	@echo "=== FIN TEST SECURITY RUNTIME ==="

# ------------------------------------------
# SMTP (pipeline coherente)
# ------------------------------------------

# --- test-smtp-ci

.PHONY: test-smtp-ci

test-smtp-ci: \
	test-smtp-connect \
	test-smtp-banner \
	test-smtp-protocol \
	test-smtp-config-auth \
	test-smtp-relay-local \
	test-smtp-queue \
	test-smtp-logs-clean

test-smtp-all: test-smtp-connect test-smtp-banner test-smtp-protocol test-smtp-config-auth test-smtp-relay-flow test-smtp-delivery test-smtp-queue test-smtp-logs-clean

.PHONY: \

test-smtp-all: \
	test-smtp-connect \
	test-smtp-banner \
	test-smtp-protocol \
	test-smtp-config-auth \
	test-smtp-relay-flow \
	test-smtp-delivery \
	test-smtp-queue \
	test-smtp-logs-clean

# --- test-smtp-connect
## Testea:
## - Test mínimo viable: conectividad + handshake
## Dependencias:
## [ smtp-relay ]
##    └── servicio independiente (infra soporte)

test-smtp-connect:
	@echo ""
	@echo "=== TEST SMTP CONNECT ==="

	@echo "Asegurando debug toolbox..."
	@docker ps | grep monitoring-debug >/dev/null || make debug-toolbox-up

	@echo "Test conexión SMTP"
	@docker exec monitoring-debug nc -zv smtp-relay 587 || \
		(echo "[FAIL] no conecta a smtp-relay" && exit 1)

	@echo "[ OK ] conexión TCP correcta"
	@echo ""

# --- test-smtp-send-banner

test-smtp-banner:
	@echo "=== TEST SMTP BANNER ==="

	@docker exec monitoring-debug sh -c "\
		timeout 5 nc smtp-relay 587 | head -n 1 \
	" | grep -E '^220' >/dev/null || \
		(echo '[FAIL] banner SMTP inválido' && exit 1)

	@echo "[ OK ] banner SMTP correcto"
	@echo ""

# --- test-smtp-protocol (EHLO)

test-smtp-protocol:
	@echo "=== TEST SMTP PROTOCOL ==="

	@docker exec monitoring-debug sh -c '\
		( \
			sleep 1; echo "EHLO test"; \
			sleep 1; echo "QUIT"; \
		) | nc smtp-relay 587 \
	' | grep -q "250" || \
		(echo "[FAIL] SMTP handshake inválido" && exit 1)

	@echo "[ OK ] SMTP handshake válido"
	@echo ""

# --- test-smtp-config-auth

test-smtp-config-auth:
	@echo "=== TEST SMTP AUTH ==="
	@docker exec monitoring-smtp-relay postconf smtp_sasl_auth_enable | grep -q yes || \
		(echo "[FAIL] SASL desactivado" && exit 1)
	@echo "[ OK ] SASL activo"
	@echo ""

# --- test-smtp-config-auth (para CI, sin credenciales reales)

.PHONY: test-smtp-relay-local

test-smtp-relay-local:
	@echo "=== TEST SMTP RELAY LOCAL (SIN POSTMARK) ==="

	@docker exec monitoring-debug sh -c '\
		( \
			sleep 1; echo "EHLO test"; \
			sleep 1; echo "MAIL FROM:<test@local>"; \
			sleep 1; echo "RCPT TO:<fake@local>"; \
			sleep 1; echo "DATA"; \
			sleep 1; echo "Subject: test"; \
			sleep 1; echo ""; \
			sleep 1; echo "body"; \
			sleep 1; echo "."; \
			sleep 1; echo "QUIT"; \
		) | nc smtp-relay 587 \
	' | grep -q "250" || \
		(echo "[FAIL] relay local no acepta flujo SMTP" && exit 1)

	@echo "[ OK ] relay acepta MAIL FROM / RCPT / DATA"
	@echo ""

# --- test-smtp-relay-flow (relay acceptance)

test-smtp-relay-flow:
	@echo "=== TEST SMTP RELAY FLOW (POSTMARK API) ==="
	docker exec monitoring-python python3 scripts/test_mail.py || (echo "Fallo Relay Flow" && exit 1)
	@echo ""


# --- test-smtp-delivery (external provider)

test-smtp-delivery:
	@echo "=== TEST SMTP DELIVERY ==="

	@QUEUE_ID=$$(docker exec monitoring-python cat /tmp/smtp_queue_id); \
	echo "[INFO] Buscando queue_id: $$QUEUE_ID"; \
	docker logs monitoring-smtp-relay --tail 100 > /tmp/smtp_status.log || true; \
	if grep -q "$$QUEUE_ID" /tmp/smtp_status.log && grep -q "status=sent" /tmp/smtp_status.log; then \
		echo "[ OK ] entregado (relay → Postmark)"; \
	elif grep -q "$$QUEUE_ID" /tmp/smtp_status.log && grep -q "status=deferred" /tmp/smtp_status.log; then \
		echo "[WARN] deferred"; exit 1; \
	elif grep -q "$$QUEUE_ID" /tmp/smtp_status.log && grep -q "status=bounced" /tmp/smtp_status.log; then \
		echo "[FAIL] bounced"; exit 1; \
	else \
		echo "[FAIL] no se encontró el queue_id en logs"; exit 1; \
	fi

	@echo "[INFO] comprobar manualmente en Postmark Activity"
	@echo ""

# --- test-smtp-queue (Postfix interno)

test-smtp-queue:
	@echo "=== TEST SMTP QUEUE ==="

	@docker exec monitoring-smtp-relay postqueue -p | grep -q "^[A-F0-9]" && \
	(echo "[WARN] hay correos en cola") || \
	(echo "[ OK ] cola vacía")
	@echo ""

# --- test-smtp-logs-clean

test-smtp-logs-clean:
	@echo "=== TEST SMTP LOG CLEAN ==="
	@docker logs monitoring-smtp-relay --since 30s | grep -i warning && \
	(echo "[WARN] warnings en logs") || \
	(echo "[ OK ] logs limpios")
	@echo ""

# --- Network

.PHONY: test-network

test-network:
	docker network inspect backend-net
	docker network inspect observability-net
	docker network inspect restricted-net
	@echo ""

	docker exec monitoring-python nc -z monitoring-postgres 5432
	@echo ""

# --- Unitarios + integración (Python)

.PHONY: test-smtp-unitarios-integration

test-smtp-unitarios-integration:
	@echo "=== TEST SMTP UNIT & INTEGRATION ==="
	@if command -v pytest >/dev/null 2>&1; then \
		echo "Utilizando system pytest"; \
		PYTHONPATH=src pytest tests/unit -q || exit 1; \
		PYTHONPATH=src pytest tests/integration -q || exit 1; \
	else \
		echo "⚠️ pytest no encontrado. Intentando entorno virtual temporal..."; \
		if command -v python3 >/dev/null 2>&1 && python3 -c "import venv" >/dev/null 2>&1; then \
			rm -rf .venv-test; \
			python3 -m venv .venv-test; \
			./.venv-test/bin/python3 -m pip install --upgrade pip; \
			./.venv-test/bin/python3 -m pip install --no-cache-dir -r requirements.txt pytest; \
			PYTHONPATH=src ./.venv-test/bin/pytest tests/unit -q || exit 1; \
			PYTHONPATH=src ./.venv-test/bin/pytest tests/integration -q || exit 1; \
			rm -rf .venv-test; \
		else \
			echo "[ERROR] pytest no disponible y python3-venv no instalado"; \
			exit 1; \
		fi; \
	fi

# ------------------------------------------
# DEBUG (troubleshooting)
# debug = exploración manual (humano, ad-hoc, no determinista)
# Características:
# - no tiene PASS / FAIL claro
# - es interactivo
# - depende del operador
# - objetivo: investigar problema
# ------------------------------------------

.PHONY: debug

debug:
	@echo "=== DEBUG COMMANDS ==="
	@echo "make debug-shell STACK=<name>"
	@echo "make debug-containers"
	@echo "make debug-net"
	@echo "make debug-loki"
	@echo ""

# --- Shell

.PHONY: debug-shell

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
	@echo ""

# --- Network

.PHONY: debug-net

debug-net: ## Verifica resolución DNS entre contenedores
	@echo "=== Test DNS interno ==="
	@docker exec monitoring-python getent hosts monitoring-postgres || echo "[ERROR] DNS fallo"
	@echo ""

# --- Containers logs

.PHONY: debug-containers

debug-containers: ## Logs rápidos de todos los contenedores
	@for c in $$(docker ps --format '{{.Names}}'); do \
		echo "===== $$c ====="; \
		docker logs $$c --tail=10; \
	done
	@echo ""

# --- Loki

.PHONY: debug-loki

debug-loki: ## Test acceso interno a Loki (sin exposición de puertos)
	@echo "=== DEBUG LOKI (internal) ==="

	@echo "[1] Comprobando contenedor..."
	@docker ps | grep loki >/dev/null || (echo "[ERROR] Loki no está corriendo" && exit 1)

	@echo "[2] Test /ready desde red interna..."
	@docker exec monitoring-python curl -s http://loki:3100/ready || (echo "[ERROR] Loki no responde" && exit 1)

	@echo ""
	@echo "[3] Labels disponibles:"
	@docker exec monitoring-python curl -s http://loki:3100/loki/api/v1/labels

	@echo ""
	@echo "[ OK ] Loki accesible vía red interna"
	@echo ""

debug-ports: ## Ver puertos expuestos en host
	@echo "=== Puertos escuchando en host ==="
	ss -tulpn
	@echo ""

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
	@echo ""

# ------------------------------------------
# Debug container (toolbox)
# ------------------------------------------

DEBUG_IMAGE = nicolaka/netshoot
DEBUG_CONTAINER = monitoring-debug

DEBUG_NET ?= restricted-net

debug-toolbox-up: ## Levanta contenedor de debugging (DEBUG_NET=$(DEBUG_NET))
	@echo "=== Iniciando contenedor debug (network=$(DEBUG_NET)) ==="
	@docker rm -f $(DEBUG_CONTAINER) >/dev/null 2>&1 || true
	@docker run -d --name $(DEBUG_CONTAINER) \
		--network $(DEBUG_NET) \
		$(DEBUG_IMAGE) sleep infinity
	@echo "[ OK ] contenedor debug activo"
	@echo ""

debug-toolbox-shell: ## Shell en contenedor debug
	@docker exec -it $(DEBUG_CONTAINER) sh
	@echo ""

debug-toolbox-down: ## Elimina contenedor debug
	@docker rm -f $(DEBUG_CONTAINER) || true
	@echo "[ OK ] contenedor debug eliminado"
	@echo ""

# ------------------------------------------
# Stack management - restart (simulación de fallo)
# ------------------------------------------

.PHONY: stack-up stack-down stack-restart stack-status

stack-up:  ## Levanta un stack (STACK=nombre)
	$(call validate_stack)
	@DIR=$$( $(call stack_path) ); \
	echo "=== 🚀 Levantando stack $(STACK) ==="; \
	cd $$DIR && $(COMPOSE) up -d --build
	@echo ""

stack-down:  ## Detiene un stack
	$(call validate_stack)
	@DIR=$$( $(call stack_path) ); \
	echo "=== ⛔ Parando stack $(STACK) ==="; \
	cd $$DIR && $(COMPOSE) down
	@echo ""

stack-restart:  ## Reinicia un stack
	$(call validate_stack)
	@DIR=$$( $(call stack_path) ); \
	echo "=== 🔁 Reiniciando stack $(STACK) ==="; \
	cd $$DIR && $(COMPOSE) restart
	@echo ""

stack-rebuild:
	$(call validate_stack)
	@DIR=$$( $(call stack_path) ); \
	echo "=== 🔁 Rebuild stack $(STACK) ==="; \
	cd $$DIR && $(COMPOSE) up -d --build --force-recreate
	@echo ""

stack-status:  ## Estado de un stack
	$(call validate_stack)
	@DIR=$$( $(call stack_path) ); \
	echo "=== Estado stack $(STACK) ==="; \
	cd $$DIR && $(COMPOSE) ps
	@echo ""

stack-logs:
	$(call validate_stack)
	@DIR=$$( $(call stack_path) ); \
	cd $$DIR && $(COMPOSE) logs -f
	@echo ""

# ------------------------------------------
# Build / Deploy: Infraestructura base (ADR-0008 compliant)
# ------------------------------------------

.PHONY: monitoring-networks

monitoring-networks:  ## Crea las redes Docker usadas por la plataforma
	@echo "=== [INFRA] Bootstrap (monitoring networks) ==="
	@docker network inspect backend-net >/dev/null 2>&1 || docker network create backend-net
	@docker network inspect observability-net >/dev/null 2>&1 || docker network create observability-net
	@docker network inspect restricted-net >/dev/null 2>&1 || docker network create restricted-net
	@echo "[ OK ] networks ready"


# ------------------------------------------
# Build / Deploy
# ------------------------------------------

.PHONY: build build-python build-cron deploy deploy deploy-infra deploy-services deploy-validate

## Inicialización completa - construye todas las imágenes
build: build-python build-cron
	@echo "[ OK ] imágenes construidas"
	@echo "[ OK ] entorno inicializado"
	@echo ""

build-python:
	@echo "[BUILD] python"
	docker build --no-cache -f ops/stacks/python/Dockerfile -t monitoring-python .
	@echo ""

build-cron:
	@echo "[BUILD] cron"
	docker build --no-cache -f ops/stacks/cron/Dockerfile -t monitoring-cron .
	@echo ""

deploy: monitoring-networks build deploy-infra deploy-services deploy-validate runtime-apply
	@echo "[ OK ] build completo"
	@echo "=== 🚀 Despliegue completo ==="; \


# 🔑 Infra primero (correcto según ADR-0008)
deploy-infra:
	@echo "=== [DEPLOY] Infra stacks ==="
	@set -e; \
	for s in $(INFRA_STACKS); do \
		echo "→ desplegando $$s"; \
		(cd $(STACK_DIR)/$$s && $(COMPOSE) up -d --build); \
	done

# 🔑 Luego micro-stacks
deploy-services:
	@echo "=== [DEPLOY] Service stacks ==="
	@set -e; \
	for s in $(SERVICE_STACKS); do \
		echo "→ desplegando $$s"; \
		(cd $(SERVICE_DIR)/$$s && $(COMPOSE) up -d --build); \
	done

# ------------------------------------------
# Validación post-deploy
# ------------------------------------------

deploy-validate:
	@echo "=== [VALIDACIÓN] Estado contenedores ==="
	@docker ps

	@echo "[CHECK] healthchecks"
	@docker ps --format '{{.Names}} {{.Status}}' | grep -E "unhealthy" && \
		(echo "[FAIL] contenedores unhealthy"; exit 1) || \
		echo "[ OK ] todos healthy"

	@echo "[CHECK] redes de monitorización (backend/observability/restricted)"
	@docker network inspect backend-net >/dev/null 2>&1 \
		&& docker network inspect observability-net >/dev/null 2>&1 \
		&& docker network inspect restricted-net >/dev/null 2>&1 \
		&& echo "[ OK ] redes operativas" \
		|| (echo "[FAIL] alguna red no disponible"; exit 1)

	@echo "[CHECK] conectividad mínima postgres"
	@docker exec monitoring-python nc -z monitoring-postgres 5432 \
		&& echo "[ OK ] postgres accesible" \
		|| echo "[WARN] postgres no accesible (revisar dependencias)"

	@echo "[ OK ] validación completada"

# ------------------------------------------
# Runtime hardening
# ------------------------------------------

.PHONY: runtime-apply

runtime-apply:
	@echo "[RUNTIME] aplicando límites"
	bash ops/deployment/configure_docker_limits.sh
	@echo "[ OK ] runtime aplicado"

# ------------------------------------------
# Limpieza
# ------------------------------------------

.PHONY: clean clean-docker

clean:
	@echo "[INFO] limpiando imágenes dangling"
	docker image prune -f
	@echo ""

clean-docker:
	@echo "[INFO] limpieza completa Docker"
	docker container prune -f
	docker image prune -f
	docker builder prune -f
	@echo ""

# ------------------------------------------
# Esquemas
# ------------------------------------------

.PHONY: esquema

esquema:
	@echo "=== SCHEME COMMANDS ==="
	@echo "make esquema-arquitectura"
	@echo "make esquema-git"
	@echo ""

esquema-arquitectura:
	@echo "[INFO] Esquema de arquitectura"
	find . -not -path '*/.git*' | sed -e 's;[^/]*/;|____;g;s;____|; |;g'
	@echo ""

esquema-git:
	@echo "[INFO] Esquema de ramas Git"
	sudo git log --oneline --decorate --graph --all -n 25
	@echo ""

# ------------------------------------------
# TEST DE CERTIFICACION (SRE + IaC)
# ------------------------------------------

.PHONY: test-SRE

test-SRE:
	@echo ""
	@echo "=== Bateria de Test de Certificación (SRE + IaC) ==="
	@echo ""
	@echo "CORE:"
	@echo "  test-reproducibilidad"
	@echo "  test-aislamiento-red"
	@echo "  test-dependencias-host"
	@echo "  test-permisos"
	@echo "  test-arranque-desordenado"
	@echo "  test-aislamiento-fs"
	@echo ""

test-SRE-completo: test-reproducibilidad test-aislamiento-red test-dependencias-host test-permisos test-arranque-desordenado test-aislamiento-fs

force-recreate:
	@echo "=== RECREATE postgres / python ==="
	docker compose -f ops/services/postgres/compose.yml down
	docker compose -f ops/stacks/python/compose.yml down
	docker compose -f ops/services/postgres/compose.yml up -d --build
	docker compose -f ops/stacks/python/compose.yml up -d --build
	docker system prune -f
	@echo ""

.PHONY: test-reproducibilidad

test-reproducibilidad:
	@echo "\n=== TEST REPRODUCIBILIDAD ==="

	@echo "[1] Eliminando entorno completo"
	docker compose -f ops/stacks/observability/compose.yml down -v || true
	docker compose -f ops/stacks/python/compose.yml down -v || true
	docker compose -f ops/stacks/cron/compose.yml down -v || true
	docker compose -f ops/services/postgres/compose.yml down -v || true
	docker compose -f ops/services/smtp_relay/compose.yml down -v || true

	@echo "[2] Limpieza sistema"
	docker system prune -af --volumes

	@echo "[3] Re-creando red compartida: bootstrap infraestructura"
	$(MAKE) monitoring-networks

	@echo "[4] Levantando infraestructura base (Postgres)"
	docker compose -f ops/services/postgres/compose.yml up -d --build

	@echo "[WAIT] esperando Postgres healthy..."
	@until [ "$$(docker inspect --format='{{.State.Health.Status}}' monitoring-postgres 2>/dev/null)" = "healthy" ]; do \
		sleep 2; \
	done

	@echo "[4] Observabilidad"
	docker compose -f ops/stacks/observability/compose.yml up -d --build

	@echo "[5] Stacks aplicación"
	docker compose -f ops/stacks/python/compose.yml up -d --build
	docker compose -f ops/stacks/cron/compose.yml up -d --build

	@echo "[6] SMTP relay"
	docker compose -f ops/services/smtp_relay/compose.yml up -d --build

	@echo "[7] Verificación estado"
	docker ps

	@echo "[ OK ] reproducibilidad validada"


test-aislamiento-red:
	@echo "\n=== TEST AISLAMIENTO RED ==="

	@echo "[1] Intentando conexión indebida (desde restricted-net)"
	@docker run --rm --network restricted-net nicolaka/netshoot sh -c '\
		if nc -zv monitoring-postgres 5432 >/dev/null 2>&1; then \
			echo "[FAIL] acceso permitido (revisar)"; exit 1; \
		else \
			echo "[ OK ] acceso restringido (esperado)"; \
		fi'

	@echo "[2] Validando redes internas"
	@docker network inspect backend-net | grep Containers || true
	@docker network inspect observability-net | grep Containers || true
	@docker network inspect restricted-net | grep Containers || true

	@echo "[ OK ] test aislamiento completado"

test-dependencias-host:
	@echo "\n=== TEST DEPENDENCIAS HOST ==="

	@echo "[1] Buscando bind mounts peligrosos"
	@docker inspect monitoring-python | grep Mounts

	@echo "[2] Verificando /opt/monitoring interno"
	@docker exec monitoring-python ls /opt/monitoring/src >/dev/null \
	&& echo "[ OK ] código disponible dentro del contenedor" \
	|| echo "[FAIL] dependencia externa detectada"

	@echo "[ OK ] test dependencias finalizado"

test-permisos:
	@echo "\n=== TEST PERMISOS ==="

	@echo "[1] UID en contenedores"
	@docker exec monitoring-python id
	@docker exec monitoring-cron id

	@echo "[2] escritura en logs"
	@docker exec monitoring-cron sh -c "touch /opt/monitoring/logs/test.log" \
	&& echo "[ OK ] escritura válida" \
	|| echo "[FAIL] problema permisos"

	@echo "[ OK ] test permisos completado"

test-arranque-desordenado:
	@echo "\n=== TEST ARRANQUE DESORDENADO ==="

	@echo "[1] levantando python SIN postgres"
	docker compose -f ops/stacks/python/compose.yml up -d

	sleep 5

	@echo "[2] ejecutando healthcheck"
	docker inspect --format='{{.State.Health.Status}}' monitoring-python

	@echo "[3] levantando postgres después"
	docker compose -f ops/services/postgres/compose.yml up -d

	sleep 10

	@echo "[ OK ] sistema tolera orden variable"

test-aislamiento-fs:
	@echo "\n=== TEST AISLAMIENTO FS ==="

	@echo "[1] escribiendo en contenedor A"
	docker exec monitoring-python sh -c "echo test > /tmp/testfile"

	@echo "[2] comprobando en contenedor B"
	@docker exec monitoring-cron sh -c "cat /tmp/testfile" 2>/dev/null \
	&& echo "[FAIL] fuga de filesystem" \
	|| echo "[ OK ] aislamiento correcto"

# ------------------------------------------
# ------------------------------------------
# ------------------------------------------
# POSIBLE BORRADO A PARTIR DE AQUI
# ------------------------------------------
# ------------------------------------------
# ------------------------------------------

# ------------------------------------------
# Git utilities
# ------------------------------------------

.PHONY: git-log

git-log: ## Historial git resumido
	@echo ""
	@echo "=== Git history (últimos 25 commits) ==="
	sudo git log --oneline --decorate --graph --all -n 25
	@echo ""

# ------------------------------------------
# LIFECYCLE: Despliegue completo
# ------------------------------------------

.PHONY: dev-up dev-down

dev-up:
	$(COMPOSE) -f $(DEV_COMPOSE) up -d
	@echo ""

dev-down:
	$(COMPOSE) -f $(DEV_COMPOSE) down
	@echo ""

# ------------------------------------------
# LIFECYCLE: Rebuild
# ------------------------------------------

.PHONY: rebuild rebuild-all

rebuild: clean build
	@echo "[ OK ] rebuild realizado"
	@echo ""

rebuild-all:
	make clean-docker
	make build
	make deploy
	@echo ""

# ------------------------------------------
# Logs
# ------------------------------------------

logs:  ## Muestra logs recientes del sistema y contenedores
	@echo "=== Logs del sistema ==="
	@echo ""
	@echo "=== Logs de todos los contenedores activos ==="
	@for c in $$(docker ps --format '{{.Names}}'); do \
		echo "===== $$c ====="; \
		docker logs $$c --tail=20 2>/dev/null || echo "⚠️  No se pudo obtener logs de $$c"; \
	done
	@echo ""
