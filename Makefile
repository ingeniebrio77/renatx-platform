# =============================================================================
# Makefile Operativo — Plataforma Comercial Renatx (renatx.com)
# Autor: Franco Renato Palavecino (Hamburgo, Alemania)
# Orquestación con Podman + Traefik + FastAPI + Next.js + PostgreSQL + RustDesk
# =============================================================================

.PHONY: help init up dev down logs ps db-shell db-backup \
        rustdesk-local-up rustdesk-local-down rustdesk-key \
        rustdesk-cloud-up rustdesk-cloud-down cost-report mcp-postgres

COMPOSE_CMD := $(shell if command -v podman-compose >/dev/null 2>&1; then echo "podman-compose"; else echo "podman compose"; fi)
TF_CMD := $(shell if command -v tofu >/dev/null 2>&1; then echo "tofu"; else echo "terraform"; fi)

help:
	@echo "====================================================================="
	@echo "  RENATX PLATFORM (renatx.com) — Franco Renato Palavecino"
	@echo "====================================================================="
	@echo "1. Plataforma Web Comercial (Local con Podman + Traefik):"
	@echo "  make up                  -> Construye y levanta la plataforma web + API"
	@echo "  make down                -> Detiene los contenedores web/API"
	@echo "  make ps                  -> Muestra el estado de los contenedores"
	@echo "  make logs                -> Sigue los logs en tiempo real"
	@echo "  make db-shell            -> Abre consola interactiva psql en PostgreSQL"
	@echo "  make db-backup           -> Genera volcado SQL en ./backups/"
	@echo ""
	@echo "2. Soporte Remoto RustDesk (Por Horas / Minutos):"
	@echo "  make rustdesk-local-up   -> Levanta servidor RustDesk (hbbs/hbbr) en local"
	@echo "  make rustdesk-local-down -> Apaga servidor RustDesk local"
	@echo "  make rustdesk-key        -> Muestra la clave pública Ed25519 generada"
	@echo "  make rustdesk-cloud-up   -> Crea VPS efímero en Hetzner (0,007 €/h)"
	@echo "  make rustdesk-cloud-down -> Destruye el VPS efímero de RustDesk (0,00 €/h)"
	@echo ""
	@echo "3. FinOps y Auditoría de Costes:"
	@echo "  make cost-report         -> Muestra desglose de costes (Local/Efímero/Prod)"
	@echo "====================================================================="

init:
	@mkdir -p backups infra-platform/rustdesk/data
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "[OK] Archivo .env creado desde .env.example (configurado para renatx.localhost)"; \
	else \
		echo "[OK] El archivo .env ya existe."; \
	fi

up: init
	@if ! command -v podman-compose >/dev/null 2>&1 && ! podman compose version >/dev/null 2>&1; then \
		echo "[ERROR] Falta el proveedor compose para Podman."; \
		echo "        En Arch Linux instálalo con: sudo pacman -S podman-compose"; \
		exit 1; \
	fi
	$(COMPOSE_CMD) up -d --build --force-recreate
	@echo ""
	@echo "====================================================================="
	@echo "  Plataforma Comercial Renatx (ES/DE) activa en local:"
	@echo "  -> Web Comercial:     http://renatx.localhost:8080"
	@echo "  -> API Health:        http://renatx.localhost:8080/api/health"
	@echo "  -> API Swagger Docs:  http://api.renatx.localhost:8080/docs"
	@echo "====================================================================="

dev: up

down:
	$(COMPOSE_CMD) down

ps:
	$(COMPOSE_CMD) ps

logs:
	$(COMPOSE_CMD) logs -f

db-shell:
	@set -a && . ./.env && set +a && \
	podman exec -it renatx-postgres psql -U $$POSTGRES_USER -d $$POSTGRES_DB

db-backup: init
	@set -a && . ./.env && set +a && \
	BACKUP_FILE="backups/renatx_db_$$(date +%Y%m%d_%H%M%S).sql" && \
	podman exec renatx-postgres pg_dump -U $$POSTGRES_USER $$POSTGRES_DB > $$BACKUP_FILE && \
	echo "[OK] Backup creado en: $$BACKUP_FILE"

# -----------------------------------------------------------------------------
# Operaciones RustDesk Bajo Demanda (Local y Cloud Efímero)
# -----------------------------------------------------------------------------
rustdesk-local-up: init
	$(COMPOSE_CMD) -f compose.rustdesk.yaml up -d
	@sleep 2
	@$(MAKE) rustdesk-key

rustdesk-local-down:
	$(COMPOSE_CMD) -f compose.rustdesk.yaml down

rustdesk-key:
	@if [ -f infra-platform/rustdesk/data/id_ed25519.pub ]; then \
		echo "====================================================================="; \
		echo "  CLAVE PÚBLICA RUSTDESK (Pegar en el cliente RustDesk -> Key):"; \
		cat infra-platform/rustdesk/data/id_ed25519.pub; echo ""; \
		echo "====================================================================="; \
	else \
		echo "[INFO] Aún no existe id_ed25519.pub. Ejecuta 'make rustdesk-local-up' primero."; \
	fi

rustdesk-cloud-up:
	$(TF_CMD) -chdir=infra-platform/terraform/envs/rustdesk-ondemand init
	$(TF_CMD) -chdir=infra-platform/terraform/envs/rustdesk-ondemand apply

rustdesk-cloud-down:
	$(TF_CMD) -chdir=infra-platform/terraform/envs/rustdesk-ondemand destroy

cost-report:
	@if command -v infracost >/dev/null 2>&1; then \
		infracost breakdown --config-file infra-platform/infracost.yml; \
	else \
		echo "====================================================================="; \
		echo "  AUDITORÍA FINOPS ESTIMADA — RENATX PLATFORM (Hetzner Cloud DE)"; \
		echo "====================================================================="; \
		echo "  Entorno           | Recurso Hetzner | Uso              | Coste"; \
		echo "  ------------------+-----------------+------------------+-------------------"; \
		echo "  rustdesk-ondemand | CX22 (fsn1)     | Por hora/minutos | ~0,007 €/hora"; \
		echo "  preprod           | CX22 (fsn1)     | Efímero pruebas  | ~0,007 €/hora"; \
		echo "  prod              | CX32 (fsn1)     | Web 24/7         | ~8,32 €/mes"; \
		echo "  DNS / Dominio     | renatx.com      | Cloudflare Reg   | ~0,88 €/mes"; \
		echo "====================================================================="; \
	fi

# -----------------------------------------------------------------------------
# Servidor MCP de PostgreSQL (postgres-mcp de Crystal DBA, modo RESTRICTED)
# Lee la contraseña desde .env y se une a la red interna db_net de Podman.
# Se usa como servidor MCP 'postgres' definido en .opencode/opencode.jsonc
# -----------------------------------------------------------------------------
mcp-postgres:
	@set -a && . ./.env 2>/dev/null; set +a; \
	exec podman run -i --rm \
		--network renatx-platform_db_net \
		-e "DATABASE_URI=postgresql://$${POSTGRES_USER:-renatx_admin}:$${POSTGRES_PASSWORD:-renatx_local_dev_password_change_me}@postgres:5432/$${POSTGRES_DB:-renatx_db}" \
		docker.io/crystaldba/postgres-mcp:latest \
		--access-mode=restricted
