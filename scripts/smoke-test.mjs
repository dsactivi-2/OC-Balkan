// =============================================================================
// OpenClaw Balkan — Smoke Test
// Tests: health, leads API, orders API, static pages, validation
// Usage: node scripts/smoke-test.mjs
//   or:  BASE_URL=https://balkan.activi.io ADMIN_TOKEN=xxx node scripts/smoke-test.mjs
// =============================================================================

const baseUrl = process.env.BASE_URL || "http://127.0.0.1:4173";
const adminToken = process.env.ADMIN_TOKEN || "";

let passed = 0;
let failed = 0;

async function test(name, fn) {
  try {
    await fn();
    passed++;
    console.log(`  ✓ ${name}`);
  } catch (err) {
    failed++;
    console.error(`  ✗ ${name}: ${err.message}`);
  }
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

async function main() {
  console.log(`\nSmoke Test — ${baseUrl}\n`);

  // ── Health ──
  await test("GET /health returns ok", async () => {
    const r = await fetch(`${baseUrl}/health`);
    assert(r.ok, `status ${r.status}`);
    const j = await r.json();
    assert(j.ok === true, "ok !== true");
    assert(j.service === "openclaw-balkan", `service = ${j.service}`);
  });

  // ── Static Pages ──
  for (const page of ["/", "/ba.html", "/rs.html"]) {
    await test(`GET ${page} returns HTML`, async () => {
      const r = await fetch(`${baseUrl}${page}`);
      assert(r.ok, `status ${r.status}`);
      const ct = r.headers.get("content-type") || "";
      assert(ct.includes("text/html"), `content-type = ${ct}`);
    });
  }

  // ── Leads API ──
  await test("POST /api/leads creates lead", async () => {
    const r = await fetch(`${baseUrl}/api/leads`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: "Smoke Test",
        company: "Test d.o.o.",
        email: "smoke@example.com",
        phone: "+38763000000",
        segment: "office",
        message: "Automated smoke test.",
        page: "/ba.html",
        website: "",
      }),
    });
    assert(r.ok, `status ${r.status}`);
    const j = await r.json();
    assert(j.ok === true, "ok !== true");
    assert(j.id > 0, `id = ${j.id}`);
  });

  await test("POST /api/leads rejects honeypot", async () => {
    const r = await fetch(`${baseUrl}/api/leads`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: "Bot", company: "Bot Corp", email: "bot@spam.com",
        segment: "office", message: "spam",
        website: "http://spam.com",
      }),
    });
    assert(r.ok, "honeypot should silently succeed");
  });

  await test("POST /api/leads rejects missing fields", async () => {
    const r = await fetch(`${baseUrl}/api/leads`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: "Only Name" }),
    });
    assert(r.status === 400, `expected 400, got ${r.status}`);
  });

  await test("GET /api/leads requires auth", async () => {
    const r = await fetch(`${baseUrl}/api/leads`);
    assert(r.status === 401, `expected 401, got ${r.status}`);
  });

  // ── Orders API ──
  await test("POST /api/orders creates order", async () => {
    const r = await fetch(`${baseUrl}/api/orders`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: "Smoke Test Buyer",
        company: "Test Firma d.o.o.",
        email: "buyer@example.com",
        phone: "+38763111111",
        bundle: "solo",
        preferredChannel: "email",
        businessType: "freelancer",
        message: "Automated order smoke test",
        market: "ba",
        page: "/ba.html",
        website: "",
      }),
    });
    assert(r.ok, `status ${r.status}`);
    const j = await r.json();
    assert(j.ok === true, "ok !== true");
    assert(j.orderRef && j.orderRef.startsWith("OC-"), `orderRef = ${j.orderRef}`);
    assert(j.bundle === "Solo Agent", `bundle = ${j.bundle}`);
    assert(j.price === 25, `price = ${j.price}`);
  });

  await test("POST /api/orders rejects invalid bundle", async () => {
    const r = await fetch(`${baseUrl}/api/orders`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: "Test", company: "Test", email: "t@t.com", phone: "+1234",
        bundle: "nonexistent",
      }),
    });
    assert(r.status === 400, `expected 400, got ${r.status}`);
  });

  await test("POST /api/orders rejects invalid channel", async () => {
    const r = await fetch(`${baseUrl}/api/orders`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: "Test", company: "Test", email: "t@t.com", phone: "+1234",
        bundle: "solo", preferredChannel: "telegram",
      }),
    });
    assert(r.status === 400, `expected 400, got ${r.status}`);
  });

  await test("POST /api/orders rejects missing fields", async () => {
    const r = await fetch(`${baseUrl}/api/orders`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: "Only Name" }),
    });
    assert(r.status === 400, `expected 400, got ${r.status}`);
  });

  await test("GET /api/orders requires auth", async () => {
    const r = await fetch(`${baseUrl}/api/orders`);
    assert(r.status === 401, `expected 401, got ${r.status}`);
  });

  // ── All bundles valid ──
  for (const bundle of ["solo", "learning", "marketing", "research", "office"]) {
    await test(`POST /api/orders accepts bundle '${bundle}'`, async () => {
      const r = await fetch(`${baseUrl}/api/orders`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: `Test ${bundle}`,
          company: "Bundle Test d.o.o.",
          email: `${bundle}@example.com`,
          phone: "+38763222222",
          bundle,
          preferredChannel: "whatsapp",
          market: "rs",
          website: "",
        }),
      });
      assert(r.ok, `status ${r.status}`);
      const j = await r.json();
      assert(j.ok === true, "ok !== true");
      assert(j.orderRef.startsWith("OC-"), `orderRef invalid: ${j.orderRef}`);
    });
  }

  // ── Admin endpoints (if token provided) ──
  if (adminToken) {
    await test("GET /api/leads with admin token", async () => {
      const r = await fetch(`${baseUrl}/api/leads`, {
        headers: { "x-admin-token": adminToken },
      });
      assert(r.ok, `status ${r.status}`);
      const j = await r.json();
      assert(j.ok === true && Array.isArray(j.leads), "leads payload malformed");
    });

    await test("GET /api/orders with admin token", async () => {
      const r = await fetch(`${baseUrl}/api/orders`, {
        headers: { "x-admin-token": adminToken },
      });
      assert(r.ok, `status ${r.status}`);
      const j = await r.json();
      assert(j.ok === true && Array.isArray(j.orders), "orders payload malformed");
      assert(j.orders.length > 0, "no orders found (should have smoke test orders)");
    });

    await test("GET /api/orders/:ref returns order", async () => {
      // First get the list to find a ref
      const listR = await fetch(`${baseUrl}/api/orders`, {
        headers: { "x-admin-token": adminToken },
      });
      const listJ = await listR.json();
      const ref = listJ.orders[0]?.orderRef;
      assert(ref, "no order ref to test");

      const r = await fetch(`${baseUrl}/api/orders/${ref}`, {
        headers: { "x-admin-token": adminToken },
      });
      assert(r.ok, `status ${r.status}`);
      const j = await r.json();
      assert(j.ok === true && j.order.orderRef === ref, "order mismatch");
    });

    await test("GET /api/orders/:ref returns 404 for unknown", async () => {
      const r = await fetch(`${baseUrl}/api/orders/OC-999999-ZZZZZZ`, {
        headers: { "x-admin-token": adminToken },
      });
      assert(r.status === 404, `expected 404, got ${r.status}`);
    });
  } else {
    console.log("  - Skipping admin tests (no ADMIN_TOKEN)");
  }

  // ── Summary ──
  console.log(`\n${passed + failed} tests: ${passed} passed, ${failed} failed\n`);
  if (failed > 0) process.exit(1);
}

main().catch((err) => {
  console.error("Fatal:", err.message);
  process.exit(1);
});
