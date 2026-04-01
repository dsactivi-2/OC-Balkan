# ============================================
# OpenClaw Balkan — Makefile
# ============================================
# Quick commands for day-to-day operations.

.PHONY: help up down restart logs status backup restore deploy update prune

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

up: ## Start all services
	docker compose up -d

down: ## Stop all services
	docker compose down

restart: ## Restart all services
	docker compose restart

logs: ## Tail logs (all containers)
	docker compose logs -f --tail=100

logs-app: ## Tail OpenClaw logs only
	docker compose logs -f --tail=100 openclaw

logs-nginx: ## Tail Nginx logs only
	docker compose logs -f --tail=100 nginx

logs-db: ## Tail PostgreSQL logs only
	docker compose logs -f --tail=100 postgres

status: ## Show system status dashboard
	@./scripts/status.sh

backup: ## Run database backup now
	@./scripts/backup.sh

restore: ## Restore from backup (usage: make restore FILE=backups/xxx.sql.gz)
	@./scripts/restore.sh $(FILE)

deploy: ## Run full server deployment
	@./scripts/deploy.sh

update: ## Pull latest images and restart
	docker compose pull
	docker compose up -d

prune: ## Clean up unused Docker resources
	docker system prune -af --volumes --filter "until=168h"

shell-app: ## Shell into OpenClaw container
	docker exec -it openclaw-app /bin/sh

shell-db: ## Shell into PostgreSQL container
	docker exec -it openclaw-postgres psql -U $${POSTGRES_USER:-openclaw} -d $${POSTGRES_DB:-openclaw}

shell-redis: ## Shell into Redis container
	docker exec -it openclaw-redis redis-cli --no-auth-warning -a $${REDIS_PASSWORD}

ssl-renew: ## Force SSL certificate renewal
	docker compose run --rm certbot renew --force-renewal
	docker compose restart nginx

monitor: ## Watch monitor log
	tail -f /var/log/openclaw-monitor.log
