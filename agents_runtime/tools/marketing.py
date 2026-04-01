"""
Marketing tools — social media posting, content scheduling, SEO.
Used by the Marketing agent to run autonomous campaigns.
"""
from __future__ import annotations

import json
from datetime import datetime

import httpx
from langchain_core.tools import tool

from agents_runtime import config


# ── Facebook / Instagram ────────────────────────────────────────

@tool
def facebook_create_post(message: str, link: str = "") -> str:
    """Create a post on the Facebook page.

    Args:
        message: Post text content.
        link: Optional URL to include in the post.
    """
    if not config.FACEBOOK_PAGE_TOKEN:
        return "ERROR: FACEBOOK_PAGE_TOKEN not configured"

    payload = {"message": message, "access_token": config.FACEBOOK_PAGE_TOKEN}
    if link:
        payload["link"] = link

    resp = httpx.post(
        "https://graph.facebook.com/v19.0/me/feed",
        data=payload,
        timeout=15,
    )
    if resp.status_code == 200:
        post_id = resp.json().get("id")
        return f"OK: Facebook post created — ID {post_id}"
    return f"ERROR: Facebook API {resp.status_code}: {resp.text[:200]}"


@tool
def instagram_create_post(image_url: str, caption: str) -> str:
    """Create an Instagram post (requires business account + image URL).

    Args:
        image_url: Public URL of the image to post.
        caption: Post caption text.
    """
    if not config.INSTAGRAM_ACCESS_TOKEN:
        return "ERROR: INSTAGRAM_ACCESS_TOKEN not configured"

    # Step 1: Create media container
    resp1 = httpx.post(
        "https://graph.facebook.com/v19.0/me/media",
        data={
            "image_url": image_url,
            "caption": caption,
            "access_token": config.INSTAGRAM_ACCESS_TOKEN,
        },
        timeout=15,
    )
    if resp1.status_code != 200:
        return f"ERROR: Instagram container creation failed: {resp1.text[:200]}"

    container_id = resp1.json().get("id")

    # Step 2: Publish
    resp2 = httpx.post(
        "https://graph.facebook.com/v19.0/me/media_publish",
        data={
            "creation_id": container_id,
            "access_token": config.INSTAGRAM_ACCESS_TOKEN,
        },
        timeout=15,
    )
    if resp2.status_code == 200:
        return f"OK: Instagram post published — ID {resp2.json().get('id')}"
    return f"ERROR: Instagram publish failed: {resp2.text[:200]}"


@tool
def linkedin_create_post(text: str) -> str:
    """Create a LinkedIn post on the company page.

    Args:
        text: Post text content (supports markdown-like formatting).
    """
    if not config.LINKEDIN_ACCESS_TOKEN:
        return "ERROR: LINKEDIN_ACCESS_TOKEN not configured"

    # LinkedIn UGC API
    payload = {
        "author": "urn:li:organization:PLACEHOLDER",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }

    resp = httpx.post(
        "https://api.linkedin.com/v2/ugcPosts",
        headers={
            "Authorization": f"Bearer {config.LINKEDIN_ACCESS_TOKEN}",
            "X-Restli-Protocol-Version": "2.0.0",
        },
        json=payload,
        timeout=15,
    )
    if resp.status_code in (200, 201):
        return f"OK: LinkedIn post published"
    return f"ERROR: LinkedIn API {resp.status_code}: {resp.text[:200]}"


# ── Content Planning ────────────────────────────────────────────

@tool
def generate_content_calendar(
    num_weeks: int = 4,
    focus_topics: list[str] | None = None,
) -> str:
    """Generate a content calendar plan for social media.
    Returns a structured plan — actual posts must be created separately.

    Args:
        num_weeks: Number of weeks to plan ahead.
        focus_topics: List of focus topics/themes for the content.
    """
    if not focus_topics:
        focus_topics = [
            "AI za mali biznis",
            "Automatizacija customer service",
            "Social media marketing AI",
            "Case study: lokalni biznis",
            "Tutorial: kako koristiti AI agente",
        ]

    calendar = []
    platforms = ["facebook", "instagram", "linkedin", "viber_broadcast"]
    days = ["Ponedjeljak", "Srijeda", "Petak"]

    for week in range(1, num_weeks + 1):
        week_plan = {
            "week": week,
            "theme": focus_topics[(week - 1) % len(focus_topics)],
            "posts": [],
        }
        for i, day in enumerate(days):
            week_plan["posts"].append({
                "day": day,
                "platform": platforms[i % len(platforms)],
                "content_type": ["educational", "case_study", "promotional"][i % 3],
                "status": "planned",
            })
        calendar.append(week_plan)

    return json.dumps(calendar, indent=2, ensure_ascii=False)


# ── Analytics ───────────────────────────────────────────────────

@tool
def get_website_analytics() -> str:
    """Get basic website analytics from the server access logs.
    Parses nginx access logs for visitor counts and top pages.
    """
    from agents_runtime.tools.ops import _ssh

    result = _ssh(
        "cat /var/log/nginx/access.log 2>/dev/null | "
        "awk '{print $7}' | sort | uniq -c | sort -rn | head -20 && "
        "echo '---TOTAL---' && "
        "wc -l < /var/log/nginx/access.log 2>/dev/null"
    )
    return f"Website traffic (from nginx logs):\n{result}"


@tool
def get_lead_conversion_stats() -> str:
    """Get lead-to-order conversion statistics from the database."""
    from agents_runtime.tools.ops import _ssh

    result = _ssh(
        "docker exec openclaw-app node -e \""
        "const db = require('./src/db.js');"
        "const leads = db.listLeads ? db.listLeads().length : '?';"
        "const orders = db.listOrders ? db.listOrders().length : '?';"
        "console.log(JSON.stringify({leads, orders, conversion: orders > 0 && leads > 0 ? (orders/leads*100).toFixed(1)+'%' : 'N/A'}));"
        "\""
    )
    return f"Conversion stats: {result}"
