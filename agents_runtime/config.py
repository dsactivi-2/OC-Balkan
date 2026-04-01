"""
Configuration loaded from environment variables.
Every external credential and endpoint lives here.
"""
from __future__ import annotations

import os


def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


# ── LLM ─────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = _env("ANTHROPIC_API_KEY")
LITELLM_BASE_URL = _env("LITELLM_BASE_URL", "http://37.27.71.134:14000")
LITELLM_API_KEY = _env("LITELLM_API_KEY")

# Model assignments per agent tier
MODEL_SMART = _env("MODEL_SMART", "claude-sonnet-4-6")      # complex reasoning
MODEL_FAST = _env("MODEL_FAST", "claude-haiku-4-5-20251001")  # simple tasks
MODEL_LOCAL = _env("MODEL_LOCAL", "litellm/qwen3.5")        # cost-free local

# ── Viber Business ──────────────────────────────────────────────
VIBER_AUTH_TOKEN = _env("VIBER_AUTH_TOKEN")
VIBER_SENDER_NAME = _env("VIBER_SENDER_NAME", "OpenClaw Balkan")
VIBER_SENDER_AVATAR = _env("VIBER_SENDER_AVATAR", "")

# ── WhatsApp Business (via 360dialog or Meta Cloud API) ─────────
WHATSAPP_API_URL = _env("WHATSAPP_API_URL")
WHATSAPP_API_TOKEN = _env("WHATSAPP_API_TOKEN")

# ── SMTP (outgoing email) ──────────────────────────────────────
SMTP_HOST = _env("SMTP_HOST")
SMTP_PORT = int(_env("SMTP_PORT", "587"))
SMTP_USER = _env("SMTP_USER")
SMTP_PASS = _env("SMTP_PASS")
SMTP_FROM = _env("SMTP_FROM", "hallo@openclawbalkan.ba")

# ── Hetzner Cloud API (server + DNS management) ────────────────
HETZNER_API_TOKEN = _env("HETZNER_API_TOKEN")
HETZNER_DNS_TOKEN = _env("HETZNER_DNS_TOKEN")

# ── Internal services ──────────────────────────────────────────
WEBSITE_BASE_URL = _env("WEBSITE_BASE_URL", "https://balkan.activi.io")
OPENCLAW_PLATFORM_URL = _env("OPENCLAW_PLATFORM_URL", "http://openclaw-platform:18789")
N8N_BASE_URL = _env("N8N_BASE_URL", "http://37.27.71.134:5678")
POSTGRES_URL = _env("POSTGRES_URL", "postgresql://openclaw:openclaw@postgres:5432/openclaw")

# ── SSH for server ops ──────────────────────────────────────────
SERVER_IP = _env("SERVER_IP", "116.203.236.137")
SERVER_SSH_KEY = _env("SERVER_SSH_KEY", "/root/.ssh/id_oc_balkan")

# ── Finance ─────────────────────────────────────────────────────
STRIPE_SECRET_KEY = _env("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = _env("STRIPE_WEBHOOK_SECRET")
BANK_IBAN = _env("BANK_IBAN", "")
BANK_BIC = _env("BANK_BIC", "")
BANK_NAME = _env("BANK_NAME", "")

# ── Social Media ────────────────────────────────────────────────
FACEBOOK_PAGE_TOKEN = _env("FACEBOOK_PAGE_TOKEN")
INSTAGRAM_ACCESS_TOKEN = _env("INSTAGRAM_ACCESS_TOKEN")
LINKEDIN_ACCESS_TOKEN = _env("LINKEDIN_ACCESS_TOKEN")

# ── Admin ───────────────────────────────────────────────────────
ADMIN_VIBER_ID = _env("ADMIN_VIBER_ID")       # Denis Viber user ID for escalations
ADMIN_EMAIL = _env("ADMIN_EMAIL", "ds.selmanovic@gmail.com")
ADMIN_TOKEN = _env("ADMIN_TOKEN", "")
