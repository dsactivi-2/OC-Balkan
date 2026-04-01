#!/usr/bin/env bash
# =============================================================================
# OpenClaw Balkan — Kunden-Deployment (8 Schritte)
#
# Verwendung:
#   ./deploy-customer.sh \
#     --customer-id "kunde001" \
#     --bundle "social-marketing-team" \
#     --email "inhaber@friseur.ba" \
#     --name "Friseur Amira"
#
# Voraussetzungen:
#   - SSH-Alias "rocky2" konfiguriert in ~/.ssh/config
#   - LITELLM_MASTER_KEY als Umgebungsvariable gesetzt
#     (alternativ: deploy/.env.deploy Datei mit LITELLM_MASTER_KEY=...)
#   - Qdrant auf CCT via SSH-Tunnel erreichbar (Port 16333)
#   - Docker + nginx + certbot auf rocky2 installiert
# =============================================================================

set -euo pipefail

# ─── Pfade ───────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${SCRIPT_DIR}/logs"
LOG_FILE="${LOG_DIR}/deploy-$(date +%Y%m%d-%H%M%S).log"
TEMPLATE_COMPOSE="${SCRIPT_DIR}/docker-compose.customer.yml"
TEMPLATE_NGINX="${SCRIPT_DIR}/nginx-customer.conf.template"
REMOTE_ENV_GEN="${SCRIPT_DIR}/remote-generate-env.sh"

# ─── Server-Konfiguration ────────────────────────────────────────────────────
ROCKY2_SSH="rocky2"
ROCKY2_DEPLOY_BASE="/opt/openclaw-balkan/kunden"
LITELLM_LOCAL="http://127.0.0.1:14000"
CCT_QDRANT="http://127.0.0.1:16333"
NGINX_CONF_DIR="/etc/nginx/conf.d"
BASE_DOMAIN="openclaw-balkan.com"
OPENCLAW_IMAGE="openclaw/openclaw:latest"
CERTBOT_MAIL="admin@openclaw-balkan.com"

# ─── LiteLLM Master-Key (nur aus Umgebungsvariable oder .env.deploy) ─────────
# Konfigurieren via:  export LITELLM_MASTER_KEY="..."
# Oder in Datei:      echo 'LITELLM_MASTER_KEY=...' > deploy/.env.deploy
_load_master_key() {
  if [[ -n "${LITELLM_MASTER_KEY:-}" ]]; then return 0; fi
  local env_file="${SCRIPT_DIR}/.env.deploy"
  if [[ -f "${env_file}" ]]; then
    # Lese nur diesen einen Wert, ohne eval
    local val
    val="$(grep -E '^LITELLM_MASTER_KEY=' "${env_file}" | cut -d'=' -f2- | tr -d '"'"'")"
    [[ -n "${val}" ]] && export LITELLM_MASTER_KEY="${val}"
  fi
}

# ─── Bundle-Konfiguration ─────────────────────────────────────────────────────
declare -A BUNDLE_BUDGETS=(
  ["social-marketing-team"]="5"
  ["office-bundle"]="10"
  ["research-bundle"]="15"
  ["learning-buddy"]="10"
  ["solo-agent"]="3"
)

declare -A BUNDLE_MODELS=(
  ["social-marketing-team"]="qwen3.5-uncensored"
  ["office-bundle"]="claude-sonnet-4-6"
  ["research-bundle"]="claude-sonnet-4-6"
  ["learning-buddy"]="claude-sonnet-4-6"
  ["solo-agent"]="qwen3.5-uncensored"
)

# =============================================================================
# Hilfsfunktionen
# =============================================================================

log() {
  local level="$1"; shift
  local ts; ts="$(date '+%Y-%m-%d %H:%M:%S')"
  local line="[${ts}] [${level}] $*"
  echo "${line}" | tee -a "${LOG_FILE}"
}
log_info()  { log "INFO " "$@"; }
log_ok()    { log "OK   " "$@"; }
log_warn()  { log "WARN " "$@"; }
log_error() { log "ERROR" "$@"; }

die() {
  log_error "$@"
  log_error "Deployment abgebrochen. Log: ${LOG_FILE}"
  exit 1
}

require_tool() { command -v "$1" >/dev/null 2>&1 || die "Benoetigt: $1 — bitte installieren"; }
require_file() { [[ -f "$1" ]] || die "Datei fehlt: $1"; }

# SSH-Befehl auf rocky2
r2() { ssh "${ROCKY2_SSH}" "$@"; }

# Datei sicher auf rocky2 uebertragen
r2_upload() { scp "$1" "${ROCKY2_SSH}:$2"; }

# =============================================================================
# Argument-Parsing
# =============================================================================

CUSTOMER_ID=""
BUNDLE=""
EMAIL=""
NAME=""
DRY_RUN=false
SKIP_SSL=false

usage() {
  cat <<'EOF'
Verwendung: deploy-customer.sh [OPTIONEN]

Pflichtfelder:
  --customer-id ID    Kunden-ID (z.B. "kunde001")
  --bundle BUNDLE     social-marketing-team | office-bundle |
                      research-bundle | learning-buddy | solo-agent
  --email EMAIL       E-Mail des Kunden
  --name NAME         Unternehmensname

Optionen:
  --dry-run           Nur simulieren, nichts ausfuehren
  --skip-ssl          SSL-Schritt ueberspringen (Entwicklung)
  -h, --help          Hilfe anzeigen
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --customer-id) CUSTOMER_ID="$2"; shift 2 ;;
    --bundle)      BUNDLE="$2";      shift 2 ;;
    --email)       EMAIL="$2";       shift 2 ;;
    --name)        NAME="$2";        shift 2 ;;
    --dry-run)     DRY_RUN=true;     shift ;;
    --skip-ssl)    SKIP_SSL=true;    shift ;;
    -h|--help)     usage; exit 0 ;;
    *) die "Unbekanntes Argument: $1 — benutze --help" ;;
  esac
done

[[ -n "${CUSTOMER_ID}" ]] || { usage; die "--customer-id fehlt"; }
[[ -n "${BUNDLE}" ]]      || { usage; die "--bundle fehlt"; }
[[ -n "${EMAIL}" ]]       || { usage; die "--email fehlt"; }
[[ -n "${NAME}" ]]        || { usage; die "--name fehlt"; }
[[ -n "${BUNDLE_BUDGETS[$BUNDLE]+_}" ]] || \
  die "Unbekanntes Bundle: '${BUNDLE}'. Valide: ${!BUNDLE_BUDGETS[*]}"

# =============================================================================
# Initialisierung
# =============================================================================

mkdir -p "${LOG_DIR}"
log_info "============================================"
log_info "OpenClaw Balkan — Deployment Start"
log_info "============================================"
log_info "Customer-ID:  ${CUSTOMER_ID}"
log_info "Bundle:       ${BUNDLE}"
log_info "E-Mail:       ${EMAIL}"
log_info "Name:         ${NAME}"
[[ "${DRY_RUN}" == true ]] && log_warn "DRY-RUN aktiv — keine Aenderungen"

require_tool ssh
require_tool scp
require_tool curl
require_tool sed
require_file "${TEMPLATE_COMPOSE}"
require_file "${TEMPLATE_NGINX}"
require_file "${REMOTE_ENV_GEN}"

# Master-Key laden (nie hardcoded)
_load_master_key
[[ -n "${LITELLM_MASTER_KEY:-}" ]] || \
  die "LITELLM_MASTER_KEY nicht gesetzt. Bitte als env var oder in .env.deploy konfigurieren."

# SSH-Verbindung testen
log_info "Pruefe SSH-Verbindung zu rocky2..."
r2 "echo ok" >/dev/null 2>&1 || die "SSH zu rocky2 nicht moeglich"
log_ok "SSH-Verbindung ok"

# =============================================================================
# Schritt 1: Customer-ID + Subdomain ableiten
# =============================================================================
log_info "── Schritt 1: Customer-ID + Subdomain ──"

SUBDOMAIN="${CUSTOMER_ID,,}"
SUBDOMAIN="${SUBDOMAIN//_/-}"
SUBDOMAIN="${SUBDOMAIN//[^a-z0-9-]/}"
FQDN="${SUBDOMAIN}.${BASE_DOMAIN}"
DEPLOY_DIR="${ROCKY2_DEPLOY_BASE}/${CUSTOMER_ID}"
BUNDLE_MODEL="${BUNDLE_MODELS[$BUNDLE]}"
BUDGET="${BUNDLE_BUDGETS[$BUNDLE]}"

log_info "FQDN:        ${FQDN}"
log_info "Deploy-Dir:  ${DEPLOY_DIR}"

if [[ "${DRY_RUN}" == false ]]; then
  r2 "test -d '${DEPLOY_DIR}'" 2>/dev/null && \
    die "Verzeichnis existiert bereits: ${DEPLOY_DIR}"
  r2 "mkdir -p '${DEPLOY_DIR}'"
  log_ok "Schritt 1 OK"
else
  log_info "[DRY-RUN] mkdir -p ${DEPLOY_DIR}"
fi

# =============================================================================
# Schritt 2: Docker-Netzwerk + Volumes (isoliert pro Kunde)
# =============================================================================
log_info "── Schritt 2: Docker-Netzwerk + Volumes ──"

NET="net_${CUSTOMER_ID}"
VOL_DATA="vol_${CUSTOMER_ID}_data"
VOL_PG="vol_${CUSTOMER_ID}_pg"

if [[ "${DRY_RUN}" == false ]]; then
  r2 "docker network inspect '${NET}' >/dev/null 2>&1 || docker network create --driver bridge '${NET}'" \
    || die "Netzwerk-Erstellung fehlgeschlagen"
  r2 "docker volume inspect '${VOL_DATA}' >/dev/null 2>&1 || docker volume create '${VOL_DATA}'" \
    || die "Volume ${VOL_DATA} fehlgeschlagen"
  r2 "docker volume inspect '${VOL_PG}' >/dev/null 2>&1 || docker volume create '${VOL_PG}'" \
    || die "Volume ${VOL_PG} fehlgeschlagen"
  log_ok "Schritt 2 OK"
else
  log_info "[DRY-RUN] Netzwerk ${NET}, Volumes ${VOL_DATA} ${VOL_PG}"
fi

# =============================================================================
# Schritt 3: OpenClaw-Container starten
# =============================================================================
log_info "── Schritt 3: Container starten ──"

# Container-Port: ab 13000, hochzaehlen basierend auf laufenden Kunden
if [[ "${DRY_RUN}" == false ]]; then
  CNT=$(r2 "docker ps --filter 'label=openclaw.customer' --format '{{.ID}}' 2>/dev/null | wc -l" || echo "0")
  PORT=$((13000 + CNT))
else
  PORT=13001
fi
log_info "Container-Port: ${PORT}"

DB_USER="oc_${CUSTOMER_ID//[^a-z0-9]/_}"
DB_NAME="${DB_USER}"

if [[ "${DRY_RUN}" == false ]]; then
  # .env wird REMOTE generiert — keine Credentials lokal sichtbar
  log_info "Generiere .env auf rocky2 (remote)..."
  r2 "bash -s '${CUSTOMER_ID}' '${DB_USER}' '${DB_NAME}' \
      '${BUNDLE}' '${FQDN}' '${BUNDLE_MODEL}' '${PORT}' \
      '${LITELLM_LOCAL}' '${NAME}' '${EMAIL}' \
      '${DEPLOY_DIR}'" < "${REMOTE_ENV_GEN}" \
    || die ".env-Generierung auf rocky2 fehlgeschlagen"
  log_ok ".env remote erstellt"

  # docker-compose Template mit neutralen Platzhaltern ersetzen
  local_cmp="/tmp/dc.${CUSTOMER_ID}.yml"
  sed \
    -e "s|{CUSTOMER_ID}|${CUSTOMER_ID}|g" \
    -e "s|{NET}|${NET}|g" \
    -e "s|{VOL_DATA}|${VOL_DATA}|g" \
    -e "s|{VOL_PG}|${VOL_PG}|g" \
    -e "s|{PORT}|${PORT}|g" \
    -e "s|{BUNDLE}|${BUNDLE}|g" \
    -e "s|{IMAGE}|${OPENCLAW_IMAGE}|g" \
    "${TEMPLATE_COMPOSE}" > "${local_cmp}"
  r2_upload "${local_cmp}" "${DEPLOY_DIR}/docker-compose.yml"
  rm -f "${local_cmp}"

  r2 "cd '${DEPLOY_DIR}' && docker compose up -d --pull always" \
    || die "docker compose up fehlgeschlagen"

  # Warten auf healthy (max 90s)
  log_info "Warte auf Container-Health (max 90s)..."
  local_attempts=0
  until r2 "docker inspect --format='{{.State.Health.Status}}' 'openclaw_${CUSTOMER_ID}' 2>/dev/null | grep -q healthy" 2>/dev/null; do
    local_attempts=$((local_attempts + 1))
    [[ $local_attempts -ge 18 ]] && { log_warn "Container nicht healthy nach 90s"; break; }
    sleep 5
  done

  log_ok "Schritt 3 OK: Container auf Port ${PORT}"
else
  log_info "[DRY-RUN] Container openclaw_${CUSTOMER_ID} auf Port ${PORT}"
fi

# =============================================================================
# Schritt 4: Qdrant-Collections anlegen (CCT via SSH-Tunnel)
# =============================================================================
log_info "── Schritt 4: Qdrant Collections ──"

_create_qdrant_col() {
  local col="$1"
  local resp
  resp=$(curl -sf -X PUT "${CCT_QDRANT}/collections/${col}" \
    -H "Content-Type: application/json" \
    -d '{"vectors":{"size":1024,"distance":"Cosine"},"optimizers_config":{"default_segment_number":2}}' \
    2>&1) || true
  if echo "${resp}" | grep -q '"status":"ok"'; then
    log_ok "Qdrant Collection: ${col}"
  else
    log_warn "Qdrant ${col}: ${resp}"
  fi
}

if [[ "${DRY_RUN}" == false ]]; then
  _create_qdrant_col "${CUSTOMER_ID}_knowledge"
  _create_qdrant_col "${CUSTOMER_ID}_conversations"
  log_ok "Schritt 4 OK"
else
  log_info "[DRY-RUN] Qdrant Collections: ${CUSTOMER_ID}_knowledge + _conversations"
fi

# =============================================================================
# Schritt 5: LiteLLM Virtual Key erstellen
# =============================================================================
log_info "── Schritt 5: LiteLLM Virtual Key ──"

VKEY=""
if [[ "${DRY_RUN}" == false ]]; then
  # API-Call auf rocky2 (LITELLM_MASTER_KEY wird als env var uebergeben, nie in Datei geschrieben)
  RESP=$(r2 "LITELLM_MASTER_KEY='${LITELLM_MASTER_KEY}' \
    curl -sf -X POST '${LITELLM_LOCAL}/key/generate' \
      -H 'Authorization: Bearer \${LITELLM_MASTER_KEY}' \
      -H 'Content-Type: application/json' \
      -d '{\"key_alias\":\"${CUSTOMER_ID}\",
           \"metadata\":{\"customer_id\":\"${CUSTOMER_ID}\",\"bundle\":\"${BUNDLE}\"},
           \"tags\":[\"${CUSTOMER_ID}\",\"${BUNDLE}\",\"openclaw-balkan\"],
           \"max_budget\":${BUDGET},
           \"budget_duration\":\"1mo\",
           \"models\":[\"${BUNDLE_MODEL}\",\"claude-sonnet-4-6\",\"qwen3.5-uncensored\"]}'" \
  2>&1) || die "LiteLLM Key-Generierung fehlgeschlagen"

  VKEY=$(echo "${RESP}" | grep -o '"key":"[^"]*"' | cut -d'"' -f4 || true)

  if [[ -z "${VKEY}" ]]; then
    log_warn "VKEY nicht extrahierbar. Antwort: ${RESP}"
    VKEY="MANUAL_SETUP_REQUIRED"
  else
    log_ok "Virtual Key erstellt (Budget: ${BUDGET} USD/Monat)"
    # Key remote in .env eintragen — wird nie lokal gespeichert
    r2 "sed -i 's|LITELLM_VKEY=PENDING|LITELLM_VKEY=${VKEY}|' '${DEPLOY_DIR}/.env'"
    r2 "cd '${DEPLOY_DIR}' && docker compose restart openclaw" \
      || log_warn "Neustart nach Key-Update fehlgeschlagen"
  fi
  log_ok "Schritt 5 OK"
else
  VKEY="DRY_RUN"
  log_info "[DRY-RUN] LiteLLM Virtual Key (Budget: ${BUDGET} USD/Monat)"
fi

# =============================================================================
# Schritt 6: Nginx-Config schreiben + reload
# =============================================================================
log_info "── Schritt 6: Nginx-Config ──"

local_ng="/tmp/ng.${CUSTOMER_ID}.conf"
sed \
  -e "s|{CUSTOMER_ID}|${CUSTOMER_ID}|g" \
  -e "s|{FQDN}|${FQDN}|g" \
  -e "s|{PORT}|${PORT}|g" \
  -e "s|{SUBDOMAIN}|${SUBDOMAIN}|g" \
  "${TEMPLATE_NGINX}" > "${local_ng}"

if [[ "${DRY_RUN}" == false ]]; then
  r2_upload "${local_ng}" "/tmp/ng.${CUSTOMER_ID}.conf"
  rm -f "${local_ng}"
  r2 "sudo mv '/tmp/ng.${CUSTOMER_ID}.conf' '${NGINX_CONF_DIR}/${CUSTOMER_ID}.conf'" \
    || die "Nginx-Config verschieben fehlgeschlagen"
  r2 "sudo nginx -t" || die "Nginx-Config ungueltig"
  r2 "sudo nginx -s reload" || die "Nginx reload fehlgeschlagen"
  log_ok "Schritt 6 OK: ${FQDN} aktiv"
else
  rm -f "${local_ng}"
  log_info "[DRY-RUN] Nginx ${NGINX_CONF_DIR}/${CUSTOMER_ID}.conf"
fi

# =============================================================================
# Schritt 7: SSL via Certbot
# =============================================================================
log_info "── Schritt 7: SSL-Zertifikat ──"

if [[ "${SKIP_SSL}" == true ]]; then
  log_warn "SSL uebersprungen (--skip-ssl)"
elif [[ "${DRY_RUN}" == false ]]; then
  log_info "Warte 10s auf DNS..."
  sleep 10
  r2 "sudo certbot --nginx -d '${FQDN}' \
    --non-interactive --agree-tos \
    --email '${CERTBOT_MAIL}' --redirect" \
  || log_warn "Certbot fehlgeschlagen — manuell: ssh rocky2 'sudo certbot --nginx -d ${FQDN}'"
  log_ok "Schritt 7 OK"
else
  log_info "[DRY-RUN] certbot --nginx -d ${FQDN}"
fi

# =============================================================================
# Schritt 8: Smoke-Test
# =============================================================================
log_info "── Schritt 8: Smoke-Test ──"

PROTO="https"
[[ "${SKIP_SSL}" == true ]] && PROTO="http"
SMOKE_OK=true

if [[ "${DRY_RUN}" == false ]]; then
  for i in 1 2 3; do
    STATUS=$(curl -sf -o /dev/null -w "%{http_code}" --max-time 15 \
      "${PROTO}://${FQDN}/health" 2>/dev/null || echo "000")
    [[ "${STATUS}" == "200" ]] && break
    log_warn "Health-Check ${i}/3: HTTP ${STATUS} — warte 10s..."
    sleep 10
  done
  if [[ "${STATUS}" == "200" ]]; then
    log_ok "Smoke-Test bestanden (HTTP 200)"
  else
    log_warn "Smoke-Test fehlgeschlagen (HTTP ${STATUS})"
    SMOKE_OK=false
  fi
else
  log_info "[DRY-RUN] curl ${PROTO}://${FQDN}/health"
fi

# =============================================================================
# Zusammenfassung
# =============================================================================
log_info "============================================"
log_info "Deployment abgeschlossen"
log_info "============================================"
log_info "Kunde:      ${NAME}"
log_info "URL:        ${PROTO}://${FQDN}"
log_info "Bundle:     ${BUNDLE} (${BUDGET} USD Budget/Monat)"
log_info "Container:  openclaw_${CUSTOMER_ID}:${PORT}"
log_info "Smoke-Test: ${SMOKE_OK}"
log_info "Log:        ${LOG_FILE}"
log_info "============================================"

if [[ "${DRY_RUN}" == true ]]; then
  log_info "DRY-RUN abgeschlossen — keine Aenderungen"
elif [[ "${SMOKE_OK}" == true ]]; then
  log_ok "Instanz produktiv und erreichbar."
else
  log_warn "Deployment mit Warnungen — Logs pruefen"
  exit 1
fi
