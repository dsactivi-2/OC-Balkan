const baseUrl = process.env.BASE_URL || "http://127.0.0.1:4173";
const adminToken = process.env.ADMIN_TOKEN || "";

async function assertOk(name, response) {
  if (!response.ok) {
    const body = await response.text();
    throw new Error(`${name} failed: ${response.status} ${body}`);
  }
}

async function main() {
  const health = await fetch(`${baseUrl}/health`);
  await assertOk("health", health);

  const healthJson = await health.json();
  if (healthJson.ok !== true) {
    throw new Error("health payload missing ok=true");
  }

  const submit = await fetch(`${baseUrl}/api/leads`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      name: "Smoke Test",
      company: "OpenClaw Balkan",
      email: "smoke@example.com",
      phone: "+38763000000",
      segment: "office",
      message: "Smoke test submit.",
      page: "/ba.html",
      website: "",
    }),
  });
  await assertOk("submit", submit);

  const unauth = await fetch(`${baseUrl}/api/leads`);
  if (unauth.status !== 401) {
    throw new Error(`unauthorized leads check failed: expected 401, got ${unauth.status}`);
  }

  if (!adminToken) {
    console.log("smoke ok (without admin list check, ADMIN_TOKEN not provided)");
    return;
  }

  const authed = await fetch(`${baseUrl}/api/leads`, {
    headers: {
      "x-admin-token": adminToken,
    },
  });
  await assertOk("authorized leads", authed);

  const authedJson = await authed.json();
  if (!authedJson.ok || !Array.isArray(authedJson.leads)) {
    throw new Error("authorized leads payload malformed");
  }

  console.log("smoke ok");
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
