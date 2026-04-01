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


# ══════════════════════════════════════════════════════════════════
# ── Admin Panel APIs ─────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════

import json
import os
import shutil
import uuid
from typing import Optional

SOULS_DIR = Path(__file__).parent / "souls"
TOOLS_DIR = Path(__file__).parent / "tools"
RUNTIME_DIR = Path(__file__).parent

# Store chat history in memory (backed by checkpointer for persistence)
_chat_sessions: dict[str, list[dict]] = {}
# Store logs in memory ring buffer
_log_buffer: list[dict] = []
MAX_LOG_ENTRIES = 500


def _add_log(level: str, source: str, message: str):
    """Add to in-memory log buffer."""
    entry = {
        "ts": datetime.utcnow().isoformat(),
        "level": level,
        "source": source,
        "message": message,
    }
    _log_buffer.append(entry)
    if len(_log_buffer) > MAX_LOG_ENTRIES:
        _log_buffer.pop(0)


# ── 1. Soul MD Files — Read & Write ─────────────────────────────

@app.get("/api/admin/souls")
async def list_souls():
    """List all SOUL.md files."""
    souls = {}
    for f in sorted(SOULS_DIR.glob("*.md")):
        souls[f.stem] = {
            "filename": f.name,
            "size": f.stat().st_size,
            "preview": f.read_text(encoding="utf-8")[:200],
        }
    return {"ok": True, "souls": souls}


@app.get("/api/admin/souls/{name}")
async def get_soul(name: str):
    """Read a SOUL.md file."""
    path = SOULS_DIR / f"{name}.md"
    if not path.exists():
        raise HTTPException(404, f"Soul not found: {name}")
    return {"ok": True, "name": name, "content": path.read_text(encoding="utf-8")}


class SoulUpdate(BaseModel):
    content: str

@app.put("/api/admin/souls/{name}")
async def update_soul(name: str, body: SoulUpdate):
    """Update a SOUL.md file."""
    path = SOULS_DIR / f"{name}.md"
    if not path.exists():
        raise HTTPException(404, f"Soul not found: {name}")
    # Backup
    backup = SOULS_DIR / f"{name}.md.bak"
    shutil.copy2(path, backup)
    path.write_text(body.content, encoding="utf-8")
    _add_log("INFO", "admin", f"Soul updated: {name}.md ({len(body.content)} chars)")
    return {"ok": True, "name": name, "size": len(body.content)}


@app.post("/api/admin/souls/{name}")
async def create_soul(name: str, body: SoulUpdate):
    """Create a new SOUL.md file."""
    path = SOULS_DIR / f"{name}.md"
    if path.exists():
        raise HTTPException(409, f"Soul already exists: {name}")
    path.write_text(body.content, encoding="utf-8")
    _add_log("INFO", "admin", f"Soul created: {name}.md")
    return {"ok": True, "name": name, "created": True}


# ── 2. Agent Configuration ───────────────────────────────────────

@app.get("/api/admin/agents/config")
async def get_agents_config():
    """Full agent config: models, tools, souls."""
    from agents_runtime.agents import TOOL_SETS, AGENT_MODELS, SOUL_NAMES
    from agents_runtime.config import MODEL_SMART, MODEL_FAST, MODEL_LOCAL
    agents = {}
    for name in TOOL_SETS:
        soul_path = SOULS_DIR / f"{name.replace('_agent', '')}.md"
        agents[name] = {
            "model": AGENT_MODELS.get(name, MODEL_SMART),
            "soul_name": SOUL_NAMES.get(name, name),
            "soul_file": soul_path.name if soul_path.exists() else None,
            "tools": [t.name for t in TOOL_SETS[name]],
            "tool_count": len(TOOL_SETS[name]),
        }
    return {
        "ok": True,
        "agents": agents,
        "available_models": {
            "smart": MODEL_SMART,
            "fast": MODEL_FAST,
            "local": MODEL_LOCAL,
        },
    }


class AgentCloneRequest(BaseModel):
    source_agent: str
    new_name: str
    new_soul_content: Optional[str] = None
    model: Optional[str] = None

@app.post("/api/admin/agents/clone")
async def clone_agent(req: AgentCloneRequest):
    """Clone an agent's soul file (runtime tool assignment needs restart)."""
    source_soul = req.source_agent.replace("_agent", "")
    source_path = SOULS_DIR / f"{source_soul}.md"
    if not source_path.exists():
        raise HTTPException(404, f"Source soul not found: {source_soul}")

    new_soul = req.new_name.replace("_agent", "")
    new_path = SOULS_DIR / f"{new_soul}.md"
    if new_path.exists():
        raise HTTPException(409, f"Soul already exists: {new_soul}")

    content = req.new_soul_content or source_path.read_text(encoding="utf-8")
    new_path.write_text(content, encoding="utf-8")

    _add_log("INFO", "admin", f"Agent cloned: {source_soul} → {new_soul}")
    return {
        "ok": True,
        "cloned_from": source_soul,
        "new_agent": new_soul,
        "note": "Soul file created. Add to TOOL_SETS in agents.py and restart to activate.",
    }


# ── 3. Chat History ──────────────────────────────────────────────

@app.get("/api/admin/chats")
async def list_chats():
    """List all chat sessions."""
    sessions = []
    for sid, msgs in _chat_sessions.items():
        sessions.append({
            "session_id": sid,
            "message_count": len(msgs),
            "last_message": msgs[-1] if msgs else None,
        })
    return {"ok": True, "sessions": sessions}


@app.get("/api/admin/chats/{session_id}")
async def get_chat(session_id: str):
    """Get messages for a chat session."""
    msgs = _chat_sessions.get(session_id, [])
    return {"ok": True, "session_id": session_id, "messages": msgs}


@app.post("/api/admin/chat")
async def admin_chat(request: Request):
    """Admin chat — stores history, returns response."""
    body = await request.json()
    text = body.get("text", "")
    session_id = body.get("session_id", str(uuid.uuid4())[:12])
    agent = body.get("agent", "auto")
    channel = body.get("channel", "web")

    if not text.strip():
        raise HTTPException(400, "Empty message")

    # Store user message
    if session_id not in _chat_sessions:
        _chat_sessions[session_id] = []

    _chat_sessions[session_id].append({
        "role": "user",
        "text": text,
        "ts": datetime.utcnow().isoformat(),
        "agent": agent,
    })

    _add_log("INFO", "chat", f"[{session_id}] User: {text[:80]}")

    # Build graph call
    extra = {"customer_channel": channel}
    if agent != "auto":
        extra["next_agent"] = agent

    thread = f"admin-{session_id}"
    result = await run_graph(message=text, thread_id=thread, **extra)

    response_text = result.get("response", result.get("error", "Keine Antwort"))
    responding_agent = result.get("agent", agent)

    # Store assistant message
    _chat_sessions[session_id].append({
        "role": "assistant",
        "text": response_text,
        "ts": datetime.utcnow().isoformat(),
        "agent": responding_agent,
        "actions": result.get("actions", []),
    })

    _add_log("INFO", "chat", f"[{session_id}] {responding_agent}: {response_text[:80]}")

    return {
        "ok": result.get("ok", False),
        "session_id": session_id,
        "agent": responding_agent,
        "response": response_text,
        "actions": result.get("actions", []),
    }


# ── 4. Logs ──────────────────────────────────────────────────────

@app.get("/api/admin/logs")
async def get_logs(limit: int = 100, level: str = ""):
    """Get recent log entries."""
    logs = _log_buffer[-limit:]
    if level:
        logs = [l for l in logs if l["level"].upper() == level.upper()]
    return {"ok": True, "count": len(logs), "logs": logs}


# ── 5. Config / Settings ─────────────────────────────────────────

@app.get("/api/admin/config")
async def get_config():
    """Get current configuration (redacted secrets)."""
    from agents_runtime import config as cfg

    def _redact(val: str) -> str:
        if not val or len(val) < 8:
            return "***" if val else ""
        return val[:4] + "..." + val[-4:]

    return {
        "ok": True,
        "config": {
            "models": {
                "MODEL_SMART": cfg.MODEL_SMART,
                "MODEL_FAST": cfg.MODEL_FAST,
                "MODEL_LOCAL": cfg.MODEL_LOCAL,
            },
            "credentials": {
                "ANTHROPIC_API_KEY": _redact(cfg.ANTHROPIC_API_KEY),
                "VIBER_AUTH_TOKEN": _redact(cfg.VIBER_AUTH_TOKEN),
                "WHATSAPP_API_TOKEN": _redact(cfg.WHATSAPP_API_TOKEN),
                "HETZNER_API_TOKEN": _redact(cfg.HETZNER_API_TOKEN),
                "STRIPE_SECRET_KEY": _redact(cfg.STRIPE_SECRET_KEY),
                "FACEBOOK_PAGE_TOKEN": _redact(cfg.FACEBOOK_PAGE_TOKEN),
                "INSTAGRAM_ACCESS_TOKEN": _redact(cfg.INSTAGRAM_ACCESS_TOKEN),
            },
            "services": {
                "WEBSITE_BASE_URL": cfg.WEBSITE_BASE_URL,
                "OPENCLAW_PLATFORM_URL": cfg.OPENCLAW_PLATFORM_URL,
                "N8N_BASE_URL": cfg.N8N_BASE_URL,
                "POSTGRES_URL": _redact(cfg.POSTGRES_URL),
                "LITELLM_BASE_URL": cfg.LITELLM_BASE_URL,
            },
            "smtp": {
                "SMTP_HOST": cfg.SMTP_HOST,
                "SMTP_PORT": cfg.SMTP_PORT,
                "SMTP_FROM": cfg.SMTP_FROM,
                "SMTP_USER": _redact(cfg.SMTP_USER),
            },
            "admin": {
                "ADMIN_EMAIL": cfg.ADMIN_EMAIL,
                "SERVER_IP": cfg.SERVER_IP,
            },
        },
    }


# ── 6. File Upload ───────────────────────────────────────────────

from fastapi import UploadFile, File

UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/api/admin/upload")
async def upload_file(file: UploadFile = File(...), target: str = "uploads"):
    """Upload a file (souls, uploads, or tools directory)."""
    ALLOWED_TARGETS = {
        "uploads": UPLOAD_DIR,
        "souls": SOULS_DIR,
    }
    target_dir = ALLOWED_TARGETS.get(target, UPLOAD_DIR)
    target_dir.mkdir(exist_ok=True)

    dest = target_dir / file.filename
    content = await file.read()
    dest.write_bytes(content)

    _add_log("INFO", "upload", f"File uploaded: {file.filename} → {target}/ ({len(content)} bytes)")
    return {
        "ok": True,
        "filename": file.filename,
        "target": target,
        "size": len(content),
    }

@app.get("/api/admin/files/{directory}")
async def list_files(directory: str):
    """List files in a directory."""
    ALLOWED = {
        "souls": SOULS_DIR,
        "tools": TOOLS_DIR,
        "uploads": UPLOAD_DIR,
        "static": STATIC_DIR,
    }
    dir_path = ALLOWED.get(directory)
    if not dir_path or not dir_path.exists():
        raise HTTPException(404, f"Directory not found: {directory}")

    files = []
    for f in sorted(dir_path.iterdir()):
        if f.is_file():
            files.append({
                "name": f.name,
                "size": f.stat().st_size,
                "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
            })
    return {"ok": True, "directory": directory, "files": files}


# ── 7. Tools Catalog ─────────────────────────────────────────────

@app.get("/api/admin/tools")
async def list_all_tools():
    """List all tool modules and their functions."""
    from agents_runtime.agents import TOOL_SETS
    catalog = {}
    for agent_name, tools in TOOL_SETS.items():
        for t in tools:
            if t.name not in catalog:
                catalog[t.name] = {
                    "name": t.name,
                    "description": getattr(t, "description", ""),
                    "used_by": [],
                }
            catalog[t.name]["used_by"].append(agent_name)

    return {
        "ok": True,
        "total": len(catalog),
        "tools": catalog,
    }


# ── 8. Server Status (detailed) ──────────────────────────────────

@app.get("/api/admin/status")
async def admin_status():
    """Detailed server status for admin panel."""
    from agents_runtime.agents import TOOL_SETS, AGENT_MODELS
    from agents_runtime.memory import get_checkpointer
    import sys

    return {
        "ok": True,
        "version": "2.0.0",
        "python": sys.version,
        "agents": len(TOOL_SETS),
        "total_tools": sum(len(v) for v in TOOL_SETS.values()),
        "persistent_memory": get_checkpointer() is not None,
        "chat_sessions": len(_chat_sessions),
        "log_entries": len(_log_buffer),
        "uptime_ts": datetime.utcnow().isoformat(),
        "souls_dir": str(SOULS_DIR),
        "upload_dir": str(UPLOAD_DIR),
    }
