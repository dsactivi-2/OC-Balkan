# System-Architektur — OpenClaw Balkan

> Version: 1.0 | Stand: 2026-03-31 | Status: Architektur-Entwurf
> Basis: BLUEPRINT-V2.md + RESEARCH-V2.md

---

## 1. Ueberblick

### Systemkontext (C4 Level 1)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        EXTERNAL ACTORS                                  │
│                                                                         │
│   [Kunde BiH/SRB]   [Facebook Messenger]   [Viber Business]            │
│   [WhatsApp]        [E-Mail (SMTP)]        [Stripe / Bankueberweisung]  │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │ Webhooks / API
┌───────────────────────────────▼─────────────────────────────────────────┐
│                  OPENCLAW BALKAN PLATFORM                               │
│                                                                         │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐  │
│  │  Interne Agenten │    │  Kunden-Instanzen│    │  Infrastruktur   │  │
│  │  (Denis Betrieb) │    │  (OpenClaw)      │    │  (Shared)        │  │
│  └──────────────────┘    └──────────────────┘    └──────────────────┘  │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │ SSH / Tailscale
┌───────────────────────────────▼─────────────────────────────────────────┐
│                        SERVER-INFRASTRUKTUR                             │
│                                                                         │
│  [rocky2: 37.27.71.134]    [CCT: 178.104.51.123]    [Hetzner Kunde-VPS]│
│  LiteLLM / OpenClaw        Qdrant / Mem0 / Neo4j    OpenClaw Instanzen │
└─────────────────────────────────────────────────────────────────────────┘
```

### Container-Uebersicht (C4 Level 2)

```
┌─────────────────────────── rocky2 (37.27.71.134) ───────────────────────┐
│                                                                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐ │
│  │ OpenClaw        │  │ LiteLLM         │  │ n8n                     │ │
│  │ (Supervisor Ava)│  │ :14000/:4000    │  │ Workflow-Automatisierung │ │
│  │ Port: 18789     │  │ Ollama Fallback  │  │ Billing / Onboarding    │ │
│  └────────┬────────┘  └────────┬────────┘  └────────────┬────────────┘ │
│           │                   │                          │              │
│  ┌────────▼────────────────────▼──────────────────────── ▼────────────┐ │
│  │              Tailscale (mac-ds.tail47b17c.ts.net)                  │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────┘

┌─────────────────────── CCT (178.104.51.123) ────────────────────────────┐
│                                                                          │
│  ┌────────────┐  ┌────────────┐  ┌──────────┐  ┌────────────────────┐  │
│  │ Qdrant     │  │ Mem0       │  │ Neo4j    │  │ HippoRAG           │  │
│  │ Port:16333 │  │ Port:8002  │  │ :7474    │  │ Port:8001          │  │
│  │ Vektoren   │  │ 97 Mem.    │  │ :7687    │  │ Knowledge Graph    │  │
│  └────────────┘  └────────────┘  └──────────┘  └────────────────────┘  │
│                                                                          │
│  Shared Memory-Backbone fuer alle Agenten                               │
└──────────────────────────────────────────────────────────────────────────┘

┌─────────────────── Hetzner Kunden-VPS (pro ~10-15 Kunden) ──────────────┐
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Docker Compose Stack (pro Kunden-Gruppe)                        │   │
│  │                                                                   │   │
│  │  kunde_001/  kunde_002/  ... kunde_015/                          │   │
│  │  ├─ openclaw/  ├─ openclaw/      ├─ openclaw/                    │   │
│  │  ├─ postgres/  ├─ postgres/      ├─ postgres/                    │   │
│  │  └─ nginx/     └─ nginx/         └─ nginx/                       │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  Hetzner CX31: 8 vCPU / 8 GB RAM / 80 GB SSD — ca. 35 EUR/Monat       │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Deployment-Architektur

### 2.1 Kundeninstanz-Modell: Hybrid-Tenant

**Entscheidung: Shared-Host, Isolated-Container (nicht vollstaendig getrennte VPS pro Kunde)**

Begruendung: Ein separater VPS pro Kunde waere bei 15-20 EUR/Monat Einnahmen nicht kostendeckend (Hetzner CAX11 allein kostet bereits 7 EUR/Monat). Stattdessen: Docker-Isolierung auf geteiltem Host, aber vollstaendig getrennte Daten.

```
┌─────────────────────────────────────────────────────────────────┐
│  Hetzner VPS (Kunden-Host)                                       │
│                                                                  │
│  ┌──────────────────────┐    ┌──────────────────────┐           │
│  │  kunde_abc (Friseur) │    │  kunde_xyz (Makler)  │           │
│  │                      │    │                      │           │
│  │  OpenClaw Container  │    │  OpenClaw Container  │           │
│  │  Port: intern        │    │  Port: intern        │           │
│  │                      │    │                      │           │
│  │  PostgreSQL Volume   │    │  PostgreSQL Volume   │           │
│  │  /data/kunde_abc/    │    │  /data/kunde_xyz/    │           │
│  └──────────┬───────────┘    └──────────┬───────────┘           │
│             │                           │                        │
│  ┌──────────▼───────────────────────────▼──────────────────────┐ │
│  │  Nginx Reverse Proxy                                         │ │
│  │  abc.openclawbalkan.ba  →  kunde_abc:PORT                   │ │
│  │  xyz.openclawbalkan.ba  →  kunde_xyz:PORT                   │ │
│  └──────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

**Isolation-Garantien:**
- Jeder Kunde hat eigenes Docker-Network (kein Container-zu-Container-Zugriff)
- Eigenes PostgreSQL-Volume (kein geteiltes DB-Schema)
- Eigene OpenClaw-Konfiguration unter `/opt/openclaw-balkan/kunden/{kunde_id}/`
- Eigene Subdomain: `{kunde_slug}.openclawbalkan.ba`
- Eigene Webhook-Endpunkte fuer Viber/Messenger/WhatsApp

**Was NICHT isoliert ist (akzeptables Shared-Layer):**
- LiteLLM auf rocky2 (Modellzugriff geteilt, aber Requests isoliert durch API-Keys pro Kunde)
- Qdrant auf CCT (eigene Collections pro Kunde: `kundeid_knowledge`, `kundeid_conversations`)
- Nginx auf dem Host (Layer-7-Proxy, kein Datenzugriff)

### 2.2 One-Click-Deploy Wizard — Technischer Ablauf

```
TRIGGER: Onboarding Agent bestaetigt neue Kunde ist bereit

Schritt 1: Kunden-ID generieren
  → n8n Workflow: generate_customer_id()
  → Format: "ba_friseur_sarajevo_001" oder "rs_makler_beograd_007"
  → In PostgreSQL (rocky2, Verwaltungs-DB) anlegen

Schritt 2: DNS-Eintrag erstellen
  → Hetzner DNS API: CNAME {kunde_slug}.openclawbalkan.ba → kunden-vps-01.openclawbalkan.ba
  → TTL: 300 Sekunden

Schritt 3: Docker-Stack deployen
  → SSH auf Kunden-Host via rocky2 (Tailscale)
  → Template kopieren: /opt/templates/openclaw-standard/ → /opt/kunden/{kunde_id}/
  → docker compose up -d
  → Umgebungsvariablen aus Vault (sops-encrypted .env) einsetzen:
      CUSTOMER_ID, DB_PASSWORD, OPENAI_COMPATIBLE_KEY, VIBER_TOKEN, etc.

Schritt 4: Qdrant Collection anlegen
  → CCT API: PUT /collections/{kunde_id}_knowledge
  → CCT API: PUT /collections/{kunde_id}_conversations
  → Embedding-Modell: bge-m3 (bereits auf CCT verfuegbar)

Schritt 5: LiteLLM Virtual Key erstellen
  → rocky2 LiteLLM API: POST /key/generate
  → Tags: [kunde_id, bundle_type] (fuer Kosten-Tracking)
  → Budget-Limit setzen: je nach Bundle (z.B. 10 USD/Monat fuer Solo Agent)

Schritt 6: OpenClaw konfigurieren
  → Bundle-Template laden (z.B. social_marketing_team.yaml)
  → Skills aktivieren (Mapping in Abschnitt 4)
  → Sprache setzen: BKS (bosnisch/serbisch je nach Region)
  → Kanaele verbinden: Viber Webhook, Messenger Webhook

Schritt 7: SSL-Zertifikat
  → Certbot auf Kunden-Host: certbot --nginx -d {slug}.openclawbalkan.ba --non-interactive

Schritt 8: Smoke Test
  → HTTP GET https://{slug}.openclawbalkan.ba/health → 200 erwartet
  → Testmessage via Viber-Webhook senden → Antwort pruefen
  → Ergebnis an Onboarding Agent zurueckgeben

Schritt 9: Benachrichtigungen
  → Kunde: Willkommensnachricht via Viber (Onboarding Agent)
  → Denis: Telegram/Viber Alert "Neue Instanz live: {kunde_id}"
  → Monitoring: Uptimerobot / Grafana-Alert registrieren

GESAMT-DAUER: ca. 8-12 Minuten (vollautomatisch)
```

**Implementierung des Wizards:** n8n-Workflow auf rocky2, getriggert vom Onboarding Agent via HTTP POST.

### 2.3 Server-Zuweisung

| Server | Rolle | Zugriff |
|--------|-------|---------|
| rocky2 (37.27.71.134) | OpenClaw Supervisor (Ava), LiteLLM Gateway, n8n, Interne Agenten, Verwaltungs-DB | SSH rocky2, Tailscale |
| CCT (178.104.51.123) | Shared Memory-Backbone: Qdrant, Mem0, Neo4j, HippoRAG | SSH + cct-tunnels alias |
| Hetzner Kunden-VPS | Kunden-OpenClaw-Instanzen (10-15 pro Host) | SSH via rocky2 Bastion |
| mac-ds (lokal) | Entwicklung, Testing, OpenClaw lokal | Tailscale |

---

## 3. Interne Agent-Infrastruktur

### 3.1 Architektur der internen Agenten

Alle internen Agenten laufen unter dem OpenClaw-Supervisor "Ava" auf rocky2 (Port 18789).

```
┌─────────────────────────────────────────────────────────────────────┐
│  OpenClaw Supervisor "Ava" — rocky2                                  │
│                                                                      │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────────┐  │
│  │ Sales      │  │ Onboarding │  │ CS Agent   │  │ Billing      │  │
│  │ Agent      │  │ Agent      │  │            │  │ Agent        │  │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └──────┬───────┘  │
│        │               │               │                 │          │
│  ┌─────┴──────┐  ┌─────┴──────┐  ┌─────┴──────┐  ┌──────┴───────┐  │
│  │ Marketing  │  │ Technical  │  │ Reporting  │  │ Escalation   │  │
│  │ Agent      │  │ Agent      │  │ Agent      │  │ Router       │  │
│  └────────────┘  └────────────┘  └────────────┘  └──────────────┘  │
│                                                                      │
│  Shared Memory: CCT Qdrant (interne_ops Collection) + Neo4j          │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 Sales Agent

**Kanal:** Viber Business (Primär), WhatsApp Business (Sekundär), Facebook Messenger (Tertiaer)
**Modell:** LiteLLM → claude-sonnet-4-6 (Cloud) fuer Qualifikation; qwen3.5-uncensored (lokal, rocky2) fuer einfache FAQ-Antworten
**Memory-Typ:** Mem0 (kurzfristig, per Lead); Qdrant Collection `internal_leads` (strukturiert)

**Tools:**
- `viber_send_message` — Antworten via Viber Business API (Sinch oder Infobip als BSP)
- `create_lead_record` — n8n Webhook → Eintrag in Verwaltungs-DB (PostgreSQL rocky2)
- `send_demo_link` — Generiert personalisierten Demo-Link fuer Live-Demo-Instanz
- `create_offer_draft` — Erstellt Angebots-PDF basierend auf Bundle + Marktpreisen aus BLUEPRINT-V2
- `schedule_followup` — n8n scheduled trigger fuer Follow-up nach 2 Tagen ohne Antwort

**Ablauf:**
```
Eingehende Nachricht (Viber/Messenger)
  → Ava routet zu Sales Agent
  → Qualifizierung: Branche? Groesse? Hauptproblem? Kanal?
  → Passendes Bundle bestimmen (Mapping in Abschnitt 4)
  → Demo-Link senden oder Live-Demo anbieten
  → Bei Interesse: create_lead_record + Onboarding Agent informieren
  → Kein Interesse: Follow-up in 14 Tagen (n8n)
```

### 3.3 Onboarding Agent

**Kanal:** Viber (Primär), E-Mail (Sekundaer)
**Modell:** LiteLLM → claude-sonnet-4-6
**Memory-Typ:** Strukturiertes Formular in PostgreSQL (nicht Vektoren — klare Felder noetig)

**Sammelt folgende Daten:**
```yaml
onboarding_form:
  business_name: string
  contact_name: string
  contact_viber: string
  contact_email: string
  city: string  # Sarajevo / Banja Luka / Beograd / etc.
  country: "BA" | "RS"
  language_variant: "bosnisch" | "srpski" | "hrvatski"
  bundle: "social_marketing" | "office" | "research" | "learning" | "solo"
  channels:
    - viber: boolean
    - messenger: boolean
    - whatsapp: boolean
    - email: boolean
    - webchat: boolean
  viber_business_account_exists: boolean
  facebook_page_url: string | null
  business_hours: string
  top_faq_questions: list[string]  # Kunde gibt 5-10 haeufigste Fragen an
  billing_method: "bank_transfer" | "stripe" | "corvuspay"
  billing_email: string
  annual_payment: boolean
```

**Nach vollstaendigem Formular:**
- Trigger: One-Click-Deploy Wizard (n8n Webhook)
- DPA-Dokument per E-Mail senden (generiert aus Template, pre-filled mit Kundendaten)
- Erstrechnung via Billing Agent erstellen

### 3.4 Customer Success (CS) Agent

**Kanal:** Viber (Primär), Messenger, E-Mail
**Modell:** qwen3.5-uncensored (lokal, Kostenvorteil) fuer Standard-Anfragen; claude-sonnet-4-6 fuer komplexe Faelle
**Memory-Typ:** Qdrant Collection `cs_tickets` + Verlaufs-Memory in Mem0 pro Kunde

**Tools:**
- `get_customer_status` — prueft Instanzstatus, letzte Aktivitaet, Ticket-Historie
- `get_monthly_report` — generiert Report aus Qdrant-Konversationsdaten (Abfragen, Antwortrate, Eskalationsrate)
- `escalate_to_denis` — Sendet Viber-Nachricht an Denis mit Kontext
- `update_agent_config` — einfache Konfigurationsaenderungen (FAQ hinzufuegen, Oeffnungszeiten)
- `send_renewal_reminder` — 30 Tage vor Ablauf automatisch

**Eskalations-Trigger:**
- Technisches Problem das Agent selbst nicht loesen kann
- Kundenwunsch nach Konfigurationsaenderung die Template-Aenderung erfordert
- Zahlungsproblem
- Beschwerde

### 3.5 Billing Agent

**Kanal:** E-Mail (Primär — fuer Rechnungen), Viber (Zahlungserinnerungen)
**Modell:** qwen3.5-uncensored (lokal — reine Textgenerierung, kein Reasoning noetig)
**Memory-Typ:** PostgreSQL (Billing-DB) — keine Vektoren, strukturierte Finanzdaten

**Stripe-Integration:**
- Step2Job GmbH (Denis existierende Stripe-Anbindung) als Merchant
- Kunden aus BiH/SRB zahlen via Stripe (wenn Karte vorhanden) oder Bankueberweisung
- Stripe Webhook (payment_intent.succeeded) → Billing Agent → Instanz als bezahlt markieren

**Ablauf:**
```
Monatsanfang (1. des Monats, 09:00):
  n8n Schedule → Billing Agent
  → fuer jeden Kunden: Rechnung generieren (Noman Finance MCP oder lokal)
  → Zahlungsmethode pruefen (Stripe → automatisch; Ueberweisung → manuell)
  → Rechnung per E-Mail senden (SMTP)
  → Viber-Benachrichtigung: "Deine monatliche Rechnung ist bereit"

Tag 10 (wenn nicht bezahlt):
  → Erinnerung 1 via Viber

Tag 20 (wenn nicht bezahlt):
  → Erinnerung 2 via E-Mail + Viber
  → Denis alert

Tag 30 (wenn nicht bezahlt):
  → Instanz pausieren (nginx returns 402)
  → Denis Eskalation
```

**Token-Kosten-Tracking (pro Kunde):**
- LiteLLM Virtual Keys pro Kunde (Budget-Tags)
- Monatliche Abfrage: `GET /key/info?key={kunde_virtual_key}` → spend_in_period
- Kosten automatisch in Kundenrechnung einkalkulieren wenn ueber Schwellenwert

### 3.6 Marketing Agent

**Aktivierung:** Phase 2 (Monat 4+), Phase 1 manuell kuratiert von Denis
**Kanal:** Facebook Page API, Buffer API, Meta Ads API via Make
**Modell:** claude-sonnet-4-6 (Texterstellung braucht Qualitaet)
**Memory-Typ:** Qdrant Collection `marketing_content` (fuer Content-Recycling)

**Tools (Phase 2):**
- `generate_post_ideas` — basierend auf Pilot-Cases und aktuellen Kundenerfolgen
- `schedule_buffer_post` — Buffer API POST /updates/create
- `create_meta_ad_draft` — Make Webhook → Meta Ads API (Denis genehmigt vor Aktivierung)
- `get_ad_performance` — Meta Ads Insights API → automatischer Report

### 3.7 Technical Agent

**Kanal:** Intern (kein Kundenkontakt) — Alerts via Telegram oder Viber an Denis
**Modell:** qwen3.5-uncensored (lokal — Monitoring braucht kein GPT-4)
**Trigger:** Cron (alle 5 Minuten), Uptimerobot Webhook bei Downtime

**Monitoring-Zyklus:**
```
Alle 5 Minuten (n8n Schedule):
  → HTTP Check: alle {slug}.openclawbalkan.ba/health
  → LiteLLM Health: rocky2:14000/health
  → Qdrant Health: CCT:16333/healthz (via cct-tunnel)
  → Mem0 Health: CCT:8002/health

Bei Fehler:
  → Schritt 1: Auto-Restart (docker restart {container})
  → Schritt 2 (nach 3 Minuten): erneuter Check
  → Schritt 3 (immer noch Fehler): Alert an Denis (Viber)
  → Schritt 4 (kritisch): Instanz als "maintenance" markieren, Kunde benachrichtigen
```

---

## 4. Bundle-Technologie

### Allgemeine technische Basis (alle Bundles)

| Komponente | Technologie | Instanz |
|-----------|-------------|---------|
| Agent-Runtime | OpenClaw (selbst-gehostet) | Kunden-Host (Docker) |
| LLM-Gateway | LiteLLM (rocky2) | Shared, Virtual Key pro Kunde |
| Vektorspeicher | Qdrant (CCT :16333) | Collection pro Kunde |
| Kurzzeit-Memory | Mem0 (CCT :8002) | User-Namespace pro Kunde |
| Datenbank | PostgreSQL (Docker, Kunden-Host) | Pro Kunde isoliert |
| Reverse Proxy | Nginx | Shared auf Kunden-Host |
| Viber-Gateway | Sinch oder Infobip BSP | Shared Account Denis |
| Messenger-Gateway | Facebook Graph API | Pro Kunde eigene Page-Token |

### Bundle 1 — Social Marketing Team

**Zielgruppe:** Friseur, Restaurant, Boutique, Cafe, Kosmetikstudio

**OpenClaw-Skills:**
- `faq-agent` — statische Wissensbasis (Oeffnungszeiten, Preise, Lage)
- `appointment-intake` — Terminanfragen erfassen + weiterleiten (kein automatisches Buchen in Phase 1)
- `comment-responder` — Facebook Page Kommentare automatisch beantworten
- `monthly-report` — Konversationsstatistiken aggregieren

**Kanale:**
- Viber Business (Pflicht, via Sinch/Infobip BSP)
- Facebook Messenger (Pflicht, via Graph API Webhook)
- WhatsApp Business (Optional Phase 2, via BSP)

**Modell:** LiteLLM → qwen3.5-uncensored (lokal) fuer FAQ und Standard; claude-sonnet-4-6 fuer komplexe Anfragen
- Kosten-Logik: 95% der Anfragen lokal (0 EUR Tokens), 5% cloud (~1-2 EUR/Monat)

**Memory-Typ:**
- Qdrant: Vektoren der FAQ-Datenbank (Produktkatalog, Preisliste, FAQs)
- Kein persistentes Konversations-Memory (jede Anfrage = frische Konversation, kein Login)

**Integrationen:**
- Google Calendar (Schreib-Zugriff fuer Terminerfassung, optional)
- Facebook Graph API (Page Messaging + Comments)
- Viber Business API (Chat)

**Konfiguration pro Instanz:**
```yaml
bundle: social_marketing_team
knowledge_base:
  - type: faq
    source: onboarding_form.top_faq_questions
  - type: document
    source: uploaded_pdfs  # Speisekarte, Preisliste
language: bosnisch | srpski  # aus onboarding_form
escalation:
  trigger: "Frage nicht beantwortbar"
  target: viber:{contact_viber}
channels:
  viber: true
  messenger: true
  whatsapp: false  # Phase 2
```

---

### Bundle 2 — Office Bundle

**Zielgruppe:** Anwalt, Arzt, Makler, Architekt, Steuerberater

**OpenClaw-Skills:**
- `lead-intake` — Anliegen + Kontaktdaten strukturiert erfassen
- `appointment-qualifier` — Erstberatung / Termin qualifizieren (Anliegen, Prioritaet, Budgetrahmen)
- `email-categorizer` — eingehende E-Mails kategorisieren und Standardantworten generieren
- `faq-agent` — Leistungsangebot, Preisrahmen, Ablauf erklaeren
- `weekly-report` — Lead-Eingang, Terminrate, offene Anfragen

**Kanale:**
- E-Mail (SMTP/IMAP, Pflicht)
- Viber Business (Pflicht)
- WhatsApp Business (Optional)
- Web-Widget (Optional, via OpenClaw native Widget)

**Modell:** claude-sonnet-4-6 fuer Qualifizierungsgespraeche (hoehere Praezision noetig)
- Erwartete Kosten: 3-6 EUR/Monat (mehr komplexe Anfragen als Bundle 1)

**Memory-Typ:**
- Qdrant: Leistungsbeschreibung, Preis-FAQ, Ablauf-Dokumentation
- Mem0: persistentes Lead-Memory (Kontext bleibt zwischen Konversationen erhalten — Anwalt muss nicht zweimal erklaeren)
- Neo4j (CCT): Relationen zwischen Leads, Terminen, Status (optionell ab Phase 2)

**Integrationen:**
- Google Calendar (Termin-Slots abrufen + blockieren)
- IMAP (E-Mail lesen) + SMTP (E-Mail senden), via n8n
- Optional: Calendly API als einfacherer Kalender-Ersatz

**Wichtig:** Kein direktes Kalender-Buchen ohne Inhaber-Bestaetigung in Phase 1. Agent stellt Anfrage ein, Inhaber bestaetigt manuell per Klick.

---

### Bundle 3 — Research Bundle

**Zielgruppe:** Studenten, NGOs, Forscher, wissenschaftliche Mitarbeiter

**OpenClaw-Skills:**
- `document-search` — durchsuchbare Wissensbasis aus eigenen Dokumenten (PDFs, Markdown)
- `summarizer` — lange Texte strukturiert aufbereiten (Gliederung, Kernpunkte, Zitate)
- `research-assistant` — Themenrecherche, Quellenvorschlaege, Outline erstellen
- `export-formatter` — Output als Markdown, Plain Text, strukturierte Outline

**Kanale:**
- Web-Widget (Primär — kein Viber/Messenger noetig, akademische Nutzung)
- Optional: Telegram (alternative zu Viber fuer juengere Zielgruppe)

**Modell:** claude-sonnet-4-6 (Reasoning-Qualitaet kritisch fuer Research)
- Kosten: 5-10 EUR/Monat (hohe Eingabe-Token durch lange Dokumente)

**Memory-Typ:**
- Qdrant: Hochgeladene Dokumente als Vektoren (bge-m3 auf CCT)
- Mem0: Nutzer-spezifisches Research-Profil (Themengebiete, bevorzugte Quellen)
- Kein Neo4j (kein Beziehungsgraph noetig)

**Integrationen:**
- PDF-Upload direkt im Web-Widget
- Markdown-Export
- Zotero-Import (Phase 2 — BibTeX-Parsing)

**Besonderheit:** Dieser Bundle braucht keinen Viber-Account und kein Facebook. Deployment einfacher. Gut fuer digitale Direktakquise (Uni-Gruppen, LinkedIn).

---

### Bundle 4 — Learning Buddy

**Zielgruppe:** Schulkinder (8-16), Eltern, Nachhilfe-Einrichtungen

**OpenClaw-Skills:**
- `tutor-agent` — erklaert Themen kindgerecht auf BKS (Mathe, Natur, Geschichte, Sprachen)
- `homework-coach` — fuehrt durch Aufgaben Schritt fuer Schritt (Sokrates-Methode: nicht Loesung geben, sondern fuehren)
- `parent-info` — Eltern-gerichtete Zusammenfassung (Lernstand, Tipps, Problembereiche)
- `subject-selector` — Fach + Schuljahr beim Start konfigurieren

**Kanale:**
- Viber (Primär — Eltern-Gruppen in Viber stark, 35+ Zielgruppe)
- Web-Widget (Sekundaer)

**Modell:** claude-sonnet-4-6 (Paedagogische Qualitaet und Erklaerungstiefe kritisch)
- Safety-Prompting: kein Loesungen direkt nennen, keine Off-Topic-Inhalte fuer Kinder
- Kosten: 4-8 EUR/Monat (moderate Konversationstiefe)

**Memory-Typ:**
- Mem0: Lernprofil pro Schueler (Schuljahr, Faecher, bekannte Problembereiche)
- Qdrant: Schulfach-Wissensbasis (Lehrplan BiH/Serbien, haeufige Pruefungsthemen)

**Integrationen:**
- Keine externen CRM-Integrationen
- Eltern erhalten wochentliche Summary per Viber (automatisch generiert)

**Skalierungsmuster:** Viber-Elterngruppen-Empfehlung (Mundpropaganda). Pro Familie 1 Account. Kein geteilter Account.

---

### Bundle 5 — Solo Agent

**Zielgruppe:** Freelancer, Einzelunternehmer, Einzelpersonen

**OpenClaw-Skills:** 1 aus folgendem Katalog (Kunde waehlt beim Onboarding):
- `faq-agent`
- `lead-intake`
- `appointment-intake`
- `document-search`

**Kanale:** 2 nach Wahl (aus Viber, Messenger, Web-Widget, E-Mail)

**Modell:** qwen3.5-uncensored (lokal, Kostenminimierung)
- Nur bei Komplexitaet Fallback auf LiteLLM → Cloud

**Memory-Typ:**
- Qdrant: Basis-Wissensbasis (minimal, 50-100 Dokumente)
- Kein persistentes Memory (zu kleines Volumen fuer sinnvolle Insights)

**Upgrade-Logik:**
- Nach 60 Tagen aktiver Nutzung: automatischer Vorschlag via CS Agent ("Du hast 120 Anfragen beantwortet. Willst du einen zweiten Agent hinzufuegen?")
- Upgrade: Bundle wechseln = neues Docker-Template deployen, Daten migrieren

---

## 5. Datenschutz-Architektur

### 5.1 Datenlokalisierung

```
┌─────────────────────────────────────────────────────────────────────┐
│  DATENSPEICHERUNG — UEBERSICHT                                       │
│                                                                      │
│  Kunden-Konversationsdaten:                                          │
│    → PostgreSQL (Docker Volume auf Hetzner-VPS)                     │
│    → Hetzner Datacenter: Helsinki (FI) oder Nuernberg (DE)          │
│    → Europaeischer Server = DSGVO-konform                            │
│                                                                      │
│  Vektor-Embeddings (Wissensbasis):                                   │
│    → Qdrant auf CCT Server (178.104.51.123)                          │
│    → CCT Server: Standort pruefen + dokumentieren                    │
│    → Hetzner Standort (empfohlen) oder anderer EU-Anbieter           │
│                                                                      │
│  Memory / Konversationsgedaechtnis:                                  │
│    → Mem0 auf CCT — selber Standort wie Qdrant                       │
│                                                                      │
│  Interne Agenten-Logs:                                               │
│    → PostgreSQL auf rocky2 (37.27.71.134 — Standort klaeren)        │
│    → rocky2 ist Hetzner Helsinki — EU-Standort                       │
│                                                                      │
│  LLM-Verarbeitung:                                                   │
│    → Lokal (qwen3.5 auf rocky2): keine Daten verlassen EU            │
│    → Cloud (claude-sonnet-4-6 via Anthropic): Daten verlassen EU!   │
│       → AV-Vertrag mit Anthropic noetig (existiert bereits fuer US)  │
│       → Kunden muessen in Datenschutzerklaerung informiert werden    │
└─────────────────────────────────────────────────────────────────────┘
```

### 5.2 DSGVO BiH — Datenschutzgesetz (Oktober 2025)

**Zustaendige Behoerde:** Agencija za zaštitu licnih podataka BiH

**Pflichten fuer Denis als Auftragsverarbeiter:**

1. **Auftragsverarbeitungsvertrag (AVV / DPA)** — vor erstem Live-Betrieb
   - Denis = Auftragsverarbeiter (verarbeitet Daten IM AUFTRAG des Kunden)
   - Kunde = Verantwortlicher (bestimmt Zweck + Mittel)
   - Vorlage: BiH-spezifische AVV-Vorlage von lokalem Rechtsanwalt erstellen lassen (500-800 EUR einmalig)

2. **Datenschutzerklaerung** pro Kunden-Endpunkt (Webhook-URL)
   - Welche Daten werden gespeichert?
   - Wie lange? (Empfehlung: 12 Monate, dann automatische Loeschung)
   - Welche Subauftragsverarbeiter? (Anthropic fuer Cloud-LLM, Hetzner fuer Hosting, Sinch/Infobip fuer Viber)
   - Betroffenenrechte (Auskunft, Loeschung, Portabilitaet)

3. **Datenkategorien-Beschraenkung** (Phase 1):
   - Erlaubt: Name, Kontaktdaten, Anfrageinhalte (Businesskontext)
   - Verboten: Gesundheitsdaten, Finanzprofile, HR-Screening, biometrische Daten
   - Verboten: Kinder unter 14 Jahren ohne elterliche Einwilligung (Ausnahme: Learning Buddy mit expliziter Eltern-Einwilligung)

4. **Einwilligung fuer Marketing** (Viber-Broadcasts, Newsletter):
   - Double-Opt-In Prozess via n8n implementieren
   - Opt-in in Qdrant `consent_store` Collection speichern (mit Timestamp + IP)

### 5.3 Serbien PDPA (Zakon o zaštiti podataka o licnosti)

**Hauptunterschiede zu BiH:**
- SCCs (Standardvertragsklauseln) fuer Datentransfers zu Anthropic (US) explizit noetig
- B2B-Vertraege muessen AVV-Klauseln enthalten (nicht optional)
- Aufsicht: Poverenik fuer Datenschutz (aktiver als BiH-Behoerde)

**Praktische Massnahme:** Separater AVV-Anhang fuer serbische Kunden (500-600 EUR einmalig, lokaler Rechtsanwalt Belgrad).

### 5.4 DPA-Onboarding-Prozess

```
Onboarding Agent schickt DPA-Link (PDF, pre-filled)
  → Kunde liest und akzeptiert (E-Mail mit Bestaetigung = ausreichend fuer Phase 1)
  → Bestaetigung in PostgreSQL gespeichert (timestamp, IP, Dokument-Hash)
  → Erst danach: One-Click-Deploy Wizard ausfuehren

Phase 2: DocuSign oder HelloSign fuer rechtssichere digitale Unterschrift
```

### 5.5 Subauftragsverarbeiter-Liste (Pflicht in AVV)

| Subauftragsverarbeiter | Leistung | Standort | Rechtsgrundlage |
|------------------------|----------|----------|-----------------|
| Hetzner Online GmbH | Server-Hosting | Deutschland/Finnland (EU) | DSGVO Art. 28 |
| Anthropic PBC | LLM-Verarbeitung (Cloud) | USA | SCCs |
| Sinch AB oder Infobip | Viber Business Messaging | EU/International | SCCs |
| Meta Platforms | Facebook Messenger | USA | SCCs |

---

## 6. Monitoring & Observability

### 6.1 Stack

```
Uptimerobot (externer Check) → HTTP GET /health alle 5 Min
  → Bei Downtime: Webhook an n8n → Technical Agent → Denis Viber

Prometheus + Grafana (intern, rocky2 Docker)
  → Metriken: CPU, RAM, Request-Rate, Token-Spend, Fehlerrate
  → Dashboard: ein Panel pro Kunden-Instanz
  → Alert-Rules: response_time > 5s, error_rate > 10%, spend > budget_threshold

n8n Health-Check Workflow (alle 5 Min)
  → Prueft alle /health Endpunkte
  → Schreibt Status in PostgreSQL (health_log Tabelle)
  → Technical Agent liest health_log und handelt
```

### 6.2 Health-Check Endpunkte

Jede Kunden-Instanz exponiert:
- `GET /health` — HTTP 200 wenn Container laeuft
- `GET /health/deep` — prueft DB-Verbindung, LiteLLM-Erreichbarkeit, Qdrant-Verbindung

### 6.3 Kosten-Tracking pro Kunde

**LiteLLM Virtual Keys (Basis-Mechanismus):**
```
Jeder Kunde bekommt eigenen Virtual Key bei Deploy:
  POST rocky2:14000/key/generate
  Body: {
    "metadata": {"customer_id": "ba_friseur_001", "bundle": "social_marketing"},
    "budget_duration": "monthly",
    "max_budget": 10.0,  // USD, je nach Bundle
    "tags": ["ba_friseur_001"]
  }

Monatlicher Report (1. des Monats via n8n):
  GET /spend/tags?tags=ba_friseur_001&start_date=...&end_date=...
  → spend_usd in Rechnung einkalkulieren wenn > 5 USD
```

**Schwellenwerte nach Bundle:**
| Bundle | Lokales Modell (Rocky2 Ollama) | Cloud Budget (USD/Monat) |
|--------|-------------------------------|--------------------------|
| Social Marketing Team | qwen3.5 (0 USD) Standard | Max 5 USD (fuer Komplexitaet) |
| Office Bundle | 50/50 lokal/cloud | Max 10 USD |
| Research Bundle | claude-sonnet Primär | Max 15 USD |
| Learning Buddy | claude-sonnet Primär | Max 10 USD |
| Solo Agent | qwen3.5 Primär | Max 3 USD |

### 6.4 Alert-Konfiguration

```yaml
alerts:
  instance_down:
    check: HTTP /health
    interval: 5min
    threshold: 2 failures
    action: auto_restart → viber_alert_denis

  high_token_spend:
    check: LiteLLM /spend/tags
    interval: daily
    threshold: 80% of max_budget
    action: viber_alert_denis + cs_agent_notify_customer

  disk_space:
    check: host df -h /opt/kunden
    interval: hourly
    threshold: 85% full
    action: viber_alert_denis

  qdrant_collection_size:
    check: CCT Qdrant /collections/{id}
    interval: weekly
    threshold: 500k vectors
    action: cleanup_old_conversations
```

---

## 7. Skalierung

### 7.1 Kapazitaet pro Server

**Kunden-Host (Hetzner CX31: 8 vCPU / 8 GB RAM / 80 GB SSD, ca. 35 EUR/Monat):**

Pro OpenClaw-Instanz im Idle: ~150-200 MB RAM, ~0.1 vCPU
Pro OpenClaw-Instanz bei Last (5 gleichzeitige Konversationen): ~400 MB RAM, ~0.5 vCPU

Konservative Rechnung (Peak-Last berücksichtigt):
- 8 GB RAM → max. 15-18 Instanzen
- 8 vCPU → max. 12-15 Instanzen bei gleichzeitiger Last
- **Praktisch: 10-12 Kunden pro CX31**

Empfehlung: Max. 10 Kunden pro Host fuer Sicherheitspuffer.

**rocky2 (LiteLLM, n8n, Interne Agenten):**
- Aktuelle Kapazitaet: ausreichend fuer 50-80 Kunden (LiteLLM routet effizient)
- Bottleneck: Ollama auf rocky2 fuer lokale Modelle — bei hohem Volumen Upgrade auf CPU-heavy Server

**CCT (Qdrant, Mem0, Neo4j):**
- Qdrant: 97 Memories aktuell, Kapazitaet fuer Tausende Collections
- Bottleneck bei 100+ Kunden: RAM (aktuell 16 GB auf CCT pruefen)

### 7.2 Skalierungsplan

```
Kunden 1-10:
  → 1x Kunden-Host (Hetzner CX31, 35 EUR/Monat)
  → rocky2 (existing)
  → CCT (existing)
  → Gesamtinfrastruktur: ca. 95 EUR/Monat (CX31 + CCT + rocky2)

Kunden 11-20:
  → 2x Kunden-Host (2x CX31 = 70 EUR/Monat)
  → rocky2 + CCT unveraendert
  → Gesamtinfrastruktur: ca. 130 EUR/Monat

Kunden 21-40:
  → 3-4x Kunden-Host (105-140 EUR/Monat)
  → Rocky2 Upgrade pruefen: CX31 → CX41 (60 EUR, 16 vCPU)
  → CCT RAM-Check: ggf. Qdrant RAM erhoehen
  → Gesamtinfrastruktur: ca. 200-240 EUR/Monat

Kunden 40-80:
  → 4-8x Kunden-Host
  → Dedicated LiteLLM-Server (separater Hetzner) falls rocky2 Bottleneck
  → Load Balancer fuer Kunden-Hosts (Hetzner Load Balancer, 8 EUR/Monat)
  → Gesamtinfrastruktur: ca. 400-600 EUR/Monat
```

### 7.3 Wirtschaftlichkeit Skalierung

```
Szenario: 30 Kunden, Ø 35 EUR/Monat Netto pro Kunde

  MRR:                           1.050 EUR
  Infrastruktur (3 Hosts + CCT):  ~185 EUR
  LLM-API-Kosten:                 ~100 EUR (ca. 3-4 EUR/Kunde)
  Tools (Make, Buffer, etc.):      ~50 EUR
  -------------------------------------------
  Netto-Marge:                    ~715 EUR (68%)

Szenario: 80 Kunden, Ø 38 EUR/Monat Netto

  MRR:                           3.040 EUR
  Infrastruktur (8 Hosts + CCT):  ~450 EUR
  LLM-API-Kosten:                 ~250 EUR
  Tools:                           ~80 EUR
  -------------------------------------------
  Netto-Marge:                  ~2.260 EUR (74%)
```

**Break-Even neuer Server (Hetzner CX31, 35 EUR/Monat):**
- Ein neuer Server wird benoetigt wenn bestehender Host >10 Kunden erreicht
- Kosten decken sich durch 1 neuen Kunden (35 EUR > 35 EUR Server)
- Faktisch: Server lohnt sich ab dem 2. Kunden auf diesem Host

### 7.4 Trigger fuer naechsten Server

```
n8n Alert (Technical Agent):
  IF count(active_instances_on_host) >= 9
    → Alert: "Host voll — neuen Hetzner CX31 bereitstellen"
    → Terraform-Script (optional Phase 3) oder manuell Denis
    → Neue Deploy-Ziel-IP in n8n Konfiguration eintragen
```

---

## 8. Offene Technische Fragen

### 8.1 Kritisch (vor erstem Kunden klaeren)

**F1: CCT-Server Standort**
- Qdrant und Mem0 laufen auf CCT (178.104.51.123) — welcher Hosting-Anbieter, welcher Standort?
- Wenn ausserhalb EU: Datentransfer-Dokumentation und SCCs noetig
- Handlung: `curl https://ipinfo.io/178.104.51.123` → Standort pruefen

**F2: Viber BSP-Entscheidung (Sinch vs. Infobip)**
- Beide BSPs sind fuer Viber Business API autorisiert
- Sinch: simpler API, transparentere Preise
- Infobip: hat lokale Praesenzen in Serbien (nth.rs kooperiert), mehr Features
- Handlung: Infobip fuer BiH+SRB evaluieren, nth.rs direkt anfragen

**F3: rocky2 Standort-Verifikation**
- rocky2 (37.27.71.134) — Hetzner Helsinki laut Memory, bestaetigen
- Handlung: `ssh rocky2 'curl https://ipinfo.io'`

**F4: WhatsApp BSP fuer Phase 2**
- Meta-Verifizierung fuer WhatsApp Business API dauert 2-6 Wochen
- Prozess jetzt starten (parallel zu Phase 1) damit Phase 2 reibungslos startet
- BSP-Empfehlung: Infobip (hat BiH+SRB Erfahrung) oder 360dialog (guenstig)

### 8.2 Wichtig (vor Phase 2 klaeren)

**F5: CorvusPay-Integration fuer automatisches Billing**
- Phase 1: manuelle Bankueberweisung
- Phase 2: CorvusPay Checkout-Link fuer BiH, oder Stripe fuer internationale Karten
- Handlung: CorvusPay API-Dokumentation pruefen, Denis Merchant-Account erfordert BiH-Firma oder Partnerschaft

**F6: OpenClaw Update-Management**
- OpenClaw ist Open Source — wie wird mit Updates umgegangen?
- Pro Kunden-Container: eigenes Image oder geteiltes Base-Image?
- Empfehlung: Eigenes Docker-Base-Image (`openclawbalkan:1.0`) von offizieller OpenClaw-Release ableiten
- Kunden-spezifische Konfiguration via Volume-Mount (nicht im Image)
- Updates: `docker pull openclawbalkan:latest && docker compose up -d` per n8n

**F7: Backup-Strategie Kunden-Daten**
- PostgreSQL-Volumes auf Kunden-Host muessen gesichert werden
- Hetzner Volumes Snapshots (1 EUR/10 GB/Monat) — automatisierbar
- Handlung: n8n Schedule → `pg_dump → Hetzner Object Storage` (taeglich, 30 Tage Retention)

**F8: Viber Business Account Setup-Zeit**
- Verifizierungsprozess fuer Viber Business API (via BSP) kann 1-4 Wochen dauern
- Denis muss einen einzigen Absender-Account einrichten (nicht pro Kunde)
- Outgoing Nachrichten gehen von Denis' Business Account, Webhook-Routing per Konversations-ID zu Kunden-Instanz

**F9: Skalierung Qdrant auf CCT**
- Aktuell: 97 Memories, bge-m3 Embeddings (1024 Dimensionen)
- Jeder Kunde: ~500-5000 Vektoren (FAQ-Dokumente + Konversationen)
- Bei 50 Kunden: ~250.000 Vektoren — absolut unproblematisch fuer Qdrant
- Bei 200 Kunden: ~1 Million Vektoren — RAM auf CCT pruefen (bge-m3 Quantization aktivieren)

### 8.3 Niedrige Prioritaet (Phase 3)

**F10: Multi-Tenant Admin-Dashboard**
- Phase 3: Eigenes Web-Dashboard fuer Denis (Kunden-Uebersicht, Status, Billing)
- Optionen: Retool (Low-Code), eigene React-App, oder Grafana-Erweiterung
- Kosten Phase 3 evaluieren

**F11: Self-Serve-Signup**
- Phase 3: Kunden koennen sich selbst registrieren (Kreditkarte, automatischer Deploy)
- Erfordert: CorvusPay/Stripe Merchant + vollautomatisierten Deploy ohne menschliche Freigabe
- Risiko: Abuse-Cases (Spam, automatische Registrierungen) — Screening noetig

**F12: Voice Agent Integration**
- Phase 3: Viber-Voice oder Telefon-AI fuer Kunden die telefonische Anfragen haben
- OpenClaw hat Voice-Kanal-Support (Denis hat Erfahrung vom activi.io Voice-System)
- Potenziell als Premium-Addon (+ 15-20 EUR/Monat)

---

*Dokument: ARCHITECTURE.md | Stand: 2026-03-31 | Erstellt auf Basis von BLUEPRINT-V2.md + RESEARCH-V2.md*
