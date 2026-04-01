# OpenClaw Balkan — Research

> Version: 2.0 | Stand: 2026-03-30 | Status: Arbeitsresearch mit verifizierten Eckpunkten und offenen Punkten

## 1. Zweck

Dieses Dokument beantwortet nicht "Ist das Business sicher gut?", sondern:

- welche Marktannahmen sind brauchbar
- welche Blocker sind real
- was ist verifiziert
- was ist noch offen

## 2. Verifizierte Eckpunkte

### 2.1 Social und Distribution

**Bosnien-Herzegowina**
- Facebook hat laut NapoleonCat fuer Dezember 2025 rund `2.122.100` Nutzer in BiH
- das entspricht laut Quelle `61,5%` der Gesamtbevoelkerung

**Einordnung**
- Facebook ist fuer lokale KMU weiter relevant
- fuer Friseur, Restaurant, Beauty und lokale Services bleibt Facebook ein plausibler Primarkanal

**Quelle**
- NapoleonCat, Social media users in Bosnia and Herzegovina 2025:
  https://stats.napoleoncat.com/social-media-users-in-bosnia_and_herzegovina/2025/

### 2.2 Viber als realer Business-Kanal

Viber bietet verifizierte Business-Accounts, Business Inbox und Business Messaging. Das ist keine hypothetische Option, sondern ein realer Produktpfad.

**Wichtige Implikation**
- Viber darf im Balkan-Modell nicht als Randkanal behandelt werden
- fuer lokale KMU muss Viber mindestens als evaluierter Phase-1/2-Kanal eingeplant werden

**Quellen**
- Viber Help, Business accounts on Viber:
  https://help.viber.com/hc/en-us/articles/9755182032669-Business-accounts-on-Rakuten-Viber
- Viber for Business, Business Messages:
  https://www.forbusiness.viber.com/en/business-messages/

### 2.3 Stripe als lokaler Basis-Stack ungeeignet

Die offizielle Stripe-Seite zur globalen Verfuegbarkeit listet unterstuetzte Laender. Bosnien-Herzegowina und Serbien erscheinen dort nicht als lokal unterstuetzte Stripe-Business-Jurisdiktionen.

**Implikation**
- das Vorhaben darf nicht auf einem lokalen `Stripe-first`-Modell fuer BiH/Serbien aufbauen
- Rechnung, Banktransfer oder andere Strukturen muessen frueh eingeplant werden

**Quelle**
- Stripe global availability:
  https://stripe.com/global

### 2.4 Serbien: E-Invoicing ist real und relevant

Die serbischen offiziellen Stellen dokumentieren das elektronische Rechnungswesen ueber das System der elektronischen Rechnungen (`SEF`) seit 2022. Das betrifft direkt alle spaeteren Rechnungs-/Billing-Produkte fuer serbische B2B-Kunden.

**Implikation**
- Billing-/Invoice-Automation fuer Serbien ist kein Quick Win
- jede spaetere Rechnungsfunktion muss gegen SEF-Prozesse gedacht werden

**Quellen**
- Ministarstvo finansija, privater Sektor ab 1. Juli 2022 verpflichtet:
  https://mfin.gov.rs/sr/aktivnosti-1/privatni-sektor-od-sutra-obavezan-da-prima-i-uva-elektronske-fakture-1
- Elektronische Rechnungsregeln:
  https://www.efaktura.gov.rs/tekst/en/5683/electronic-invoicing-regulations.php
- Konsolidierte Gesetzesreferenz:
  https://www.mfin.gov.rs/sr/propisi-1/zakon-o-elektronskom-fakturisanju-1

## 3. Plausible, aber noch nicht final verifizierte Annahmen

Diese Punkte sind brauchbare Arbeitshypothesen, aber noch nicht abschliessend belegt:

- lokale KMU in BiH und Serbien sind fuer einfache AI-Assistenz offen, wenn der Nutzen klar und schnell sichtbar ist
- Friseur, Restaurant, Beauty und kleine Offices sind bessere Einstiegssegmente als komplexe Branchen
- BKS-Lokalisierung ist ein echter Vertrauensvorteil
- service-led onboarding wird bessere Conversion haben als Self-Serve

## 4. Kritische offene Fragen

### 4.1 OpenClaw-Partnerstatus

Nicht verifiziert:
- offizielles Partner- oder Reseller-Programm
- White-Label-Rechte
- erlaubte regionale Vermarktung
- Preisstruktur
- SLA / Supportbedingungen

Ohne diese Klaerung darf das Modell nicht als offizielles Reseller-Modell geplant werden.

### 4.2 Wettbewerb

Nicht ausreichend analysiert:
- lokale Agenturen in Bosnien
- lokale Agenturen in Serbien
- regionale WhatsApp-/Viber-/Bot-Anbieter
- bestehende CRM-/Automation-Angebote fuer KMU

Ohne Wettbewerbsbild bleibt jede Preispositionierung fragil.

### 4.3 Payment-Stack

Noch offen:
- welcher Zahlungsweg ist fuer BiH praktisch am besten
- wie hoch ist die Akzeptanz fuer Jahresvorauszahlung
- ob Serbien lokal sauber ueber Kartenmodell oder ebenfalls besser ueber Rechnung startet

### 4.4 Datenschutz / Compliance

Es gibt starke Hinweise auf relevante Datenschutzanforderungen, aber fuer belastbare Aussagen braucht es offizielle Primaerquellen bzw. juristische Prüfung pro Markt.

Fuer das operative Projekt heisst das:
- Start nur mit Low-Risk-Use-Cases
- keine sensiblen Kategorien im MVP
- keine aggressiven Compliance-Versprechen

## 5. Schlussfolgerungen fuer Produkt und Marktstart

### Was der Marktstart wahrscheinlich tragen kann

- FAQ-Agent
- Inbox-Agent
- Messaging-/Booking-Flow
- Lead Intake
- lokale Support- und Monatsreporting-Funktionen

### Was nicht als MVP taugt

- vollautomatisches White-Label-Agentur-OS
- serbische B2B-Rechnungsautomation
- Voice-Agenten als Kernangebot
- hochregulierte Datenverarbeitung
- Self-Serve-SaaS mit Vollautomatisierung

## 6. Empfohlene Research-Backlog

1. OpenClaw direkt kontaktieren und Partner-/Reseller-Status schriftlich klaeren
2. 10 lokale Wettbewerber in BiH/Serbien mit Preis, Angebot und Kanalen erfassen
3. Payment-Pfad fuer BiH und Serbien operativ definieren
4. Viber Business technisch und kommerziell evaluieren
5. juristische Minimum-Dokumente fuer Pilotkunden definieren
6. reale TAM/SAM/SOM fuer 3 Startsegmente abschaetzen

## 7. Arbeitsfazit

Der Markt ist nicht widerlegt. Aber das urspruengliche Modell war zu breit, zu optimistisch und zu stark von ungeklaerten Partner- und Payment-Annahmen abhaengig.

Die beste derzeitige Lesart ist:

- **Marktstart ja**
- **aber nur als enger, service-led MVP**
- **mit konservativem Billing**
- **mit Viber/WhatsApp/Facebook als Kommunikationskern**
- **und ohne unbestaetigte Partnerclaims**
