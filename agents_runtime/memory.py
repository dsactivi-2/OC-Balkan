"""
Persistent memory via LangGraph PostgreSQL Checkpointer.
Gives every agent conversation history across sessions.
"""
from __future__ import annotations

import logging

from agents_runtime.config import POSTGRES_URL

logger = logging.getLogger("ava.memory")

_saver = None
_connection = None


def get_checkpointer():
    """Get or create the PostgreSQL checkpointer singleton.
    Handles both sync and context-manager versions of the API.
    """
    global _saver, _connection

    if _saver is not None:
        return _saver

    if not POSTGRES_URL:
        logger.warning("No POSTGRES_URL — running without persistent memory")
        return None

    try:
        from langgraph.checkpoint.postgres import PostgresSaver

        # New API: from_conn_string returns a context manager
        cm = PostgresSaver.from_conn_string(POSTGRES_URL)
        if hasattr(cm, '__enter__'):
            _connection = cm
            _saver = cm.__enter__()
        else:
            _saver = cm

        if hasattr(_saver, 'setup'):
            _saver.setup()

        logger.info(f"PostgreSQL checkpointer connected")
        return _saver
    except Exception as e:
        logger.warning(f"Checkpointer not available: {e} — running without persistent memory")
        return None


def thread_id_for_customer(customer_id: str, channel: str = "") -> str:
    """Deterministic thread ID for a customer conversation."""
    if customer_id and channel:
        return f"customer-{customer_id}-{channel}"
    if customer_id:
        return f"customer-{customer_id}"
    return f"anon-{abs(hash(customer_id)) % 100000}"


def thread_id_for_task(task_name: str, date_key: str = "") -> str:
    """Thread ID for scheduled tasks (one per day per task)."""
    if date_key:
        return f"task-{task_name}-{date_key}"
    from datetime import datetime
    return f"task-{task_name}-{datetime.utcnow().strftime('%Y%m%d')}"
