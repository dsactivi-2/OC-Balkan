"""
MCP (Model Context Protocol) Server for AVA Agent Runtime.
Exposes AVA agents, tools, and operations as MCP tools.
Runs as stdio transport for local Claude Desktop / Cowork integration,
or as HTTP overlay on the existing FastAPI server.

Usage (stdio):
    python -m agents_runtime.mcp_server

Usage (as part of FastAPI):
    Import and mount in server.py
"""
from __future__ import annotations

import json
import logging
from typing import Any

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

logger = logging.getLogger("ava.mcp")

# ── Configuration ────────────────────────────────────────────────
AVA_BASE_URL = "http://localhost:8000"

# ── MCP Server Instance ─────────────────────────────────────────
mcp = Server("ava-agent-runtime")


async def _ava_request(method: str, path: str, body: dict | None = None) -> dict:
    """Make HTTP request to AVA FastAPI backend."""
    async with httpx.AsyncClient(base_url=AVA_BASE_URL, timeout=120) as client:
        if method == "GET":
            resp = await client.get(path)
        else:
            resp = await client.post(path, json=body or {})
        return resp.json()


# ── Tool Definitions ─────────────────────────────────────────────

@mcp.list_tools()
async def list_tools() -> list[Tool]:
    """List all available MCP tools."""
    return [
        Tool(
            name="ava_health",
            description="Check AVA service health status. Returns version, uptime, and service status.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="ava_list_agents",
            description="List all active AVA agents with their models, tools, and soul configurations. "
                        "Returns: sales_agent, onboarding_agent, support_agent, billing_agent, marketing_agent, ops_agent.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="ava_send_message",
            description="Send a customer message to AVA for processing. The supervisor routes it to the appropriate agent "
                        "(sales, support, onboarding, etc.) based on content. Supports multi-turn conversations via sender_id.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The message text to process"
                    },
                    "channel": {
                        "type": "string",
                        "enum": ["viber", "whatsapp", "email", "web"],
                        "description": "Communication channel",
                        "default": "web"
                    },
                    "sender_id": {
                        "type": "string",
                        "description": "Unique sender identifier for conversation continuity"
                    },
                    "sender_name": {
                        "type": "string",
                        "description": "Name of the sender (optional)"
                    },
                    "market": {
                        "type": "string",
                        "enum": ["ba", "rs"],
                        "description": "Market: ba (Bosnia) or rs (Serbia)",
                        "default": "ba"
                    }
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="ava_invoke_agent",
            description="Directly invoke a specific AVA agent, bypassing the supervisor router. "
                        "Useful for testing or when you know exactly which agent should handle the task. "
                        "Valid agents: sales_agent, onboarding_agent, support_agent, billing_agent, marketing_agent, ops_agent.",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_name": {
                        "type": "string",
                        "enum": ["sales_agent", "onboarding_agent", "support_agent",
                                 "billing_agent", "marketing_agent", "ops_agent"],
                        "description": "The agent to invoke directly"
                    },
                    "message": {
                        "type": "string",
                        "description": "The message/task for the agent"
                    }
                },
                "required": ["agent_name", "message"]
            }
        ),
        Tool(
            name="ava_trigger_task",
            description="Trigger a scheduled task manually. Tasks: billing_run (monthly invoices), "
                        "marketing_post (social media), ops_check (infrastructure check), "
                        "daily_report (status report), payment_reminder (overdue invoices).",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_name": {
                        "type": "string",
                        "enum": ["billing_run", "marketing_post", "ops_check",
                                 "daily_report", "payment_reminder"],
                        "description": "The scheduled task to trigger"
                    }
                },
                "required": ["task_name"]
            }
        ),
        Tool(
            name="ava_new_order",
            description="Submit a new customer order to AVA. Triggers the onboarding flow. "
                        "Requires customer details and bundle selection.",
            inputSchema={
                "type": "object",
                "properties": {
                    "orderRef": {
                        "type": "string",
                        "description": "Order reference number (e.g., ORD-001)"
                    },
                    "bundleId": {
                        "type": "string",
                        "enum": ["solo", "learning", "social", "research", "office"],
                        "description": "Bundle ID"
                    },
                    "bundleName": {
                        "type": "string",
                        "description": "Bundle display name"
                    },
                    "price": {
                        "type": "number",
                        "description": "Monthly price in EUR (netto)"
                    },
                    "customerName": {
                        "type": "string",
                        "description": "Customer full name"
                    },
                    "company": {
                        "type": "string",
                        "description": "Company name"
                    },
                    "email": {
                        "type": "string",
                        "description": "Customer email"
                    },
                    "phone": {
                        "type": "string",
                        "description": "Customer phone number"
                    },
                    "preferredChannel": {
                        "type": "string",
                        "enum": ["viber", "whatsapp", "email"],
                        "description": "Preferred communication channel"
                    },
                    "market": {
                        "type": "string",
                        "enum": ["ba", "rs"],
                        "description": "Market: ba or rs"
                    }
                },
                "required": ["orderRef", "bundleId", "bundleName", "price",
                             "customerName", "company", "email"]
            }
        ),
        Tool(
            name="ava_server_status",
            description="Get a quick overview of all OpenClaw Balkan infrastructure: "
                        "running containers, disk usage, memory/CPU, and health check results. "
                        "Invokes the ops_agent with a status request.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
    ]


@mcp.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Execute an MCP tool call."""
    try:
        if name == "ava_health":
            result = await _ava_request("GET", "/health")

        elif name == "ava_list_agents":
            result = await _ava_request("GET", "/api/agents")

        elif name == "ava_send_message":
            body = {
                "channel": arguments.get("channel", "web"),
                "sender_id": arguments.get("sender_id", "mcp-client"),
                "sender_name": arguments.get("sender_name", "MCP User"),
                "text": arguments["text"],
                "market": arguments.get("market", "ba"),
            }
            result = await _ava_request("POST", "/api/message", body)

        elif name == "ava_invoke_agent":
            result = await _ava_request(
                "POST",
                f"/api/invoke/{arguments['agent_name']}",
                {"message": arguments["message"]}
            )

        elif name == "ava_trigger_task":
            result = await _ava_request(
                "POST",
                f"/api/scheduled/{arguments['task_name']}"
            )

        elif name == "ava_new_order":
            body = {
                "event": "order.created",
                **arguments
            }
            result = await _ava_request("POST", "/api/webhook/order", body)

        elif name == "ava_server_status":
            result = await _ava_request(
                "POST",
                "/api/invoke/ops_agent",
                {"message": "Gib mir einen vollständigen Server-Status: Container, Disk, Memory, Health-Checks."}
            )

        else:
            result = {"error": f"Unknown tool: {name}"}

        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, ensure_ascii=False)
        )]

    except httpx.ConnectError:
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": "Cannot connect to AVA service",
                "hint": f"Ensure AVA is running at {AVA_BASE_URL}"
            })
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e)})
        )]


# ── Main entry point (stdio transport) ──────────────────────────
async def main():
    """Run MCP server with stdio transport."""
    async with stdio_server() as (read_stream, write_stream):
        await mcp.run(read_stream, write_stream, mcp.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
