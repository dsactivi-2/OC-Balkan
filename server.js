import path from "node:path";
import { fileURLToPath } from "node:url";
import { exec } from "node:child_process";

import express from "express";

import { getDbPath, insertLead, listLeads, insertOrder, listOrders, getOrder, updateOrderStatus } from "./src/db.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const distDir = path.join(__dirname, "dist");

const app = express();
const host = process.env.HOST || "0.0.0.0";
const port = Number(process.env.PORT || 4173);
const adminToken = process.env.ADMIN_TOKEN || "";
const leadWebhookUrl = process.env.LEAD_WEBHOOK_URL || "";
const orderWebhookUrl = process.env.ORDER_WEBHOOK_URL || "";
const avaBaseUrl = process.env.AVA_BASE_URL || "http://ava:8000";
const provisionScript = process.env.PROVISION_SCRIPT || "";
const allowedOrigins = (process.env.ALLOWED_ORIGINS || "")
  .split(",")
  .map((origin) => origin.trim())
  .filter(Boolean);
const leadRateWindowMs = 15 * 60 * 1000;
const leadRateLimit = 10;
const leadBuckets = new Map();

const VALID_BUNDLES = {
  solo: { id: "solo_agent", name: "Solo Agent", price: 25 },
  learning: { id: "learning_buddy", name: "Learning Buddy", price: 29 },
  marketing: { id: "social_marketing_team", name: "Social Marketing Team", price: 39 },
  research: { id: "research_bundle", name: "Research Bundle", price: 49 },
  office: { id: "office_bundle", name: "Office Bundle", price: 79 },
};

const VALID_CHANNELS = ["whatsapp", "viber", "email"];

app.use(express.json({ limit: "1mb" }));
app.use(express.static(distDir));

function getClientIp(req) {
  const forwarded = req.headers["x-forwarded-for"];
  if (typeof forwarded === "string" && forwarded.trim()) {
    return forwarded.split(",")[0].trim();
  }
  return req.socket.remoteAddress || "unknown";
}

function isRateLimited(ip) {
  const now = Date.now();
  const bucket = leadBuckets.get(ip);
  if (!bucket || now - bucket.windowStart > leadRateWindowMs) {
    leadBuckets.set(ip, { count: 1, windowStart: now });
    return false;
  }
  if (bucket.count >= leadRateLimit) return true;
  bucket.count += 1;
  return false;
}

function isOriginAllowed(req) {
  if (allowedOrigins.length === 0) return true;
  const origin = req.headers.origin;
  if (typeof origin !== "string" || !origin.trim()) return true;
  return allowedOrigins.includes(origin);
}

async function forwardWebhook(url, payload) {
  if (!url) return;
  try {
    await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  } catch {
    // webhook failures are non-blocking
  }
}

function triggerProvision(orderRef, bundleId) {
  if (!provisionScript) {
    console.log(`[provision] No PROVISION_SCRIPT set, skipping for ${orderRef}`);
    return;
  }
  const safeRef = orderRef.replace(/[^A-Za-z0-9\-]/g, "");
  const safeBundle = bundleId.replace(/[^a-z_]/g, "");
  const cmd = `${provisionScript} "${safeRef}" "${safeBundle}"`;
  exec(cmd, { timeout: 120_000 }, (err, stdout, stderr) => {
    if (err) {
      console.error(`[provision] Error for ${orderRef}:`, stderr || err.message);
      return;
    }
    console.log(`[provision] Success for ${orderRef}:`, stdout.trim());
    try {
      updateOrderStatus(orderRef, "provisioned");
    } catch {
      console.error(`[provision] DB update failed for ${orderRef}`);
    }

    // Schedule onboarding trigger (5 minutes delay)
    scheduleOnboarding(orderRef, safeBundle);
  });
}

function scheduleOnboarding(orderRef, bundleId) {
  const onboardingWebhook = process.env.ONBOARDING_WEBHOOK_URL || "";
  if (!onboardingWebhook) {
    console.log(`[onboarding] No ONBOARDING_WEBHOOK_URL set, skipping for ${orderRef}`);
    return;
  }
  const delayMs = 5 * 60 * 1000; // 5 minutes
  console.log(`[onboarding] Scheduling onboarding for ${orderRef} in 5 minutes`);
  setTimeout(async () => {
    try {
      const order = getOrder(orderRef);
      if (!order) {
        console.error(`[onboarding] Order ${orderRef} not found`);
        return;
      }
      const payload = {
        event: "onboarding_start",
        orderRef,
        bundleId,
        customerName: order.name,
        company: order.company,
        email: order.email,
        phone: order.phone,
        preferredChannel: order.preferredChannel,
        market: order.market,
      };
      await fetch(onboardingWebhook, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      console.log(`[onboarding] Triggered for ${orderRef}`);
    } catch (err) {
      console.error(`[onboarding] Error for ${orderRef}:`, err.message);
    }
  }, delayMs);
}

// ── Health ──────────────────────────────────────────────────────

app.get("/health", (_req, res) => {
  res.json({ ok: true, service: "openclaw-balkan", dbPath: getDbPath() });
});

// ── Leads ───────────────────────────────────────────────────────

app.post("/api/leads", (req, res) => {
  (async () => {
    const payload = req.body || {};
    const ip = getClientIp(req);
    const required = ["name", "company", "email", "segment", "message"];
    const missing = required.filter((f) => !String(payload[f] || "").trim());

    if (!isOriginAllowed(req)) { res.status(403).json({ error: "Origin not allowed" }); return; }
    if (String(payload.website || "").trim()) { res.status(200).json({ ok: true }); return; }
    if (isRateLimited(ip)) { res.status(429).json({ error: "Too many requests" }); return; }
    if (missing.length > 0) { res.status(400).json({ error: "Missing required fields", missing }); return; }

    try {
      const leadPayload = { ...payload, createdAt: new Date().toISOString() };
      const id = insertLead(leadPayload);
      await forwardWebhook(leadWebhookUrl, { id, ...leadPayload });
      res.json({ ok: true, id });
    } catch {
      res.status(500).json({ error: "Failed to store lead" });
    }
  })();
});

app.get("/api/leads", (req, res) => {
  if (!adminToken || req.headers["x-admin-token"] !== adminToken) {
    res.status(401).json({ error: "Unauthorized" }); return;
  }
  try {
    res.json({ ok: true, dbPath: getDbPath(), leads: listLeads() });
  } catch {
    res.status(500).json({ error: "Failed to fetch leads" });
  }
});

// ── Orders ──────────────────────────────────────────────────────

app.post("/api/orders", (req, res) => {
  (async () => {
    const payload = req.body || {};
    const ip = getClientIp(req);

    if (!isOriginAllowed(req)) { res.status(403).json({ error: "Origin not allowed" }); return; }
    if (String(payload.website || "").trim()) { res.status(200).json({ ok: true }); return; }
    if (isRateLimited(ip)) { res.status(429).json({ error: "Too many requests" }); return; }

    const required = ["name", "company", "email", "phone", "bundle"];
    const missing = required.filter((f) => !String(payload[f] || "").trim());
    if (missing.length > 0) { res.status(400).json({ error: "Missing required fields", missing }); return; }

    const bundle = VALID_BUNDLES[payload.bundle];
    if (!bundle) { res.status(400).json({ error: "Invalid bundle", valid: Object.keys(VALID_BUNDLES) }); return; }

    const channel = payload.preferredChannel || "email";
    if (!VALID_CHANNELS.includes(channel)) { res.status(400).json({ error: "Invalid channel", valid: VALID_CHANNELS }); return; }

    try {
      const orderPayload = {
        name: payload.name,
        company: payload.company,
        email: payload.email,
        phone: payload.phone,
        bundleId: bundle.id,
        bundleName: bundle.name,
        bundlePrice: bundle.price,
        preferredChannel: channel,
        businessType: payload.businessType || null,
        message: payload.message || null,
        market: payload.market || "ba",
        page: payload.page || null,
        createdAt: new Date().toISOString(),
      };

      const { id, orderRef } = insertOrder(orderPayload);

      // Fire webhooks and provisioning asynchronously
      await forwardWebhook(orderWebhookUrl, { id, orderRef, ...orderPayload });
      triggerProvision(orderRef, bundle.id);

      // Notify AVA agent runtime about the new order
      forwardWebhook(`${avaBaseUrl}/api/webhook/order`, {
        event: "new_order",
        orderRef,
        bundleId: bundle.id,
        bundleName: bundle.name,
        price: bundle.price,
        customerName: orderPayload.name,
        company: orderPayload.company,
        email: orderPayload.email,
        phone: orderPayload.phone,
        preferredChannel: channel,
        market: orderPayload.market || "ba",
      });

      res.json({ ok: true, id, orderRef, bundle: bundle.name, price: bundle.price });
    } catch (err) {
      console.error("[orders] Error:", err);
      res.status(500).json({ error: "Failed to store order" });
    }
  })();
});

app.get("/api/orders", (req, res) => {
  if (!adminToken || req.headers["x-admin-token"] !== adminToken) {
    res.status(401).json({ error: "Unauthorized" }); return;
  }
  try {
    res.json({ ok: true, orders: listOrders() });
  } catch {
    res.status(500).json({ error: "Failed to fetch orders" });
  }
});

app.get("/api/orders/:ref", (req, res) => {
  if (!adminToken || req.headers["x-admin-token"] !== adminToken) {
    res.status(401).json({ error: "Unauthorized" }); return;
  }
  try {
    const order = getOrder(req.params.ref);
    if (!order) { res.status(404).json({ error: "Order not found" }); return; }
    res.json({ ok: true, order });
  } catch {
    res.status(500).json({ error: "Failed to fetch order" });
  }
});

// ── Static pages ────────────────────────────────────────────────

app.get("/", (_req, res) => { res.sendFile(path.join(distDir, "index.html")); });
app.get("/ba.html", (_req, res) => { res.sendFile(path.join(distDir, "ba.html")); });
app.get("/rs.html", (_req, res) => { res.sendFile(path.join(distDir, "rs.html")); });

app.listen(port, host, () => {
  console.log(`OpenClaw Balkan server listening on http://${host}:${port}`);
});
