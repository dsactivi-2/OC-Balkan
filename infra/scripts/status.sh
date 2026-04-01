#!/usr/bin/env bash
# ============================================
# OpenClaw Balkan — Quick Status Dashboard
# ============================================
# Run manually: ./scripts/status.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

if [[ -f "$PROJECT_DIR/.env" ]]; then
    set -a
    source "$PROJECT_DIR/.env"
    set +a
fi

BOLD='\033[1m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m'

echo -e "${BOLD}══════════════════════════════════════════${NC}"
echo -e "${BOLD}  OpenClaw Balkan — System Status${NC}"
echo -e "${BOLD}══════════════════════════════════════════${NC}"
echo ""

# ─── System ───
echo -e "${BOLD}System:${NC}"
echo "  Hostname:  $(hostname)"
echo "  Uptime:    $(uptime -p)"
echo "  Disk:      $(df -h / | awk 'NR==2 {print $3 "/" $2 " (" $5 " used)"}')"
echo "  Memory:    $(free -h | awk '/Mem:/ {print $3 "/" $2 " (" int($3/$2*100) "% used)"}')"
echo "  CPU Load:  $(cat /proc/loadavg | awk '{print $1, $2, $3}') ($(nproc) cores)"
echo ""

# ─── Docker Containers ───
echo -e "${BOLD}Containers:${NC}"
CONTAINERS=("openclaw-app" "openclaw-postgres" "openclaw-redis" "openclaw-nginx" "openclaw-certbot")
for C in "${CONTAINERS[@]}"; do
    STATUS=$(docker inspect --format='{{.State.Status}}' "$C" 2>/dev/null || echo "not found")
    UPTIME=$(docker inspect --format='{{.State.StartedAt}}' "$C" 2>/dev/null | xargs -I{} date -d {} "+%Y-%m-%d %H:%M" 2>/dev/null || echo "n/a")
    if [[ "$STATUS" == "running" ]]; then
        echo -e "  ${GREEN}●${NC} $C: running (since $UPTIME)"
    else
        echo -e "  ${RED}●${NC} $C: $STATUS"
    fi
done
echo ""

# ─── OpenClaw Health ───
echo -e "${BOLD}Application:${NC}"
PORT="${OPENCLAW_PORT:-3000}"
[[ "$PORT" =~ ^[0-9]+$ ]] || PORT=3000
HTTP=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "http://localhost:${PORT}/api/health" 2>/dev/null || echo "000")
if [[ "$HTTP" == "200" ]]; then
    echo -e "  ${GREEN}●${NC} OpenClaw API: healthy (HTTP 200)"
else
    echo -e "  ${RED}●${NC} OpenClaw API: unhealthy (HTTP $HTTP)"
fi

# ─── PostgreSQL ───
PG_SIZE=$(PGPASSWORD="${POSTGRES_PASSWORD}" docker exec -e PGPASSWORD openclaw-postgres psql -U "${POSTGRES_USER:-openclaw}" -d "${POSTGRES_DB:-openclaw}" -tAc "SELECT pg_size_pretty(pg_database_size(current_database()));" 2>/dev/null || echo "n/a")
PG_CONNS=$(PGPASSWORD="${POSTGRES_PASSWORD}" docker exec -e PGPASSWORD openclaw-postgres psql -U "${POSTGRES_USER:-openclaw}" -d "${POSTGRES_DB:-openclaw}" -tAc "SELECT count(*) FROM pg_stat_activity;" 2>/dev/null || echo "n/a")
echo "  PostgreSQL: DB size=$PG_SIZE, connections=$PG_CONNS"
echo ""

# ─── Backups ───
echo -e "${BOLD}Backups:${NC}"
BACKUP_DIR="${BACKUP_PATH:-$PROJECT_DIR/backups}"
LATEST=$(ls -t "$BACKUP_DIR"/openclaw_*.sql.gz 2>/dev/null | head -1)
if [[ -n "$LATEST" ]]; then
    echo "  Latest:    $(basename "$LATEST") ($(du -h "$LATEST" | cut -f1))"
    echo "  Total:     $(ls "$BACKUP_DIR"/openclaw_*.sql.gz 2>/dev/null | wc -l) backups"
else
    echo -e "  ${YELLOW}●${NC} No backups found"
fi
echo ""

# ─── SSL ───
echo -e "${BOLD}SSL:${NC}"
if [[ -n "${DOMAIN:-}" ]]; then
    EXPIRY=$(timeout 5 bash -c "echo | openssl s_client -servername \"${DOMAIN}\" -connect \"${DOMAIN}:443\" 2>/dev/null | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2" || echo "n/a")
    echo "  Domain:    ${DOMAIN}"
    echo "  Expires:   ${EXPIRY}"
else
    echo "  Domain not configured yet"
fi
echo ""
echo -e "${BOLD}══════════════════════════════════════════${NC}"
