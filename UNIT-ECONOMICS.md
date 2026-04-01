# OpenClaw Balkan — Unit Economics & P&L

> Version 1.0 | Stand: 2026-03-30 | Autor: Denis Selmanovic
> Basis: RESEARCH.md v2.0, BLUEPRINT.md v2.0

---

## 1. Kostenstruktur (Monatlich)

### 1.1 Fixkosten

| Position | Monat 1–3 | Monat 4–8 | Monat 9–12 | Anmerkung |
|----------|-----------|-----------|------------|-----------|
| Hetzner Server (CX31) | 12 EUR | 24 EUR | 48 EUR | Skaliert mit Kunden (1 Server / ~50 Agents) |
| LLM API (Claude/GPT) | 50 EUR | 200 EUR | 500 EUR | ~0,50–1,00 EUR/Kunde/Monat bei Ø 500 Msg |
| Viber Business API | 100 EUR | 100 EUR | 100 EUR | Minimum 100 EUR/Mo, Nachrichten separat |
| WhatsApp Business API | 50 EUR | 100 EUR | 200 EUR | Meta-Verifizierung + per-Message-Kosten |
| Domain + DNS | 5 EUR | 5 EUR | 5 EUR | openclaw.ba + openclaw.rs |
| Stripe-Gebühren (2,9% + 0,30) | 15 EUR | 100 EUR | 200 EUR | Prozentual am Umsatz |
| E-Mail-Service (Resend/Postmark) | 0 EUR | 20 EUR | 40 EUR | Transaktionale E-Mails |
| Monitoring (Uptime, Logs) | 0 EUR | 15 EUR | 25 EUR | Betterstack o.ä. |
| **Summe Fixkosten** | **232 EUR** | **564 EUR** | **1.118 EUR** | |

### 1.2 Variable Kosten pro Kunde

| Position | Kosten/Kunde/Monat | Anmerkung |
|----------|-------------------|-----------|
| LLM API (Nachrichten) | 0,50–1,50 EUR | Je nach Paket und Nachrichtenvolumen |
| Viber-Nachrichten | 0,10–0,30 EUR | ~0,0025 EUR/Msg × Ø 80 Msgs/Mo |
| WhatsApp-Nachrichten | 0,50–2,00 EUR | 0,05–0,08 EUR/Msg × Ø 30 Msgs/Mo |
| Stripe-Gebühren | ~1,50–3,00 EUR | 2,9% + 0,30 EUR pro Transaktion |
| Support (anteilig) | 0,50 EUR | Agent-basiert, fast null Grenzkosten |
| **Summe variable Kosten** | **3,10–7,30 EUR** | Ø **5 EUR/Kunde/Monat** |

### 1.3 Einmalige Kosten (Setup)

| Position | Betrag | Wann |
|----------|--------|------|
| Rechtliches (Anwalt: DPA, Privacy Policy, DPIA) | 1.200 EUR | Monat 1 |
| Website-Entwicklung | 500 EUR | Monat 1 (oder selbst gebaut) |
| Domain-Registrierung (.ba + .rs) | 50 EUR | Monat 1 |
| Erste Video-Produktion (3 Videos) | 200 EUR | Monat 2 (oder selbst gedreht) |
| **Summe Setup** | **1.950 EUR** | Einmalig |

---

## 2. Revenue-Modell

### 2.1 Paket-Mix Annahme (Jahr 1)

| Paket | Anteil | Preis/Mo | Beitrag zum MRR |
|-------|--------|---------|----------------|
| Starter (25 EUR) | 30% | 25 EUR | 7,50 EUR/Ø-Kunde |
| Friseur/Beauty (39 EUR) | 25% | 39 EUR | 9,75 EUR/Ø-Kunde |
| Restaurant (49 EUR) | 25% | 49 EUR | 12,25 EUR/Ø-Kunde |
| Webshop (79 EUR) | 10% | 79 EUR | 7,90 EUR/Ø-Kunde |
| Immobilien (99 EUR) | 5% | 99 EUR | 4,95 EUR/Ø-Kunde |
| Agentur (199 EUR) | 5% | 199 EUR | 9,95 EUR/Ø-Kunde |
| **Ø ARPU** | | | **52,30 EUR/Kunde** |

### 2.2 Add-on Revenue (geschätzt)

~15% der Kunden kaufen mindestens ein Add-on (Ø 12 EUR/Mo). Effektiver Ø ARPU inkl. Add-ons: **~55 EUR/Kunde/Monat**.

---

## 3. Marge pro Kunde

| Position | Betrag |
|----------|--------|
| Ø Revenue pro Kunde | 55 EUR |
| − Variable Kosten | −5 EUR |
| **= Deckungsbeitrag pro Kunde** | **50 EUR (91% Bruttomarge)** |

**Deckungsbeitrag 50 EUR/Kunde/Monat** — das ist eine sehr gesunde SaaS-Marge weil die variablen Kosten niedrig sind (LLM API + Messaging-Kosten sind die Haupttreiber).

---

## 4. Break-Even-Analyse

### 4.1 Monatlicher Break-Even

| Phase | Fixkosten/Mo | DB/Kunde | Break-Even bei X Kunden |
|-------|-------------|---------|------------------------|
| Monat 1–3 | 232 EUR | 50 EUR | **5 Kunden** |
| Monat 4–8 | 564 EUR + 300 EUR Ads = 864 EUR | 50 EUR | **18 Kunden** |
| Monat 9–12 | 1.118 EUR + 1.000 EUR Ads = 2.118 EUR | 50 EUR | **43 Kunden** |

### 4.2 Kumulierter Break-Even (inkl. Setup-Kosten)

Setup-Investition: 1.950 EUR

| Monat | Kunden (netto) | MRR | Kosten/Mo | Monats-P&L | Kumuliert |
|-------|---------------|-----|-----------|------------|-----------|
| 1 | 0 | 0 | 232 + 650* | −882 EUR | −2.832 EUR |
| 2 | 3 | 165 | 232 | −67 EUR | −2.899 EUR |
| 3 | 8 | 440 | 232 | +208 EUR | −2.691 EUR |
| 4 | 15 | 825 | 864 | −39 EUR | −2.730 EUR |
| 5 | 25 | 1.375 | 864 | +511 EUR | −2.219 EUR |
| 6 | 38 | 2.090 | 864 | +1.226 EUR | −993 EUR |
| 7 | 52 | 2.860 | 864 | +1.996 EUR | +1.003 EUR |
| 8 | 68 | 3.740 | 2.118 | +1.622 EUR | +2.625 EUR |
| 9 | 82 | 4.510 | 2.118 | +2.392 EUR | +5.017 EUR |
| 10 | 95 | 5.225 | 2.118 | +3.107 EUR | +8.124 EUR |
| 11 | 108 | 5.940 | 2.118 | +3.822 EUR | +11.946 EUR |
| 12 | 120 | 6.600 | 2.118 | +4.482 EUR | +16.428 EUR |

*Monat 1 inkl. 650 EUR anteilige Setup-Kosten (Rest der 1.950 EUR auf Monat 1–3 verteilt)*

**Kumulierter Break-Even: Monat 7** (ca. 52 Kunden)

**Jahresende (Monat 12):** 120 Kunden, 6.600 EUR MRR, 16.428 EUR kumulierter Gewinn.

---

## 5. Churn-Modell

### 5.1 Churn-Annahmen

| Szenario | Monatlicher Churn | Begründung |
|----------|------------------|------------|
| **Optimistisch** | 5% | Starkes Onboarding, schneller Aha-Moment |
| **Realistisch** | 7% | Typisch für KMU-SaaS in Emerging Markets |
| **Pessimistisch** | 12% | Hohe Preissensitivität, unklarer Wert |

### 5.2 Auswirkung auf Kundenzahl

Bei 15 Neukunden/Monat (ab Monat 4):

| Monat | Neukunden | Churn (7%) | Netto-Bestand |
|-------|-----------|-----------|---------------|
| 4 | 15 | 0,6 | 23 (+8 aus Phase 1) |
| 5 | 15 | 1,6 | 36 |
| 6 | 15 | 2,5 | 49 |
| 7 | 18 | 3,4 | 63 |
| 8 | 18 | 4,4 | 77 |
| 9 | 18 | 5,4 | 90 |
| 10 | 18 | 6,3 | 102 |
| 11 | 18 | 7,1 | 113 |
| 12 | 18 | 7,9 | 123 |

**Bei 7% Churn und 15–18 Neukunden/Monat: ~120 Kunden Ende Jahr 1.** Das passt zum Blueprint-Ziel.

### 5.3 Worst Case (12% Churn)

Bei 12% monatlichem Churn und gleicher Neukundenrate: nur ~85 Kunden Ende Jahr 1 (MRR: ~4.675 EUR). Immer noch profitabel (Break-Even bei 43 Kunden in Phase 3), aber deutlich langsamer.

### 5.4 Churn-Mitigations (im Blueprint beschrieben)

- Onboarding-Agent: Aha-Moment in Woche 1
- Monatlicher Impact-Report
- Downgrade statt Kündigung
- Win-Back-Flow nach 30 Tagen
- Jahresabo-Option (reduziert effektiven Churn)

---

## 6. Customer Acquisition Cost (CAC) & LTV

### 6.1 CAC nach Kanal

| Kanal | CAC | Begründung |
|-------|-----|------------|
| Persönliches Netzwerk | 0 EUR | Piloten, Empfehlungen |
| Facebook Ads | 80–120 EUR | Typisch für SaaS-Ads in Emerging Markets, konservativ |
| YouTube/Organic | 0–20 EUR | Kein direkter Ad-Spend, aber Zeitaufwand |
| Agentur-Multiplikator | 0 EUR pro Endkunde | Agentur zahlt Paket, Endkunden sind deren Problem |
| Referral/Affiliate | 30–50 EUR | 20% des ersten Monatsumsatzes als Provision |
| **Blended CAC** | **~60 EUR** | Gewichteter Durchschnitt über alle Kanäle |

### 6.2 Customer Lifetime Value (LTV)

| Parameter | Wert |
|-----------|------|
| Ø ARPU | 55 EUR/Monat |
| Ø Deckungsbeitrag | 50 EUR/Monat |
| Monatlicher Churn | 7% |
| Ø Lebensdauer | 1/0,07 = **14,3 Monate** |
| **LTV** | 50 × 14,3 = **714 EUR** |

### 6.3 LTV:CAC Ratio

| Metrik | Wert | Benchmark |
|--------|------|-----------|
| LTV | 714 EUR | — |
| Blended CAC | 60 EUR | — |
| **LTV:CAC** | **11,9x** | Gut (>3x ist gesund, >5x ist exzellent) |

### 6.4 CAC Payback Period

60 EUR CAC / 50 EUR DB pro Monat = **1,2 Monate** Payback.

Das bedeutet: Jeder Neukunde hat seine Akquisitionskosten nach ~5 Wochen eingespielt. Sehr gesund.

---

## 7. 12-Monats P&L Zusammenfassung

| Position | Jahr 1 (Summe) |
|----------|---------------|
| **Revenue** | |
| SaaS-Abos (MRR kumuliert) | ~36.000 EUR |
| Add-ons | ~3.000 EUR |
| Einmalige Services (Setup, Custom) | ~2.000 EUR |
| **Gesamt Revenue** | **~41.000 EUR** |
| | |
| **Kosten** | |
| Setup (einmalig) | −1.950 EUR |
| Fixkosten (Server, APIs, Domains) | −8.500 EUR |
| Facebook/Instagram Ads | −5.400 EUR |
| Variable Kosten (LLM, Messaging) | −4.200 EUR |
| Rechtskosten | −1.200 EUR |
| **Gesamt Kosten** | **~21.250 EUR** |
| | |
| **Netto-Ergebnis Jahr 1** | **~19.750 EUR** |
| **Netto-Marge** | **~48%** |

---

## 8. Sensitivitäts-Analyse

### Was passiert wenn...

| Szenario | Auswirkung auf MRR (Monat 12) | Auswirkung auf Jahres-P&L |
|----------|-------------------------------|--------------------------|
| Churn steigt auf 12% | 4.675 EUR (−29%) | ~12.500 EUR Gewinn |
| Ø ARPU sinkt auf 40 EUR | 4.800 EUR (−27%) | ~11.000 EUR Gewinn |
| CAC steigt auf 150 EUR | Kein MRR-Effekt | ~8.500 EUR Gewinn (Ads-Budget steigt) |
| Nur 8 Neukunden/Monat (statt 15–18) | 3.300 EUR (−50%) | ~6.000 EUR Gewinn |
| **Worst Case (alle negativ)** | **~2.000 EUR MRR** | **~Break-Even** |
| **Best Case** (5% Churn, Ø 65 EUR ARPU, 20 NK/Mo) | **10.400 EUR MRR** | **~30.000 EUR Gewinn** |

### Break-Even-Schwelle (absolutes Minimum)

Bei den geplanten Fixkosten + Ads: Minimum **43 zahlende Kunden** für Monatsprofitabilität in Phase 3. Das ist erreichbar bis Monat 6 in allen Szenarien außer dem absoluten Worst Case.

---

## 9. Jahr 2 Ausblick (Indikativ)

| Annahme | Wert |
|---------|------|
| Startbestand | 120 Kunden |
| Neukunden/Monat | 20–30 (Ads + Agenturen + Organic) |
| Churn/Monat | 5–7% (verbessert durch Erfahrung) |
| Ø ARPU | 60 EUR (Upsells, Add-ons) |
| **Kunden Ende Jahr 2** | **300–450** |
| **MRR Ende Jahr 2** | **18.000–27.000 EUR** |
| **ARR** | **216.000–324.000 EUR** |

Voraussetzung: Mindestens 3 aktive Agentur-Partner (liefern 30–75 Kunden ohne direkte Akquisekosten) und erhöhtes Ads-Budget (1.500–2.500 EUR/Monat).

---

## 10. Key Metrics Dashboard (monatlich tracken)

| Metrik | Zielwert (Monat 12) |
|--------|---------------------|
| MRR | >6.000 EUR |
| Aktive Kunden | >100 |
| Churn Rate | <8%/Monat |
| ARPU | >50 EUR |
| LTV:CAC | >5x |
| CAC Payback | <2 Monate |
| Agent-Resolution-Rate | >85% (ohne Denis-Eskalation) |
| Support-Eskalationen/Woche | <5 |
| NPS | >40 |

---

*Dokument: UNIT-ECONOMICS.md v1.0 | Konsistent mit BLUEPRINT.md v2.0 und RESEARCH.md v2.0*
