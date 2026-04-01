# OpenClaw Balkan — Business Blueprint

> Version 2.0 | Stand: 2026-03-30 | Autor: Denis Selmanovic
> Basis: RESEARCH.md v2.0, BLUEPRINT-REVIEW.md v1.0, RESEARCH-REVIEW.md v1.0

---

## 1. Executive Summary

**Was:** AI-Agent-Pakete für KMU in Bosnien & Herzegowina und Serbien — fertig konfiguriert, in lokaler Sprache, zu Westbalkan-Preisen.

**Wie:** Self-Hosted OpenClaw auf EU-Infrastruktur (Hetzner DE). Kein Reseller-Vertrag nötig — OpenClaw ist Open Source. Billing über bestehende DE/AT-Entity via Stripe. Vollautomatisierter Betrieb (Zero Human Company).

**Warum jetzt:** KI-Tools sind im Westbalkan fast unbekannt (<5% Adoption bei KMU). Kein Wettbewerber bietet fertige Agent-Pakete in lokaler Sprache zu lokalen Preisen. Das ist ein 2–3 Jahre First-Mover-Fenster.

**Ziel Jahr 1:** 120 zahlende Kunden, 6.600 EUR MRR, Break-Even in Monat 8.

---

## 2. Geschäftsmodell

### 2.1 Revenue Streams

| Stream | Typ | Beschreibung |
|--------|-----|-------------|
| **Basis SaaS-Abo** | Recurring (monatlich) | Plattform-Zugang + enthaltene Agenten |
| **Zusatz-Skills** | Recurring (monatlich) | Add-on Kanäle, Sprachen, Voice-Agent |
| **Einmaliges Setup** | Einmalig | Assisted Onboarding, Custom Agent Dev, Datenmigration |
| **Agentur White-Label** | Recurring (monatlich) | Multi-Workspace + API-Zugang für Weiterverkauf |

### 2.2 Warum KEIN Reseller-Vertrag nötig

OpenClaw ist Open Source (MIT License). Es existiert kein offizielles Reseller-Programm. Das Geschäftsmodell basiert auf:

1. Self-Hosting der OpenClaw-Plattform auf eigener Infrastruktur
2. Eigene Konfiguration, Lokalisierung und Produktisierung als Mehrwert
3. Eigene Kundenbeziehung und Billing

**Vorteil:** Keine Abhängigkeit von Vendor-Konditionen, keine laufenden Lizenzgebühren. **Risiko:** Kein offizieller Support — eigene technische Kompetenz ist Pflicht.

---

## 3. Zielgruppen — 3 Segmente

### Segment 1: Lokale Dienstleister (Primär-Segment)

Restaurants, Friseure, Kosmetikstudios, Fitnessstudios, Zahnarztpraxen, Autowerkstätten.

- Größe: 1–15 Mitarbeiter
- Problem: Verlorene Buchungen, keine Kapazität für Kundenkommunikation, kein Budget für Assistenten
- Kaufentscheidung: Schnell, preisorientiert, braucht Demo die sofort funktioniert
- Zahlungsbereitschaft: 25–59 EUR/Monat
- Kommunikationskanal: **Viber** (35+) oder WhatsApp (25–35)
- Typischer Entscheider: Inhaber, 40–55 Jahre, nutzt Facebook + Viber, hat evtl. keine Kreditkarte

### Segment 2: E-Commerce & Webshops

Lokale Online-Shops (WooCommerce, Shopify, eigene Lösungen). Mode, Kosmetik, Elektronik.

- Größe: 1–10 Mitarbeiter
- Problem: Kundenanfragen häufen sich, Retouren kosten Zeit, Social-Media bleibt liegen
- Kaufentscheidung: Mittel, braucht ROI-Argumentation
- Zahlungsbereitschaft: 49–99 EUR/Monat
- Typischer Entscheider: Jünger (25–40), tech-affiner, hat Kreditkarte

### Segment 3: Agenturen & Freelancer (Multiplikator-Segment)

Werbeagenturen, Web-Developer, Social-Media-Manager. Wollen AI-Agenten an ihre Kunden weiterverkaufen.

- Größe: 1–30 Personen
- Problem: Kunden fragen nach AI, wissen nicht wie anfangen
- Kaufentscheidung: Langsam, technisch interessiert, braucht API-Zugang
- Zahlungsbereitschaft: 149–299 EUR/Monat (+ Marge auf Weiterverkauf)
- Multiplikator-Effekt: 1 Agentur = 5–15 Endkunden

---

## 4. Produkt — Bundle-Pakete

### 4.1 Pakete und Preise

| Paket | Zielgruppe | Enthaltene Agenten | Kanäle | Preis/Monat |
|-------|-----------|-------------------|--------|-------------|
| **Starter** | Jeder Einsteiger | FAQ-Agent + Termin-Chat | 1 Kanal (Viber ODER WhatsApp ODER FB) | **25 EUR** |
| **Friseur/Beauty** | Friseur, Nagelstudio, Kosmetik | Termin-Buchung + Erinnerungen + Preisliste + Feedback | Viber + WhatsApp + FB | **39 EUR** |
| **Restaurant** | Restaurant, Café, Pizzeria | Reservierung + Menü + Öffnungszeiten + Google-Bewertungen | Viber + WhatsApp + FB | **49 EUR** |
| **Webshop** | Online-Shops | Kundenservice + Produktempfehlung + Retouren + Bewertungen | WhatsApp + FB + E-Mail | **79 EUR** |
| **Immobilien** | Makler, Vermietung | Objekt-Anfragen + Besichtigung + Lead-Qualifizierung | Viber + WhatsApp + FB + E-Mail | **99 EUR** |
| **Agentur** | Agenturen, IT-Dienstleister | Alle Pakete White-Label + API + 5 Kunden-Workspaces | Alle Kanäle | **199 EUR** |

**Preisanpassungen vs. v1.0:**
- Starter: 29 → 25 EUR (unter der psychologischen 30-EUR-Schwelle, näher am BiH-Komfortniveau)
- Restaurant: 59 → 49 EUR (innerhalb des Research-bestätigten 15–40 EUR BiH-SMB-Ranges)
- Agentur: 299 → 199 EUR (niedrigere Einstiegshürde, aber nur 5 statt 10 Workspaces — Erweiterung als Upsell)
- **NEU:** Viber als Standard-Kanal in ALLEN Paketen ab Friseur/Beauty

### 4.2 Add-ons

| Add-on | Preis/Monat |
|--------|-------------|
| Zusätzlicher Kanal (Telegram, Instagram DM) | +9 EUR |
| Zusätzliche Sprache (Englisch, Deutsch) | +9 EUR |
| Voice-Agent (KI-Sprachanruf) | +29 EUR |
| +5 Agentur-Workspaces | +79 EUR |

### 4.3 Einmalige Services

| Service | Preis |
|---------|-------|
| Assisted Onboarding (60 Min, AI-geführt) | 59 EUR |
| Custom Agent Development | ab 199 EUR |
| Datenmigration (Kontakte, Buchungen) | 79 EUR |

### 4.4 Jahresabo

Ab Phase 1 verfügbar (nicht erst Phase 3 wie in v1.0):
- **10 Monate zahlen, 12 Monate nutzen** (2 Monate gratis)
- Reduziert Churn (Commitment), verbessert Cash-Flow
- Banküberweisung als Zahlungsmethode für Jahresabos (für BiH-Kunden ohne Kreditkarte)

### 4.5 Trial-Modell

**v1.0 hatte:** 14-Tage-Trial ohne Kreditkarte → prognostizierte Free-to-Paid Conversion <5%.

**v2.0:** 7-Tage-Trial MIT optionaler Kartenangabe. Alternativ: Freemium-Starter mit 50 Nachrichten/Monat Limit (genügt für Demo-Wert, erzwingt Upgrade bei echtem Einsatz).

---

## 5. Zero Human Company — Agent-Team

### 5.1 Interne Agenten

| Agent | Verantwortung | Kanäle | Eskalation |
|-------|--------------|--------|------------|
| **Sales Agent** | Leads qualifizieren, Demo-Links senden, Angebote schreiben, 3-Tage-Follow-up | FB Messenger, Viber, WhatsApp, E-Mail | Lead will Sonderkondition → Denis |
| **Onboarding Agent** | Wizard durchführen, Daten sammeln, Deployment triggern, 7-Tage-Check-in | Web-Chat, Viber, E-Mail | Setup scheitert technisch → Technical Agent |
| **CS Agent** | 24/7 Support, FAQ beantworten, einfache Probleme lösen | Viber-Support, WhatsApp, E-Mail | Problem nicht lösbar nach 3 Versuchen → Denis |
| **Billing Agent** | Rechnungen senden, Zahlungserinnerungen (Tag 7, 14, 30), Kündigungen verarbeiten | Stripe Webhooks, E-Mail | Zahlungsausfall >30 Tage → Denis entscheidet |
| **Marketing Agent** | Content erstellen (2x/Woche eigener, 2x/Woche kuratiert), Kampagnen planen | FB Business API, Buffer | Nur Reporting an Denis |
| **Technical Agent** | Uptime-Monitoring, Auto-Restart bei Fehler, Config-Updates | OpenClaw API, Alerting | Uptime <99% → Sofort-Alert an Denis |

### 5.2 Realistische Zeitplanung

**v1.0 behauptete:** 5 Stunden/Woche ab Tag 1. Das ist unrealistisch.

**v2.0 Realismus:**

| Phase | Denis' Zeitaufwand/Woche | Begründung |
|-------|-------------------------|------------|
| Monat 1–2 | 25–30 Stunden | Setup, Agent-Training, erste Kunden, Debugging |
| Monat 3–4 | 15–20 Stunden | CS-Eskalationen (Wissensbasis noch dünn), Ads-Optimierung |
| Monat 5–6 | 8–12 Stunden | Agenten sind trainiert, Wissensbasis gewachsen |
| Monat 7–12 | 5–8 Stunden | Ziel-@ustand: nur noch Entscheidungs-Eskalationen |

### 5.3 Eskalations-Matrix

| Schweregrad | Beispiel | Max. Reaktionszeit | Wer entscheidet |
|-------------|---------|-------------------|----------------|
| **P1 — Kritisch** | System down, Datenverlust | 1 Stunde | Denis (Telegram-Alert) |
| **P2 — Hoch** | Kunde kann Agent nicht nutzen | 4 Stunden | CS Agent, eskaliert nach 3 Versuchen |
| **P3 — Mittel** | Feature-Request, Konfigfrage | 24 Stunden | CS Agent löst selbst |
| **P4 — Niedrig** | Feedback, allgemeine Frage | 48 Stunden | CS Agent löst selbst |

**Bei 120 Kunden (Ende Jahr 1):**
- Geschätzte Eskalationen: 2–3% der Kunden/Woche = 3–4 Eskalationen/Woche
- Davon P1/P2: ~1/Woche
- Geschätzter Zeitaufwand: 2–4 Stunden/Woche für Eskalationen allein

### 5.4 Support-Skalierung (ab 200+ Kunden)

- Zweiter CS Agent mit spezialisiertem Wissen (Billing vs. Technical)
- FAQ-Datenbank wächst automatisch (jede gelöste Eskalation → neuer FAQ-Eintrag)
- Backup-Plan wenn Denis nicht verfügbar: Pre-defined Playbooks für alle P1/P2-Szenarien

---

## 6. Marketing-Strategie

### 6.1 Facebook Pages

| Seite | Sprache | Städte | Content-Fokus |
|-------|---------|--------|---------------|
| **OpenClaw Bosna** | Bosnisch | Sarajevo, Banja Luka, Mostar, Tuzla | Lokale Beispiele (Ćevabdžinica, Frizerski salon) |
| **OpenClaw Srbija** | Serbisch | Beograd, Novi Sad, Niš, Subotica | E-Commerce-Szene, Tech-Startups |

**Posting-Mix (4x/Woche pro Seite):**
- 1x Use-Case-Demo (Video + Text) — echte lokale Beispiele
- 1x Bildungs-Post ("Was ist ein AI-Agent? 3 Sätze")
- 1x Kundenstimme / Testimonial (ab Monat 3: echte Kunden)
- 1x Lokaler Content (echte Orte, echte Menschen — kein generierter AI-Content)

**WICHTIG (v2.0 Korrektur):** Mindestens 50% des Contents muss ECHT sein (echte Kunden, echte Orte, echte Ergebnisse). Generierter AI-Content wird in der Region schnell erkannt und untergräbt Vertrauen.

### 6.2 Website

Domains: `openclaw.ba` + `openclaw.rs` → gleiche Seite mit Regions-Umschaltung (NICHT "Sprach-Umschaltung" — siehe Sprachpolitik in RESEARCH.md).

Seitenstruktur:
1. Hero: "Tvoj prvi AI zaposlenik — aktivan za 24 sata" + Demo-Button
2. Live-Demo: Interaktiver Chat-Agent direkt auf der Seite
3. Pakete: Preistabelle, "Najpopularniji" Badge auf Restaurant-Paket
4. Use Cases: 6 konkrete Beispiele mit Screenshots
5. Testimonials: Ab Monat 3 echte Stimmen
6. FAQ: 15 Fragen, Agent beantwortet auch per Chat
7. "Započni sad" → Wizard-Einstieg

**Onboarding-Versprechen:** "Dein Agent ist innerhalb von 24 Stunden aktiv" (NICHT "3 Minuten" wie in v1.0 — das war Marketing-Copy, keine technische Realität).

### 6.3 YouTube-Kanal

"OpenClaw Balkan" — primär auf Bosnisch/Serbisch.

- Tutorial-Serie (10 Videos): Schritt-für-Schritt Setup, 5–8 Min
- Use-Case-Demos: Echter Kunde zeigt seinen Agent, 2–3 Min
- "KI erklärt" Serie: Für Nicht-Techniker, 3–5 Min
- Posting: 1 Video/Woche in den ersten 6 Monaten

### 6.4 Piloten & Social Proof

**Phase 1 (Monat 1–2): 3–5 kostenlose Pilot-Installationen**

Konkrete Zielkandidaten:
- 1 Restaurant in Sarajevo (Denis' persönliches Netzwerk)
- 1 Friseur in Beograd (über Social Media identifizieren)
- 1 Webshop (über Facebook-Gruppen für bosnische/serbische Unternehmer)

Pro Pilot: Video-Testimonial aufnehmen (30–60 Sekunden), Erlaubnis für Referenz einholen.

### 6.5 Ads-Budget

| Phase | Monat | Budget/Monat | Kanal | Erwartete CAC |
|-------|-------|-------------|-------|---------------|
| Setup | 1–2 | 0 EUR | Organic + Netzwerk | 0 EUR (Piloten) |
| Wachstum | 3–6 | 300 EUR | Facebook Ads | 80–120 EUR |
| Scale | 7–12 | 800–1.200 EUR | Facebook + Instagram Ads | 50–80 EUR |

**v2.0 Korrektur:** 300 EUR/Monat reicht NICHT für das Monat-12-Ziel von 300 Kunden (v1.0). Mit realistischer CAC von 80–120 EUR und 300 EUR Budget: ~3 Neukunden/Monat über Paid. Daher: Ads-Budget in Phase 3 auf 800–1.200 EUR erhöhen, ODER Agentur-Multiplikatoren als Primärkanal nutzen.

### 6.6 Agentur-Partner-Programm

Das Agentur-Paket (199 EUR) ist der größte Skalierungshebel: 1 Agentur = 5–15 Endkunden.

**Partner-Onboarding-Prozess:**
1. Agentur registriert sich für Agentur-Paket
2. White-Label Setup (eigenes Logo, eigene Domain) — automatisiert
3. Partner-Dokumentation: Wie Agent konfigurieren, wie an Endkunden verkaufen
4. Revenue-Share: Agentur behält 100% ihrer Endkunden-Marge (wir verdienen am Agentur-Paket)
5. Quartals-Review: Performance-Daten, Feedback, Upsell-Möglichkeiten

**Ziel:** 3–5 aktive Agentur-Partner in Jahr 1 = 30–75 indirekte Endkunden.

---

## 7. Phasenplan

### Phase 1: Foundation (Monat 1–3)

**Ziel:** Infrastruktur live, 3–10 zahlende Kunden, Product-Market-Fit testen.

| Woche | Tasks |
|-------|-------|
| 1–2 | Hetzner-Server aufsetzen, OpenClaw deployen, erste Agent-Templates konfigurieren |
| 3–4 | Website launchen (.ba + .rs), Facebook-Seiten aufbauen, Stripe Billing aktivieren |
| 5–6 | 3 Pilot-Installationen (kostenlos), Feedback sammeln, Agent-Qualität iterieren |
| 7–8 | Paid Onboarding starten, erstes Demo-Video, erste Testimonials |
| 9–12 | 5–10 zahlende Kunden, Viber-Integration live, interne Agenten (Sales, CS, Billing) deployen |

**Meilensteine:**
- Woche 2: OpenClaw self-hosted läuft auf Hetzner
- Woche 4: Website + Facebook live
- Woche 8: Erste zahlende Kunden
- Woche 12: 10 aktive Kunden, alle internen Agenten live

**v2.0 Korrektur:** v1.0 hatte "10 zahlende Kunden in Monat 1–2" — unrealistisch. Phase 1 geht über 3 Monate. Die ersten 2 Monate sind rein Setup + Piloten.

### Phase 2: Wachstum (Monat 4–8)

**Ziel:** 50–80 zahlende Kunden, MRR >3.500 EUR, Break-Even Richtung Monat 8.

| Task | Detail |
|------|--------|
| Facebook Paid Ads | 300 EUR/Monat, A/B-Testing verschiedener Use Cases |
| YouTube-Kanal | 20+ Videos, Tutorial-Serie abschließen |
| Erste Testimonials | Video-Testimonials von Pilot-Kunden |
| Agentur-Akquise | 1–2 Agentur-Partner aktiv gewinnen |
| Upsell-Flows | Basierend auf echten Nutzungsdaten optimieren |
| Churn-Management | Win-Back-Flow für Kündigungen, Downgrade-Angebot statt Kündigung |

### Phase 3: Scale (Monat 9–12)

**Ziel:** 100–150 Kunden, MRR >6.000 EUR, stabile Unit Economics.

| Task | Detail |
|------|--------|
| Ads-Budget erhöhen | 800–1.200 EUR/Monat |
| Agentur-Programm formalisieren | 3–5 aktive Partner, Partner-Dokumentation |
| Jahresabo-Konversion | Bestehende Monats-Kunden auf Jahresabo upsellen |
| Zweites Land evaluieren | Kroatien oder Nordmazedonien (gleiche Sprache/ähnlicher Markt) |
| Automatisierung >90% | Agent-Team löst >90% aller Anfragen ohne Denis |

### Meilensteine (konservativ)

| Zeitpunkt | Kunden | MRR | Status |
|-----------|--------|-----|--------|
| Monat 3 | 10 | 500 EUR | Product-Market-Fit validiert |
| Monat 6 | 40 | 2.200 EUR | Paid Ads profitabel |
| Monat 8 | 70 | 3.850 EUR | **Break-Even** |
| Monat 12 | 120 | 6.600 EUR | Stabil, Scale-ready |

**v2.0 Korrektur:** v1.0 hatte "300 Kunden, 19.500 EUR MRR in Monat 12" — das erforderte 33 Neukunden/Monat bei 300 EUR Ads-Budget. Unrealistisch. v2.0 setzt konservative Ziele die mit dem geplanten Budget und einer realistischen CAC erreichbar sind.

---

## 8. Risiken & Mitigations

### R1: Niedrige AI-Adoption (HOCH)

KMU-Inhaber im Westbalkan haben oft noch nie mit AI-Tools gearbeitet.

**Mitigation:** Demo-First-Approach. Kunde erlebt den Agent auf der Website live bevor er sich registriert. YouTube-Tutorials in lokaler Sprache. 7-Tage-Trial. Keine technischen Begriffe im Marketing ("Dein digitaler Mitarbeiter" statt "AI-Agent").

### R2: Churn (HOCH)

Westbalkan-KMU sind preissensitiv und kündigen schnell wenn der Wert unklar ist.

**Mitigation:**
- Onboarding-Agent stellt sicher: Aha-Moment in der ersten Woche
- Monatlicher Impact-Report per E-Mail: "Dein Agent hat 47 Anfragen bearbeitet = 6 Stunden gespart"
- Bei Kündigung: Automatisches Downgrade-Angebot (Starter-Paket für 25 EUR statt Kündigung)
- Win-Back-Flow: 30 Tage nach Kündigung automatische Nachricht mit neuem Feature/Angebot
- Churn-Annahme im Finanzmodell: 7%/Monat (konservativ für Emerging Market KMU-SaaS)

### R3: Zahlungsinfrastruktur BiH (MITTEL)

~25% der BiH-KMU-Inhaber haben keine Kreditkarte.

**Mitigation:** Stripe als Standard + Jahresabo per Banküberweisung als Fallback. Paddle als alternativer Payment Processor. Langfristig: Lokale d.o.o. mit Bankkonto für Direktüberweisungen.

### R4: Sprachpolitik (NIEDRIG aber KONSEQUENT)

Falsche Sprachbezeichnung kann Kunden in BiH abschrecken.

**Mitigation:** Regionen statt Sprachen. Neutrale Agent-Persona. Keine politisch aufgeladenen Begriffe. Siehe RESEARCH.md Abschnitt 8.

### R5: Technische Abhängigkeit von OpenClaw (MITTEL)

OpenClaw ist Open Source — aber breaking changes in neuen Versionen können Kunden-Agents breaken.

**Mitigation:** Version pinning. Eigene Test-Pipeline vor Upgrades. Ab Monat 6: Evaluierung alternativer Agent-Stacks (n8n + eigene LLM-Layer) als Notfallplan.

### R6: Denis' Verfügbarkeit (MITTEL)

Einziger Entscheidungsträger. Bei Krankheit/Urlaub: P1/P2-Eskalationen bleiben liegen.

**Mitigation:** Pre-defined Playbooks für alle P1/P2-Szenarien. CS Agent hat Entscheidungskompetenz für definierte Szenarien (z.B. kostenlose Verlängerung bei technischem Problem). Ziel: Denis ist ab Monat 6 für 2 Wochen am Stück abwesend, ohne dass Kunden es merken.

---

## 9. Compliance-Checkliste

### Vor Go-Live (Monat 1–2)

- [ ] Privacy Policy (BS/SR) auf Website und jeder Agent-Instanz
- [ ] DPA-Template für KMU-Kunden (Standardvertrag, Download auf Website)
- [ ] Cookie-Banner auf Web-Interfaces
- [ ] Hosting auf Hetzner DE (EU-Rechenzentrum)
- [ ] Datenpanne-Prozedur dokumentiert (72h Meldepflicht)

### Bei Scale (ab Monat 6)

- [ ] DPO benennen oder externen DPO beauftragen
- [ ] DPIA für AI-Entscheidungsfindung erstellen
- [ ] BiH: SCC-Prozess für EU-Datentransfer
- [ ] Serbien: Lokalen Datenschutz-Vertreter benennen

### Geschätzte Kosten

| Position | Einmalig | Recurring |
|----------|----------|-----------|
| Lokaler Anwalt (DPA, Privacy Policy, DPIA-Grundlage) | 1.200 EUR | — |
| Externer DPO (ab Scale) | — | 150–300 EUR/Monat |

---

## 10. Unternehmensstruktur

**Phase 1–2 (Monat 1–8):** Betrieb über bestehende DE/AT-Entität. Kein Grund für lokale Gründung. Stripe über DE, Kunden zahlen in EUR.

**Phase 3 (ab Monat 9, optional):** Lokale d.o.o. in BiH oder Serbien gründen wenn: (a) Banküberweisung für >20 Kunden nötig, (b) steuerliche Optimierung sinnvoll (BiH: 10% KSt vs. DE: ~30%), (c) lokale Geschäftsadresse für Vertrauen gewünscht.

---

## Anhang A: Erste-Schritte-Checkliste

### Monat 1 (Infrastruktur)

- [ ] Hetzner CX31 Server bestellen (12 EUR/Mo)
- [ ] OpenClaw self-hosted deployen
- [ ] Domain openclaw.ba + openclaw.rs registrieren
- [ ] Stripe Billing konfigurieren (Recurring Subscriptions)
- [ ] Facebook Business Manager: 2 Seiten aufsetzen
- [ ] Viber Business Account über Infobip beantragen
- [ ] Privacy Policy + DPA-Template beim Anwalt in Auftrag geben

### Monat 2 (Produkt)

- [ ] 3 Agent-Pakete fertig konfigurieren (Starter, Friseur, Restaurant)
- [ ] Website launchen mit Live-Demo
- [ ] YouTube-Kanal erstellen, erstes Demo-Video (Restaurant Use Case)
- [ ] 3 Pilot-Kunden identifizieren und ansprechen
- [ ] Interne Agenten (Sales, CS, Billing) konfigurieren

### Monat 3 (Go-Live)

- [ ] Pilot-Installationen durchführen
- [ ] Video-Testimonials aufnehmen
- [ ] Erste zahlende Kunden onboarden
- [ ] Billing-Flow End-to-End testen
- [ ] Facebook Ads vorbereiten (Creative + Targeting)

---

## Anhang B: Widersprüche aus v1.0 — aufgelöst

| Widerspruch (v1.0) | Lösung (v2.0) |
|--------------------|---------------|
| Preise über Research-Empfehlung (Restaurant 59 EUR vs. max. 40 EUR BiH) | Preise angepasst: Restaurant 49 EUR, Starter 25 EUR |
| "Zero Human" ab Tag 1 vs. "Denis entscheidet" | Realistischer Zeitplan: 25–30h/Woche in Monat 1–2, Ziel 5–8h ab Monat 7 |
| "3 Minuten live" (One-Click-Deploy) | Korrigiert zu "innerhalb von 24 Stunden aktiv" |
| "14-Tage-Trial ohne Kreditkarte" → niedrige Conversion | 7-Tage-Trial mit optionaler Karte, oder Freemium 50 Msg/Monat |
| Kein Viber trotz dominanter Nutzung | Viber ab Tag 1 in allen Paketen (ab Friseur/Beauty) |
| Kein P&L / keine Kostenstruktur | Siehe UNIT-ECONOMICS.md |
| "10 Kunden in Monat 1" | Phase 1 auf 3 Monate gestreckt, 10 Kunden = Monat-3-Ziel |
| Monat-12-Ziel 300 Kunden / 19.500 EUR MRR | Korrigiert zu 120 Kunden / 6.600 EUR MRR (realistisch) |

---

*Dokument: BLUEPRINT.md v2.0 | Alle Review-Punkte aus BLUEPRINT-REVIEW.md v1.0 adressiert.*
