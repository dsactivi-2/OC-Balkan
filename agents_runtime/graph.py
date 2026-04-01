"""
The main LangGraph graph — wires Supervisor Ava to all agent nodes.
This is the brain of the Zero-Human Company.
"""
from __future__ import annotations

from typing import Literal

from langgraph.graph import StateGraph, END

from agents_runtime.state import CompanyState
from agents_runtime.agents import (
    supervisor_node,
    sales_agent,
    onboarding_agent,
    support_agent,
    billing_agent,
    marketing_agent,
    ops_agent,
)


# ── Routing function ────────────────────────────────────────────
def route_from_supervisor(state: CompanyState) -> str:
    """Conditional edge: read state.next_agent and route to that node."""
    agent = state.next_agent
    valid = {
        "sales_agent",
        "onboarding_agent",
        "support_agent",
        "billing_agent",
        "marketing_agent",
        "ops_agent",
    }
    if agent in valid:
        return agent
    # Default fallback
    return "support_agent"


def should_continue(state: CompanyState) -> str:
    """After an agent runs, decide if we need another round or end."""
    if state.should_end:
        return "end"
    if state.next_agent and state.next_agent != state.current_agent:
        return "supervisor"
    return "end"


# ── Build the graph ─────────────────────────────────────────────
def build_company_graph() -> StateGraph:
    """Construct and compile the full agent graph."""

    graph = StateGraph(CompanyState)

    # Add nodes
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("sales_agent", sales_agent)
    graph.add_node("onboarding_agent", onboarding_agent)
    graph.add_node("support_agent", support_agent)
    graph.add_node("billing_agent", billing_agent)
    graph.add_node("marketing_agent", marketing_agent)
    graph.add_node("ops_agent", ops_agent)

    # Entry point: always start with supervisor
    graph.set_entry_point("supervisor")

    # Supervisor routes to one of the agents
    graph.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "sales_agent": "sales_agent",
            "onboarding_agent": "onboarding_agent",
            "support_agent": "support_agent",
            "billing_agent": "billing_agent",
            "marketing_agent": "marketing_agent",
            "ops_agent": "ops_agent",
        },
    )

    # Each agent either ends or loops back to supervisor
    for agent_name in [
        "sales_agent",
        "onboarding_agent",
        "support_agent",
        "billing_agent",
        "marketing_agent",
        "ops_agent",
    ]:
        graph.add_conditional_edges(
            agent_name,
            should_continue,
            {
                "end": END,
                "supervisor": "supervisor",
            },
        )

    return graph.compile()


# ── Singleton instance ──────────────────────────────────────────
company_graph = build_company_graph()
