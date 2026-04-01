"""
Scheduled tasks — the autonomous heartbeat of the Zero-Human Company.

IMPORTANT: The 5-minute ops check is SILENT (no LLM call).
It only triggers the full LLM-powered ops agent if something is wrong.
This saves API credits.
"""
from __future__ import annotations

import logging
from datetime import datetime

import httpx
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger("ava.scheduler")

SELF_URL = "http://localhost:8000"

scheduler = BackgroundScheduler()


def _trigger_task(task_name: str):
    """Fire a scheduled task via our own API (triggers LLM agent)."""
    try:
        resp = httpx.post(f"{SELF_URL}/api/scheduled/{task_name}", timeout=120)
        logger.info(f"[scheduler] {task_name} → {resp.status_code}")
    except Exception as e:
        logger.error(f"[scheduler] {task_name} FAILED: {e}")


def _silent_health_check():
    """Lightweight health check — NO LLM call.
    Only triggers the full ops agent if something is actually broken.
    """
    checks = {
        "website": f"{SELF_URL.replace(':8000', ':4173')}/health",
        "ava": f"{SELF_URL}/health",
    }

    problems = []
    for name, url in checks.items():
        try:
            # Try internal Docker network URLs
            resp = httpx.get(url, timeout=5)
            if resp.status_code != 200:
                problems.append(f"{name}: HTTP {resp.status_code}")
        except Exception as e:
            problems.append(f"{name}: {e}")

    # Also check container status via Docker
    import subprocess
    try:
        result = subprocess.run(
            "docker ps --format '{{.Names}}:{{.Status}}' | grep openclaw",
            shell=True, capture_output=True, text=True, timeout=10,
        )
        for line in result.stdout.strip().split("\n"):
            if line and "unhealthy" in line.lower():
                container = line.split(":")[0]
                problems.append(f"Container unhealthy: {container}")
            elif line and "restarting" in line.lower():
                container = line.split(":")[0]
                problems.append(f"Container restarting: {container}")
    except Exception as e:
        problems.append(f"Docker check failed: {e}")

    if problems:
        logger.warning(f"[health] Problems detected: {problems}")
        # NOW trigger the full LLM ops agent to diagnose and fix
        _trigger_task("ops_check")
    else:
        logger.info("[health] All systems OK (silent check)")


def start_scheduler():
    """Register all scheduled jobs."""

    # ── Silent health check (every 5 min, NO LLM cost) ────────
    scheduler.add_job(
        _silent_health_check,
        CronTrigger(minute="*/5"),
        id="silent_health_5min",
        name="Silent health check (every 5 min, no LLM)",
        replace_existing=True,
        max_instances=1,
    )

    # ── Marketing: 3x per week (Mo/Mi/Fr 10:00 CET) ───────────
    scheduler.add_job(
        _trigger_task,
        CronTrigger(day_of_week="mon,wed,fri", hour=10, minute=0),
        args=["marketing_post"],
        id="marketing_post",
        name="Social media post (Mo/Mi/Fr 10:00)",
        replace_existing=True,
    )

    # ── Billing: Monthly (1st, 09:00) ──────────────────────────
    scheduler.add_job(
        _trigger_task,
        CronTrigger(day=1, hour=9, minute=0),
        args=["billing_run"],
        id="billing_monthly",
        name="Monthly billing run (1st, 09:00)",
        replace_existing=True,
    )

    # ── Payment reminders (10th and 20th, 10:00) ───────────────
    scheduler.add_job(
        _trigger_task,
        CronTrigger(day="10,20", hour=10, minute=0),
        args=["payment_reminder"],
        id="payment_reminder",
        name="Payment reminders (10th/20th, 10:00)",
        replace_existing=True,
    )

    # ── Daily report (18:00) ───────────────────────────────────
    scheduler.add_job(
        _trigger_task,
        CronTrigger(hour=18, minute=0),
        args=["daily_report"],
        id="daily_report",
        name="Daily status report (18:00)",
        replace_existing=True,
    )

    # ── Full ops check (daily 06:00 — WITH LLM) ───────────────
    scheduler.add_job(
        _trigger_task,
        CronTrigger(hour=6, minute=0),
        args=["ops_check"],
        id="daily_ops_check",
        name="Full infrastructure check (06:00, with LLM)",
        replace_existing=True,
    )

    scheduler.start()
    logger.info(f"[scheduler] Started with {len(scheduler.get_jobs())} jobs")
    for job in scheduler.get_jobs():
        logger.info(f"  → {job.name} | next: {job.next_run_time}")


def stop_scheduler():
    scheduler.shutdown(wait=False)
    logger.info("[scheduler] Stopped")
