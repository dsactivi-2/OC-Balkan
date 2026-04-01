#!/usr/bin/env bash
# ============================================
# OpenClaw Balkan — One-Command Server Deploy
# ============================================
# Run on a fresh Hetzner CX31 (Ubuntu 22.04 LTS):
#
#   ssh root@YOUR_SERVER_IP
#   git clone https://github.com/YOUR_REPO/openclaw-infra.git /opt/openclaw
#   cd /opt/openclaw
#   cp .env.example .env
#   nano .env  # Fill in your values
#   chmod +x scripts/*.sh
#   ./scripts/deploy.sh
#
# This script is IDEMPOTENT — safe to run multiple times.

set -euo pipefail

BOLD='\033[1m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

log()  { echo -e "${GREEN}[✓]${NC} $*"; }
warn() { echo -e "${YELLOW}[!]${NC} $*"; }
err()  { echo -e "${RED}[✗]${NC} $*"; exit 1; }

echo -e "${BOLD}"
echo "══════════════════════════════════════════"
echo "  OpenClaw Balkan — Server Deployment"
echo "══════════════════════════════════════════"
echo -e "${NC}"

# ─── Pre-checks ───
[[ $EUID -eq 0 ]] || err "This script must be run as root"
[[ -f "$PROJECT_DIR/.env" ]] || err ".env file not found. Copy .env.example to .env and fill in your values."

# Load environment
set -a
source "$PROJECT_DIR/.env"
set +a

# Validate DOMAIN format
[[ "$DOMAIN" =~ ^[a-zA-Z0-9.-]+$ ]] || err "Invalid DOMAIN format"

# Validate required vars
for VAR in DOMAIN LETSENCRYPT_EMAIL POSTGRES_PASSWORD REDIS_PASSWORD OPENCLAW_SECRET_KEY; do
    [[ -n "${!VAR:-}" ]] || err "Required variable $VAR is not set in .env"
done

# ─── Step 1: System Update ───
echo -e "\n${BOLD}Step 1/8: System Update${NC}"
apt-get update -qq
apt-get upgrade -y -qq
apt-get install -y -qq curl wget git ufw fail2ban unattended-upgrades \
    apt-transport-https ca-certificates gnupg lsb-release jq mailutils
log "System updated"

# ─── Step 2: Install Docker ───
echo -e "\n${BOLD}Step 2/8: Docker${NC}"
if ! command -v docker &>/dev/null; then
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
    log "Docker installed"
else
    log "Docker already installed ($(docker --version | awk '{print $3}'))"
fi

if ! command -v docker compose &>/dev/null && ! docker compose version &>/dev/null; then
    apt-get install -y -qq docker-compose-plugin
    log "Docker Compose plugin installed"
else
    log "Docker Compose already installed"
fi

# ─── Step 3: Timezone ───
echo -e "\n${BOLD}Step 3/8: Timezone${NC}"
timedatectl set-timezone "${SERVER_TIMEZONE:-Europe/Sarajevo}"
log "Timezone set to ${SERVER_TIMEZONE:-Europe/Sarajevo}"

# ─── Step 4: Firewall (UFW) ───
echo -e "\n${BOLD}Step 4/8: Firewall${NC}"
ufw --force reset > /dev/null 2>&1
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp comment 'SSH'
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'
ufw --force enable
log "UFW configured (SSH + HTTP + HTTPS only)"

# ─── Step 5: Fail2Ban ───
echo -e "\n${BOLD}Step 5/8: Fail2Ban${NC}"
cat > /etc/fail2ban/jail.local <<'JAIL'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5
backend = systemd

[sshd]
enabled = true
port = ssh
filter = sshd
maxretry = 3
bantime = 7200
JAIL
systemctl enable fail2ban
systemctl restart fail2ban
log "Fail2Ban configured (SSH: 3 attempts, 2h ban)"

# ─── Step 6: SSH Hardening ───
echo -e "\n${BOLD}Step 6/8: SSH Hardening${NC}"

# Check for SSH key before hardening
[[ -f /root/.ssh/authorized_keys ]] && [[ -s /root/.ssh/authorized_keys ]] || err "No SSH key found! Add your SSH key first to avoid lockout."

SSHD_CONFIG="/etc/ssh/sshd_config"
# Disable password auth (only key-based)
sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication no/' "$SSHD_CONFIG"
sed -i 's/^#*PermitRootLogin.*/PermitRootLogin prohibit-password/' "$SSHD_CONFIG"
sed -i 's/^#*MaxAuthTries.*/MaxAuthTries 3/' "$SSHD_CONFIG"
sed -i 's/^#*X11Forwarding.*/X11Forwarding no/' "$SSHD_CONFIG"

# Validate sshd_config before restarting
sshd -t || err "Invalid sshd_config"
# Ubuntu 24.04 uses ssh.service, not sshd
    if systemctl list-units --type=service | grep -q "ssh.service"; then
        systemctl restart ssh
    else
        systemctl restart sshd
    fi
log "SSH hardened (key-only, max 3 attempts)"

# ─── Step 7: Prepare & Start Services ───
echo -e "\n${BOLD}Step 7/8: Docker Services${NC}"

# Create directories
mkdir -p "$PROJECT_DIR/backups"
mkdir -p /var/log

# Initial deploy: use HTTP-only nginx config (no SSL yet)
if [[ ! -d "/etc/letsencrypt/live/${DOMAIN}" ]]; then
    warn "No SSL cert yet — starting with HTTP-only config"
    cp "$PROJECT_DIR/nginx/conf.d/http-only.conf.initial" "$PROJECT_DIR/nginx/conf.d/default.conf.bak"
    cp "$PROJECT_DIR/nginx/conf.d/http-only.conf.initial" "$PROJECT_DIR/nginx/conf.d/default.conf"
fi

# Pull and start
cd "$PROJECT_DIR"
docker compose pull
docker compose up -d

log "All containers started"

# Wait for services to be healthy
echo -n "  Waiting for services"
for i in $(seq 1 30); do
    if docker exec openclaw-postgres pg_isready -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" &>/dev/null; then
        echo ""
        log "PostgreSQL is ready"
        break
    fi
    echo -n "."
    sleep 2
done

# ─── Step 7b: SSL Certificate ───
if [[ ! -d "/etc/letsencrypt/live/${DOMAIN}" ]]; then
    echo -e "\n${BOLD}Step 7b: SSL Certificate${NC}"

    # Get certificate via Certbot
    docker compose run --rm certbot certonly \
        --webroot \
        --webroot-path=/var/www/certbot \
        --email "${LETSENCRYPT_EMAIL}" \
        --agree-tos \
        --no-eff-email \
        -d "${DOMAIN}" \
        ${CERTBOT_DOMAINS:+-d $(echo "$CERTBOT_DOMAINS" | tr ',' '\n' | sed 's/^ *//' | sed 's/^/-d /' | tr '\n' ' ')}

    if [[ -d "/etc/letsencrypt/live/${DOMAIN}" ]]; then
        log "SSL certificate obtained"

        # Switch to HTTPS nginx config
        # Replace placeholder domain in default.conf
        HTTPS_CONF="$PROJECT_DIR/nginx/conf.d/default.conf"
        cp "$PROJECT_DIR/nginx/conf.d/default.conf.bak" "$HTTPS_CONF.orig" 2>/dev/null || true

        # Read the original HTTPS config and replace placeholders
        sed "s|_DOMAIN_PLACEHOLDER_|${DOMAIN//&/\\&}|g" \
            "$PROJECT_DIR/nginx/conf.d/default.conf.orig" > "$HTTPS_CONF" 2>/dev/null || \
        sed -i "s|_DOMAIN_PLACEHOLDER_|${DOMAIN//&/\\&}|g" "$HTTPS_CONF"

        docker compose restart nginx
        log "Nginx switched to HTTPS"
    else
        warn "SSL certificate failed — staying on HTTP. Run certbot manually later."
    fi
else
    log "SSL certificate already exists"
    # Ensure domain placeholder is replaced
    sed -i "s|_DOMAIN_PLACEHOLDER_|${DOMAIN//&/\\&}|g" "$PROJECT_DIR/nginx/conf.d/default.conf"
    docker compose restart nginx
fi

# ─── Step 8: Make scripts executable ───
echo -e "\n${BOLD}Step 8/10: Script Permissions${NC}"
chmod +x "$SCRIPT_DIR"/provision-bundle.sh 2>/dev/null || true
chmod +x "$SCRIPT_DIR"/deploy-onboarding-agent.sh 2>/dev/null || true
chmod +x "$SCRIPT_DIR"/setup-channels.sh 2>/dev/null || true
chmod +x "$SCRIPT_DIR"/monitor.sh 2>/dev/null || true
chmod +x "$SCRIPT_DIR"/backup.sh 2>/dev/null || true
chmod +x "$SCRIPT_DIR"/status.sh 2>/dev/null || true
chmod +x "$SCRIPT_DIR"/restore.sh 2>/dev/null || true
log "All scripts made executable"

# ─── Step 9: Deploy Onboarding Agent ───
echo -e "\n${BOLD}Step 9/10: Onboarding Agent${NC}"
# Wait for openclaw-platform to be healthy
echo -n "  Waiting for OpenClaw Platform"
for i in $(seq 1 30); do
    PLATFORM_STATUS=$(docker inspect --format='{{.State.Health.Status}}' openclaw-platform 2>/dev/null || echo "starting")
    if [[ "$PLATFORM_STATUS" == "healthy" ]]; then
        echo ""
        log "OpenClaw Platform is healthy"
        break
    fi
    echo -n "."
    sleep 3
done

# Deploy onboarding agent
if [[ -x "$SCRIPT_DIR/deploy-onboarding-agent.sh" ]]; then
    "$SCRIPT_DIR/deploy-onboarding-agent.sh" && log "Onboarding agent deployed" || warn "Onboarding agent deploy failed — run manually later"
fi

# Setup channels if credentials are available
if [[ -x "$SCRIPT_DIR/setup-channels.sh" ]]; then
    "$SCRIPT_DIR/setup-channels.sh" && log "Channels configured" || warn "Channel setup incomplete — run setup-channels.sh later with credentials"
fi

# ─── Step 10: Cron Jobs ───
echo -e "\n${BOLD}Step 10/10: Cron Jobs${NC}"

# Remove old openclaw cron entries and add new ones atomically
{ crontab -l 2>/dev/null | grep -v "openclaw" || true; cat <<CRON
# OpenClaw Balkan — Automated Tasks
0 3 * * * /opt/openclaw/scripts/backup.sh >> /var/log/openclaw-backup.log 2>&1
*/5 * * * * /opt/openclaw/scripts/monitor.sh >> /var/log/openclaw-monitor.log 2>&1
0 4 * * 0 docker system prune -af --volumes --filter "until=168h" >> /var/log/openclaw-docker-prune.log 2>&1
CRON
} | crontab -

log "Cron jobs installed (backup 3:00, monitor every 5min, prune weekly)"

# ─── Done ───
echo ""
echo -e "${BOLD}══════════════════════════════════════════${NC}"
echo -e "${GREEN}  Deployment complete!${NC}"
echo -e "${BOLD}══════════════════════════════════════════${NC}"
echo ""
echo "  Domain:     https://${DOMAIN}"
echo "  Status:     ./scripts/status.sh"
echo "  Backup:     ./scripts/backup.sh"
echo "  Restore:    ./scripts/restore.sh <file>"
echo "  Monitor:    tail -f /var/log/openclaw-monitor.log"
echo ""
echo "  Next steps:"
echo "  1. Point your DNS A record to this server's IP"
echo "  2. Run ./scripts/status.sh to verify everything"
echo "  3. Configure OpenClaw at https://${DOMAIN}"
echo ""
