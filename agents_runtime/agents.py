"""
Agent node definitions for the LangGraph company graph.
Each agent is a function that takes CompanyState, calls an LLM with tools, and returns updated state.
"""
from __future__ import annotations

import json
from typing import Any

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from agents_runtime.state import CompanyState
from agents_runtime.config import ANTHROPIC_API_KEY, MODEL_SMART, MODEL_FAST
from agents_runtime.prompts.system_prompts import (
    SUPERVISOR_PROMPT,
    SALES_PROMPT,
    ONBOARDING_PROMPT,
    SUPPORT_PROMPT,
    BILLING_PROMPT,
    MARKETING_PROMPT,
    OPS_PROMPT,
)

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


# ── LLM instances ──────────────────────────────────────────────
def _llm(model: str = MODEL_SMART, temperature: float = 0.3) -> ChatAnthropic:
    return ChatAnthropic(
        model=model,
        api_key=ANTHROPIC_API_KEY,
        temperature=temperature,
        max_tokens=4096,
    )


# ── Tool sets per agent ────────────────────────────────────────
SALES_TOOLS = [send_customer_message, viber_send_message, send_email]

ONBOARDING_TOOLS = [
    send_customer_message,
    viber_send_message,
    send_email,
    openclaw_create_agent,
    openclaw_bind_channel,
    openclaw_list_channels,
]

SUPPORT_TOOLS = [
    send_customer_message,
    viber_send_message,
    send_email,
    openclaw_agent_status,
    openclaw_list_agents,
    server_health_check,
]

BILLING_TOOLS = [
    send_email,
    generate_invoice,
    calculate_monthly_costs,
    calculate_revenue_forecast,
    check_stripe_balance,
    list_overdue_customers,
    hetzner_get_invoice_list,
    hetzner_check_payment_status,
]

MARKETING_TOOLS = [
    facebook_create_post,
    instagram_create_post,
    linkedin_create_post,
    viber_broadcast,
    generate_content_calendar,
    get_website_analytics,
    get_lead_conversion_stats,
]

OPS_TOOLS = [
    server_docker_status,
    server_health_check,
    server_disk_usage,
    server_memory_cpu,
    server_docker_logs,
    server_restart_container,
    server_pull_and_rebuild,
    server_ssl_status,
    check_website_externally,
    openclaw_platform_health,
    hetzner_list_servers,
    hetzner_server_status,
    hetzner_reboot_server,
    hetzner_create_dns_record,
]


# ── Supervisor (router) ────────────────────────────────────────
def supervisor_node(state: CompanyState) -> dict[str, Any]:
    """Route incoming request to the correct agent."""
    llm = _llm(MODEL_FAST, temperature=0.0)

    messages = [SystemMessage(content=SUPERVISOR_PROMPT)] + list(state.messages)

    response = llm.invoke(messages)
    content = response.content

    # Parse the routing decision
    try:
        # Try to extract JSON from the response
        if "{" in content:
            json_str = content[content.index("{") : content.rindex("}") + 1]
            decision = json.loads(json_str)
            next_agent = decision.get("next_agent", "support_agent")
            reason = decision.get("reason", "")
        else:
            next_agent = "support_agent"
            reason = "Could not parse routing decision, defaulting to support"
    except (json.JSONDecodeError, ValueError):
        next_agent = "support_agent"
        reason = "JSON parse error, defaulting to support"

    return {
        "current_agent": "supervisor",
        "next_agent": next_agent,
        "actions_taken": [f"[supervisor] Routed to {next_agent}: {reason}"],
        "messages": [response],
    }


# ── Agent node factory ─────────────────────────────────────────
def _make_agent_node(
    agent_name: str,
    system_prompt: str,
    tools: list,
    model: str = MODEL_SMART,
):
    """Create an agent node function with the given prompt and tools."""

    def agent_node(state: CompanyState) -> dict[str, Any]:
        llm = _llm(model).bind_tools(tools)

        messages = [SystemMessage(content=system_prompt)] + list(state.messages)

        # Run the agent loop (tool calls)
        response = llm.invoke(messages)
        result_messages = [response]
        actions = []

        # Handle tool calls iteratively (max 5 rounds)
        rounds = 0
        while response.tool_calls and rounds < 5:
            rounds += 1
            tool_results = []
            for tc in response.tool_calls:
                # Find and invoke the tool
                tool_fn = next((t for t in tools if t.name == tc["name"]), None)
                if tool_fn:
                    try:
                        result = tool_fn.invoke(tc["args"])
                        actions.append(f"[{agent_name}] Called {tc['name']} → {str(result)[:100]}")
                    except Exception as e:
                        result = f"ERROR: {e}"
                        actions.append(f"[{agent_name}] {tc['name']} FAILED: {e}")
                else:
                    result = f"Unknown tool: {tc['name']}"

                from langchain_core.messages import ToolMessage
                tool_results.append(
                    ToolMessage(content=str(result), tool_call_id=tc["id"])
                )

            result_messages.extend(tool_results)
            messages.extend([response] + tool_results)

            # Next LLM round
            response = llm.invoke(messages)
            result_messages.append(response)

        return {
            "current_agent": agent_name,
            "next_agent": "",
            "messages": result_messages,
            "actions_taken": actions,
            "final_response": response.content if isinstance(response.content, str) else "",
            "should_end": True,
        }

    agent_node.__name__ = agent_name
    return agent_node


# ── Create all agent nodes ─────────────────────────────────────
sales_agent = _make_agent_node("sales_agent", SALES_PROMPT, SALES_TOOLS)
onboarding_agent = _make_agent_node("onboarding_agent", ONBOARDING_PROMPT, ONBOARDING_TOOLS)
support_agent = _make_agent_node("support_agent", SUPPORT_PROMPT, SUPPORT_TOOLS)
billing_agent = _make_agent_node("billing_agent", BILLING_PROMPT, BILLING_TOOLS, MODEL_FAST)
marketing_agent = _make_agent_node("marketing_agent", MARKETING_PROMPT, MARKETING_TOOLS)
ops_agent = _make_agent_node("ops_agent", OPS_PROMPT, OPS_TOOLS)
