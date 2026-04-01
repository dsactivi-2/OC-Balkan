#!/usr/bin/env bash
# ============================================
# OpenClaw Balkan — PostgreSQL Restore Script
# ============================================
# Usage: ./scripts/restore.sh [backup_file]
# If no file specified, shows available backups.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

if [[ -f "$PROJECT_DIR/.env" ]]; then
    set -a
    source "$PROJECT_DIR/.env"
    set +a
fi

BACKUP_DIR="${BACKUP_PATH:-$PROJECT_DIR/backups}"

# ─── No argument: list available backups ───
if [[ $# -eq 0 ]]; then
    echo "Available backups:"
    echo "──────────────────"
    ls -lh "$BACKUP_DIR"/openclaw_*.sql.gz 2>/dev/null || echo "  No backups found."
    echo ""
    echo "Usage: $0 <backup_file>"
    echo "Example: $0 $BACKUP_DIR/openclaw_20260401_030000.sql.gz"
    exit 0
fi

BACKUP_FILE="$1"

if [[ ! -f "$BACKUP_FILE" ]]; then
    echo "ERROR: File not found: $BACKUP_FILE"
    exit 1
fi

# ─── Validate gzip format ───
gunzip -t "$BACKUP_FILE" 2>/dev/null || err "File is not valid gzip: $BACKUP_FILE"

echo "================================================"
echo "WARNING: This will REPLACE the current database!"
echo "File: $BACKUP_FILE"
echo "Database: ${POSTGRES_DB:-openclaw}"
echo "================================================"
read -rp "Type 'yes' to continue: " CONFIRM

if [[ "$CONFIRM" != "yes" ]]; then
    echo "Aborted."
    exit 0
fi

echo "[$(date)] Stopping OpenClaw..."
docker compose -f "$PROJECT_DIR/docker-compose.yml" stop openclaw

echo "[$(date)] Restoring from backup..."
# Plain SQL format: use psql instead of pg_restore
gunzip -c "$BACKUP_FILE" | docker exec -i openclaw-postgres psql \
    -U "${POSTGRES_USER:-openclaw}" \
    -d "${POSTGRES_DB:-openclaw}" \
    --set ON_ERROR_STOP=on \
    2>&1

RESTORE_EXIT=$?
if [[ $RESTORE_EXIT -ne 0 ]]; then
    echo "[$(date)] ERROR: Restore failed (exit code $RESTORE_EXIT)"
    echo "Check the output above. OpenClaw will NOT be started to avoid data corruption."
    exit 1
fi

echo "[$(date)] Starting OpenClaw..."
docker compose -f "$PROJECT_DIR/docker-compose.yml" start openclaw

echo "[$(date)] Restore complete."
