"""
Shared state for the OpenClaw Balkan agent graph.
All agents read/write to this typed state.
"""
from __future__ import annotations

import operator
from dataclasses import dataclass, field
from typing import Annotated, Any, Literal

from langgraph.graph import MessagesState


# ── Merge helper ────────────────────────────────────────────────
def merge_dicts(left: dict, right: dict) -> dict:
    """Shallow merge – right wins on conflicts."""
    return {**left, **right}


# ── Core state ──────────────────────────────────────────────────
class CompanyState(MessagesState):
    """
    Central state shared by every node in the graph.

    Convention:
      - `messages` (inherited) carries the LLM conversation
      - everything else is structured business data
    """

    # ── Routing ─────────────────────────────────────────────────
    current_agent: str = "supervisor"
    next_agent: str = ""
    task_type: Literal[
        "inbound_lead",
        "inbound_order",
        "inbound_support",
        "scheduled_billing",
        "scheduled_marketing",
        "scheduled_ops",
        "scheduled_report",
        "manual",
        "",
    ] = ""

    # ── Customer / Lead context ─────────────────────────────────
    customer_id: str = ""
    customer_name: str = ""
    customer_company: str = ""
    customer_email: str = ""
    customer_phone: str = ""
    customer_channel: Literal["viber", "whatsapp", "email", "web", ""] = ""
    customer_market: Literal["ba", "rs", ""] = ""
    customer_language: Literal["bosnisch", "srpski", "hrvatski", ""] = ""

    # ── Order context ───────────────────────────────────────────
    order_ref: str = ""
    bundle_id: str = ""
    bundle_name: str = ""
    bundle_price: float = 0.0

    # ── Agent scratchpad (per-agent working memory) ─────────────
    agent_notes: Annotated[dict[str, Any], merge_dicts] = field(default_factory=dict)

    # ── Action log (append-only) ────────────────────────────────
    actions_taken: Annotated[list[str], operator.add] = field(default_factory=list)

    # ── Final output ────────────────────────────────────────────
    final_response: str = ""
    should_end: bool = False
