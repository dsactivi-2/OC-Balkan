# OpenClaw Balkan — Conservative P&L

> Version: 1.0 | Stand: 2026-03-30 | Status: Planungsmodell, keine verifizierte Ist-Kalkulation

## 1. Wichtiger Hinweis

Diese P&L ist **konservativ und modellhaft**.

Nicht final verifiziert:
- OpenClaw-Partnerkosten
- reale Kanalgebuehren je Markt und Kanal
- echte LLM-Kosten pro Kundenprofil
- juristische Fixkosten je Land

Die Tabelle ist deshalb eine **Steuerungsrechnung**, keine Finanzwahrheit.

## 2. Arbeitsannahmen

### Angebotsmix

- `Local Inbox`
  - ARPU: 29 EUR/Monat
- `Business Front Desk`
  - ARPU: 59 EUR/Monat

### Kundenmix im Basismodell

- 70% Local Inbox
- 30% Business Front Desk

### Gewichteter ARPU

`0.7 * 29 + 0.3 * 59 = 38 EUR`

Zur Vereinfachung rechnen wir mit:

- **Plan-ARPU: 39 EUR/Monat**

### Variable Kosten pro Kunde / Monat

Konservative Planannahme:

- LLM + Messaging + E-Mail + Infra-Anteil:
  - `8 EUR` pro aktivem Kunden / Monat

Das ist absichtlich nicht aggressiv optimiert.

### Fixkosten pro Monat

| Block | Annahme |
|---|---|
| Server / Basis-Infra | 25 EUR |
| Monitoring / Log / kleine Tools | 20 EUR |
| E-Mail / CRM / Ops | 15 EUR |
| Domain / Sonstiges umgelegt | 10 EUR |
| Content / kleine Softwarekosten | 30 EUR |
| Rechts-/Admin-Rueckstellung | 100 EUR |
| Akquise-Budget Minimum | 100 EUR |

**Gesamt Fixkosten:** `300 EUR / Monat`

## 3. Unit Economics

### Deckungsbeitrag pro Kunde

- Umsatz pro Kunde: `39 EUR`
- variable Kosten pro Kunde: `8 EUR`

**Deckungsbeitrag 1:** `31 EUR`

### Break-even

`300 / 31 = 9,68`

**Plan-Break-even:** rund `10 aktive Kunden`

## 4. Szenarien

| Szenario | Kunden | ARPU | Umsatz | Variable Kosten | Deckungsbeitrag | Fixkosten | Operativer Beitrag |
|---|---:|---:|---:|---:|---:|---:|---:|
| Pilot | 3 | 39 | 117 | 24 | 93 | 300 | -207 |
| Early | 10 | 39 | 390 | 80 | 310 | 300 | 10 |
| Stable | 25 | 39 | 975 | 200 | 775 | 300 | 475 |
| Growth | 50 | 39 | 1950 | 400 | 1550 | 300 | 1250 |

## 5. Reality Check

### Warum dieses Modell absichtlich vorsichtig ist

- kein aggressiver ARPU
- keine unrealistisch niedrigen Toolkosten
- keine versteckten "AI macht alles gratis"-Annahmen
- kein vollautomatischer Vertrieb eingepreist

### Was noch fehlt

- Founder-Zeit als echter Kostenfaktor
- Steuerlast
- Payment Fees
- Reisekosten / lokale Termine
- moegliche Support-Spitzen

## 6. Founder-Time als Schattenkosten

Wenn Denis in den ersten 2 Monaten stark eingebunden ist, sollte intern mit einem Schattenlohn gerechnet werden.

Beispiel:

- 40 Stunden/Monat
- interner Zielstundensatz: 35 EUR

**Schattenkosten:** `1.400 EUR / Monat`

Dann verschiebt sich der echte Break-even deutlich.

### Break-even inkl. Founder-Zeit

Fixkosten neu:

- `300 + 1400 = 1700 EUR`

`1700 / 31 = 54,8`

**Echter vollkostenbasierter Break-even:** rund `55 Kunden`

## 7. Schlussfolgerung daraus

Das Business ist in Phase 1 nicht mit dem Ziel "sofort profitabel fuer Vollkosten" zu fuehren.

Sondern mit dem Ziel:

- Produkt fit validieren
- Setup-Zeit drastisch senken
- Cases und Testimonials gewinnen
- variable Kosten kontrollieren

## 8. Hebel fuer bessere Economics

### Hebel 1

Setup Fee aktiv verlangen:

- `99-299 EUR` einmalig

Das verbessert Cashflow massiv.

### Hebel 2

Jahresvorauszahlung:

- 2 Monate Rabatt oder 10-15% Nachlass

Das senkt Churn und verbessert Liquiditaet.

### Hebel 3

Nur 2 Startangebote:

- weniger Support-Komplexitaet
- schnellere Onboardings
- bessere Wiederverwendbarkeit

### Hebel 4

Kundenwissen standardisieren:

- FAQ-Template
- Kanal-Template
- Report-Template

Das drueckt die laufenden Kosten.

## 9. Minimalziele fuer die ersten 60 Tage

1. 3 Piloten live
2. 2 zahlende Kunden
3. Setup Fee bei mindestens einem Kunden durchsetzen
4. durchschnittliche Setup-Zeit unter 3 Stunden
5. dokumentierte variable Kosten pro Kunde erheben

## 10. Fazit

Mit konservativen Annahmen ist ein operativer Deckungsbeitrag ab etwa `10 Kunden` plausibel.

Mit echter Founder-Zeit als Kostenblock ist das Modell erst deutlich spaeter wirtschaftlich.

Deshalb ist die richtige Reihenfolge:

1. validieren
2. standardisieren
3. automatisieren
4. dann skalieren
