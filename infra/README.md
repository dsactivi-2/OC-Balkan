# OpenClaw Balkan — Infrastructure

Production infrastructure for OpenClaw Balkan. Self-hosted on Hetzner CX31 (4 vCPU, 8 GB RAM), designed for 120+ customers in Phase 1.

## Architecture

```
                    ┌──────────────────────────────────────┐
                    │          Hetzner CX31                 │
                    │       Ubuntu 22.04 LTS                │
                    │                                       │
   Internet ───────▶│  ┌─────────┐    ┌──────────────┐     │
      :80/:443      │  │  Nginx  │───▶│   OpenClaw    │     │
                    │  │  + SSL  │    │   (App)       │     │
                    │  └─────────┘    └──────┬───────┘     │
                    │                        │              │
                    │               ┌────────┴────────┐    │
                    │               │                  │    │
                    │        ┌──────▼──────┐   ┌──────▼──┐ │
                    │        │ PostgreSQL  │   │  Redis   │ │
                    │        │   16        │   │   7      │ │
                    │        └─────────────┘   └─────────┘ │
                    │                                       │
                    │  ┌───────────┐  ┌──────────────────┐ │
                    │  │  Certbot  │  │   Watchtower     │ │
                    │  │ (SSL)     │  │ (Auto-Update)    │ │
                    │  └───────────┘  └──────────────────┘ │
                    └──────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Fresh Hetzner CX31 with Ubuntu 22.04 LTS
- SSH key configured
- Domain with DNS A record pointing to server IP

### Deploy

```bash
# 1. SSH into your server
ssh root@YOUR_SERVER_IP

# 2. Clone the repo
git clone https://github.com/YOUR_REPO/openclaw-infra.git /opt/openclaw
cd /opt/openclaw

# 3. Configure environment
cp .env.example .env
nano .env  # Fill in ALL values

# 4. Deploy (one command)
chmod +x scripts/*.sh
./scripts/deploy.sh
```

The deploy script handles everything: system updates, Docker installation, firewall, Fail2Ban, SSL certificates, cron jobs, and starting all services.

### After Deploy

```bash
# Check status
make status

# View logs
make logs

# Run backup
make backup
```

## File Structure

```
openclaw-infra/
├── docker-compose.yml          # All services
├── .env.example                # Environment template
├── .gitignore
├── Makefile                    # Quick commands
├── README.md
├── nginx/
│   ├── nginx.conf              # Main Nginx config
│   └── conf.d/
│       ├── default.conf        # HTTPS site config
│       └── http-only.conf.initial  # Pre-SSL config
├── scripts/
│   ├── deploy.sh               # One-command server setup
│   ├── backup.sh               # Daily PostgreSQL backup
│   ├── restore.sh              # Restore from backup
│   ├── monitor.sh              # Health checks (every 5min)
│   └── status.sh               # Status dashboard
└── backups/                    # Backup storage (gitignored)
```

## Services

| Service | Image | Purpose | Port |
|---------|-------|---------|------|
| nginx | nginx:1.27-alpine | Reverse proxy + SSL | 80, 443 |
| openclaw | openclaw/openclaw:latest | AI Agent platform | 3000 (internal) |
| postgres | postgres:16-alpine | Database | 5432 (internal) |
| redis | redis:7-alpine | Cache + sessions | 6379 (internal) |
| certbot | certbot/certbot | SSL cert management | — |
| watchtower | containrrr/watchtower | Auto-update containers | — |

## Security

- **Firewall**: UFW — only SSH (22), HTTP (80), HTTPS (443) open
- **Fail2Ban**: SSH brute-force protection (3 attempts → 2h ban)
- **SSH**: Key-only authentication, no password login, max 3 auth attempts
- **SSL**: Let's Encrypt with auto-renewal (every 12h check)
- **Docker**: Backend network is internal (no external access to DB/Redis)
- **Nginx**: Rate limiting (30 req/s general, 5 req/min login), security headers
- **Updates**: Watchtower checks for image updates daily

## Backups

- **Schedule**: Daily at 03:00 (server time)
- **Retention**: 30 days (configurable via `BACKUP_RETENTION_DAYS`)
- **Format**: Compressed PostgreSQL custom format (`.sql.gz`)
- **Location**: `/opt/openclaw/backups/`

```bash
# Manual backup
make backup

# List backups
./scripts/restore.sh

# Restore
make restore FILE=backups/openclaw_20260401_030000.sql.gz
```

## Monitoring

- **Health checks**: Every 5 minutes via `monitor.sh`
- **Checks**: Disk, Memory, CPU, Container status, HTTP health, PostgreSQL, SSL expiry
- **Alerts**: Email + Healthchecks.io (configure in `.env`)
- **Docker**: Built-in healthchecks on all containers

```bash
# Watch monitor log
make monitor

# Quick status
make status
```

## Day-to-Day Commands

```bash
make help          # Show all commands
make up            # Start services
make down          # Stop services
make restart       # Restart services
make logs          # Tail all logs
make logs-app      # Tail OpenClaw logs
make shell-db      # PostgreSQL shell
make shell-redis   # Redis shell
make update        # Pull latest images + restart
make ssl-renew     # Force SSL renewal
```

## Scaling

Current setup (CX31, 12 EUR/Mo) handles ~50-100 concurrent agents. When you need more:

1. **Vertical**: Upgrade to CX41 (8 vCPU, 16 GB) or CX51 — just resize in Hetzner Cloud console
2. **Horizontal** (Phase 2+): Add a second server, separate DB from app, add load balancer

## Cost

| Component | Monthly |
|-----------|---------|
| Hetzner CX31 | 12 EUR |
| Domain (.ba + .rs) | ~4 EUR |
| Total Infrastructure | **~16 EUR/Mo** |

LLM API costs, Viber/WhatsApp API costs, and Stripe fees are separate (see UNIT-ECONOMICS.md).
