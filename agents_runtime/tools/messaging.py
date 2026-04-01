"""
Messaging tools: Viber, WhatsApp, Email.
These are the customer-facing communication channels.
"""
from __future__ import annotations

import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import httpx
from langchain_core.tools import tool

from agents_runtime import config


# ── Viber Business API ──────────────────────────────────────────

@tool
def viber_send_message(receiver_id: str, text: str, message_type: str = "text") -> str:
    """Send a message to a Viber user via Viber Business API.

    Args:
        receiver_id: The Viber user ID of the recipient.
        text: The message text to send.
        message_type: Type of message — 'text', 'picture', or 'rich_media'.
    """
    if not config.VIBER_AUTH_TOKEN:
        return "ERROR: VIBER_AUTH_TOKEN not configured"

    payload = {
        "receiver": receiver_id,
        "min_api_version": 1,
        "sender": {
            "name": config.VIBER_SENDER_NAME,
            "avatar": config.VIBER_SENDER_AVATAR,
        },
        "type": message_type,
        "text": text,
    }

    resp = httpx.post(
        "https://chatapi.viber.com/pa/send_message",
        headers={"X-Viber-Auth-Token": config.VIBER_AUTH_TOKEN},
        json=payload,
        timeout=10,
    )
    data = resp.json()
    if data.get("status") == 0:
        return f"OK: Message sent to {receiver_id}"
    return f"ERROR: Viber API returned status {data.get('status')}: {data.get('status_message')}"


@tool
def viber_broadcast(user_ids: list[str], text: str) -> str:
    """Broadcast a message to multiple Viber users at once.

    Args:
        user_ids: List of Viber user IDs (max 300 per call).
        text: The message text to broadcast.
    """
    if not config.VIBER_AUTH_TOKEN:
        return "ERROR: VIBER_AUTH_TOKEN not configured"

    payload = {
        "broadcast_list": user_ids[:300],
        "min_api_version": 1,
        "sender": {"name": config.VIBER_SENDER_NAME},
        "type": "text",
        "text": text,
    }

    resp = httpx.post(
        "https://chatapi.viber.com/pa/broadcast_message",
        headers={"X-Viber-Auth-Token": config.VIBER_AUTH_TOKEN},
        json=payload,
        timeout=10,
    )
    data = resp.json()
    if data.get("status") == 0:
        return f"OK: Broadcast sent to {len(user_ids)} users"
    return f"ERROR: {data.get('status_message')}"


# ── WhatsApp Cloud API ──────────────────────────────────────────

@tool
def whatsapp_send_message(phone_number: str, text: str) -> str:
    """Send a WhatsApp message to a phone number via Business API.

    Args:
        phone_number: International phone number with country code (e.g. +38763123456).
        text: The message text to send.
    """
    if not config.WHATSAPP_API_TOKEN:
        return "ERROR: WHATSAPP_API_TOKEN not configured"

    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number.replace("+", "").replace(" ", ""),
        "type": "text",
        "text": {"body": text},
    }

    resp = httpx.post(
        config.WHATSAPP_API_URL,
        headers={"Authorization": f"Bearer {config.WHATSAPP_API_TOKEN}"},
        json=payload,
        timeout=10,
    )
    if resp.status_code == 200:
        return f"OK: WhatsApp message sent to {phone_number}"
    return f"ERROR: WhatsApp API {resp.status_code}: {resp.text[:200]}"


# ── Email (SMTP) ────────────────────────────────────────────────

@tool
def send_email(to_email: str, subject: str, body_html: str, body_text: str = "") -> str:
    """Send an email via SMTP.

    Args:
        to_email: Recipient email address.
        subject: Email subject line.
        body_html: HTML body of the email.
        body_text: Plain text fallback (optional, derived from HTML if empty).
    """
    if not config.SMTP_HOST:
        return "ERROR: SMTP_HOST not configured"

    msg = MIMEMultipart("alternative")
    msg["From"] = config.SMTP_FROM
    msg["To"] = to_email
    msg["Subject"] = subject

    if not body_text:
        # rough strip of HTML tags
        import re
        body_text = re.sub(r"<[^>]+>", "", body_html)

    msg.attach(MIMEText(body_text, "plain", "utf-8"))
    msg.attach(MIMEText(body_html, "html", "utf-8"))

    try:
        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=15) as server:
            server.starttls()
            server.login(config.SMTP_USER, config.SMTP_PASS)
            server.send_message(msg)
        return f"OK: Email sent to {to_email}"
    except Exception as e:
        return f"ERROR: SMTP failed: {e}"


@tool
def send_customer_message(
    channel: str, recipient: str, text: str
) -> str:
    """Send a message to a customer on their preferred channel.
    Automatically routes to Viber, WhatsApp, or Email.

    Args:
        channel: One of 'viber', 'whatsapp', 'email'.
        recipient: Viber user ID, phone number, or email address.
        text: The message to send.
    """
    if channel == "viber":
        return viber_send_message.invoke({"receiver_id": recipient, "text": text})
    elif channel == "whatsapp":
        return whatsapp_send_message.invoke({"phone_number": recipient, "text": text})
    elif channel == "email":
        return send_email.invoke({
            "to_email": recipient,
            "subject": "OpenClaw Balkan",
            "body_html": f"<p>{text}</p>",
        })
    return f"ERROR: Unknown channel '{channel}'"
