"""
Finance tools — invoicing, payment tracking, cost calculation.
Used by the Billing/Finance agent.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta

import httpx
from langchain_core.tools import tool

from agents_runtime import config


# ── Invoice Generation ──────────────────────────────────────────

@tool
def generate_invoice(
    customer_name: str,
    customer_company: str,
    customer_email: str,
    bundle_name: str,
    amount_eur: float,
    invoice_number: str = "",
    period: str = "",
) -> str:
    """Generate an invoice record and return invoice details as JSON.

    Args:
        customer_name: Full name of the customer.
        customer_company: Company name.
        customer_email: Email for sending the invoice.
        bundle_name: Name of the subscribed bundle.
        amount_eur: Amount in EUR (incl. VAT if applicable).
        invoice_number: Custom invoice number (auto-generated if empty).
        period: Billing period (e.g. '2026-04' for April 2026).
    """
    if not invoice_number:
        now = datetime.utcnow()
        invoice_number = f"INV-{now.strftime('%Y%m%d')}-{abs(hash(customer_email)) % 10000:04d}"

    if not period:
        period = datetime.utcnow().strftime("%Y-%m")

    invoice = {
        "invoice_number": invoice_number,
        "date": datetime.utcnow().isoformat(),
        "period": period,
        "customer_name": customer_name,
        "customer_company": customer_company,
        "customer_email": customer_email,
        "items": [
            {
                "description": f"{bundle_name} — Monatliches Abonnement ({period})",
                "quantity": 1,
                "unit_price_eur": amount_eur,
                "total_eur": amount_eur,
            }
        ],
        "subtotal_eur": amount_eur,
        "vat_rate": 0.17,  # 17% VAT in Bosnia
        "vat_eur": round(amount_eur * 0.17, 2),
        "total_eur": round(amount_eur * 1.17, 2),
        "payment_details": {
            "bank_name": config.BANK_NAME,
            "iban": config.BANK_IBAN,
            "bic": config.BANK_BIC,
            "reference": invoice_number,
        },
        "status": "draft",
    }

    return json.dumps(invoice, indent=2, ensure_ascii=False)


@tool
def calculate_monthly_costs() -> str:
    """Calculate total monthly operating costs for OpenClaw Balkan.
    Includes hosting, LLM API costs, and service fees.
    """
    costs = {
        "hetzner_server_cx31": 11.97,       # CX31 monthly
        "domain_activi_io": 0.0,             # included in existing domain
        "litellm_api_estimate": 15.0,        # estimated LLM API costs
        "viber_business_api": 0.0,           # free for PA messages
        "whatsapp_business_api": 5.0,        # estimated per-message costs
        "smtp_email": 0.0,                   # self-hosted
        "total_fixed": 0.0,
        "total_variable_estimate": 0.0,
    }

    fixed = costs["hetzner_server_cx31"] + costs["domain_activi_io"]
    variable = costs["litellm_api_estimate"] + costs["whatsapp_business_api"]
    costs["total_fixed"] = round(fixed, 2)
    costs["total_variable_estimate"] = round(variable, 2)
    costs["total_estimate"] = round(fixed + variable, 2)

    return json.dumps(costs, indent=2)


@tool
def calculate_revenue_forecast(active_customers: int, bundle_mix: dict[str, int]) -> str:
    """Calculate monthly revenue based on active customers and bundle distribution.

    Args:
        active_customers: Total number of active paying customers.
        bundle_mix: Dict mapping bundle name to count, e.g. {'solo': 3, 'learning': 2}.
    """
    PRICES = {
        "solo": 25.0,
        "learning": 29.0,
        "marketing": 39.0,
        "research": 49.0,
        "office": 79.0,
    }

    revenue = 0.0
    breakdown = []
    for bundle, count in bundle_mix.items():
        price = PRICES.get(bundle, 0)
        sub = price * count
        revenue += sub
        breakdown.append(f"  {bundle}: {count} x {price:.0f} EUR = {sub:.0f} EUR")

    return (
        f"Revenue forecast:\n"
        + "\n".join(breakdown)
        + f"\n\n  TOTAL MRR: {revenue:.0f} EUR/mo"
        + f"\n  Active customers: {active_customers}"
    )


# ── Payment Tracking ────────────────────────────────────────────

@tool
def check_stripe_balance() -> str:
    """Check current Stripe account balance."""
    if not config.STRIPE_SECRET_KEY:
        return "ERROR: STRIPE_SECRET_KEY not configured — no payment processing active"

    try:
        resp = httpx.get(
            "https://api.stripe.com/v1/balance",
            headers={"Authorization": f"Bearer {config.STRIPE_SECRET_KEY}"},
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            available = data.get("available", [{}])
            pending = data.get("pending", [{}])
            return (
                f"Stripe Balance:\n"
                f"  Available: {available[0].get('amount', 0) / 100:.2f} {available[0].get('currency', 'eur').upper()}\n"
                f"  Pending: {pending[0].get('amount', 0) / 100:.2f} {pending[0].get('currency', 'eur').upper()}"
            )
        return f"ERROR: Stripe API {resp.status_code}"
    except Exception as e:
        return f"ERROR: {e}"


@tool
def list_overdue_customers() -> str:
    """List customers with overdue payments (placeholder — reads from local DB).
    In production this would query the billing database.
    """
    # Placeholder: in production, query PostgreSQL billing table
    return (
        "Overdue customers: (checking billing database...)\n"
        "Note: Full billing DB integration pending. "
        "Currently tracking orders in SQLite at /app/data/openclaw-balkan.sqlite"
    )
