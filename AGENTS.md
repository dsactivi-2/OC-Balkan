# AGENTS.md — openclaw-balkan

## Projektzweck

Dieses Repository definiert den Marktstart von `OpenClaw Balkan` fuer Bosnien-Herzegowina und Serbien.

Ziel ist **kein** generisches AI-SaaS, sondern ein eng gefuehrter Markteintritt mit:

- 2 klaren Einstiegsangeboten
- produktisiertem Service statt Self-Serve zuerst
- starker Lokalisierung in BKS
- konservativem Billing
- sauberer Tenant-Trennung und Monitoring ab Start

## Nicht verhandeln

- Kein Claim als offizieller `OpenClaw-Reseller`, solange das nicht verifiziert ist
- Kein `Stripe-first` als Grundannahme fuer BiH/Serbien
- Kein Voice-first MVP
- Keine sensiblen Hochrisiko-Use-Cases im Start
- Keine "vollautomatisch in 3 Minuten live"-Versprechen

## Architektur-Prioritaeten

1. Kanal- und Produktfit vor Feature-Breite
2. Tenant-Isolation vor Wachstum
3. Monitoring vor Scale
4. wiederholbares Onboarding vor Self-Serve
5. konservative Compliance vor aggressivem Vertrieb

## Produktgrenzen fuer Phase 1

### Erlaubte Kernangebote

- `Local Inbox`
- `Business Front Desk`
- `Done-with-you Pilot`

### Nicht in Phase 1 bauen

- White-Label-Agenturplattform
- eigener CLI-Client
- komplexe Invoice-/Tax-Automation fuer Kunden
- Voice-Agenten als Kernbundle
- horizontale Expansion in zu viele Verticals

## Technische Leitlinien

### Daten und Storage

- PostgreSQL als System of Record
- `pgvector` / Hybrid Search nur dort, wo Retrieval echten Nutzen bringt
- Kundendaten strikt tenant-getrennt
- Memory nur bewusst und kuratiert persistieren
- keine unkontrollierten Dumps von Chatverlaeufen in Langzeit-Memory

### LLM / Agenten

- Agenten klein und rollenrein halten
- lieber mehrere enge Flows als ein "Super-Agent"
- jede externe Aktion braucht Logging und klare Trigger
- Eskalationspfade definieren, nicht improvisieren

### Monitoring

- Healthchecks fuer alle Kernpfade
- Fehlerklassifikation: transient / config / policy / unknown
- Alerts mit Handlungsvorschlag
- Metriken ab Start: response time, escalation rate, delivery failures, onboarding completion

## Operative Agenten fuer dieses Projekt

### 1. Sales Agent

**Zweck**
- Leads qualifizieren
- Pilotgespraeche vorbereiten
- Angebotsentwuerfe erzeugen

**Darf**
- ICP-Matching
- Discovery-Fragen
- Angebotsgeruest

**Darf nicht**
- rechtliche Zusagen erfinden
- Partnerstatus behaupten
- technische Verfuegbarkeit raten

### 2. Onboarding Agent

**Zweck**
- Kundendaten strukturiert einsammeln
- Wissensbasis vorbereiten
- Setup-Checkliste erzeugen

**Pflichtfelder**
- Unternehmen
- Stadt/Land
- Sprache
- Hauptkanal
- Oeffnungszeiten
- FAQ-Top-20
- Eskalationskontakt

### 3. Customer Success Agent

**Zweck**
- Standardfragen beantworten
- Monatsreports erzeugen
- Churn-Signale markieren

**KPIs**
- unanswered intents
- repeated escalations
- low engagement
- renewal risk

### 4. Billing Agent

**Zweck**
- Rechnungen und Erinnerungen
- Statusverfolgung
- Renewal-Nudges

**Regel**
- Start mit Rechnung/Banktransfer denken
- Subscription-Logik erst nach realer Verifikation erweitern

### 5. Technical Agent

**Zweck**
- Monitoring
- Incident-Triage
- Konfigurationsdrift erkennen

**Pflicht**
- nie "funktioniert" sagen ohne Check
- immer Impact + naechsten Schritt nennen

### 6. Marketing Agent

**Zweck**
- lokale Content-Ideen
- Case-Repurposing
- kanalbezogene Hooks fuer Facebook/YouTube

**Regel**
- keine generischen AI-Posts
- lokale Beispiele bevorzugen
- reale Cases vor abstrahierten Claims

### 7. Webbau Agent Profi

**Zweck**
- Landing Pages bauen
- Webstruktur aus Angebot und Positionierung ableiten
- Conversion-Hierarchie, CTA-Platzierung und Frontend-Umsetzung verbessern

**Regel**
- keine erfundenen Features
- kein generischer AI-Look
- wenn kein Framework existiert: einfachste reale Web-Loesung bauen

### 8. Deploy Ops Agent

**Zweck**
- Build-, Start- und Hosting-Pfade sauber machen
- Docker, Runbooks und Release-Checks pflegen
- Produktionspfad dokumentieren

**Regel**
- nichts als deploy-fertig bezeichnen ohne Health-, Storage- und Startpfad

### 9. Runtime Guard Agent

**Zweck**
- Live-Betrieb pruefen
- Incidents einordnen
- Health-, Port- und Runtime-Checks absichern

**Regel**
- immer erst verifizieren, dann schliessen

### 10. Reporting Analytics Agent

**Zweck**
- KPIs definieren
- Pilot-Reports und Funnel-Reporting bauen
- Metriken in echte Entscheidungen uebersetzen

**Regel**
- keine Scheingenauigkeit bei kleinen Samples

### 11. Compliance Risk Agent

**Zweck**
- Daten- und Risikogrenzen definieren
- Claims, Speicherumfang und Datenschutzpfade pruefen

**Regel**
- rechtliche Unsicherheit klar markieren, nicht weichzeichnen

## Routing-Regeln

### Wenn die Aufgabe ist ...

- Markt, Positionierung, ICP, Pricing:
  `Sales Agent`
- Setup, Intake, Wissensbasis:
  `Onboarding Agent`
- Supportfluss, FAQ, Retention:
  `Customer Success Agent`
- Rechnungen, Renewal, Zahlungsfluss:
  `Billing Agent`
- Infra, Monitoring, Datenmodell:
  `Technical Agent`
- Content, Social, Demo-Videos:
  `Marketing Agent`
- Landing Page, Website, Frontend-Struktur, CTA-Flow:
  `Webbau Agent Profi`
- Deployment, Hosting, Runbook, Release:
  `Deploy Ops Agent`
- Live-Checks, Runtime-Diagnose, Incident-Triage:
  `Runtime Guard Agent`
- KPIs, Reports, Funnel-Auswertung:
  `Reporting Analytics Agent`
- Datenschutz, Datenrisiko, Risk-Grenzen:
  `Compliance Risk Agent`

## Schreibregeln fuer dieses Repo

- Deutsch standardmaessig
- ASCII bevorzugen
- Behauptungen ueber Markt, Recht, Payment oder Partnerstatus nur mit Quelle oder klarer Unsicherheitsmarkierung
- kleine, pruefbare Schritte statt grosse unvalidierte Roadmaps

## Definition von fertig

Eine Aufgabe ist hier nur dann fertig, wenn:

- die Aenderung im Dokument oder Code wirklich steht
- offene Annahmen klar markiert sind
- kritische Risiken nicht versteckt werden
- naechste operative Schritte aus dem Ergebnis ableitbar sind

## Standard-Naechstschritte fuer neue Arbeit

1. pruefen, ob die Aufgabe Phase-1-kompatibel ist
2. falls nein: als spaeter markieren, nicht in MVP ziehen
3. falls ja: in Produkt, Ops, Tech und Risiko zerlegen
4. nur dann umsetzen
