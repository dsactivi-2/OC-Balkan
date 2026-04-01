import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import Database from "better-sqlite3";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, "..");
const dataDir = path.join(rootDir, "data");
const dbPath = path.join(dataDir, "openclaw-balkan.sqlite");

let db;

function getDb() {
  if (db) {
    return db;
  }

  fs.mkdirSync(dataDir, { recursive: true });
  db = new Database(dbPath);
  db.pragma("journal_mode = WAL");
  db.exec(`
    CREATE TABLE IF NOT EXISTS leads (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      company TEXT NOT NULL,
      email TEXT NOT NULL,
      phone TEXT,
      segment TEXT NOT NULL,
      message TEXT NOT NULL,
      page TEXT,
      created_at TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_leads_created_at ON leads(created_at DESC);
    CREATE INDEX IF NOT EXISTS idx_leads_segment ON leads(segment);
  `);

  return db;
}

export function insertLead(payload) {
  const stmt = getDb().prepare(`
    INSERT INTO leads (name, company, email, phone, segment, message, page, created_at)
    VALUES (@name, @company, @email, @phone, @segment, @message, @page, @created_at)
  `);

  const result = stmt.run({
    name: payload.name,
    company: payload.company,
    email: payload.email,
    phone: payload.phone || null,
    segment: payload.segment,
    message: payload.message,
    page: payload.page || null,
    created_at: payload.createdAt,
  });

  return result.lastInsertRowid;
}

export function listLeads(limit = 50) {
  return getDb()
    .prepare(`
      SELECT id, name, company, email, phone, segment, message, page, created_at AS createdAt
      FROM leads
      ORDER BY id DESC
      LIMIT ?
    `)
    .all(limit);
}

export function getDbPath() {
  getDb();
  return dbPath;
}
