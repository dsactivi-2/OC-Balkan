#!/usr/bin/env bash
# =============================================================================
# OpenClaw Balkan — Kosten-Tracking per Kunde
#
# Fragt LiteLLM API auf rocky2 ab und gibt Kosten pro Customer-ID aus.
# LiteLLM Master-Key MUSS als Umgebungsvariable LITELLM_MASTER_KEY gesetzt sein.
#
# Verwendung:
#   ./cost-tracker.sh                    # aktuellen Monat
#   ./cost-tracker.sh --month 2026-03    # bestimmten Monat
#   ./cost-tracker.sh --output report.csv
#   ./cost-tracker.sh --format json
#
# Voraussetzungen:
#   - SSH-Alias "rocky2" konfiguriert
#   - LITELLM_MASTER_KEY als Umgebungsvariable
#   - jq installiert (fuer JSON-Parsing)
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${SCRIPT_DIR}/logs"
ROCKY2_SSH="rocky2"
LITELLM_LOCAL="http://127.0.0.1:14000"

# =============================================================================
# Argument-Parsing
# =============================================================================

MONTH="$(date +%Y-%m)"
OUTPUT_FILE=""
FORMAT="csv"

usage() {
  cat <<'EOF'
Verwendung: cost-tracker.sh [OPTIONEN]

Optionen:
  --month YYYY-MM     Monat (Standard: aktueller Monat)
  --output DATEI      Ausgabe in CSV-Datei schreiben
  --format csv|json   Ausgabeformat (Standard: csv)
  -h, --help          Hilfe
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --month)  MONTH="$2";  shift 2 ;;
    --output) OUTPUT_FILE="$2"; shift 2 ;;
    --format) FORMAT="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unbekanntes Argument: $1" >&2; exit 1 ;;
  esac
done

# =============================================================================
# Validierung
# =============================================================================

command -v jq >/dev/null 2>&1 || { echo "jq nicht installiert" >&2; exit 1; }
command -v ssh >/dev/null 2>&1 || { echo "ssh nicht installiert" >&2; exit 1; }

# Master-Key laden
if [[ -z "${LITELLM_MASTER_KEY:-}" ]]; then
  env_file="${SCRIPT_DIR}/.env.deploy"
  if [[ -f "${env_file}" ]]; then
    val="$(grep -E '^LITELLM_MASTER_KEY=' "${env_file}" | cut -d'=' -f2- | tr -d '"'"'")"
    [[ -n "${val}" ]] && export LITELLM_MASTER_KEY="${val}"
  fi
fi
[[ -n "${LITELLM_MASTER_KEY:-}" ]] || {
  echo "LITELLM_MASTER_KEY nicht gesetzt" >&2
  exit 1
}

# Monat validieren
[[ "${MONTH}" =~ ^[0-9]{4}-[0-9]{2}$ ]] || {
  echo "Unguelltiges Monatsformat: ${MONTH} (erwartet: YYYY-MM)" >&2
  exit 1
}

mkdir -p "${LOG_DIR}"
RUNLOG="${LOG_DIR}/cost-tracker-${MONTH}.log"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "${RUNLOG}"; }

log "Starte Kosten-Abfrage fuer Monat: ${MONTH}"

# =============================================================================
# Daten von LiteLLM abrufen
# =============================================================================

# LiteLLM API wird direkt auf rocky2 aufgerufen (kein lokaler Tunnel noetig)
# /spend/tags gibt Kosten gruppiert nach Tags zurueck
log "Frage LiteLLM /spend/tags ab..."

RAW_RESPONSE=$(ssh "${ROCKY2_SSH}" \
  "curl -sf \
    -H 'Authorization: Bearer \${LITELLM_MASTER_KEY}' \
    '${LITELLM_LOCAL}/spend/tags?start_date=${MONTH}-01&end_date=${MONTH}-31'" \
  2>&1) || {
  log "FEHLER: LiteLLM-Abfrage fehlgeschlagen"
  exit 1
}

# Pruefen ob valides JSON
if ! echo "${RAW_RESPONSE}" | jq . >/dev/null 2>&1; then
  log "FEHLER: Keine valide JSON-Antwort: ${RAW_RESPONSE}"
  exit 1
fi

log "Antwort erhalten (${#RAW_RESPONSE} Bytes)"

# =============================================================================
# Ergaenzend: /spend/keys fuer detailliertere Daten
# =============================================================================

log "Frage LiteLLM /spend/keys ab..."

KEYS_RESPONSE=$(ssh "${ROCKY2_SSH}" \
  "curl -sf \
    -H 'Authorization: Bearer \${LITELLM_MASTER_KEY}' \
    '${LITELLM_LOCAL}/spend/keys?start_date=${MONTH}-01&end_date=${MONTH}-31'" \
  2>&1) || KEYS_RESPONSE="[]"

# =============================================================================
# Daten verarbeiten und ausgeben
# =============================================================================

# Aus /spend/tags: Summiere Kosten fuer Tags die mit einem Kunden-Pattern matchen
# LiteLLM-Tags Format: ["kunde001", "social-marketing-team", "openclaw-balkan"]
# Wir gruppieren nach dem ersten Tag (= customer_id)

PROCESSED=$(echo "${RAW_RESPONSE}" | jq -r '
  # Annahme: API gibt Array von {tag, spend, total_tokens}
  if type == "array" then .
  elif .data then .data
  else []
  end
  | map(select(.tag != null))
  # Nur openclaw-balkan Tags (customer IDs, nicht bundle-Namen)
  | map(select(
      .tag != "openclaw-balkan" and
      (.tag | test("^(social-marketing-team|office-bundle|research-bundle|learning-buddy|solo-agent)$") | not)
    ))
  | sort_by(.spend // 0) | reverse
  | .[]
  | [.tag, (.total_tokens // 0 | tostring), (.spend // 0 | tostring)]
  | join(",")
' 2>/dev/null || echo "")

# Ergaenzend aus /spend/keys (hoeherer Detailgrad)
KEYS_PROCESSED=$(echo "${KEYS_RESPONSE}" | jq -r '
  if type == "array" then .
  elif .data then .data
  else []
  end
  | map(select(.key_alias != null and .key_alias != ""))
  | map(select(.key_alias | test("^(social-marketing-team|office-bundle|research-bundle|learning-buddy|solo-agent)$") | not))
  | sort_by(.spend // 0) | reverse
  | .[]
  | [.key_alias, (.total_tokens // 0 | tostring), (.spend // 0 | tostring)]
  | join(",")
' 2>/dev/null || echo "")

# Datenquelle waehlen: keys bevorzugt (detaillierter), tags als Fallback
if [[ -n "${KEYS_PROCESSED}" ]]; then
  DATA="${KEYS_PROCESSED}"
  SOURCE="spend/keys"
else
  DATA="${PROCESSED}"
  SOURCE="spend/tags"
fi

log "Datenquelle: ${SOURCE}"

# =============================================================================
# Ausgabe formatieren
# =============================================================================

HEADER="customer_id,tokens_used,cost_usd,month"

output_csv() {
  echo "${HEADER}"
  if [[ -z "${DATA}" ]]; then
    echo "# Keine Daten fuer ${MONTH}"
    return
  fi
  while IFS=',' read -r cid tokens cost; do
    printf '%s,%s,%s,%s\n' "${cid}" "${tokens}" "${cost}" "${MONTH}"
  done <<< "${DATA}"
}

output_json() {
  if [[ -z "${DATA}" ]]; then
    echo "[]"
    return
  fi
  echo "["
  local first=true
  while IFS=',' read -r cid tokens cost; do
    [[ "${first}" == true ]] && first=false || echo ","
    printf '  {"customer_id":"%s","tokens_used":%s,"cost_usd":%s,"month":"%s"}' \
      "${cid}" "${tokens}" "${cost}" "${MONTH}"
  done <<< "${DATA}"
  echo ""
  echo "]"
}

# Ausgabe erstellen
case "${FORMAT}" in
  csv)  RESULT="$(output_csv)" ;;
  json) RESULT="$(output_json)" ;;
  *)    echo "Unbekanntes Format: ${FORMAT}" >&2; exit 1 ;;
esac

# In Datei oder stdout ausgeben
if [[ -n "${OUTPUT_FILE}" ]]; then
  echo "${RESULT}" > "${OUTPUT_FILE}"
  log "Gespeichert: ${OUTPUT_FILE}"
else
  echo "${RESULT}"
fi

# =============================================================================
# Zusammenfassung loggen
# =============================================================================

TOTAL_COST=$(echo "${DATA}" | awk -F',' '{sum += $3} END {printf "%.4f", sum}' || echo "0")
TOTAL_TOKENS=$(echo "${DATA}" | awk -F',' '{sum += $2} END {printf "%.0f", sum}' || echo "0")
CUSTOMER_COUNT=$(echo "${DATA}" | grep -c '.' || echo "0")

log "Zusammenfassung ${MONTH}:"
log "  Kunden:          ${CUSTOMER_COUNT}"
log "  Tokens gesamt:   ${TOTAL_TOKENS}"
log "  Kosten gesamt:   \$${TOTAL_COST} USD"
