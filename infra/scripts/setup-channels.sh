#!/usr/bin/env bash
# =============================================================================
# OpenClaw Balkan — Channel Setup Script
# Configures WhatsApp, Viber, and Email channels on the OpenClaw platform.
# Run once after deploying the platform: ./scripts/setup-channels.sh
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

if [[ -f "${PROJECT_DIR}/.env" ]]; then
  set -a; source "${PROJECT_DIR}/.env"; set +a
fi

CONTAINER="${OPENCLAW_CONTAINER:-openclaw-platform}"
OC="docker exec ${CONTAINER} openclaw"

BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

log()  { echo -e "${GREEN}[+]${NC} $*"; }
warn() { echo -e "${YELLOW}[!]${NC} $*"; }
err()  { echo -e "${RED}[x]${NC} $*"; }

echo -e "${BOLD}"
echo "══════════════════════════════════════════"
echo "  OpenClaw Balkan — Channel Setup"
echo "══════════════════════════════════════════"
echo -e "${NC}"

CHANNELS_ADDED=0

# ── WhatsApp Business ─────────────────────────────────────────────
echo -e "\n${BOLD}1. WhatsApp Business${NC}"
if [[ -n "${WHATSAPP_API_TOKEN:-}" ]] && [[ -n "${WHATSAPP_PHONE_NUMBER_ID:-}" ]]; then
  ${OC} channels add whatsapp \
    --name "whatsapp-business" \
    --config "{\"phone_number_id\": \"${WHATSAPP_PHONE_NUMBER_ID}\", \"access_token\": \"${WHATSAPP_API_TOKEN}\", \"business_account_id\": \"${WHATSAPP_BUSINESS_ACCOUNT_ID:-}\"}" \
    --non-interactive \
    --json 2>&1 && {
      log "WhatsApp channel added"
      CHANNELS_ADDED=$((CHANNELS_ADDED + 1))
    } || err "Failed to add WhatsApp channel"
else
  warn "Skipping WhatsApp — WHATSAPP_API_TOKEN or WHATSAPP_PHONE_NUMBER_ID not set"
  echo "  Set these in .env:"
  echo "    WHATSAPP_API_TOKEN=your_token"
  echo "    WHATSAPP_PHONE_NUMBER_ID=your_phone_id"
  echo "    WHATSAPP_BUSINESS_ACCOUNT_ID=your_account_id"
fi

# ── Viber Business ────────────────────────────────────────────────
echo -e "\n${BOLD}2. Viber Business${NC}"
if [[ -n "${VIBER_AUTH_TOKEN:-}" ]]; then
  ${OC} channels add viber \
    --name "viber-business" \
    --config "{\"auth_token\": \"${VIBER_AUTH_TOKEN}\", \"name\": \"${VIBER_BOT_NAME:-OpenClaw Balkan}\", \"webhook\": \"https://${DOMAIN:-balkan.activi.io}/api/webhooks/viber\"}" \
    --non-interactive \
    --json 2>&1 && {
      log "Viber channel added"
      CHANNELS_ADDED=$((CHANNELS_ADDED + 1))
    } || err "Failed to add Viber channel"
else
  warn "Skipping Viber — VIBER_AUTH_TOKEN not set"
  echo "  Set this in .env:"
  echo "    VIBER_AUTH_TOKEN=your_token"
  echo "    VIBER_BOT_NAME=OpenClaw Balkan"
fi

# ── Email (SMTP) ──────────────────────────────────────────────────
echo -e "\n${BOLD}3. Email (SMTP)${NC}"
if [[ -n "${SMTP_HOST:-}" ]] && [[ -n "${SMTP_USER:-}" ]]; then
  ${OC} channels add email \
    --name "email-smtp" \
    --config "{\"smtp_host\": \"${SMTP_HOST}\", \"smtp_port\": ${SMTP_PORT:-587}, \"smtp_user\": \"${SMTP_USER}\", \"smtp_pass\": \"${SMTP_PASS:-}\", \"from_address\": \"${SMTP_FROM:-setup@openclawbalkan.ba}\", \"from_name\": \"OpenClaw Balkan\"}" \
    --non-interactive \
    --json 2>&1 && {
      log "Email channel added"
      CHANNELS_ADDED=$((CHANNELS_ADDED + 1))
    } || err "Failed to add Email channel"
else
  warn "Skipping Email — SMTP_HOST or SMTP_USER not set"
  echo "  Set these in .env:"
  echo "    SMTP_HOST=smtp.example.com"
  echo "    SMTP_PORT=587"
  echo "    SMTP_USER=setup@openclawbalkan.ba"
  echo "    SMTP_PASS=your_password"
  echo "    SMTP_FROM=setup@openclawbalkan.ba"
fi

# ── Bind channels to onboarding agent ─────────────────────────────
echo -e "\n${BOLD}4. Binding channels to onboarding agent${NC}"
if (( CHANNELS_ADDED > 0 )); then
  ${OC} agents bind onboarding-agent whatsapp-business viber-business email-smtp \
    --non-interactive --json 2>&1 && {
      log "Channels bound to onboarding agent"
    } || warn "Some channels may not have been bound — verify manually"
else
  warn "No channels added — skipping bind"
fi

# ── List all channels ─────────────────────────────────────────────
echo -e "\n${BOLD}Current channels:${NC}"
${OC} channels list --json 2>&1 || true

# ── Summary ───────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}══════════════════════════════════════════${NC}"
echo -e "${GREEN}  ${CHANNELS_ADDED} channel(s) configured${NC}"
echo -e "${BOLD}══════════════════════════════════════════${NC}"
echo ""

if (( CHANNELS_ADDED < 3 )); then
  echo "Missing channels? Add the credentials to .env and re-run this script."
fi
