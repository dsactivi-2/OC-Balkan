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

declare -A BUNDLE_YAML=(
  [solo_agent]="solo-agent.yaml"
  [learning_buddy]="learning-buddy.yaml"
  [social_marketing_team]="social-marketing-team.yaml"
  [research_bundle]="research-bundle.yaml"
  [office_bundle]="office-bundle.yaml"
)

# Agent roles per bundle (pipe-separated)
declare -A BUNDLE_AGENTS=(
  [solo_agent]="agent"
  [learning_buddy]="erklaerer|quiz|lernplan|eltern"
  [social_marketing_team]="content|scheduling|community|ads"
  [research_bundle]="research|summary|citation|study-planner"
  [office_bundle]="termin|telefon|mail|dokument"
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

docker exec "${CONTAINER}" mkdir -p "${WORKSPACE}/memory" "${WORKSPACE}/docs" "${WORKSPACE}/config"

log "Created workspace: ${WORKSPACE}"

# ── Copy bundle YAML to workspace ────────────────────────────────
YAML_FILE="${BUNDLE_YAML[${BUNDLE_ID}]}"
if docker exec "${CONTAINER}" test -f "${BUNDLES_DIR}/${YAML_FILE}" 2>/dev/null; then
  docker exec "${CONTAINER}" cp "${BUNDLES_DIR}/${YAML_FILE}" "${WORKSPACE}/config/bundle.yaml"
  log "Copied bundle definition: ${YAML_FILE}"
else
  log "WARN: Bundle YAML not found at ${BUNDLES_DIR}/${YAML_FILE} — continuing without"
fi

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
6. Never share customer data with other customers.
7. Log important interactions to memory.
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

# ── Create agents via OpenClaw CLI ────────────────────────────────
IFS='|' read -ra AGENTS <<< "${BUNDLE_AGENTS[${BUNDLE_ID}]}"
AGENT_COUNT=0

for ROLE in "${AGENTS[@]}"; do
  AGENT_NAME="${SLUG}-${ROLE}"

  log "Creating agent: ${AGENT_NAME} (model: ${MODEL})"

  ${OC} agents add "${AGENT_NAME}" \
    --workspace "${WORKSPACE}" \
    --model "${MODEL}" \
    --non-interactive \
    --json 2>&1 | tee -a "${LOG_FILE}" || {
      log "WARN: Failed to create agent ${AGENT_NAME} — continuing"
      continue
    }

  AGENT_COUNT=$((AGENT_COUNT + 1))
  log "Agent '${AGENT_NAME}' created"
done

log "Created ${AGENT_COUNT}/${#AGENTS[@]} agents"

# ── Generate status file ────────────────────────────────────────
docker exec "${CONTAINER}" bash -c "cat > ${WORKSPACE}/STATUS.json << STATUSEOF
{
  \"order_ref\": \"${ORDER_REF}\",
  \"bundle_id\": \"${BUNDLE_ID}\",
  \"bundle_name\": \"${BUNDLE_NAME}\",
  \"model\": \"${MODEL}\",
  \"agent_count\": ${AGENT_COUNT},
  \"status\": \"provisioned\",
  \"provisioned_at\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",
  \"onboarding_status\": \"pending\"
}
STATUSEOF"

log "Generated STATUS.json"

# ── List agents to verify ────────────────────────────────────────
${OC} agents list --json 2>&1 | tee -a "${LOG_FILE}" || true

log "DONE provisioning ${ORDER_REF} (${BUNDLE_NAME}) — ${AGENT_COUNT} agents created"
log "Next step: Onboarding agent should contact customer to collect setup details"

echo "OK:${ORDER_REF}:${AGENT_COUNT}"
