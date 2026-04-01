#!/usr/bin/env bash
# ============================================
# OpenClaw Balkan — PostgreSQL Backup Script
# ============================================
# Runs daily via cron. Creates compressed backups
# and rotates old ones based on retention policy.
#
# Cron entry (added by deploy.sh):
#   0 3 * * * /opt/openclaw/scripts/backup.sh >> /var/log/openclaw-backup.log 2>&1

set -euo pipefail

# ─── Config ───
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Load environment
if [[ -f "$PROJECT_DIR/.env" ]]; then
    set -a
    source "$PROJECT_DIR/.env"
    set +a
fi

BACKUP_DIR="${BACKUP_PATH:-$PROJECT_DIR/backups}"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/openclaw_${TIMESTAMP}.sql.gz"

# ─── Ensure backup directory exists ───
mkdir -p "$BACKUP_DIR"

# ─── Pre-check: Container and disk space ───
docker inspect openclaw-postgres &>/dev/null || err "Container openclaw-postgres not found"

AVAIL=$(df --output=avail "$BACKUP_DIR" | tail -1)
[[ $AVAIL -gt 1048576 ]] || err "Less than 1GB free disk space"

echo "================================================"
echo "[$(date)] Starting PostgreSQL backup..."
echo "================================================"

# ─── Create backup to temp file first ───
BACKUP_TEMP="${BACKUP_FILE}.tmp"
docker exec openclaw-postgres pg_dump \
    -U "${POSTGRES_USER:-openclaw}" \
    -d "${POSTGRES_DB:-openclaw}" \
    --format=plain \
    --verbose \
    2>/dev/null | gzip -6 > "$BACKUP_TEMP"

# ─── Verify backup with gunzip test ───
if gunzip -t "$BACKUP_TEMP" 2>/dev/null; then
    mv "$BACKUP_TEMP" "$BACKUP_FILE"
    FILESIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "[$(date)] Backup created: $BACKUP_FILE ($FILESIZE)"
else
    rm -f "$BACKUP_TEMP"
    echo "[$(date)] ERROR: Backup file is corrupted!"
    # Ping healthcheck with failure
    if [[ -n "${HEALTHCHECK_URL:-}" ]]; then
        curl -fsS --retry 3 "${HEALTHCHECK_URL}/fail" > /dev/null 2>&1 || true
    fi
    exit 1
fi

# ─── Rotate old backups ───
DELETED=$(find "$BACKUP_DIR" -name "openclaw_*.sql.gz" -type f -mtime +${RETENTION_DAYS} -print -delete | wc -l)
echo "[$(date)] Rotated $DELETED backup(s) older than ${RETENTION_DAYS} days"

# ─── Summary ───
TOTAL_BACKUPS=$(find "$BACKUP_DIR" -name "openclaw_*.sql.gz" -type f | wc -l)
TOTAL_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
echo "[$(date)] Backup complete. Total: $TOTAL_BACKUPS backups, $TOTAL_SIZE"

# ─── Ping healthcheck on success ───
if [[ -n "${HEALTHCHECK_URL:-}" ]]; then
    curl -fsS --retry 3 "${HEALTHCHECK_URL}" > /dev/null 2>&1 || true
fi

echo "================================================"
echo "[$(date)] Backup finished successfully"
echo "================================================"
