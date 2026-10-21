#!/usr/bin/env python3
"""
4_reddit_radar.py

Scan fresh troubleshooting posts from Reddit, match them to the local error database,
write a human-like reply with Gemini, and render a local dashboard for copy/open workflows.

This version uses a 3-layer fallback strategy to reduce HTTP 403 blocking:
1) curl_cffi RSS on old.reddit.com
2) curl_cffi JSON on old.reddit.com
3) PullPush / Serper external fallback
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import time
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Any

import feedparser
import requests
from curl_cffi import requests as cffi_requests

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    def load_dotenv(*_args, **_kwargs):
        return False

try:
    from google import genai
except ImportError:  # pragma: no cover
    genai = None

try:
    from slugify import slugify
except ImportError:  # pragma: no cover
    def slugify(value: str) -> str:
        return re.sub(r"[^a-z0-9]+", "-", str(value).strip().lower()).strip("-") or "item"

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
ERRORS_DB_PATH = DATA_DIR / "errors_db.json"
PROCESSED_PATH = DATA_DIR / "processed_reddit_ids.json"
SITE_DOMAIN = os.getenv("SITE_DOMAIN", "https://gettinytool.com").rstrip("/")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY and genai else None

SUBREDDITS = [
    "appliancerepair",
    "hvacadvice",
    "pools",
    "MechanicAdvice",
    "OBD2",
    "Cartalk",
    "espresso",
    "BambuLab",
    "Generator",
    "RVLiving",
    "Plumbing",
    "HomeImprovement",
]

BOT_UA = "windows:fixmycode.radar:v1.2 (by /u/fixmycode_tech)"
HEADERS = {
    "User-Agent": BOT_UA,
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
}


def ensure_data_file() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not ERRORS_DB_PATH.exists():
        raise FileNotFoundError(f"Missing error database: {ERRORS_DB_PATH}")
    PROCESSED_PATH.touch(exist_ok=True)
    try:
        with open(PROCESSED_PATH, "r", encoding="utf-8") as f:
            json.load(f)
    except Exception:
        with open(PROCESSED_PATH, "w", encoding="utf-8") as f:
            json.dump([], f)


def load_errors_db() -> list[dict[str, Any]]:
    ensure_data_file()
    with open(ERRORS_DB_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else []


def load_processed_ids() -> set[str]:
    ensure_data_file()
    try:
        with open(PROCESSED_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return set(data) if isinstance(data, list) else set()
    except FileNotFoundError:
        return set()


def save_processed_ids(processed_ids: set[str]) -> None:
    with open(PROCESSED_PATH, "w", encoding="utf-8") as f:
        json.dump(sorted(processed_ids), f, indent=2)


def strip_html(text: str) -> str:
    cleaned = re.sub(r"<[^>]+>", " ", text or "")
    cleaned = html.unescape(cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def build_item_keywords(item: dict[str, Any]) -> list[str]:
    parts = [
        item.get("brand", ""),
        item.get("model_series", ""),
        item.get("short_symptom", ""),
        item.get("primary_part_name", ""),
        item.get("plain_english_meaning", ""),
        item.get("equipment_type", ""),
    ]
    keywords: list[str] = []
    for piece in parts:
        for word in re.split(r"[^a-z0-9]+", str(piece).lower()):
            if len(word) > 3 and word not in {"with", "that", "this", "from", "code", "issue", "fault", "does"}:
                keywords.append(word)
    return keywords


def find_best_match(post_title: str, post_body: str, errors_db: list[dict[str, Any]]) -> dict[str, Any] | None:
    full_text = f"{post_title} {post_body}".lower()
    best_item = None
    best_score = 0

    for item in errors_db:
        score = 0
        error_code = str(item.get("error_code", "")).lower().strip()
        brand = str(item.get("brand", "")).lower().strip()
        short_symptom = str(item.get("short_symptom", "")).lower().strip()
        part_name = str(item.get("primary_part_name", "")).lower().strip()

        if len(error_code) >= 2 and re.search(rf"\b{re.escape(error_code)}\b", full_text):
            score += 8
        if error_code.startswith(("p0", "p1", "p2", "c0", "b0", "u0", "e0", "e1", "e2", "e3", "e4", "e5")) and error_code in full_text:
            score += 8
        if brand and brand in full_text:
            score += 3
        if short_symptom and short_symptom in full_text:
            score += 2
        if part_name and part_name in full_text:
            score += 2

        keyword_hits = 0
        for kw in build_item_keywords(item):
            if kw in full_text:
                keyword_hits += 1
        if keyword_hits:
            score += min(keyword_hits, 4)

        if score > best_score and score >= 3:
            best_score = score
            best_item = item

    return best_item


def format_fallback_reply(matched_item: dict[str, Any]) -> str:
    brand = str(matched_item.get("brand", "brand"))
    brand_slug = slugify(brand)
    target_url = f"{SITE_DOMAIN}/{brand_slug}/{matched_item.get('slug', 'guide')}/"
    part = matched_item.get("primary_part_name", "part")
    step = matched_item.get("diagnostic_and_fix_steps", ["Check the wiring and connector before replacing the part."])[0]
    return (
        f"I’ve seen this same pattern before on a similar unit. The real culprit is usually the {part}, and it tends to fail when the signal drifts or the circuit loses ground. "
        f"First thing I’d check is {step.lower()} That lines up with your symptoms, and the exact OEM breakdown is here: {target_url}"
    )


def generate_human_reply(post_title: str, post_body: str, matched_item: dict[str, Any]) -> str:
    brand = str(matched_item.get("brand", "brand"))
    brand_slug = slugify(brand)
    target_url = f"{SITE_DOMAIN}/{brand_slug}/{matched_item.get('slug', 'guide')}/"

    prompt = f"""
    Write a short, authentic Reddit comment replying to a troubleshooting post.

    USER POST TITLE: {post_title}
    USER POST TEXT: {post_body[:900]}

    MATCHED TECHNICAL DATA:
    - Brand/System: {matched_item.get('brand')} ({matched_item.get('model_series')})
    - Error Code: {matched_item.get('error_code')} ({matched_item.get('short_symptom')})
    - Root Cause: {matched_item.get('plain_english_meaning')}
    - Key Fix Step: {matched_item.get('diagnostic_and_fix_steps', [''])[0]}
    - Main Replacement Part: {matched_item.get('primary_part_name')} (OEM: {matched_item.get('oem_part_number')})
    - Reference Guide Link: {target_url}

    STYLE RULES:
    1. Sound like a real tech/DIYer speaking from experience.
    2. Keep it casual and concise: 3-5 sentences max.
    3. Say the actual problem in plain English and mention one quick visual/test step.
    4. Name the exact part and naturally include the link {target_url} as a reference.
    5. No greetings, no bullet list, no raw Amazon links.
    """

    if not client:
        return format_fallback_reply(matched_item)

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={"temperature": 0.7, "max_output_tokens": 220},
        )
        text = getattr(response, "text", "")
        if not text:
            return format_fallback_reply(matched_item)
        cleaned = text.strip()
        if len(cleaned) < 80:
            return format_fallback_reply(matched_item)
        return cleaned
    except Exception as exc:  # pragma: no cover
        print(f"Gemini generation failed: {exc}")
        return format_fallback_reply(matched_item)


def maybe_auto_post_reply(comment_text: str, post_url: str, subreddit: str) -> bool:
    try:
        import praw
    except ImportError:  # pragma: no cover
        return False

    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    username = os.getenv("REDDIT_USERNAME")
    password = os.getenv("REDDIT_PASSWORD")
    if not all([client_id, client_secret, username, password]):
        return False

    try:
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password,
            user_agent=f"reddit-radar/1.0 by {username}",
        )
        reddit.submission(url=post_url).reply(comment_text)
        print(f"[AUTO-POST] Replied to {post_url} on r/{subreddit}")
        return True
    except Exception as exc:  # pragma: no cover
        print(f"PRAW auto-post failed for {post_url}: {exc}")
        return False


def build_html_dashboard(leads: list[dict[str, Any]]) -> str:
    cards: list[str] = []
    for idx, lead in enumerate(leads):
        safe_title = html.escape(str(lead.get("title", "")))
        safe_selftext = html.escape(str(lead.get("selftext", "")))
        safe_reply = html.escape(str(lead.get("reply_text", "")))
        safe_subreddit = html.escape(str(lead.get("subreddit", "")))
        safe_brand = html.escape(str(lead.get("matched_brand", "")))
        safe_code = html.escape(str(lead.get("matched_code", "")))
        safe_url = html.escape(str(lead.get("post_url", "")))
        safe_target = html.escape(str(lead.get("target_url", "")))
        created_time = html.escape(str(lead.get("created_time", "")))

        cards.append(
            f"""
            <div class=\"bg-slate-800 border border-slate-700 rounded-xl p-5 mb-4 shadow-lg\">
                <div class=\"flex justify-between items-center mb-2\">
                    <span class=\"px-2.5 py-1 bg-orange-500/20 text-orange-400 text-xs font-mono rounded\">r/{safe_subreddit} • Matched: {safe_code} ({safe_brand})</span>
                    <span class=\"text-slate-400 text-xs\">{created_time}</span>
                </div>
                <h3 class=\"text-lg font-bold text-white mb-2\">{safe_title}</h3>
                <p class=\"text-slate-400 text-sm mb-3 line-clamp-2\">{safe_selftext}</p>
                <div class=\"bg-slate-900 border border-slate-700 rounded-lg p-3 mb-3\">
                    <textarea id=\"reply-{idx}\" rows=\"4\" class=\"w-full bg-transparent text-emerald-300 text-sm font-sans focus:outline-none\">{safe_reply}</textarea>
                </div>
                <div class=\"flex flex-wrap gap-3\">
                    <button onclick=\"copyAndOpen('reply-{idx}', '{safe_url}')\" class=\"bg-orange-500 hover:bg-orange-600 text-white font-semibold px-4 py-2 rounded-lg text-sm transition cursor-pointer\">
                        ⚡ 1-Click Copy Reply & Open Reddit Thread →
                    </button>
                    <a href=\"{safe_target}\" target=\"_blank\" class=\"bg-slate-700 hover:bg-slate-600 text-slate-200 px-4 py-2 rounded-lg text-sm\">
                        Preview Our Fix Page
                    </a>
                </div>
            </div>
            """
        )

    body_cards = "\n".join(cards) if cards else '<p class="text-slate-400">No fresh Reddit posts are available right now. The radar will continue polling once the environment stops returning 403s.</p>'
    html_doc = f"""<!DOCTYPE html>
    <html lang=\"en\">
    <head>
        <meta charset=\"UTF-8\">
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
        <title>FixMyCode — Reddit Radar</title>
        <script src=\"https://cdn.tailwindcss.com\"></script>
        <style>
            .line-clamp-2 {{
                display: -webkit-box;
                -webkit-line-clamp: 2;
                -webkit-box-orient: vertical;
                overflow: hidden;
            }}
        </style>
    </head>
    <body class=\"bg-slate-950 text-slate-100 p-8 max-w-5xl mx-auto\">
        <div class=\"flex justify-between items-center mb-8 border-b border-slate-800 pb-4\">
            <div>
                <h1 class=\"text-2xl font-bold text-white\">🎯 FixMyCode Reddit Radar</h1>
                <p class=\"text-slate-400 text-sm\">Live troubleshooting threads matched to our repair guides</p>
            </div>
            <span class=\"bg-emerald-500/20 text-emerald-400 px-3 py-1 rounded-full text-sm font-mono\">{len(leads)} Ready</span>
        </div>
        {body_cards}
        <script>
            function copyAndOpen(textareaId, url) {{
                const text = document.getElementById(textareaId).value;
                navigator.clipboard.writeText(text).catch(() => console.warn('Clipboard copy blocked by browser'));
                window.open(url, '_blank');
            }}
        </script>
    </body>
    </html>"""

    dashboard_path = (BASE_DIR / "data" / "reddit_dashboard.html").resolve()
    dashboard_path.parent.mkdir(parents=True, exist_ok=True)
    dashboard_path.write_text(html_doc, encoding="utf-8")
    return str(dashboard_path)


def normalize_reddit_item(item: dict[str, Any]) -> dict[str, Any]:
    data = item.get("data", item)
    title = str(data.get("title", data.get("name", ""))).strip()
    selftext = str(data.get("selftext", data.get("summary", data.get("description", "")))).strip()
    subreddit = str(data.get("subreddit", data.get("subreddit_name_prefixed", data.get("category", "")))).strip().replace("r/", "")
    permalink = str(data.get("permalink", data.get("link", ""))).strip()
    created_utc = int(data.get("created_utc", time.time()))
    url = str(data.get("url", data.get("link", "https://www.reddit.com" + permalink if permalink else ""))).strip()
    return {
        "id": str(data.get("id") or data.get("name") or url or permalink or title),
        "title": title,
        "selftext": selftext,
        "subreddit": subreddit,
        "permalink": permalink,
        "created_utc": created_utc,
        "url": url,
    }


def fetch_from_rss(sub_query: str) -> list[dict[str, Any]]:
    rss_url = f"https://old.reddit.com/r/{sub_query}/new/.rss?limit=100"
    try:
        response = cffi_requests.get(
            rss_url,
            impersonate="chrome124",
            headers={**HEADERS, "Accept": "application/rss+xml, application/xml, text/xml, */*"},
            timeout=25,
        )
        if response.status_code != 200 or not response.text:
            return []
        feed = feedparser.parse(response.text)
        entries: list[dict[str, Any]] = []
        for entry in getattr(feed, "entries", []):
            title = strip_html(entry.get("title", ""))
            summary = strip_html(entry.get("summary", entry.get("description", "")))
            link = entry.get("link", "")
            if not title and not summary:
                continue
            category = ""
            tags = entry.get("tags", [])
            if isinstance(tags, list) and tags:
                category = str(tags[0].get("term", ""))
            category = category or str(entry.get("category", "")).strip()
            entries.append({
                "id": str(entry.get("id", link or title)),
                "title": title,
                "selftext": summary,
                "subreddit": category or "reddit",
                "permalink": link,
                "created_utc": int(time.time()),
                "url": link,
            })
        return entries
    except Exception as exc:  # pragma: no cover
        print(f"RSS fallback failed: {exc}")
        return []


def fetch_from_old_json(sub_query: str) -> list[dict[str, Any]]:
    url = f"https://old.reddit.com/r/{sub_query}/new.json?limit=100"
    try:
        response = cffi_requests.get(
            url,
            impersonate="chrome124",
            headers={**HEADERS, "Accept": "application/json"},
            timeout=25,
        )
        if response.status_code != 200:
            return []
        payload = response.json() if hasattr(response, "json") else json.loads(response.text)
        children = payload.get("data", {}).get("children", [])
        return [normalize_reddit_item(item) for item in children]
    except Exception as exc:  # pragma: no cover
        print(f"old.reddit JSON fetch failed: {exc}")
        return []


def fetch_from_pullpush(sub_query: str) -> list[dict[str, Any]]:
    url = "https://api.pullpush.io/reddit/search/submission/"
    params = {
        "subreddit": ",".join(SUBREDDITS),
        "size": 100,
        "sort": "desc",
    }
    try:
        response = requests.get(url, params=params, headers={**HEADERS, "Accept": "application/json"}, timeout=25)
        if response.status_code != 200:
            return []
        payload = response.json() if hasattr(response, "json") else json.loads(response.text)
        items = payload.get("data", payload.get("results", payload))
        if isinstance(items, dict):
            items = items.get("children", [])
        posts = []
        for item in items:
            if not isinstance(item, dict):
                continue
            entry = normalize_reddit_item(item)
            if entry.get("title"):
                posts.append(entry)
        return posts
    except Exception as exc:  # pragma: no cover
        print(f"PullPush fallback failed: {exc}")
        return []


def fetch_from_serper() -> list[dict[str, Any]]:
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        return []
    payload = {
        "q": 'site:reddit.com/r/appliancerepair OR site:reddit.com/r/hvacadvice OR site:reddit.com/r/pools OR site:reddit.com/r/MechanicAdvice "error" OR "code" OR "P0420" OR "P0171" OR "E24"',
        "num": 10,
        "tbs": "qdr:d",
    }
    try:
        response = requests.post(
            "https://google.serper.dev/search",
            json=payload,
            headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
            timeout=25,
        )
        if response.status_code != 200:
            return []
        data = response.json()
        posts = []
        for item in data.get("organic", []):
            link = item.get("link", "")
            if not link:
                continue
            posts.append({
                "id": link,
                "title": item.get("title", ""),
                "selftext": item.get("snippet", ""),
                "subreddit": "serper",
                "permalink": link,
                "created_utc": int(time.time()),
                "url": link,
            })
        return posts
    except Exception as exc:  # pragma: no cover
        print(f"Serper fallback failed: {exc}")
        return []


def fetch_reddit_posts() -> list[dict[str, Any]]:
    sub_query = "+".join(SUBREDDITS)
    sources: list[list[dict[str, Any]]] = []

    rss_posts = fetch_from_rss(sub_query)
    if rss_posts:
        sources.append(rss_posts)

    old_json_posts = fetch_from_old_json(sub_query)
    if old_json_posts:
        sources.append(old_json_posts)

    pullpush_posts = fetch_from_pullpush(sub_query)
    if pullpush_posts:
        sources.append(pullpush_posts)

    serper_posts = fetch_from_serper()
    if serper_posts:
        sources.append(serper_posts)

    merged: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for source in sources:
        for item in source:
            item_id = str(item.get("id") or item.get("url") or item.get("permalink") or "")
            if not item_id or item_id in seen_ids:
                continue
            seen_ids.add(item_id)
            merged.append(item)

    return merged


def scan_posts(args: argparse.Namespace) -> list[dict[str, Any]]:
    errors_db = load_errors_db()
    processed_ids = load_processed_ids()
    reddit_posts = fetch_reddit_posts()
    leads: list[dict[str, Any]] = []

    for item in reddit_posts:
        post_id = str(item.get("id") or item.get("url") or item.get("permalink") or "")
        if not post_id or post_id in processed_ids:
            continue

        title = str(item.get("title", "")).strip()
        selftext = str(item.get("selftext", "")).strip()
        subreddit = str(item.get("subreddit", "")).strip().replace("r/", "")
        permalink = str(item.get("permalink", "")).strip()
        post_url = str(item.get("url") or (f"https://www.reddit.com{permalink}" if permalink else "")).strip()

        matched = find_best_match(title, selftext, errors_db)
        if not matched:
            continue

        if len(leads) >= (args.max_leads or 15):
            break

        reply = generate_human_reply(title, selftext, matched)
        brand_slug = slugify(str(matched.get("brand", "brand")))
        target_url = f"{SITE_DOMAIN}/{brand_slug}/{matched.get('slug', 'guide')}/"
        leads.append({
            "subreddit": subreddit or "reddit",
            "title": title,
            "selftext": selftext[:300],
            "post_url": post_url,
            "matched_code": matched.get("error_code", ""),
            "matched_brand": matched.get("brand", ""),
            "target_url": target_url,
            "reply_text": reply,
            "created_time": datetime.fromtimestamp(int(item.get("created_utc", time.time()))).strftime("%H:%M:%S"),
        })
        processed_ids.add(post_id)

    save_processed_ids(processed_ids)
    return leads


def main() -> None:
    parser = argparse.ArgumentParser(description="Reddit radar for troubleshooting post matching.")
    parser.add_argument("--max-leads", type=int, default=15, help="Maximum matched leads to include in dashboard.")
    parser.add_argument("--no-open", action="store_true", help="Do not open the generated HTML dashboard automatically.")
    parser.add_argument("--post", action="store_true", help="Auto-post replies via PRAW when Reddit credentials are configured.")
    args = parser.parse_args()

    leads = scan_posts(args)
    dashboard_path = build_html_dashboard(leads)
    print(f"\n=== Radar Complete! Found {len(leads)} matched threads. Dashboard: {dashboard_path} ===")

    if not args.no_open:
        try:
            webbrowser.open(f"file://{dashboard_path}")
        except Exception:
            pass

    if args.post:
        for lead in leads:
            maybe_auto_post_reply(lead["reply_text"], lead["post_url"], lead["subreddit"])


if __name__ == "__main__":
    main()
