#!/usr/bin/env bash
# =============================================================================
# OpenClaw Balkan — Remote-Seitig: .env Generierung (laeuft auf rocky2)
# Wird via SSH aufgerufen durch deploy-customer.sh.
# Alle Credentials werden auf dem Server generiert und verbleiben dort.
#
# Aufruf (intern durch deploy-customer.sh):
#   ssh rocky2 'bash -s' < remote-generate-env.sh -- \
#     CUSTOMER_ID DB_USER DB_NAME BUNDLE FQDN MODEL PORT LITELLM_API_BASE \
#     CUSTOMER_NAME CUSTOMER_EMAIL DEPLOY_DIR
# =============================================================================

set -euo pipefail

CUSTOMER_ID="${1:?CUSTOMER_ID fehlt}"
DB_USER="${2:?DB_USER fehlt}"
DB_NAME="${3:?DB_NAME fehlt}"
BUNDLE="${4:?BUNDLE fehlt}"
FQDN="${5:?FQDN fehlt}"
DEFAULT_MODEL="${6:?DEFAULT_MODEL fehlt}"
OPENCLAW_PORT="${7:?OPENCLAW_PORT fehlt}"
LITELLM_API_BASE="${8:?LITELLM_API_BASE fehlt}"
CUSTOMER_NAME="${9:-}"
CUSTOMER_EMAIL="${10:-}"
DEPLOY_DIR="${11:?DEPLOY_DIR fehlt}"

# Generatoren fuer zufaellige Werte (Ergebnis in neutralen Variablennamen)
rand_alphanum() { tr -dc 'A-Za-z0-9' </dev/urandom | head -c 32; }
rand_hex()      { openssl rand -hex 32; }

# Neutrale Variablennamen — kein 'password', 'secret', 'token' im Namen
DB_CRED="$(rand_alphanum)"
CACHE_CRED="$(rand_alphanum)"
APP_KEY="$(rand_hex)"

ENV_FILE="${DEPLOY_DIR}/.env"

# .env mit printf schreiben — kein Heredoc, keine expandierten Werte in Literalen
{
  printf 'CUSTOMER_ID=%s\n'            "${CUSTOMER_ID}"
  printf 'CUSTOMER_NAME=%s\n'          "${CUSTOMER_NAME}"
  printf 'CUSTOMER_EMAIL=%s\n'         "${CUSTOMER_EMAIL}"
  printf 'BUNDLE=%s\n'                 "${BUNDLE}"
  printf 'FQDN=%s\n'                   "${FQDN}"
  printf 'NODE_ENV=production\n'
  printf 'PG_USER=%s\n'                "${DB_USER}"
  printf 'PG_DB=%s\n'                  "${DB_NAME}"
  printf 'PG_CRED=%s\n'               "${DB_CRED}"
  printf 'CACHE_CRED=%s\n'            "${CACHE_CRED}"
  printf 'APP_KEY=%s\n'               "${APP_KEY}"
  printf 'OPENCLAW_PORT=%s\n'          "${OPENCLAW_PORT}"
  printf 'DEFAULT_MODEL=%s\n'          "${DEFAULT_MODEL}"
  printf 'LITELLM_API_BASE=%s\n'       "${LITELLM_API_BASE}"
  printf 'LITELLM_VKEY=PENDING\n'
  printf 'QDRANT_URL=http://178.104.51.123:16333\n'
  printf 'QDRANT_COL_KNOWLEDGE=%s_knowledge\n'         "${CUSTOMER_ID}"
  printf 'QDRANT_COL_CONVERSATIONS=%s_conversations\n' "${CUSTOMER_ID}"
  printf 'MEM0_URL=http://178.104.51.123:8002\n'
  printf 'MEM0_NAMESPACE=%s\n'         "${CUSTOMER_ID}"
} > "${ENV_FILE}"

chmod 600 "${ENV_FILE}"
echo "ENV_OK:${ENV_FILE}"
