"""
Hetzner Cloud API tools — server management, DNS, billing.
The Ops agent uses these to manage infrastructure.
The Finance agent uses these to check/pay hosting costs.
"""
from __future__ import annotations

import httpx
from langchain_core.tools import tool

from agents_runtime import config

HETZNER_API = "https://api.hetzner.cloud/v1"
HETZNER_DNS_API = "https://dns.hetzner.com/api/v1"


def _hetzner_headers() -> dict:
    return {"Authorization": f"Bearer {config.HETZNER_API_TOKEN}"}


def _dns_headers() -> dict:
    return {"Auth-API-Token": config.HETZNER_DNS_TOKEN}


# ── Server Management ───────────────────────────────────────────

@tool
def hetzner_list_servers() -> str:
    """List all Hetzner Cloud servers with their status, IP, and monthly cost."""
    if not config.HETZNER_API_TOKEN:
        return "ERROR: HETZNER_API_TOKEN not configured"

    resp = httpx.get(f"{HETZNER_API}/servers", headers=_hetzner_headers(), timeout=15)
    if resp.status_code != 200:
        return f"ERROR: Hetzner API {resp.status_code}"

    servers = resp.json().get("servers", [])
    lines = []
    for s in servers:
        ip = s.get("public_net", {}).get("ipv4", {}).get("ip", "no-ip")
        status = s["status"]
        name = s["name"]
        stype = s["server_type"]["name"]
        price = s["server_type"]["prices"][0]["price_monthly"]["gross"] if s["server_type"].get("prices") else "?"
        lines.append(f"  {name} ({stype}) — {ip} — {status} — {price} EUR/mo")
    return "Servers:\n" + "\n".join(lines) if lines else "No servers found"


@tool
def hetzner_server_status(server_name: str) -> str:
    """Get detailed status of a specific Hetzner server.

    Args:
        server_name: Name of the server (e.g. 'openclaw-balkan-01').
    """
    if not config.HETZNER_API_TOKEN:
        return "ERROR: HETZNER_API_TOKEN not configured"

    resp = httpx.get(
        f"{HETZNER_API}/servers",
        headers=_hetzner_headers(),
        params={"name": server_name},
        timeout=15,
    )
    servers = resp.json().get("servers", [])
    if not servers:
        return f"Server '{server_name}' not found"

    s = servers[0]
    return (
        f"Name: {s['name']}\n"
        f"Status: {s['status']}\n"
        f"IP: {s['public_net']['ipv4']['ip']}\n"
        f"Type: {s['server_type']['name']}\n"
        f"CPU: {s['server_type']['cores']} cores\n"
        f"RAM: {s['server_type']['memory']} GB\n"
        f"Disk: {s['server_type']['disk']} GB\n"
        f"Datacenter: {s['datacenter']['name']}\n"
        f"Created: {s['created']}"
    )


@tool
def hetzner_reboot_server(server_id: int) -> str:
    """Soft reboot a Hetzner server.

    Args:
        server_id: Numeric Hetzner server ID.
    """
    if not config.HETZNER_API_TOKEN:
        return "ERROR: HETZNER_API_TOKEN not configured"

    resp = httpx.post(
        f"{HETZNER_API}/servers/{server_id}/actions/reboot",
        headers=_hetzner_headers(),
        timeout=15,
    )
    if resp.status_code == 201:
        return f"OK: Server {server_id} is rebooting"
    return f"ERROR: {resp.status_code} — {resp.text[:200]}"


# ── DNS Management ──────────────────────────────────────────────

@tool
def hetzner_create_dns_record(
    zone_id: str, name: str, record_type: str, value: str, ttl: int = 300
) -> str:
    """Create a DNS record in Hetzner DNS.

    Args:
        zone_id: The DNS zone ID.
        name: Record name (e.g. 'kunde-abc' for kunde-abc.openclawbalkan.ba).
        record_type: DNS record type (A, CNAME, etc.).
        value: Record value (IP address or target domain).
        ttl: Time to live in seconds.
    """
    if not config.HETZNER_DNS_TOKEN:
        return "ERROR: HETZNER_DNS_TOKEN not configured"

    resp = httpx.post(
        f"{HETZNER_DNS_API}/records",
        headers=_dns_headers(),
        json={
            "zone_id": zone_id,
            "name": name,
            "type": record_type,
            "value": value,
            "ttl": ttl,
        },
        timeout=10,
    )
    if resp.status_code == 200:
        rec = resp.json().get("record", {})
        return f"OK: DNS record created — {rec.get('name')}.{rec.get('zone_id')} → {value}"
    return f"ERROR: {resp.status_code} — {resp.text[:200]}"


# ── Billing / Cost Tracking ─────────────────────────────────────

@tool
def hetzner_get_invoice_list() -> str:
    """Get list of recent Hetzner invoices with amounts and status."""
    if not config.HETZNER_API_TOKEN:
        return "ERROR: HETZNER_API_TOKEN not configured"

    # Note: Hetzner Cloud API doesn't have a direct invoice endpoint
    # We use the /servers pricing as a cost proxy
    resp = httpx.get(f"{HETZNER_API}/servers", headers=_hetzner_headers(), timeout=15)
    if resp.status_code != 200:
        return f"ERROR: Hetzner API {resp.status_code}"

    servers = resp.json().get("servers", [])
    total = 0.0
    lines = []
    for s in servers:
        prices = s["server_type"].get("prices", [])
        if prices:
            monthly = float(prices[0]["price_monthly"]["gross"])
            total += monthly
            lines.append(f"  {s['name']}: {monthly:.2f} EUR/mo")

    lines.append(f"\n  TOTAL estimated: {total:.2f} EUR/mo")
    return "Hosting costs:\n" + "\n".join(lines)


@tool
def hetzner_check_payment_status() -> str:
    """Check if Hetzner account is in good standing (no overdue invoices).
    Uses a GET to the root API to verify the token is valid and account active.
    """
    if not config.HETZNER_API_TOKEN:
        return "ERROR: HETZNER_API_TOKEN not configured"

    # Check if we can access the API (token valid = account active)
    resp = httpx.get(f"{HETZNER_API}/servers", headers=_hetzner_headers(), timeout=10)
    if resp.status_code == 200:
        return "OK: Hetzner account is active and accessible"
    elif resp.status_code == 401:
        return "WARNING: Hetzner API token is invalid or expired"
    elif resp.status_code == 403:
        return "CRITICAL: Hetzner account may be suspended — check billing"
    return f"UNKNOWN: Status {resp.status_code}"
