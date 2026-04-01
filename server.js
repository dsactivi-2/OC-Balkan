import path from "node:path";
import { fileURLToPath } from "node:url";

import express from "express";

import { getDbPath, insertLead, listLeads } from "./src/db.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const distDir = path.join(__dirname, "dist");

const app = express();
const host = process.env.HOST || "0.0.0.0";
const port = Number(process.env.PORT || 4173);
const adminToken = process.env.ADMIN_TOKEN || "";
const leadWebhookUrl = process.env.LEAD_WEBHOOK_URL || "";
const allowedOrigins = (process.env.ALLOWED_ORIGINS || "")
  .split(",")
  .map((origin) => origin.trim())
  .filter(Boolean);
const leadRateWindowMs = 15 * 60 * 1000;
const leadRateLimit = 10;
const leadBuckets = new Map();

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

  if (bucket.count >= leadRateLimit) {
    return true;
  }

  bucket.count += 1;
  return false;
}

function isOriginAllowed(req) {
  if (allowedOrigins.length === 0) {
    return true;
  }

  const origin = req.headers.origin;
  if (typeof origin !== "string" || !origin.trim()) {
    return true;
  }

  return allowedOrigins.includes(origin);
}

async function forwardLead(payload) {
  if (!leadWebhookUrl) {
    return;
  }

  await fetch(leadWebhookUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}

app.get("/health", (_req, res) => {
  res.json({
    ok: true,
    service: "openclaw-balkan",
    dbPath: getDbPath(),
  });
});

app.post("/api/leads", (req, res) => {
  (async () => {
  const payload = req.body || {};
  const ip = getClientIp(req);
  const required = ["name", "company", "email", "segment", "message"];
  const missing = required.filter((field) => !String(payload[field] || "").trim());

  if (!isOriginAllowed(req)) {
    res.status(403).json({ error: "Origin not allowed" });
    return;
  }

  if (String(payload.website || "").trim()) {
    res.status(200).json({ ok: true });
    return;
  }

  if (isRateLimited(ip)) {
    res.status(429).json({ error: "Too many requests" });
    return;
  }

  if (missing.length > 0) {
    res.status(400).json({ error: "Missing required fields", missing });
    return;
  }

  try {
    const leadPayload = {
      ...payload,
      createdAt: new Date().toISOString(),
    };

    const id = insertLead({
      ...leadPayload,
    });

    try {
      await forwardLead({ id, ...leadPayload });
    } catch {
      // Intentionally do not fail the primary write path if webhook forwarding fails.
    }

    res.json({ ok: true, id });
  } catch {
    res.status(500).json({ error: "Failed to store lead" });
  }
  })();
});

app.get("/api/leads", (req, res) => {
  if (!adminToken || req.headers["x-admin-token"] !== adminToken) {
    res.status(401).json({ error: "Unauthorized" });
    return;
  }

  try {
    res.json({
      ok: true,
      dbPath: getDbPath(),
      leads: listLeads(),
    });
  } catch {
    res.status(500).json({ error: "Failed to fetch leads" });
  }
});

app.get("/", (_req, res) => {
  res.sendFile(path.join(distDir, "index.html"));
});

app.get("/ba.html", (_req, res) => {
  res.sendFile(path.join(distDir, "ba.html"));
});

app.get("/rs.html", (_req, res) => {
  res.sendFile(path.join(distDir, "rs.html"));
});

app.listen(port, host, () => {
  console.log(`OpenClaw Balkan server listening on http://${host}:${port}`);
});
