"""
FastAPI server — the HTTP interface for the agent graph.
Receives webhooks from the Node.js app, Viber, scheduled tasks, etc.
"""
from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

from langchain_core.messages import HumanMessage

from agents_runtime.graph import company_graph
from agents_runtime.state import CompanyState
from agents_runtime.scheduler import start_scheduler, stop_scheduler

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
logger = logging.getLogger("ava")


# ── Lifespan (startup / shutdown) ──────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("AVA starting up — Zero-Human Company agent runtime")
    start_scheduler()
    yield
    logger.info("AVA shutting down")
    stop_scheduler()


app = FastAPI(
    title="OpenClaw Balkan — AVA Agent Runtime",
    description="Zero-Human Company powered by LangGraph",
    version="1.0.0",
    lifespan=lifespan,
)


# ── Models ──────────────────────────────────────────────────────
class InboundMessage(BaseModel):
    """Generic inbound message from any channel."""
    channel: str = "web"          # viber, whatsapp, email, web
    sender_id: str = ""           # channel-specific user ID
    sender_name: str = ""
    sender_phone: str = ""
    sender_email: str = ""
    text: str
    market: str = ""              # ba, rs
    metadata: dict = {}


class OrderWebhook(BaseModel):
    """Webhook from the Node.js app when a new order is placed."""
    event: str = "new_order"
    orderRef: str
    bundleId: str
    bundleName: str = ""
    price: float = 0
    customerName: str = ""
    company: str = ""
    email: str = ""
    phone: str = ""
    preferredChannel: str = "email"
    market: str = ""


class OnboardingWebhook(BaseModel):
    """Webhook triggered 5min after provisioning."""
    event: str = "onboarding_start"
    orderRef: str
    bundleId: str
    customerName: str = ""
    company: str = ""
    email: str = ""
    phone: str = ""
    preferredChannel: str = ""
    market: str = ""


class ScheduledTask(BaseModel):
    """Manual trigger for scheduled tasks."""
    task: str  # billing_run, marketing_post, ops_check, daily_report


# ── Helper: run the graph ──────────────────────────────────────
async def run_graph(message: str, **extra_state) -> dict:
    """Invoke the company graph with a message and optional state overrides."""
    initial_state = {
        "messages": [HumanMessage(content=message)],
        **extra_state,
    }
    try:
        result = await asyncio.to_thread(company_graph.invoke, initial_state)
        return {
            "ok": True,
            "agent": result.get("current_agent", ""),
            "response": result.get("final_response", ""),
            "actions": result.get("actions_taken", []),
        }
    except Exception as e:
        logger.error(f"Graph execution failed: {e}", exc_info=True)
        return {"ok": False, "error": str(e)}


# ── Endpoints ──────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {
        "ok": True,
        "service": "ava-agent-runtime",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/api/message")
async def handle_message(msg: InboundMessage):
    """Handle an inbound customer message from any channel."""
    logger.info(f"Inbound [{msg.channel}] from {msg.sender_name or msg.sender_id}: {msg.text[:80]}")

    result = await run_graph(
        message=msg.text,
        customer_name=msg.sender_name,
        customer_email=msg.sender_email,
        customer_phone=msg.sender_phone,
        customer_channel=msg.channel,
        customer_market=msg.market,
    )
    return result


@app.post("/api/webhook/order")
async def handle_order_webhook(order: OrderWebhook):
    """Handle new order webhook from the Node.js app."""
    logger.info(f"New order: {order.orderRef} — {order.bundleName} for {order.customerName}")

    message = (
        f"Neue Bestellung eingegangen: {order.orderRef}\n"
        f"Kunde: {order.customerName} ({order.company})\n"
        f"Bundle: {order.bundleName} ({order.price} EUR)\n"
        f"Kanal: {order.preferredChannel}\n"
        f"Markt: {order.market}\n"
        f"Kontakt: {order.email} / {order.phone}\n\n"
        f"Bitte Onboarding starten."
    )

    result = await run_graph(
        message=message,
        task_type="inbound_order",
        order_ref=order.orderRef,
        bundle_id=order.bundleId,
        bundle_name=order.bundleName,
        bundle_price=order.price,
        customer_name=order.customerName,
        customer_company=order.company,
        customer_email=order.email,
        customer_phone=order.phone,
        customer_channel=order.preferredChannel,
        customer_market=order.market,
    )
    return result


@app.post("/api/webhook/onboarding")
async def handle_onboarding_webhook(data: OnboardingWebhook):
    """Handle onboarding trigger (5min after provisioning)."""
    logger.info(f"Onboarding trigger: {data.orderRef} for {data.customerName}")

    message = (
        f"Provisioning abgeschlossen fuer {data.orderRef}.\n"
        f"Kunde: {data.customerName} ({data.company})\n"
        f"Bundle: {data.bundleId}\n"
        f"Bitte kontaktiere den Kunden auf {data.preferredChannel} "
        f"und fuehre das Onboarding durch."
    )

    result = await run_graph(
        message=message,
        task_type="inbound_order",
        order_ref=data.orderRef,
        bundle_id=data.bundleId,
        customer_name=data.customerName,
        customer_company=data.company,
        customer_email=data.email,
        customer_phone=data.phone,
        customer_channel=data.preferredChannel,
        customer_market=data.market,
    )
    return result


@app.post("/api/webhook/viber")
async def handle_viber_webhook(request: Request):
    """Handle incoming Viber webhook (messages from customers)."""
    body = await request.json()
    event = body.get("event", "")

    if event == "message":
        sender = body.get("sender", {})
        message_obj = body.get("message", {})

        msg = InboundMessage(
            channel="viber",
            sender_id=sender.get("id", ""),
            sender_name=sender.get("name", ""),
            text=message_obj.get("text", ""),
        )
        return await handle_message(msg)

    elif event == "webhook":
        return {"ok": True, "event": "webhook_verified"}

    return {"ok": True, "event": event, "handled": False}


@app.post("/api/scheduled/{task_name}")
async def handle_scheduled_task(task_name: str):
    """Execute a scheduled task by name."""
    logger.info(f"Scheduled task triggered: {task_name}")

    TASK_MESSAGES = {
        "billing_run": (
            "Es ist der 1. des Monats. Bitte erstelle Rechnungen fuer alle aktiven Kunden "
            "und sende sie per Email. Pruefe auch die Hosting-Kosten bei Hetzner."
        ),
        "marketing_post": (
            "Erstelle und veroeffentliche den naechsten Social-Media-Post "
            "gemaess dem Content-Kalender. Pruefe auch die Website-Analytics."
        ),
        "ops_check": (
            "Fuehre einen vollstaendigen Infrastruktur-Check durch: "
            "Container-Status, Health-Endpoints, Disk/Memory/CPU, SSL-Zertifikat."
        ),
        "daily_report": (
            "Erstelle den taeglichen Statusbericht: "
            "Neue Leads/Orders, System-Health, offene Probleme, Marketing-Metriken."
        ),
        "payment_reminder": (
            "Pruefe alle offenen Rechnungen. Sende Zahlungserinnerungen "
            "fuer Rechnungen die aelter als 10 Tage sind."
        ),
    }

    message = TASK_MESSAGES.get(task_name)
    if not message:
        raise HTTPException(404, f"Unknown task: {task_name}")

    task_type_map = {
        "billing_run": "scheduled_billing",
        "marketing_post": "scheduled_marketing",
        "ops_check": "scheduled_ops",
        "daily_report": "scheduled_report",
        "payment_reminder": "scheduled_billing",
    }

    result = await run_graph(
        message=message,
        task_type=task_type_map.get(task_name, "manual"),
    )
    return result


# ── Direct agent invocation (for testing) ──────────────────────
@app.post("/api/invoke/{agent_name}")
async def invoke_agent_directly(agent_name: str, msg: InboundMessage):
    """Bypass supervisor and invoke a specific agent directly (for testing)."""
    result = await run_graph(
        message=msg.text,
        next_agent=agent_name,
        customer_name=msg.sender_name,
        customer_email=msg.sender_email,
        customer_phone=msg.sender_phone,
        customer_channel=msg.channel,
    )
    return result
