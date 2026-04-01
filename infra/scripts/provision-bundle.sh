#!/usr/bin/env bash
# =============================================================================
# OpenClaw Balkan — Bundle Provisioning Script
# Usage: ./provision-bundle.sh <order_ref> <bundle_id>
# Called automatically by the order API after a new order is placed.
# =============================================================================

set -euo pipefail

ORDER_REF="${1:?Usage: provision-bundle.sh <order_ref> <bundle_id>}"
BUNDLE_ID="${2:?Usage: provision-bundle.sh <order_ref> <bundle_id>}"

CONTAINER="${OPENCLAW_CONTAINER:-openclaw-platform}"
OC="docker exec ${CONTAINER} openclaw"
STATE_DIR="/home/node/.openclaw"
BUNDLES_DIR="/opt/openclaw/bundles"
LOG_FILE="/var/log/openclaw-provision.log"

log() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] [${ORDER_REF}] $*" | tee -a "${LOG_FILE}"; }

# ── Validate bundle ──────────────────────────────────────────────
declare -A BUNDLE_NAMES=(
  [solo_agent]="Solo Agent"
  [learning_buddy]="Learning Buddy"
  [social_marketing_team]="Social Marketing Team"
  [research_bundle]="Research Bundle"
  [office_bundle]="Office Bundle"
)

declare -A BUNDLE_MODELS=(
  [solo_agent]="litellm/qwen3.5-uncensored"
  [learning_buddy]="litellm/claude-sonnet-4-6"
  [social_marketing_team]="litellm/qwen3.5-uncensored"
  [research_bundle]="litellm/claude-sonnet-4-6"
  [office_bundle]="litellm/claude-sonnet-4-6"
)

# Agent counts per bundle
declare -A BUNDLE_AGENT_COUNT=(
  [solo_agent]=1
  [learning_buddy]=4
  [social_marketing_team]=4
  [research_bundle]=4
  [office_bundle]=4
)

if [[ -z "${BUNDLE_NAMES[${BUNDLE_ID}]:-}" ]]; then
  log "ERROR: Unknown bundle_id: ${BUNDLE_ID}"
  exit 1
fi

BUNDLE_NAME="${BUNDLE_NAMES[${BUNDLE_ID}]}"
MODEL="${BUNDLE_MODELS[${BUNDLE_ID}]}"
SLUG=$(echo "${ORDER_REF}" | tr '[:upper:]' '[:lower:]' | tr -c 'a-z0-9-' '-')

log "START provisioning: ${BUNDLE_NAME} (${BUNDLE_ID}) for order ${ORDER_REF}"

# ── Create customer workspace directory ──────────────────────────
WORKSPACE="${STATE_DIR}/workspaces/${SLUG}"

docker exec "${CONTAINER}" mkdir -p "${WORKSPACE}/memory"

log "Created workspace: ${WORKSPACE}"

# ── Generate SOUL.md for the customer workspace ──────────────────
docker exec "${CONTAINER}" bash -c "cat > ${WORKSPACE}/SOUL.md << 'SOULEOF'
# ${BUNDLE_NAME} — Customer Workspace

> Order: ${ORDER_REF}
> Bundle: ${BUNDLE_ID}
> Provisioned: $(date -u +%Y-%m-%dT%H:%M:%SZ)

## Identity

You are the ${BUNDLE_NAME} agent team for a customer of OpenClaw Balkan.
Your primary language is Bosnian/Serbian (BKS). You communicate naturally and professionally.

## Rules

1. Always respond in the customer's language (Bosnian or Serbian)
2. Never reveal you are AI unless directly asked. You are a \"digitalni asistent\".
3. Escalate to the business owner when unsure.
4. Be concise: max 3 sentences for comments, 5 for messages.
5. Use \"Vi\" form for professional contexts.
SOULEOF"

log "Generated SOUL.md"

# ── Generate USER.md ─────────────────────────────────────────────
docker exec "${CONTAINER}" bash -c "cat > ${WORKSPACE}/USER.md << 'USEREOF'
# Customer Profile

> Auto-generated at provisioning. Update during onboarding.

## Business Details
- **Order Reference:** ${ORDER_REF}
- **Bundle:** ${BUNDLE_NAME}
- **Company:** (to be filled during onboarding)
- **Business Type:** (to be filled during onboarding)
- **Working Hours:** (to be filled during onboarding)
- **Contact Phone:** (to be filled during onboarding)
- **Contact Email:** (to be filled during onboarding)

## FAQ / Knowledge Base
(to be populated during onboarding)

## Communication Tone
Default: Professional, friendly, concise.
USEREOF"

log "Generated USER.md"

# ── Create the agent via OpenClaw CLI ────────────────────────────
AGENT_NAME="${SLUG}"

${OC} agents add "${AGENT_NAME}" \
  --workspace "${WORKSPACE}" \
  --model "${MODEL}" \
  --non-interactive \
  --json 2>&1 | tee -a "${LOG_FILE}"

log "Agent '${AGENT_NAME}' created with model ${MODEL}"

# ── List agents to verify ────────────────────────────────────────
${OC} agents list --json 2>&1 | tee -a "${LOG_FILE}"

log "DONE provisioning ${ORDER_REF} (${BUNDLE_NAME})"
log "Next step: Onboarding agent should contact customer to collect setup details"

echo "OK:${ORDER_REF}:${AGENT_NAME}"
