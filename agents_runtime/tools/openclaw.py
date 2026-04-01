"""
OpenClaw Platform CLI tools — agent provisioning, status, configuration.
Runs commands inside the openclaw-platform Docker container.
"""
from __future__ import annotations

import json
import subprocess

import httpx
from langchain_core.tools import tool

from agents_runtime import config


def _exec_openclaw(cmd: str, timeout: int = 30) -> str:
    """Execute an openclaw CLI command inside the platform container."""
    full_cmd = f'docker exec openclaw-platform openclaw {cmd}'
    try:
        result = subprocess.run(
            full_cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return f"ERROR (exit {result.returncode}): {result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return f"ERROR: Command timed out after {timeout}s"
    except Exception as e:
        return f"ERROR: {e}"


@tool
def openclaw_list_agents() -> str:
    """List all agents currently deployed on the OpenClaw platform."""
    return _exec_openclaw("agents list --json")


@tool
def openclaw_agent_status(agent_name: str) -> str:
    """Get the status and config of a specific OpenClaw agent.

    Args:
        agent_name: Name of the agent (e.g. 'oc-260401-hp4htx-agent').
    """
    return _exec_openclaw(f'agents info "{agent_name}" --json')


@tool
def openclaw_create_agent(
    name: str, model: str, workspace: str = "", system_prompt: str = ""
) -> str:
    """Create a new agent on the OpenClaw platform.

    Args:
        name: Agent name (lowercase, hyphens allowed).
        model: LLM model to use (e.g. 'litellm/claude-sonnet-4-6').
        workspace: Workspace path inside the container.
        system_prompt: Optional system prompt for the agent.
    """
    cmd = f'agents add "{name}" --model "{model}" --non-interactive --json'
    if workspace:
        cmd += f' --workspace "{workspace}"'
    result = _exec_openclaw(cmd, timeout=60)

    if system_prompt and "ERROR" not in result:
        # Write system prompt to agent workspace
        ws = workspace or f"/home/node/.openclaw/workspaces/{name}"
        _exec_openclaw(f'bash -c "mkdir -p {ws} && echo \'{system_prompt}\' > {ws}/SOUL.md"')

    return result


@tool
def openclaw_delete_agent(agent_name: str) -> str:
    """Delete an agent from the OpenClaw platform.

    Args:
        agent_name: Name of the agent to delete.
    """
    return _exec_openclaw(f'agents remove "{agent_name}" --json')


@tool
def openclaw_bind_channel(agent_name: str, channel_name: str) -> str:
    """Bind a communication channel to an agent.

    Args:
        agent_name: Name of the agent.
        channel_name: Name of the channel (e.g. 'whatsapp-business', 'viber-business').
    """
    return _exec_openclaw(f'agents bind "{agent_name}" "{channel_name}"')


@tool
def openclaw_list_channels() -> str:
    """List all configured communication channels on the platform."""
    return _exec_openclaw("channels list --json")


@tool
def openclaw_platform_health() -> str:
    """Check the health of the OpenClaw platform."""
    try:
        resp = httpx.get(f"{config.OPENCLAW_PLATFORM_URL}/health", timeout=5)
        if resp.status_code == 200:
            return f"OK: Platform healthy — {resp.json()}"
        return f"WARNING: Platform returned {resp.status_code}"
    except Exception as e:
        return f"CRITICAL: Platform unreachable — {e}"
