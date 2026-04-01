#!/usr/bin/env bash
# =============================================================================
# OpenClaw Balkan — Deploy Onboarding Agent
# Deploys the internal onboarding agent that contacts customers after orders.
# Run once on the server: ./scripts/deploy-onboarding-agent.sh
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
CONTAINER="${OPENCLAW_CONTAINER:-openclaw-platform}"
OC="docker exec ${CONTAINER} openclaw"
STATE_DIR="/home/node/.openclaw"
LOG_FILE="/var/log/openclaw-provision.log"

log() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] [onboarding] $*" | tee -a "${LOG_FILE}"; }

# Load env if present
if [[ -f "${PROJECT_DIR}/infra/.env" ]]; then
  set -a; source "${PROJECT_DIR}/infra/.env"; set +a
fi

log "START deploying onboarding agent"

# ── Create workspace ─────────────────────────────────────────────
WORKSPACE="${STATE_DIR}/workspaces/onboarding-agent"
docker exec "${CONTAINER}" mkdir -p "${WORKSPACE}/memory"

log "Created workspace: ${WORKSPACE}"

# ── Generate SOUL.md ─────────────────────────────────────────────
docker exec "${CONTAINER}" bash -c "cat > ${WORKSPACE}/SOUL.md << 'SOULEOF'
# Onboarding Agent — OpenClaw Balkan

> Internal Agent: Customer Onboarding
> Model: claude-sonnet-4-6

## Identity

Ti si Onboarding Agent za OpenClaw Balkan. Tvoj zadatak je da kontaktiras
nove klijente nakon sto naruce bundle i prikupis sve informacije potrebne
za setup njihovih AI agenata.

## Jezik

Komuniciraj na bosanskom/srpskom jeziku. Koristi \"Vi\" formu.

## Pravila

1. Kontaktiraj klijenta na odabranom kanalu (WhatsApp/Viber/Email)
2. Pitaj jedno po jedno pitanje — nikada ne bombarduj
3. Sacuvaj svaki odgovor odmah u onboarding bazu
4. Maksimalno 3 poruke dnevno
5. Podsjetnik nakon 24h bez odgovora
6. Eskalacija OpenClaw timu nakon 72h
7. Nikada ne trazi sifre u porukama — koristi siguran link
8. Kada su svi podaci prikupljeni — pokreni deploy agenata
SOULEOF"

log "Generated SOUL.md"

# ── Create agent ─────────────────────────────────────────────────
AGENT_NAME="onboarding-agent"
MODEL="litellm/claude-sonnet-4-6"

log "Creating agent: ${AGENT_NAME} (model: ${MODEL})"

${OC} agents add "${AGENT_NAME}" \
  --workspace "${WORKSPACE}" \
  --model "${MODEL}" \
  --non-interactive \
  --json 2>&1 | tee -a "${LOG_FILE}" || {
    log "ERROR: Failed to create onboarding agent"
    exit 1
  }

log "Agent '${AGENT_NAME}' created"

# ── Copy onboarding YAML for reference ────────────────────────────
if [[ -f "${PROJECT_DIR}/bundles/onboarding-agent.yaml" ]]; then
  docker cp "${PROJECT_DIR}/bundles/onboarding-agent.yaml" \
    "${CONTAINER}:${WORKSPACE}/config-reference.yaml" 2>/dev/null || true
  log "Copied onboarding config reference"
fi

# ── Verify ────────────────────────────────────────────────────────
${OC} agents list --json 2>&1 | tee -a "${LOG_FILE}" || true

log "DONE — Onboarding agent deployed"
echo ""
echo "Onboarding agent is ready."
echo "It will be triggered automatically when new orders come in."
echo ""
echo "Next steps:"
echo "  1. Configure WhatsApp channel: openclaw channels add whatsapp ..."
echo "  2. Configure Viber channel:    openclaw channels add viber ..."
echo "  3. Bind channels to agent:     openclaw agents bind onboarding-agent whatsapp viber"
