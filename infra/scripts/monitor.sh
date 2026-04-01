#!/usr/bin/env bash
# ============================================
# OpenClaw Balkan — System Monitor
# ============================================
# Runs every 5 minutes via cron. Checks system health
# and sends alerts if thresholds are exceeded.
#
# Cron entry (added by deploy.sh):
#   */5 * * * * /opt/openclaw/scripts/monitor.sh >> /var/log/openclaw-monitor.log 2>&1

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

if [[ -f "$PROJECT_DIR/.env" ]]; then
    set -a
    source "$PROJECT_DIR/.env"
    set +a
fi

# ─── Thresholds ───
DISK_THRESHOLD=85       # percent
MEMORY_THRESHOLD=90     # percent
CPU_THRESHOLD=90        # percent (5-min load average)

ALERT_FILE="/tmp/openclaw_alert_sent"
HEALTHCHECK="${HEALTHCHECK_URL:-}"

# ─── Helper: Send alert with deduplication ───
send_alert() {
    local subject="$1"
    local body="$2"
    local severity="$3"

    # Check if alert was sent in the last 30 minutes
    ALERT_KEY=$(echo "$subject" | md5sum | cut -d' ' -f1)
    ALERT_MARKER="${ALERT_FILE}_${ALERT_KEY}"

    if [[ -f "$ALERT_MARKER" ]]; then
        LAST_ALERT=$(<"$ALERT_MARKER")
        TIME_SINCE=$(($(date +%s) - LAST_ALERT))
        if [[ $TIME_SINCE -lt 1800 ]]; then
            return  # Skip duplicate alert within 30 minutes
        fi
    fi

    echo "[$(date)] ALERT [$severity]: $subject"
    echo "$body"

    # Send email if configured
    if [[ -n "${ALERT_EMAIL:-}" ]] && command -v mail &>/dev/null; then
        echo "$body" | mail -s "[OpenClaw $severity] $subject" "${ALERT_EMAIL}"
    fi

    # Update alert timestamp
    echo "$(date +%s)" > "$ALERT_MARKER"

    # Ping healthcheck with failure
    if [[ -n "$HEALTHCHECK" ]] && [[ "$severity" == "CRITICAL" ]]; then
        curl -fsS --retry 3 "${HEALTHCHECK}/fail" > /dev/null 2>&1 || true
    fi
}

ERRORS=0

# ─── Check 1: Disk Usage ───
DISK_USAGE=$(df / | awk 'NR==2 {gsub(/%/,""); print $5}')
if (( DISK_USAGE > DISK_THRESHOLD )); then
    send_alert "Disk usage ${DISK_USAGE}%" "Root filesystem is ${DISK_USAGE}% full. Threshold: ${DISK_THRESHOLD}%." "WARNING"
    ERRORS=$((ERRORS + 1))
fi

# ─── Check 2: Memory Usage ───
MEMORY_USAGE=$(free | awk '/Mem:/ {printf("%.0f", ($3/$2) * 100)}')
if (( MEMORY_USAGE > MEMORY_THRESHOLD )); then
    send_alert "Memory usage ${MEMORY_USAGE}%" "RAM is ${MEMORY_USAGE}% used. Threshold: ${MEMORY_THRESHOLD}%." "WARNING"
    ERRORS=$((ERRORS + 1))
fi

# ─── Check 3: CPU Load ───
CPU_CORES=$(nproc)
LOAD_AVG=$(awk -v cores="$CPU_CORES" '{printf("%.0f", $1 * 100 / cores)}' /proc/loadavg)
if (( LOAD_AVG > CPU_THRESHOLD )); then
    send_alert "CPU load ${LOAD_AVG}%" "5-min load average exceeds threshold. Cores: ${CPU_CORES}." "WARNING"
    ERRORS=$((ERRORS + 1))
fi

# ─── Check 4: Docker Containers ───
CONTAINERS=("openclaw-app" "openclaw-postgres" "openclaw-redis" "openclaw-nginx")
for CONTAINER in "${CONTAINERS[@]}"; do
    STATUS=$(docker inspect --format='{{.State.Status}}' "$CONTAINER" 2>/dev/null || echo "missing")
    if [[ "$STATUS" != "running" ]]; then
        send_alert "Container $CONTAINER is $STATUS" "Container $CONTAINER status: $STATUS. Attempting restart..." "CRITICAL"
        docker compose -f "$PROJECT_DIR/docker-compose.yml" up -d "$CONTAINER" 2>/dev/null || true
        # Verify container actually started
        sleep 2
        VERIFY_STATUS=$(docker inspect --format='{{.State.Status}}' "$CONTAINER" 2>/dev/null || echo "missing")
        if [[ "$VERIFY_STATUS" != "running" ]]; then
            send_alert "Container $CONTAINER restart failed" "Failed to restart $CONTAINER. Current status: $VERIFY_STATUS" "CRITICAL"
        fi
        ERRORS=$((ERRORS + 1))
    fi
done

# ─── Check 5: OpenClaw HTTP Health ───
PORT="${OPENCLAW_PORT:-3000}"
[[ "$PORT" =~ ^[0-9]+$ ]] || PORT=3000
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "http://localhost:${PORT}/api/health" 2>/dev/null || echo "000")
if [[ "$HTTP_STATUS" != "200" ]]; then
    send_alert "OpenClaw health check failed (HTTP $HTTP_STATUS)" "Health endpoint returned $HTTP_STATUS. Expected 200." "CRITICAL"
    ERRORS=$((ERRORS + 1))
fi

# ─── Check 6: PostgreSQL Connection ───
PG_OK=$(docker exec openclaw-postgres pg_isready -U "${POSTGRES_USER:-openclaw}" -d "${POSTGRES_DB:-openclaw}" 2>/dev/null && echo "ok" || echo "fail")
if [[ "$PG_OK" != "ok" ]]; then
    send_alert "PostgreSQL connection failed" "pg_isready returned failure." "CRITICAL"
    ERRORS=$((ERRORS + 1))
fi

# ─── Check 7: SSL Certificate Expiry ───
if [[ -n "${DOMAIN:-}" ]]; then
    EXPIRY_DAYS=$(timeout 5 bash -c "echo | openssl s_client -servername \"${DOMAIN}\" -connect \"${DOMAIN}:443\" 2>/dev/null | openssl x509 -noout -dates 2>/dev/null | grep notAfter | cut -d= -f2 | xargs -I{} bash -c 'echo \$(( ( \$(date -d \"{}\" +%s) - \$(date +%s) ) / 86400 ))'" 2>/dev/null || echo "999")
    if (( EXPIRY_DAYS < 14 )); then
        send_alert "SSL cert expires in ${EXPIRY_DAYS} days" "Certificate for ${DOMAIN} expires in ${EXPIRY_DAYS} days. Certbot should auto-renew." "WARNING"
        ERRORS=$((ERRORS + 1))
    fi
fi

# ─── Result ───
if (( ERRORS == 0 )); then
    echo "[$(date)] All checks passed. Disk: ${DISK_USAGE}%, Mem: ${MEMORY_USAGE}%, CPU: ${LOAD_AVG}%, HTTP: ${HTTP_STATUS}"
    # Ping healthcheck success
    if [[ -n "$HEALTHCHECK" ]]; then
        curl -fsS --retry 3 "${HEALTHCHECK}" > /dev/null 2>&1 || true
    fi
else
    echo "[$(date)] $ERRORS check(s) failed!"
fi
