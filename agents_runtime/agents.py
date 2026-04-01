"""
Agent node definitions for the LangGraph company graph.
Each agent loads its SOUL.md, has tools, retry logic, and proper error handling.
"""
from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage

from agents_runtime.state import CompanyState
from agents_runtime.config import ANTHROPIC_API_KEY, MODEL_SMART, MODEL_FAST

logger = logging.getLogger("ava.agents")

# ── Soul loading ────────────────────────────────────────────────
SOULS_DIR = Path(__file__).parent / "souls"


def _load_soul(agent_name: str) -> str:
    """Load the SOUL.md file for an agent. Falls back to inline prompt if missing."""
    soul_path = SOULS_DIR / f"{agent_name}.md"
    if soul_path.exists():
        return soul_path.read_text(encoding="utf-8")
    logger.warning(f"No SOUL.md found for {agent_name} at {soul_path}")
    return f"Du bist der {agent_name} fuer OpenClaw Balkan."


# ── Tool imports ────────────────────────────────────────────────
from agents_runtime.tools.messaging import (
    viber_send_message,
    viber_broadcast,
    whatsapp_send_message,
    send_email,
    send_customer_message,
)
from agents_runtime.tools.hetzner import (
    hetzner_list_servers,
    hetzner_server_status,
    hetzner_reboot_server,
    hetzner_create_dns_record,
    hetzner_get_invoice_list,
    hetzner_check_payment_status,
)
from agents_runtime.tools.openclaw import (
    openclaw_list_agents,
    openclaw_agent_status,
    openclaw_create_agent,
    openclaw_delete_agent,
    openclaw_bind_channel,
    openclaw_list_channels,
    openclaw_platform_health,
)
from agents_runtime.tools.ops import (
    server_docker_status,
    server_health_check,
    server_disk_usage,
    server_memory_cpu,
    server_docker_logs,
    server_restart_container,
    server_pull_and_rebuild,
    server_ssl_status,
    check_website_externally,
)
from agents_runtime.tools.finance import (
    generate_invoice,
    generate_invoice_pdf,
    calculate_monthly_costs,
    calculate_revenue_forecast,
    check_stripe_balance,
    list_overdue_customers,
)
from agents_runtime.tools.marketing import (
    facebook_create_post,
    instagram_create_post,
    linkedin_create_post,
    generate_content_calendar,
    get_website_analytics,
    get_lead_conversion_stats,
)


# ── LLM factory ────────────────────────────────────────────────
def _llm(model: str = MODEL_SMART, temperature: float = 0.3) -> ChatAnthropic:
    return ChatAnthropic(
        model=model,
        api_key=ANTHROPIC_API_KEY,
        temperature=temperature,
        max_tokens=4096,
    )


# ── Tool sets per agent ────────────────────────────────────────
TOOL_SETS = {
    "sales_agent": [send_customer_message, viber_send_message, send_email],
    "onboarding_agent": [
        send_customer_message, viber_send_message, send_email,
        openclaw_create_agent, openclaw_bind_channel, openclaw_list_channels,
    ],
    "support_agent": [
        send_customer_message, viber_send_message, send_email,
        openclaw_agent_status, openclaw_list_agents, server_health_check,
    ],
    "billing_agent": [
        send_email, generate_invoice, generate_invoice_pdf,
        calculate_monthly_costs, calculate_revenue_forecast,
        check_stripe_balance, list_overdue_customers,
        hetzner_get_invoice_list, hetzner_check_payment_status,
    ],
    "marketing_agent": [
        facebook_create_post, instagram_create_post, linkedin_create_post,
        viber_broadcast, generate_content_calendar,
        get_website_analytics, get_lead_conversion_stats,
    ],
    "ops_agent": [
        server_docker_status, server_health_check, server_disk_usage,
        server_memory_cpu, server_docker_logs, server_restart_container,
        server_pull_and_rebuild, server_ssl_status, check_website_externally,
        openclaw_platform_health, hetzner_list_servers, hetzner_server_status,
        hetzner_reboot_server, hetzner_create_dns_record,
    ],
}

# Model assignment per agent
AGENT_MODELS = {
    "sales_agent": MODEL_SMART,
    "onboarding_agent": MODEL_SMART,
    "support_agent": MODEL_SMART,
    "billing_agent": MODEL_FAST,
    "marketing_agent": MODEL_SMART,
    "ops_agent": MODEL_FAST,
}

# Soul name mapping (filename without .md)
SOUL_NAMES = {
    "sales_agent": "sales",
    "onboarding_agent": "onboarding",
    "support_agent": "support",
    "billing_agent": "billing",
    "marketing_agent": "marketing",
    "ops_agent": "ops",
}


# ── Retry wrapper ──────────────────────────────────────────────
def _invoke_with_retry(llm, messages: list, max_retries: int = 3) -> Any:
    """Invoke LLM with exponential backoff retry on transient errors."""
    for attempt in range(max_retries):
        try:
            return llm.invoke(messages)
        except Exception as e:
            error_str = str(e).lower()
            is_transient = any(k in error_str for k in [
                "rate_limit", "overloaded", "timeout", "connection",
                "529", "503", "429",
            ])
            if is_transient and attempt < max_retries - 1:
                wait = 2 ** attempt
                logger.warning(f"LLM call failed (attempt {attempt+1}), retrying in {wait}s: {e}")
                time.sleep(wait)
                continue
            raise


# ── Tool execution ──────────────────────────────────────────────
def _execute_tool_calls(tool_calls: list, tools: list, agent_name: str) -> tuple[list[ToolMessage], list[str]]:
    """Execute tool calls and return ToolMessages + action log entries."""
    tool_map = {t.name: t for t in tools}
    messages = []
    actions = []

    for tc in tool_calls:
        tool_fn = tool_map.get(tc["name"])
        if tool_fn:
            try:
                result = tool_fn.invoke(tc["args"])
                result_str = str(result)
                actions.append(f"[{agent_name}] {tc['name']}({json.dumps(tc['args'], ensure_ascii=False)[:80]}) → {result_str[:100]}")
            except Exception as e:
                result_str = f"ERROR: {e}"
                actions.append(f"[{agent_name}] {tc['name']} FAILED: {e}")
                logger.error(f"Tool {tc['name']} failed: {e}")
        else:
            result_str = f"Unknown tool: {tc['name']}"
            actions.append(f"[{agent_name}] Unknown tool: {tc['name']}")

        messages.append(ToolMessage(content=result_str, tool_call_id=tc["id"]))

    return messages, actions


# ── Supervisor node ─────────────────────────────────────────────
def supervisor_node(state: CompanyState) -> dict[str, Any]:
    """Route incoming request to the correct agent.
    Uses task_type for deterministic routing when available,
    falls back to LLM routing for ambiguous cases.
    """
    # --- Deterministic routing by task_type ---
    task_routes = {
        "inbound_lead": "sales_agent",
        "inbound_order": "onboarding_agent",
        "inbound_support": "support_agent",
        "scheduled_billing": "billing_agent",
        "scheduled_marketing": "marketing_agent",
        "scheduled_ops": "ops_agent",
        "scheduled_report": "ops_agent",
    }

    if state.task_type and state.task_type in task_routes:
        next_agent = task_routes[state.task_type]
        reason = f"Deterministic route: task_type={state.task_type}"
        logger.info(f"[supervisor] {reason} → {next_agent}")
        return {
            "current_agent": "supervisor",
            "next_agent": next_agent,
            "actions_taken": [f"[supervisor] {reason}"],
        }

    # --- LLM-based routing for ambiguous cases ---
    soul = _load_soul("supervisor")
    llm = _llm(MODEL_FAST, temperature=0.0)
    messages = [SystemMessage(content=soul)] + list(state.messages)

    try:
        response = _invoke_with_retry(llm, messages)
        content = response.content

        # Parse JSON from response
        if "{" in content:
            json_str = content[content.index("{"):content.rindex("}") + 1]
            decision = json.loads(json_str)
            next_agent = decision.get("next_agent", "support_agent")
            reason = decision.get("reason", "LLM routing")
        else:
            next_agent = "support_agent"
            reason = "No JSON in response, defaulting to support"
    except Exception as e:
        logger.error(f"[supervisor] Routing failed: {e}")
        next_agent = "support_agent"
        reason = f"Routing error: {e}"

    valid_agents = set(TOOL_SETS.keys())
    if next_agent not in valid_agents:
        next_agent = "support_agent"
        reason += " (invalid agent name, fallback)"

    logger.info(f"[supervisor] Routed to {next_agent}: {reason}")
    return {
        "current_agent": "supervisor",
        "next_agent": next_agent,
        "actions_taken": [f"[supervisor] → {next_agent}: {reason}"],
    }


# ── Generic agent node ──────────────────────────────────────────
def _make_agent_node(agent_name: str):
    """Create an agent node that loads its SOUL.md, uses its tools,
    handles multi-turn tool calls, and has retry logic."""

    soul_name = SOUL_NAMES.get(agent_name, agent_name)
    tools = TOOL_SETS.get(agent_name, [])
    model = AGENT_MODELS.get(agent_name, MODEL_SMART)

    def agent_node(state: CompanyState) -> dict[str, Any]:
        soul = _load_soul(soul_name)
        llm = _llm(model).bind_tools(tools) if tools else _llm(model)

        # Build message chain: soul + context + conversation
        context_parts = []
        if state.customer_name:
            context_parts.append(f"Kunde: {state.customer_name}")
        if state.customer_company:
            context_parts.append(f"Firma: {state.customer_company}")
        if state.customer_email:
            context_parts.append(f"Email: {state.customer_email}")
        if state.customer_phone:
            context_parts.append(f"Telefon: {state.customer_phone}")
        if state.customer_channel:
            context_parts.append(f"Kanal: {state.customer_channel}")
        if state.customer_market:
            context_parts.append(f"Markt: {state.customer_market}")
        if state.order_ref:
            context_parts.append(f"Order: {state.order_ref}")
        if state.bundle_name:
            context_parts.append(f"Bundle: {state.bundle_name} ({state.bundle_price} EUR)")

        system_content = soul
        if context_parts:
            system_content += "\n\n## Aktueller Kontext\n" + "\n".join(context_parts)

        messages = [SystemMessage(content=system_content)] + list(state.messages)

        # Agent loop — tool calls with retry
        all_messages = []
        all_actions = []
        max_rounds = 8

        try:
            response = _invoke_with_retry(llm, messages)
        except Exception as e:
            logger.error(f"[{agent_name}] Initial LLM call failed: {e}")
            return {
                "current_agent": agent_name,
                "should_end": True,
                "final_response": f"Agent {agent_name} konnte nicht antworten: {e}",
                "actions_taken": [f"[{agent_name}] FATAL: {e}"],
            }

        all_messages.append(response)
        rounds = 0

        while response.tool_calls and rounds < max_rounds:
            rounds += 1
            tool_msgs, actions = _execute_tool_calls(response.tool_calls, tools, agent_name)
            all_messages.extend(tool_msgs)
            all_actions.extend(actions)

            messages.extend([response] + tool_msgs)

            try:
                response = _invoke_with_retry(llm, messages)
            except Exception as e:
                logger.error(f"[{agent_name}] LLM call failed in round {rounds}: {e}")
                all_actions.append(f"[{agent_name}] LLM error in round {rounds}: {e}")
                break

            all_messages.append(response)

        final_text = ""
        if isinstance(response.content, str):
            final_text = response.content
        elif isinstance(response.content, list):
            final_text = " ".join(
                block.get("text", "") for block in response.content
                if isinstance(block, dict) and block.get("type") == "text"
            )

        logger.info(f"[{agent_name}] Completed in {rounds} tool rounds, {len(all_actions)} actions")

        return {
            "current_agent": agent_name,
            "next_agent": "",
            "messages": all_messages,
            "actions_taken": all_actions,
            "final_response": final_text,
            "should_end": True,
        }

    agent_node.__name__ = agent_name
    return agent_node


# ── Create all agent nodes ─────────────────────────────────────
sales_agent = _make_agent_node("sales_agent")
onboarding_agent = _make_agent_node("onboarding_agent")
support_agent = _make_agent_node("support_agent")
billing_agent = _make_agent_node("billing_agent")
marketing_agent = _make_agent_node("marketing_agent")
ops_agent = _make_agent_node("ops_agent")
