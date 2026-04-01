"""
The main LangGraph graph — wires Supervisor Ava to all agent nodes.
Now with persistent memory via PostgreSQL Checkpointer.
"""
from __future__ import annotations

import logging

from langgraph.graph import StateGraph, END

from agents_runtime.state import CompanyState
from agents_runtime.memory import get_checkpointer
from agents_runtime.agents import (
    supervisor_node,
    sales_agent,
    onboarding_agent,
    support_agent,
    billing_agent,
    marketing_agent,
    ops_agent,
    TOOL_SETS,
)

logger = logging.getLogger("ava.graph")

AGENT_NODES = {
    "sales_agent": sales_agent,
    "onboarding_agent": onboarding_agent,
    "support_agent": support_agent,
    "billing_agent": billing_agent,
    "marketing_agent": marketing_agent,
    "ops_agent": ops_agent,
}


# ── Routing functions ───────────────────────────────────────────
def route_from_supervisor(state: CompanyState) -> str:
    """Route from supervisor to the designated agent."""
    agent = state.get("next_agent", "support_agent")
    if agent in AGENT_NODES:
        return agent
    return "support_agent"


def should_continue(state: CompanyState) -> str:
    """After an agent runs, decide: end or hand off to another agent."""
    if state.get("should_end"):
        return "end"
    next_ag = state.get("next_agent", "")
    current_ag = state.get("current_agent", "")
    if next_ag and next_ag != current_ag:
        return "supervisor"
    return "end"


# ── Build the graph ─────────────────────────────────────────────
def build_company_graph():
    """Construct and compile the full agent graph with persistent checkpointer."""

    graph = StateGraph(CompanyState)

    # Add all nodes
    graph.add_node("supervisor", supervisor_node)
    for name, node_fn in AGENT_NODES.items():
        graph.add_node(name, node_fn)

    # Entry point
    graph.set_entry_point("supervisor")

    # Supervisor → agent routing
    graph.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {name: name for name in AGENT_NODES},
    )

    # Agent → end or back to supervisor
    for name in AGENT_NODES:
        graph.add_conditional_edges(
            name,
            should_continue,
            {"end": END, "supervisor": "supervisor"},
        )

    # Compile with checkpointer for persistent memory
    checkpointer = get_checkpointer()
    if checkpointer:
        compiled = graph.compile(checkpointer=checkpointer)
        logger.info("Graph compiled WITH persistent PostgreSQL memory")
    else:
        compiled = graph.compile()
        logger.info("Graph compiled WITHOUT persistent memory (no PostgreSQL)")

    return compiled


# ── Singleton ───────────────────────────────────────────────────
company_graph = build_company_graph()
