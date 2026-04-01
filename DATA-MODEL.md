# OpenClaw Balkan — Data Model

> Version: 1.0 | Stand: 2026-03-30 | Zweck: MVP-Datenmodell fuer Multi-Tenant-Betrieb

## 1. Ziele

- klare Tenant-Trennung
- einfache Phase-1-Produkte
- Reporting und Monitoring von Anfang an
- spaetere Erweiterbarkeit ohne Totalumbau

## 2. Kernobjekte

### tenant

Ein Kunde oder Pilot.

Pflichtfelder:
- id
- name
- market
- language
- status
- package_type
- billing_mode
- created_at

### channel

Ein Kommunikationskanal pro Tenant.

Pflichtfelder:
- id
- tenant_id
- type
- status
- external_ref
- settings_json

`type`:
- messenger
- whatsapp
- viber
- webchat
- email

### faq_item

Kuratiertes Wissenselement fuer Standardfragen.

Pflichtfelder:
- id
- tenant_id
- question
- answer
- category
- active
- updated_at

### escalation_rule

Definiert, wann der Agent an einen Menschen uebergibt.

Pflichtfelder:
- id
- tenant_id
- trigger_type
- trigger_value
- destination
- active

### conversation_event

Jedes relevante Ereignis in einer Unterhaltung.

Pflichtfelder:
- id
- tenant_id
- channel_id
- conversation_key
- event_type
- payload_json
- created_at

`event_type`:
- inbound_message
- outbound_message
- escalation
- failure
- handoff

### lead

Erfasster Kontakt oder Anfrage.

Pflichtfelder:
- id
- tenant_id
- channel_id
- name
- phone
- email
- intent
- status
- source
- created_at

### monthly_report

Gespeicherter Snapshot fuer Reporting.

Pflichtfelder:
- id
- tenant_id
- report_month
- inbound_count
- answered_count
- escalation_count
- unresolved_count
- notes

### invoice

Sehr einfaches Billing-Objekt fuer Phase 1.

Pflichtfelder:
- id
- tenant_id
- invoice_number
- issue_date
- due_date
- currency
- amount_net
- amount_gross
- status

## 3. Tabellenbeziehungen

- `tenant 1:n channel`
- `tenant 1:n faq_item`
- `tenant 1:n escalation_rule`
- `tenant 1:n lead`
- `tenant 1:n monthly_report`
- `tenant 1:n invoice`
- `channel 1:n conversation_event`

## 4. PostgreSQL-Hinweise

### Pflicht

- Fremdschluessel sauber setzen
- Indizes auf `tenant_id`, `created_at`, `status`
- keine tenant-losen Daten

### Empfohlene Indizes

- `conversation_event (tenant_id, created_at desc)`
- `lead (tenant_id, status, created_at desc)`
- `faq_item (tenant_id, category, active)`
- `invoice (tenant_id, status, due_date)`

## 5. Retrieval / pgvector

`pgvector` ist nicht fuer alle Tabellen noetig.

Sinnvoll zuerst nur fuer:
- FAQ / Wissenschunks
- optionale tenant-spezifische Knowledge-Dokumente

### Tabelle knowledge_chunk

Pflichtfelder:
- id
- tenant_id
- source_type
- source_ref
- content
- embedding
- created_at

Regel:
- niemals tenant-uebergreifend suchen
- Retrieval immer erst nach `tenant_id` filtern

## 6. Monitoring-Daten

Mindestens erfassen:
- delivery failures
- escalation count
- unanswered intents
- time to first response
- onboarding completion

Optional eigene Tabelle:

### metric_snapshot

- id
- tenant_id
- metric_name
- metric_value
- snapshot_at

## 7. Phase-1-Verbote im Modell

- keine polymorphe Monster-Tabelle fuer alles
- keine globale Knowledge Base ohne Tenant-Grenze
- keine komplexe Billing-Engine im MVP
- keine zu fruehe Event-Sourcing-Komplettarchitektur

## 8. Beispiel fuer spaetere Erweiterung

Spaeter moeglich:
- CRM sync table
- campaign table
- voice_session table
- subscription table

Aber erst, wenn die Phase-1-Kernobjekte stabil sind.
