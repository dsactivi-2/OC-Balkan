# OpenClaw Balkan — One-Click-Deploy

Automatisiertes Deployment-System fuer Kunden-Instanzen auf rocky2 (37.27.71.134).

## Dateien

| Datei | Beschreibung |
|-------|-------------|
| `deploy-customer.sh` | Haupt-Deploy-Script (8 Schritte) |
| `remote-generate-env.sh` | Laeuft auf rocky2 — generiert .env sicher remote |
| `docker-compose.customer.yml` | Docker-Compose Template pro Kunde |
| `nginx-customer.conf.template` | Nginx-Config Template pro Kunde |
| `onboarding-webhook.js` | Node.js Webhook-Server (Port 3099) |
| `cost-tracker.sh` | Monatliche Kosten-Auswertung via LiteLLM API |
| `.env.deploy` | **Nicht committen** — lokale Secrets (LITELLM_MASTER_KEY) |
| `logs/` | Deployment- und Webhook-Logs |

## Voraussetzungen

### Lokal (Mac)
- SSH-Alias `rocky2` in `~/.ssh/config`
- `curl`, `sed`, `openssl` installiert
- `jq` fuer cost-tracker.sh
- Node.js fuer onboarding-webhook.js

### rocky2 (37.27.71.134)
- Docker + docker-compose installiert
- Nginx installiert und aktiv
- Certbot installiert
- Verzeichnis `/opt/openclaw-balkan/kunden/` existiert
- Bundle-Configs unter `/opt/openclaw-balkan/bundles/` (YAML-Dateien)

### CCT (178.104.51.123)
- Qdrant erreichbar auf Port 16333 (via SSH-Tunnel oder direkt)

## Installation

### 1. Secrets konfigurieren

```bash
# Datei erstellen (niemals committen)
echo 'LITELLM_MASTER_KEY=sk-activi-...' > deploy/.env.deploy
chmod 600 deploy/.env.deploy
```

Alternativ als Umgebungsvariable:
```bash
export LITELLM_MASTER_KEY="sk-activi-..."
```

### 2. Scripts ausfuehrbar machen

```bash
chmod +x deploy/deploy-customer.sh
chmod +x deploy/remote-generate-env.sh
chmod +x deploy/cost-tracker.sh
```

### 3. rocky2 vorbereiten

```bash
ssh rocky2 'mkdir -p /opt/openclaw-balkan/kunden /opt/openclaw-balkan/bundles'

# Bundle-YAML-Dateien hochladen
scp bundles/*.yaml rocky2:/opt/openclaw-balkan/bundles/
```

### 4. Webhook-Server starten (auf rocky2 oder lokal)

```bash
# Auf rocky2 deployen
scp deploy/onboarding-webhook.js rocky2:/opt/openclaw-balkan/
ssh rocky2 'cd /opt/openclaw-balkan && \
  WEBHOOK_AUTH_TOKEN="<sicherer-token>" \
  node onboarding-webhook.js'

# Oder via PM2 (empfohlen)
ssh rocky2 'cd /opt/openclaw-balkan && \
  WEBHOOK_AUTH_TOKEN="<token>" \
  pm2 start onboarding-webhook.js --name openclaw-webhook'
```

## Verwendung

### Neuen Kunden deployen

```bash
./deploy/deploy-customer.sh \
  --customer-id "ba_friseur_sarajevo_001" \
  --bundle "social-marketing-team" \
  --email "amira@friseur.ba" \
  --name "Friseur Amira"
```

**Dry-Run (ohne tatsaechliche Aenderungen):**
```bash
./deploy/deploy-customer.sh \
  --customer-id "test001" \
  --bundle "solo-agent" \
  --email "test@example.com" \
  --name "Test" \
  --dry-run
```

### Kosten auswerten

```bash
# Aktueller Monat als CSV auf stdout
./deploy/cost-tracker.sh

# Bestimmter Monat in Datei
./deploy/cost-tracker.sh --month 2026-03 --output costs-march.csv

# JSON-Format
./deploy/cost-tracker.sh --format json
```

### Webhook-API aufrufen (n8n)

```bash
# Deployment starten
curl -X POST http://rocky2:3099/deploy \
  -H "Authorization: Bearer <WEBHOOK_AUTH_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "kunde001",
    "bundle": "social-marketing-team",
    "email": "inhaber@example.ba",
    "name": "Beispiel GmbH"
  }'

# Status abfragen
curl -X POST http://rocky2:3099/status \
  -H "Authorization: Bearer <WEBHOOK_AUTH_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "kunde001"}'

# Instanz entfernen
curl -X POST http://rocky2:3099/remove \
  -H "Authorization: Bearer <WEBHOOK_AUTH_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "kunde001", "confirm": "DELETE"}'
```

## Deploy-Schritte im Detail

| Schritt | Aktion | Ziel |
|---------|--------|------|
| 1 | Customer-ID → Subdomain | Lokal |
| 2 | Docker-Netzwerk + Volumes | rocky2 |
| 3 | .env generieren + Container starten | rocky2 (remote) |
| 4 | Qdrant Collections anlegen | CCT:16333 |
| 5 | LiteLLM Virtual Key + Budget | rocky2:14000 |
| 6 | Nginx-Config + reload | rocky2 |
| 7 | SSL via Certbot | rocky2 |
| 8 | Smoke-Test (HTTP 200) | extern |

**Geschaetzte Dauer:** 8-12 Minuten

## Sicherheitshinweise

- `LITELLM_MASTER_KEY` niemals in Scripts hardcoden — immer als env var
- `.env.deploy` nicht ins Git committen (in `.gitignore` eintragen)
- `WEBHOOK_AUTH_TOKEN` fuer Produktion immer setzen
- Webhook-Server nur auf `127.0.0.1` binden, nicht `0.0.0.0`
- Rocky2-Nginx-Config fuer Webhook: nur via Tailscale oder VPN erreichbar machen

## Troubleshooting

**SSH fehlgeschlagen:**
```bash
ssh -v rocky2  # Verbindung debuggen
cat ~/.ssh/config | grep -A5 rocky2
```

**Container startet nicht:**
```bash
ssh rocky2 "docker logs openclaw_<CUSTOMER_ID> --tail 50"
ssh rocky2 "cd /opt/openclaw-balkan/kunden/<CUSTOMER_ID> && docker compose ps"
```

**Nginx-Fehler:**
```bash
ssh rocky2 "sudo nginx -t"
ssh rocky2 "sudo tail -n 50 /var/log/nginx/<CUSTOMER_ID>-error.log"
```

**LiteLLM-Budget pruefen:**
```bash
ssh rocky2 "curl -s -H 'Authorization: Bearer \$LITELLM_MASTER_KEY' \
  'http://127.0.0.1:14000/key/info?key_alias=<CUSTOMER_ID>'"
```
