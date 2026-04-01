"""
Operations tools — SSH commands, Docker management, monitoring.
Used by the Ops agent to manage the server infrastructure.
"""
from __future__ import annotations

import subprocess

import httpx
from langchain_core.tools import tool

from agents_runtime import config


def _ssh(cmd: str, timeout: int = 30) -> str:
    """Execute a command on the server via SSH."""
    ssh_cmd = (
        f'ssh -i {config.SERVER_SSH_KEY} '
        f'-o StrictHostKeyChecking=no -o ConnectTimeout=10 '
        f'root@{config.SERVER_IP} "{cmd}"'
    )
    try:
        result = subprocess.run(
            ssh_cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        output = result.stdout.strip()
        if result.returncode != 0 and result.stderr.strip():
            output += f"\nSTDERR: {result.stderr.strip()}"
        return output or "(no output)"
    except subprocess.TimeoutExpired:
        return f"ERROR: SSH command timed out after {timeout}s"
    except Exception as e:
        return f"ERROR: {e}"


@tool
def server_docker_status() -> str:
    """Get the status of all Docker containers on the server."""
    return _ssh("docker ps -a --format 'table {{.Names}}\\t{{.Status}}\\t{{.Ports}}'")


@tool
def server_health_check() -> str:
    """Run health checks against all services on the server."""
    checks = [
        ("website", "curl -s http://localhost:80/health"),
        ("app-direct", "curl -s http://$(docker inspect openclaw-app --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' | head -c 15):4173/health"),
        ("platform", "curl -s http://$(docker inspect openclaw-platform --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' | head -c 15):18789/health"),
    ]
    results = []
    for name, cmd in checks:
        out = _ssh(cmd, timeout=15)
        status = "OK" if "ok" in out.lower() or "true" in out.lower() else "FAIL"
        results.append(f"  [{status}] {name}: {out[:100]}")
    return "Health checks:\n" + "\n".join(results)


@tool
def server_disk_usage() -> str:
    """Check disk usage on the server."""
    return _ssh("df -h / && echo '---' && du -sh /opt/openclaw/ 2>/dev/null && du -sh /var/lib/docker/ 2>/dev/null")


@tool
def server_memory_cpu() -> str:
    """Check memory and CPU usage on the server."""
    return _ssh("free -h && echo '---' && uptime && echo '---' && top -bn1 | head -5")


@tool
def server_docker_logs(container: str, lines: int = 50) -> str:
    """Get recent Docker logs for a container.

    Args:
        container: Container name (e.g. 'openclaw-app', 'openclaw-platform').
        lines: Number of log lines to retrieve.
    """
    safe_container = container.replace('"', "").replace("'", "")[:30]
    return _ssh(f"docker logs {safe_container} --tail {min(lines, 200)} 2>&1")


@tool
def server_restart_container(container: str) -> str:
    """Restart a Docker container on the server.

    Args:
        container: Container name to restart.
    """
    safe_container = container.replace('"', "").replace("'", "")[:30]
    return _ssh(f"docker restart {safe_container}")


@tool
def server_pull_and_rebuild() -> str:
    """Pull latest code and rebuild containers on the server."""
    return _ssh(
        "cd /opt/openclaw && git pull origin main && "
        "docker compose build --no-cache && "
        "docker compose up -d && "
        "echo 'Rebuild complete'",
        timeout=300,
    )


@tool
def server_ssl_status() -> str:
    """Check SSL certificate expiry for the domain."""
    return _ssh(
        "echo | openssl s_client -connect balkan.activi.io:443 -servername balkan.activi.io 2>/dev/null | "
        "openssl x509 -noout -dates 2>/dev/null || echo 'SSL check failed'"
    )


@tool
def check_website_externally() -> str:
    """Check if the website is accessible from outside (via HTTPS)."""
    try:
        resp = httpx.get(f"{config.WEBSITE_BASE_URL}/health", timeout=10, verify=False)
        return f"OK: {config.WEBSITE_BASE_URL} returned {resp.status_code} — {resp.text[:100]}"
    except Exception as e:
        return f"CRITICAL: {config.WEBSITE_BASE_URL} unreachable — {e}"
