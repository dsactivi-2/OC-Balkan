# OpenClaw Balkan — Deploy

## Status

Dieses Projekt ist lokal buildbar und lokal startbar.

Verifiziert:
- `npm run build`
- `npm run start`
- `GET /health`
- `POST /api/leads`
- SQLite-Write ueber API

## Laufzeit

- Node.js 22 empfohlen
- SQLite-Datei unter `data/openclaw-balkan.sqlite`
- Standard-Port `4173`
- `ADMIN_TOKEN` fuer geschuetzten Zugriff auf `GET /api/leads`
- optional `ALLOWED_ORIGINS` fuer Origin-Whitelist
- optional `LEAD_WEBHOOK_URL` fuer Weiterleitung an externes CRM / Mail / Automation

## Lokal starten

```bash
cd /Users/dsselmanovic/activi-dev-repos/openclaw-balkan
npm install
npm run build
npm run start
```

Dann:
- `http://127.0.0.1:4173/`
- `http://127.0.0.1:4173/ba.html`
- `http://127.0.0.1:4173/rs.html`
- `http://127.0.0.1:4173/health`

Smoke-Test:

```bash
ADMIN_TOKEN=change-me npm run smoke
```

## Docker Build

```bash
docker build -t openclaw-balkan .
docker run --rm -p 4173:4173 openclaw-balkan
```

## Reverse Proxy

Empfohlen:
- Nginx
- Caddy
- Traefik

Proxy auf:
- `http://127.0.0.1:4173`

## Persistent Storage

Die SQLite-Datei liegt unter:

- `data/openclaw-balkan.sqlite`

Fuer Hosting muss dieses Verzeichnis persistent sein.

Ohne persistentes Volume gehen neue Leads bei Re-Deploy verloren.

## Minimaler Produktions-Checklist

- `npm run build` erfolgreich
- `npm run start` erfolgreich
- `/health` gibt `ok: true`
- `data/` ist persistent gemountet
- Reverse Proxy mit HTTPS davor
- Backup fuer SQLite-Datei
- `ADMIN_TOKEN` gesetzt

## Noch offen

Nicht erledigt:
- externes CRM-/Mail-Routing

Bereits eingebaut:
- Token-Schutz fuer `GET /api/leads`
- einfaches Rate Limiting fuer `POST /api/leads`
- Honeypot-Feld im Formular
- optionales Webhook-Routing fuer neue Leads
- optionaler Origin-Check fuer `POST /api/leads`

Das Projekt ist damit hosting-faehig, aber noch nicht vollstaendig sicherheitsgehaertet fuer hohes oeffentliches Marketing-Traffic.
