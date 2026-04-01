"""
Scheduled tasks — the autonomous heartbeat of the Zero-Human Company.
Uses APScheduler to trigger agents on cron schedules.
"""
from __future__ import annotations

import logging
from datetime import datetime

import httpx
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger("ava.scheduler")

# The scheduler fires HTTP requests to our own API
# This keeps the scheduling logic decoupled from the graph execution
SELF_URL = "http://localhost:8000"

scheduler = BackgroundScheduler()


def _trigger_task(task_name: str):
    """Fire a scheduled task via the API."""
    try:
        resp = httpx.post(f"{SELF_URL}/api/scheduled/{task_name}", timeout=120)
        logger.info(f"[scheduler] {task_name} → {resp.status_code}")
    except Exception as e:
        logger.error(f"[scheduler] {task_name} FAILED: {e}")


def start_scheduler():
    """Register all scheduled jobs and start the scheduler."""

    # ── Ops: Health check every 5 minutes ──────────────────────
    scheduler.add_job(
        _trigger_task,
        CronTrigger(minute="*/5"),
        args=["ops_check"],
        id="ops_check_5min",
        name="Infrastructure health check (every 5 min)",
        replace_existing=True,
        max_instances=1,  # don't overlap
    )

    # ── Marketing: Post 3x per week (Mo/Mi/Fr at 10:00 CET) ───
    scheduler.add_job(
        _trigger_task,
        CronTrigger(day_of_week="mon,wed,fri", hour=10, minute=0),
        args=["marketing_post"],
        id="marketing_post",
        name="Social media post (Mo/Mi/Fr 10:00)",
        replace_existing=True,
    )

    # ── Billing: Monthly invoice run (1st of month, 09:00) ─────
    scheduler.add_job(
        _trigger_task,
        CronTrigger(day=1, hour=9, minute=0),
        args=["billing_run"],
        id="billing_monthly",
        name="Monthly billing run (1st, 09:00)",
        replace_existing=True,
    )

    # ── Billing: Payment reminders (10th and 20th, 10:00) ──────
    scheduler.add_job(
        _trigger_task,
        CronTrigger(day="10,20", hour=10, minute=0),
        args=["payment_reminder"],
        id="payment_reminder",
        name="Payment reminders (10th/20th, 10:00)",
        replace_existing=True,
    )

    # ── Daily report (every day at 18:00) ──────────────────────
    scheduler.add_job(
        _trigger_task,
        CronTrigger(hour=18, minute=0),
        args=["daily_report"],
        id="daily_report",
        name="Daily status report (18:00)",
        replace_existing=True,
    )

    scheduler.start()
    logger.info(f"[scheduler] Started with {len(scheduler.get_jobs())} jobs")

    # Log all jobs
    for job in scheduler.get_jobs():
        logger.info(f"  → {job.name} | next run: {job.next_run_time}")


def stop_scheduler():
    """Gracefully shut down the scheduler."""
    scheduler.shutdown(wait=False)
    logger.info("[scheduler] Stopped")
