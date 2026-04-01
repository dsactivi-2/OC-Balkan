"""
FastAPI server — the HTTP interface for the agent graph.
Receives webhooks, handles multi-turn conversations via thread IDs.
"""
from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime

from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from langchain_core.messages import HumanMessage

from agents_runtime.graph import company_graph
from agents_runtime.memory import thread_id_for_customer, thread_id_for_task
from agents_runtime.scheduler import start_scheduler, stop_scheduler

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
logger = logging.getLogger("ava")


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
    version="2.0.0",
    lifespan=lifespan,
)

# ── Static Dashboard ──────────────────────────────────────────
STATIC_DIR = Path(__file__).parent / "static"
if STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/dashboard")
async def serve_dashboard():
    """Serve the AVA Command Center dashboard."""
    index = STATIC_DIR / "index.html"
    if index.exists():
        return FileResponse(str(index))
    raise HTTPException(404, "Dashboard not found")


# ── Models ──────────────────────────────────────────────────────
class InboundMessage(BaseModel):
    channel: str = "web"
    sender_id: str = ""
    sender_name: str = ""
    sender_phone: str = ""
    sender_email: str = ""
    text: str
    market: str = ""
    metadata: dict = {}


class OrderWebhook(BaseModel):
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
    event: str = "onboarding_start"
    orderRef: str
    bundleId: str
    customerName: str = ""
    company: str = ""
    email: str = ""
    phone: str = ""
    preferredChannel: str = ""
    market: str = ""


# ── Graph invocation ───────────────────────────────────────────
async def run_graph(
    message: str,
    thread_id: str = "",
    **extra_state,
) -> dict:
    """Invoke the company graph with persistent thread context."""
    initial_state = {
        "messages": [HumanMessage(content=message)],
        **extra_state,
    }

    # Config with thread_id for checkpointer (multi-turn memory)
    config = {}
    if thread_id:
        config = {"configurable": {"thread_id": thread_id}}

    try:
        result = await asyncio.to_thread(
            company_graph.invoke, initial_state, config
        )
        return {
            "ok": True,
            "thread_id": thread_id,
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
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/api/agents")
async def list_agents():
    """List all configured agents with their tools."""
    from agents_runtime.agents import TOOL_SETS, AGENT_MODELS, SOUL_NAMES
    from agents_runtime.memory import get_checkpointer
    agents = {}
    for name in TOOL_SETS:
        agents[name] = {
            "model": AGENT_MODELS.get(name, "default"),
            "soul": SOUL_NAMES.get(name, name),
            "tools": [t.name for t in TOOL_SETS[name]],
            "tool_count": len(TOOL_SETS[name]),
        }
    return {
        "ok": True,
        "agents": agents,
        "total_tools": sum(len(v) for v in TOOL_SETS.values()),
        "persistent_memory": get_checkpointer() is not None,
    }


@app.post("/api/message")
async def handle_message(msg: InboundMessage):
    """Handle an inbound customer message (multi-turn via sender_id)."""
    logger.info(f"Inbound [{msg.channel}] from {msg.sender_name or msg.sender_id}: {msg.text[:80]}")

    thread = thread_id_for_customer(
        msg.sender_id or msg.sender_email or msg.sender_phone,
        msg.channel,
    )

    return await run_graph(
        message=msg.text,
        thread_id=thread,
        customer_name=msg.sender_name,
        customer_email=msg.sender_email,
        customer_phone=msg.sender_phone,
        customer_channel=msg.channel,
        customer_market=msg.market,
    )


@app.post("/api/webhook/order")
async def handle_order_webhook(order: OrderWebhook):
    """Handle new order — routes to onboarding agent."""
    logger.info(f"New order: {order.orderRef} — {order.bundleName} for {order.customerName}")

    thread = thread_id_for_customer(order.email or order.phone, order.preferredChannel)

    message = (
        f"Neue Bestellung: {order.orderRef}\n"
        f"Kunde: {order.customerName} ({order.company})\n"
        f"Bundle: {order.bundleName} ({order.price} EUR)\n"
        f"Kanal: {order.preferredChannel} | Markt: {order.market}\n"
        f"Kontakt: {order.email} / {order.phone}\n\n"
        f"Bitte starte den Onboarding-Prozess."
    )

    return await run_graph(
        message=message,
        thread_id=thread,
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


@app.post("/api/webhook/onboarding")
async def handle_onboarding_webhook(data: OnboardingWebhook):
    """Handle onboarding trigger (5min after provisioning)."""
    logger.info(f"Onboarding trigger: {data.orderRef} for {data.customerName}")

    thread = thread_id_for_customer(data.email or data.phone, data.preferredChannel)

    message = (
        f"Provisioning abgeschlossen fuer {data.orderRef}.\n"
        f"Kunde: {data.customerName} ({data.company})\n"
        f"Bundle: {data.bundleId}\n"
        f"Kontaktiere den Kunden auf {data.preferredChannel} und fuehre das Onboarding durch."
    )

    return await run_graph(
        message=message,
        thread_id=thread,
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


@app.post("/api/webhook/viber")
async def handle_viber_webhook(request: Request):
    """Handle incoming Viber webhooks."""
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
    """Execute a scheduled task."""
    logger.info(f"Scheduled task: {task_name}")

    TASKS = {
        "billing_run": {
            "msg": "Es ist der 1. des Monats. Erstelle Rechnungen fuer alle aktiven Kunden und sende sie per Email. Pruefe auch die Hetzner-Hosting-Kosten.",
            "type": "scheduled_billing",
        },
        "marketing_post": {
            "msg": "Erstelle und veroeffentliche den naechsten Social-Media-Post gemaess Content-Kalender. Pruefe die Website-Analytics.",
            "type": "scheduled_marketing",
        },
        "ops_check": {
            "msg": "Fuehre einen vollstaendigen Infrastruktur-Check durch: Container-Status, Health-Endpoints, Disk, Memory, CPU, SSL.",
            "type": "scheduled_ops",
        },
        "daily_report": {
            "msg": "Erstelle den taeglichen Statusbericht: Neue Leads/Orders, System-Health, offene Probleme, Marketing-Metriken.",
            "type": "scheduled_report",
        },
        "payment_reminder": {
            "msg": "Pruefe offene Rechnungen. Sende Erinnerungen fuer Rechnungen aelter als 10 Tage.",
            "type": "scheduled_billing",
        },
    }

    task = TASKS.get(task_name)
    if not task:
        raise HTTPException(404, f"Unknown task: {task_name}")

    thread = thread_id_for_task(task_name)

    return await run_graph(
        message=task["msg"],
        thread_id=thread,
        task_type=task["type"],
    )


@app.post("/api/invoke/{agent_name}")
async def invoke_agent_directly(agent_name: str, msg: InboundMessage):
    """Bypass supervisor — invoke a specific agent (for testing)."""
    thread = thread_id_for_customer(
        msg.sender_id or msg.sender_email or "test",
        msg.channel,
    )
    # Force routing by setting next_agent
    return await run_graph(
        message=msg.text,
        thread_id=thread,
        next_agent=agent_name,
        customer_name=msg.sender_name,
        customer_email=msg.sender_email,
        customer_phone=msg.sender_phone,
        customer_channel=msg.channel,
    )
