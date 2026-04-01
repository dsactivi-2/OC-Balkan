# OpenClaw Balkan — Bundle Index

> Version: 1.0 | Stand: 2026-03-31
> Alle Bundle-Definitionen unter: `bundles/`

---

## Uebersicht

| # | Bundle | Datei | Zielgruppe | Agenten | Modell | Preis/Monat |
|---|--------|-------|------------|---------|--------|-------------|
| 1 | Social Marketing Team | `social-marketing-team.yaml` | Friseur, Restaurant, Boutique, Cafe | 4 | qwen3.5 (lokal) | 39 EUR |
| 2 | Office Bundle | `office-bundle.yaml` | Anwalt, Arzt, Architekt, Makler | 4 | claude-sonnet-4-6 | 79 EUR |
| 3 | Research Bundle | `research-bundle.yaml` | Studenten, Forscher, NGOs | 4 | claude-sonnet-4-6 | 49 EUR |
| 4 | Learning Buddy | `learning-buddy.yaml` | Schueler (6-18) + Eltern | 4 | claude-sonnet-4-6 | 29 EUR |
| 5 | Solo Agent | `solo-agent.yaml` | Freelancer, Einzelunternehmer | 1 | qwen3.5 (lokal) | 25 EUR |

---

## Bundle 1: Social Marketing Team

**Beschreibung:** Komplett-Paket fuer Social Media Management. Erstellt Posts mit Bild-Prompts, plant Veroeffentlichungen zu optimalen Zeiten, antwortet auf Kommentare und Messenger-Nachrichten, verwaltet Facebook Ads.

**Zielgruppe:** Laden, Boutique, Friseur, Restaurant, Cafe, Kosmetikstudio

**Enthaltene Agenten:**
1. **Content Agent** — erstellt Posts (Text + Bild-Prompt) fuer Facebook/Instagram
2. **Scheduling Agent** — plant Posts via Buffer/n8n, analysiert optimale Zeiten
3. **Community Agent** — antwortet auf Kommentare + Messenger/Viber-Nachrichten
4. **Ads Agent** — plant + verwaltet Facebook Ads via Make (Meta Ads API)

**Kanaele:** Facebook Messenger, Instagram DM, Viber Business

**Modell:** qwen3.5-uncensored (lokal, 95% der Anfragen) + claude-sonnet-4-6 (Fallback, 5%)

**Integrationen:** Facebook Graph API, Instagram API, Viber Business (Sinch), Buffer, Make, n8n

**Kosten-Kalkulation:**
| Position | Monatlich |
|----------|-----------|
| Token-Kosten (geschaetzt) | ~2 EUR |
| Infrastruktur (anteilig) | ~3 EUR |
| **Gesamt Kosten** | **~5 EUR** |
| **Preis** | **39 EUR** |
| **Marge** | **~87%** |

---

## Bundle 2: Office Bundle

**Beschreibung:** Digitale Buero-Assistenz. Verwaltet Termine, nimmt Anrufe/Nachrichten entgegen, beantwortet und priorisiert E-Mails, erstellt einfache Dokumente (Angebote, Bestaetigungen).

**Zielgruppe:** Anwalt, Arzt, Architekt, Immobilienmakler, Steuerberater

**Enthaltene Agenten:**
1. **Termin Agent** — Termine buchen, bestaetigen, erinnern (Google Calendar read-only)
2. **Telefon Agent** — Nachrichten annehmen, Callback-Requests erstellen, an Termin Agent weiterleiten
3. **Mail Agent** — E-Mails kategorisieren, beantworten, weiterleiten, priorisieren
4. **Dokument Agent** — Angebote, Terminbestaetigungen, Benachrichtigungen erstellen

**Kanaele:** Viber Business, WhatsApp Business, E-Mail (IMAP/SMTP), Web-Widget (optional)

**Modell:** claude-sonnet-4-6 (primaer — Praezision kritisch fuer professionelle Dienste)

**Integrationen:** Google Calendar (read-only), IMAP/SMTP (via n8n), Viber, WhatsApp, n8n

**Kosten-Kalkulation:**
| Position | Monatlich |
|----------|-----------|
| Token-Kosten (geschaetzt) | ~5 EUR |
| Infrastruktur (anteilig) | ~3 EUR |
| **Gesamt Kosten** | **~8 EUR** |
| **Preis** | **79 EUR** |
| **Marge** | **~90%** |

---

## Bundle 3: Research Bundle

**Beschreibung:** Akademischer Forschungsassistent. Durchsucht hochgeladene Dokumente, fasst Texte zusammen, formatiert Zitate in allen gaengigen Stilen, erstellt Lernplaene mit Deadlines.

**Zielgruppe:** Studenten, Forscher, wissenschaftliche Mitarbeiter, NGOs

**Enthaltene Agenten:**
1. **Research Agent** — Themen recherchieren, Dokumente durchsuchen, Quellen sammeln
2. **Summary Agent** — Lange Texte strukturiert zusammenfassen
3. **Citation Agent** — Referenzen formatieren (APA 7, MLA 9, Chicago, Harvard, IEEE)
4. **Study Planner** — Personalisierter Lernplan mit Deadlines und Erinnerungen

**Kanaele:** Telegram, WhatsApp, Web-Widget

**Modell:** claude-sonnet-4-6 (primaer — Reasoning-Qualitaet kritisch)

**Integrationen:** CrossRef API (DOI-Lookup), Telegram Bot, Web Widget, n8n

**Kosten-Kalkulation:**
| Position | Monatlich |
|----------|-----------|
| Token-Kosten (geschaetzt) | ~8 EUR |
| Infrastruktur (anteilig) | ~3 EUR |
| **Gesamt Kosten** | **~11 EUR** |
| **Preis** | **49 EUR** |
| **Marge** | **~78%** |

**Hinweis:** Hoechste Token-Kosten aller Bundles wegen langer Dokumente und claude-sonnet als Primaer-Modell.

---

## Bundle 4: Learning Buddy

**Beschreibung:** Persoenlicher Tutor fuer Schulkinder (6-18 Jahre). Erklaert Schulstoff kindgerecht, erstellt Quizze, verfolgt den Lernfortschritt und sendet woechentliche Berichte an Eltern.

**Zielgruppe:** Schueler + Eltern, Nachhilfe-Einrichtungen, Privatschulen

**Enthaltene Agenten:**
1. **Erklaerer Agent** — Themen altersgerecht erklaeren (Sokratische Methode)
2. **Quiz Agent** — Wissenstests erstellen und auswerten nach Lehrplan BiH/Srbija
3. **Lernplan Agent** — Personalisierten Lernplan nach Schwaechen erstellen
4. **Eltern Agent** — Woechentliche Fortschrittsberichte an Eltern senden

**Kanaele:** WhatsApp (Schueler), Viber (Eltern), Telegram (Schueler 14+)

**Modell:** claude-sonnet-4-6 (paedagogische Qualitaet und kindgerechte Sprache kritisch)

**Integrationen:** Viber Business, WhatsApp, Telegram Bot, n8n

**Sicherheit:**
- Elterliche Einwilligung Pflicht (GDPR)
- Strenger Content-Filter — keine ungeeigneten Inhalte
- Mindestalter 6, Maximalter 18
- Datenaufbewahrung: 365 Tage

**Kosten-Kalkulation:**
| Position | Monatlich |
|----------|-----------|
| Token-Kosten (geschaetzt) | ~6 EUR |
| Infrastruktur (anteilig) | ~3 EUR |
| **Gesamt Kosten** | **~9 EUR** |
| **Preis** | **29 EUR** |
| **Marge** | **~69%** |

**Upsell:** +9 EUR/Monat pro zusaetzlichem Kind.

---

## Bundle 5: Solo Agent

**Beschreibung:** Ein einzelner spezialisierter Agent. Der Kunde waehlt beim Onboarding eine von vier Rollen: FAQ-Agent, Lead-Intake, Terminannahme oder Dokumentensuche.

**Zielgruppe:** Freelancer, Einzelunternehmer, Kleinst-Betriebe

**Enthaltene Agenten (1 von 4 waehlen):**
1. **FAQ Agent** — Beantwortet haeufige Fragen aus Wissensbasis
2. **Lead Intake Agent** — Sammelt Kontaktdaten und Anfragen von Interessenten
3. **Appointment Intake Agent** — Nimmt Terminanfragen entgegen (ohne Auto-Buchung)
4. **Document Search Agent** — Durchsucht hochgeladene Dokumente

**Kanaele:** 2 nach Wahl (aus Viber, Messenger, WhatsApp, Telegram, Web-Widget)

**Modell:** qwen3.5-uncensored (lokal — Kostenminimierung)

**Integrationen:** Je nach gewaehlter Rolle — Viber, Messenger, WhatsApp, Telegram, Web Widget, n8n

**Kosten-Kalkulation:**
| Position | Monatlich |
|----------|-----------|
| Token-Kosten (geschaetzt) | ~1 EUR |
| Infrastruktur (anteilig) | ~2 EUR |
| **Gesamt Kosten** | **~3 EUR** |
| **Preis** | **25 EUR** |
| **Marge** | **~88%** |

**Upgrade-Pfad:** Nach 60 Tagen aktiver Nutzung automatischer Vorschlag fuer Bundle-Upgrade (20% Rabatt auf erste 30 Tage).

---

## Preisuebersicht — SaaS

| Bundle | Basis | +Kanal | +Sprache | +Kind | Cloud-Budget |
|--------|-------|--------|----------|-------|-------------|
| Solo Agent | 25 EUR | +9 EUR | — | — | 3 USD |
| Learning Buddy | 29 EUR | +9 EUR | — | +9 EUR | 10 USD |
| Social Marketing | 39 EUR | +9 EUR | +9 EUR | — | 5 USD |
| Research Bundle | 49 EUR | +9 EUR | +9 EUR | — | 15 USD |
| Office Bundle | 79 EUR | +9 EUR | +9 EUR | — | 10 USD |

**Jahresabo:** 10 Monate zahlen, 12 Monate nutzen (alle Bundles).

---

## Technische Basis (alle Bundles)

| Komponente | Technologie | Instanz |
|-----------|-------------|---------|
| Agent-Runtime | OpenClaw (self-hosted) | Kunden-Host (Docker) |
| LLM-Gateway | LiteLLM (rocky2:14000) | Shared, Virtual Key pro Kunde |
| Vektorspeicher | Qdrant (CCT:16333) | Collection pro Kunde |
| Kurzzeit-Memory | Mem0 (CCT:8002) | Namespace pro Kunde |
| Embedding | bge-m3 (CCT) | Shared |
| Datenbank | PostgreSQL (Docker) | Pro Kunde isoliert |
| Reverse Proxy | Nginx | Shared auf Kunden-Host |
| Automatisierung | n8n (rocky2) | Shared |

---

## Dateien in diesem Verzeichnis

```
bundles/
  INDEX.md                      ← diese Datei
  social-marketing-team.yaml    ← Bundle 1
  office-bundle.yaml            ← Bundle 2
  research-bundle.yaml          ← Bundle 3
  learning-buddy.yaml           ← Bundle 4
  solo-agent.yaml               ← Bundle 5
```
