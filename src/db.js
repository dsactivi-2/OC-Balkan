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

    CREATE TABLE IF NOT EXISTS orders (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      order_ref TEXT NOT NULL UNIQUE,
      name TEXT NOT NULL,
      company TEXT NOT NULL,
      email TEXT NOT NULL,
      phone TEXT,
      bundle_id TEXT NOT NULL,
      bundle_name TEXT NOT NULL,
      bundle_price INTEGER NOT NULL,
      preferred_channel TEXT NOT NULL DEFAULT 'email',
      business_type TEXT,
      message TEXT,
      status TEXT NOT NULL DEFAULT 'new',
      market TEXT NOT NULL DEFAULT 'ba',
      page TEXT,
      provisioned_at TEXT,
      created_at TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at DESC);
    CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
    CREATE INDEX IF NOT EXISTS idx_orders_bundle ON orders(bundle_id);
    CREATE INDEX IF NOT EXISTS idx_orders_ref ON orders(order_ref);
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

function generateOrderRef() {
  const now = new Date();
  const y = now.getFullYear().toString().slice(-2);
  const m = String(now.getMonth() + 1).padStart(2, "0");
  const d = String(now.getDate()).padStart(2, "0");
  const rand = Math.random().toString(36).slice(2, 8).toUpperCase();
  return `OC-${y}${m}${d}-${rand}`;
}

export function insertOrder(payload) {
  const orderRef = generateOrderRef();
  const stmt = getDb().prepare(`
    INSERT INTO orders (order_ref, name, company, email, phone, bundle_id, bundle_name, bundle_price, preferred_channel, business_type, message, status, market, page, created_at)
    VALUES (@order_ref, @name, @company, @email, @phone, @bundle_id, @bundle_name, @bundle_price, @preferred_channel, @business_type, @message, @status, @market, @page, @created_at)
  `);

  const result = stmt.run({
    order_ref: orderRef,
    name: payload.name,
    company: payload.company,
    email: payload.email,
    phone: payload.phone || null,
    bundle_id: payload.bundleId,
    bundle_name: payload.bundleName,
    bundle_price: payload.bundlePrice,
    preferred_channel: payload.preferredChannel || "email",
    business_type: payload.businessType || null,
    message: payload.message || null,
    status: "new",
    market: payload.market || "ba",
    page: payload.page || null,
    created_at: payload.createdAt,
  });

  return { id: result.lastInsertRowid, orderRef };
}

export function listOrders(limit = 50) {
  return getDb()
    .prepare(`
      SELECT id, order_ref AS orderRef, name, company, email, phone, bundle_id AS bundleId, bundle_name AS bundleName, bundle_price AS bundlePrice, preferred_channel AS preferredChannel, business_type AS businessType, message, status, market, page, provisioned_at AS provisionedAt, created_at AS createdAt
      FROM orders
      ORDER BY id DESC
      LIMIT ?
    `)
    .all(limit);
}

export function getOrder(orderRef) {
  return getDb()
    .prepare(`
      SELECT id, order_ref AS orderRef, name, company, email, phone, bundle_id AS bundleId, bundle_name AS bundleName, bundle_price AS bundlePrice, preferred_channel AS preferredChannel, business_type AS businessType, message, status, market, page, provisioned_at AS provisionedAt, created_at AS createdAt
      FROM orders
      WHERE order_ref = ?
    `)
    .get(orderRef);
}

export function updateOrderStatus(orderRef, status) {
  const updates = { status, order_ref: orderRef };
  if (status === "provisioned") {
    updates.provisioned_at = new Date().toISOString();
  }
  getDb()
    .prepare(`UPDATE orders SET status = @status${status === "provisioned" ? ", provisioned_at = @provisioned_at" : ""} WHERE order_ref = @order_ref`)
    .run(updates);
}

export function getDbPath() {
  getDb();
  return dbPath;
}
