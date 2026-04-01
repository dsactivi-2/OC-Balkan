# OpenClaw Balkan — Business Blueprint

> Version: 2.0 | Stand: 2026-03-30 | Status: Arbeitsgrundlage, nicht final validiert

## 1. Executive Summary

**Ziel:** OpenClaw als lokaler AI-Agenten-Anbieter fuer Bosnien-Herzegowina und Serbien positionieren, mit lokalem Support in BKS und einem operativ stark automatisierten Modell.

**Wichtige Korrektur:** Das Vorhaben darf aktuell **nicht** als "offizieller OpenClaw-Reseller" beschrieben werden, solange kein verifizierter Partner- oder Reseller-Vertrag vorliegt.

**Empfohlener Markteintritt:**
- Phase 1 nicht als reines SaaS starten
- Phase 1 als **produktisierte Service-Implementierung** starten
- danach erst zu wiederholbaren Paketen und Self-Serve-Elementen ausbauen

**Grund:** Billing, Viber, Compliance, White-Label-Rechte und tatsächliche OpenClaw-Partnerkonditionen sind noch nicht final geklaert.

## 2. Strategische Neupositionierung

### Was bleibt

- Marke: `OpenClaw Balkan`
- Fokus: lokale Sprache, lokaler Support, lokale Use Cases
- Betriebsziel: maximal automatisiert, schlanke Human-Eskalation

### Was geaendert wird

- Nicht "One-click SaaS fuer alle" zum Start
- Nicht 6 Pakete gleichzeitig
- Nicht Stripe-first fuer den Gesamtmarkt
- Nicht Voice-Agents von Tag 1 als Kernbestandteil

### Neue Startthese

Der schnellste realistische Einstieg ist:

1. 3 bis 5 Pilotkunden
2. 1 bis 2 vertikale Kernangebote
3. standardisierte Onboarding- und Support-Flows
4. wiederholbarer Betrieb
5. erst danach Self-Serve, CLI und White-Label

## 3. Zielmarkt und Priorisierung

### Land 1: Bosnien-Herzegowina

**Geeignet fuer:**
- lokale Dienstleistungen
- Restaurants
- Friseure / Beauty
- kleine Praxen / Buero-orientierte Betriebe

**Wichtige Marktfakten**
- Facebook ist weiterhin stark
- Messenger-Nutzung ist zentral
- Viber muss als Kanal ernsthaft eingeplant werden
- Preisbereitschaft ist vorhanden, aber preissensibel
- subscription-only checkout ist riskant

### Land 2: Serbien

**Geeignet fuer:**
- urbanere, digitalere KMU
- Agenturen als Multiplikatoren
- B2B-nahe Workflows
- spaeter White-Label / Partner-Modell

**Wichtige Marktfakten**
- hoeherer SaaS-Reifegrad als BiH
- groesserer TAM
- rechtliche Themen bei E-Rechnung und Datenverarbeitung muessen frueh sauber sein

### Sprachmodell

Nicht "eine Sprache fuer alle" vermarkten, sondern:

- `BKS-Base Layer` technisch gemeinsam
- pro Markt eigene Ausspielung:
  - Bosnien: bosnisch/kroatisch formuliert
  - Serbien: serbisch formuliert

Das reduziert kulturelles Reibungsrisiko im Onboarding.

## 4. Das echte Einstiegsprodukt

### Wedge Offer 1: Messaging & Booking

**Zielgruppe**
- Friseur
- Beauty
- Restaurant
- Praxis mit Terminanfragen

**Outcome**
- beantwortet Standardfragen
- nimmt Anfragen entgegen
- sammelt Leads
- uebergibt an Kalender / Mitarbeiter / Inbox

**Kanaele**
- Facebook Messenger
- WhatsApp
- Viber, falls Integration operativ tragfaehig

### Wedge Offer 2: Inbox & FAQ Assistant

**Zielgruppe**
- Kanzlei
- Makler
- Praxis
- kleines Dienstleistungsbuero

**Outcome**
- beantwortet Top-20-Fragen
- sammelt Kontakt- und Anliegendaten
- qualifiziert Anfragen
- erstellt saubere Uebergaben fuer Mensch oder CRM

### Was bewusst spaeter kommt

- vollstaendige Self-Serve-Web-UI
- eigener CLI-Client
- Voice-Agenten als Massenprodukt
- White-Label-Agenturpaket
- komplexe Rechnungs-/Steuer-Automation fuer Endkunden

## 5. Angebotsstruktur

### Paket A — Local Inbox

**Fuer:** Friseur, Beauty, Restaurant, kleine Dienstleister

**Enthaelt**
- 1 Hauptkanal
- FAQ-Agent
- Anfrage-/Termin-Intake
- lokalisierte Antworten
- Monatsreport

**Preisidee**
- BiH: 19-39 EUR/Monat
- Serbien: 25-45 EUR/Monat
- einmaliges Setup: 99-199 EUR

### Paket B — Business Front Desk

**Fuer:** Kanzlei, Makler, Praxis, Architekturbueros

**Enthaelt**
- 2 Kanaele
- FAQ + Qualifizierung
- Formular-/CRM-Uebergabe
- Eskalationslogik
- Monatsreport

**Preisidee**
- BiH: 39-69 EUR/Monat
- Serbien: 49-79 EUR/Monat
- einmaliges Setup: 149-299 EUR

### Paket C — Done-with-you Pilot

**Fuer:** erste Referenzkunden

**Enthaelt**
- individuelles Setup
- enges Feedback
- 14 Tage Iteration
- Case Study Freigabe gegen Rabatt

**Preisidee**
- 0-99 EUR Setup fuer Pilot
- danach regulaerer Paketpreis

## 6. Billing-Modell

### Startmodell

**Nicht:** reines Stripe-Abo fuer alle Maerkte

**Sondern:**
- Rechnung / Bankueberweisung als Standard in Phase 1
- optional Karte dort, wo operativ verfuegbar
- Jahresvorauszahlung mit Rabatt aktiv anbieten

### Warum

- lokale Zahlungsgewohnheiten
- geringere technische Reibung im Start
- weniger Abhaengigkeit von einem Payment-Stack
- einfacher fuer Testkunden und erste Referenzen

### Empfohlene Reihenfolge

1. Rechnung + Banktransfer
2. Kartenzahlung fuer serbische bzw. internationale Kunden
3. erst spaeter echte Self-Serve-Subscription

## 7. Betriebsmodell

### Operatives Ziel

`Zero Human Company` bleibt eine Richtung, aber nicht die Startrealitaet.

### Realistische Stufen

**Stufe 1 — Founder-led mit Automationskern**
- Denis verkauft
- Denis finalisiert Setups
- Agenten uebernehmen FAQ, Follow-up, Reporting, Billing-Reminder

**Stufe 2 — Assistierte Automatisierung**
- Sales-Agent qualifiziert
- Onboarding-Agent sammelt Daten
- Support-Agent beantwortet Standardfragen
- Technical-Agent ueberwacht und erstellt Alerts

**Stufe 3 — Nahezu autonom**
- menschliche Eingriffe nur bei Eskalation, Vertragsfragen, groesseren Stoerungen

### Interne Kernagenten fuer Phase 1

| Agent | Zweck | Start in Phase 1 |
|---|---|---|
| Sales Agent | Lead Intake, Follow-up, Angebotsentwurf | Ja |
| Onboarding Agent | Daten sammeln, Setup-Checkliste | Ja |
| Customer Success Agent | FAQ, Monatsreport, Renewal-Nudge | Ja |
| Billing Agent | Rechnung, Erinnerung, Status | Ja |
| Technical Agent | Monitoring, Fehlerklassifikation, Alarm | Ja |
| Marketing Agent | Content-Ideen, lokale Posts, Case Repurposing | Ja, aber menschlich kontrolliert |

## 8. Tech-Architektur

### Kernstack

- OpenClaw als Agentenplattform
- PostgreSQL fuer Kundendaten, Konfiguration, Events
- `pgvector` / Hybrid Search fuer Wissensbasis und Memory-Retrieval
- Queue / Jobs fuer asynchrone Workflows
- Monitoring + Alerting ab Tag 1

### Memory- und Wissensarchitektur

- pro Kunde klar getrennte Wissensbasis
- session memory fuer Support-Kontext
- kuratierte Langzeitfakten fuer Policies, Oeffnungszeiten, Preise
- keine unkontrollierte Freitext-Speicherung sensitiver Daten

### Kanalprioritaet

1. Facebook Messenger
2. WhatsApp
3. Viber
4. Webchat / Formular
5. spaeter Voice

### Was technisch nicht versprochen werden sollte

- "in 3 Minuten live"
- vollautomatisches Website-Scraping als Standard
- generische Self-Serve-Installationen ohne menschliche Validierung

## 9. Compliance-Minimum

Vor den ersten zahlenden Kunden muss mindestens stehen:

- Datenschutzhinweise je Markt
- AV-/DPA-Logik
- Datenfluss-Dokumentation
- definierte Aufbewahrungsregeln
- Incident-Prozess
- klare No-go-Datenklassen

### Praktische Regel

In Phase 1 nur solche Use Cases verkaufen, die **kein Hochrisiko-Profiling** und keine tiefe Verarbeitung sensibler Kategorien brauchen.

Damit raus aus dem Start:
- medizinische Diagnostik
- HR-Screening
- komplexe Bonitaets-/Risikomodelle

## 10. Go-to-Market

### Channel-Strategie

- Facebook Page pro Markt
- kurze Demo-Videos in BKS
- lokale Before/After-Cases
- Direktansprache von 30-50 Betrieben
- 3 Pilotkunden gegen Testimonial

### Beste erste Verticals

1. Friseur / Beauty
2. Restaurant / Cafe
3. Makler / Kanzlei / kleines Office

### Warum diese Reihenfolge

- hohes Volumen an wiederholten Fragen
- klare Reaktionszeit-Probleme
- geringer Integrationsaufwand
- leicht messbarer Nutzen

## 11. KPI-System

### Nordstern in Phase 1

Nicht MRR allein, sondern:

- `time-to-first-value`
- `weekly saved inquiries`
- `response-rate under 5 min`
- `pilot-to-paid conversion`
- `escalation rate`

### Zielwerte Phase 1

- 3 Pilotkunden live
- 2 zahlende Kunden bis Ende Monat 2
- <15% Eskalationsrate auf Standardanfragen
- >80% Antwortabdeckung der definierten FAQ-Faelle

### Zielwerte Phase 2

- 10-15 zahlende Kunden
- positive Referenzen aus beiden Maerkten
- standardisierte Setup-Zeit < 2 Stunden pro Kunde

## 12. Einfache Unit Economics

### Noch nicht final verifiziert

Es fehlt weiterhin:
- echte OpenClaw-Partnerkondition
- echter Kanalpreis pro Message
- reale Hosting- und LLM-Kosten je Kunde

### Bis zur Verifikation gilt

Es wird **nicht** mit 70-90% Marge geplant.

Arbeitsannahme fuer Planung:
- niedrige Kundenzahl
- hoeherer Serviceanteil
- konservative Marge
- Fokus auf Lernkurve statt Profitmaximierung in Monat 1-2

## 13. Harte Blocker

Diese Punkte sind vor Scale zu klaeren:

1. Gibt es ein echtes OpenClaw-Partner-/Reseller-Modell?
2. Welche Kanaele sind operativ und rechtlich belastbar?
3. Wie wird in BiH und Serbien faktisch kassiert?
4. Welche Datenschutzdokumente sind vor Pilotstart Pflicht?
5. Wie werden Kundenwissen und Memory tenant-sicher getrennt?

## 14. 30-Tage-Plan

### Woche 1

- Partner-/Reseller-Status OpenClaw klaeren
- Viber-Machbarkeit pruefen
- 2 Zielpakete finalisieren
- Standard-Onboarding-Fragebogen bauen

### Woche 2

- Demo-Instanz aufsetzen
- 2 Landing Pages erstellen: Bosnien / Serbien
- Pricing als Pilotversion definieren
- Support- und Eskalationslogik einbauen

### Woche 3

- 20-30 lokale Leads anschreiben
- 3 Pilotgespraeche fuehren
- 1. Pilot live schalten
- Monitoring und Reporting pruefen

### Woche 4

- Pilotfeedback auswerten
- FAQ / Prompt / Routing verbessern
- Testimonial-Prozess starten
- entscheiden: vertiefen, pivotieren oder stoppen

## 15. Klare Entscheidung fuer jetzt

**Nicht bauen:**
- grosses Agentur-OS fuer alle Verticals
- massives Self-Serve SaaS
- Voice-first Bundle

**Jetzt bauen:**
- 1 sauberes Demo-System
- 2 echte Wedge-Pakete
- 1 konservatives Billing-Modell
- 1 standardisierte Betriebsstrecke

## 16. Arbeitsfazit

Die optimierte Version ist kein "Moonshot-SaaS", sondern ein kontrollierter Markteintritt:

- erst Produkt + Service validieren
- dann Betriebsautomatisierung stabilisieren
- dann Paketisierung
- dann Self-Serve / White-Label / Scale

Das erhoeht die Chance auf echte Traktion deutlich und senkt das Risiko, an Billing, Partnerstatus oder Kanalrealitaet zu scheitern.
