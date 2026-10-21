#!/usr/bin/env python3
"""
3_indexnow.py - IndexNow Instant Search Engine Indexing
Pings Bing, Yandex, and IndexNow API with all pSEO URLs.
Automatically writes verification file site/public/{INDEXNOW_KEY}.txt.
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import List, Optional, Set
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("fixmycode.indexnow")

# Directory paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SITE_DIR = BASE_DIR / "site"
PUBLIC_DIR = SITE_DIR / "public"
SITE_DATA_DIR = SITE_DIR / "src" / "data"
SITE_ERRORS_DB = SITE_DATA_DIR / "errors_db.json"
DATA_ERRORS_DB = DATA_DIR / "errors_db.json"

INDEXNOW_ENDPOINT = "https://api.indexnow.org/indexnow"
REQUEST_TIMEOUT = 15


def load_environment() -> tuple[str, str]:
    """Load and validate required environment variables."""
    load_dotenv(BASE_DIR / ".env")
    key = os.getenv("INDEXNOW_KEY", "").strip()
    domain = os.getenv("SITE_DOMAIN", "https://gettinytool.com").strip().rstrip("/")
    return key, domain


def ensure_indexnow_verification_file(key: str) -> Optional[Path]:
    """
    Automatically write the verification file to site/public/{INDEXNOW_KEY}.txt
    containing the key string before the Astro build runs.
    """
    if not key:
        logger.warning("No INDEXNOW_KEY provided; skipping verification file creation.")
        return None

    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    key_file = PUBLIC_DIR / f"{key}.txt"

    try:
        key_file.write_text(key, encoding="utf-8")
        logger.info(f"Generated IndexNow verification file: {key_file.name}")
        return key_file
    except Exception as e:
        logger.error(f"Failed to write verification file {key_file}: {e}")
        return None


def collect_site_urls(site_domain: str) -> List[str]:
    """
    Parse all generated URLs from site/src/data/errors_db.json (plus brand hub URLs and home page).
    """
    db_file = SITE_ERRORS_DB if SITE_ERRORS_DB.exists() else DATA_ERRORS_DB
    if not db_file.exists():
        logger.error(f"Error database not found at {db_file}")
        return []

    try:
        with open(db_file, "r", encoding="utf-8") as f:
            records = json.load(f)
    except Exception as e:
        logger.error(f"Failed to read {db_file}: {e}")
        return []

    if not isinstance(records, list):
        logger.error(f"Unexpected JSON structure in {db_file}")
        return []

    urls: List[str] = [f"{site_domain}/"]
    brands_seen: Set[str] = set()

    for item in records:
        brand_slug = item.get("brand_slug")
        if not brand_slug and "brand" in item:
            from slugify import slugify

            brand_slug = slugify(item["brand"])

        slug = item.get("slug")

        # Brand hub page
        if brand_slug and brand_slug not in brands_seen:
            urls.append(f"{site_domain}/{brand_slug}/")
            brands_seen.add(brand_slug)

        # Money fix page
        if brand_slug and slug:
            urls.append(f"{site_domain}/{brand_slug}/{slug}/")

    logger.info(f"Extracted {len(urls)} total canonical URLs from {db_file.name}")
    return urls


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((requests.RequestException,)),
    reraise=True,
)
def post_indexnow_batch(
    host: str,
    key: str,
    key_location: str,
    url_batch: List[str],
) -> int:
    """Submit a batch of up to 10,000 URLs to IndexNow with exponential retry logic."""
    payload = {
        "host": host,
        "key": key,
        "keyLocation": key_location,
        "urlList": url_batch,
    }
    headers = {"Content-Type": "application/json; charset=utf-8"}

    response = requests.post(
        INDEXNOW_ENDPOINT,
        json=payload,
        headers=headers,
        timeout=REQUEST_TIMEOUT,
    )

    if response.status_code in (200, 202):
        logger.info(
            f"IndexNow Accepted {len(url_batch)} URLs (HTTP {response.status_code})."
        )
        return response.status_code

    logger.warning(
        f"IndexNow API returned HTTP {response.status_code}: {response.text}"
    )
    response.raise_for_status()
    return response.status_code


def run_indexnow(
    dry_run: bool = False,
    override_key: Optional[str] = None,
    write_file_only: bool = False,
) -> bool:
    """Execute IndexNow setup and submission."""
    env_key, site_domain = load_environment()
    key = override_key or env_key

    # 1. Automatically write verification file to site/public/{INDEXNOW_KEY}.txt
    if key:
        ensure_indexnow_verification_file(key)

    if write_file_only:
        return True

    # 2. Extract domain and host
    parsed = urlparse(site_domain)
    host = parsed.netloc or parsed.path
    key_location = f"{site_domain}/{key}.txt" if key else f"{site_domain}/key.txt"

    # 3. Parse all generated URLs from errors_db.json
    urls = collect_site_urls(site_domain)

    if not urls:
        logger.warning("No URLs found to submit.")
        return False

    if dry_run or not key:
        logger.info("[DRY RUN / NO KEY] IndexNow Submission Preview:")
        logger.info(f"  Target Host: {host}")
        logger.info(f"  Key Location: {key_location}")
        logger.info(f"  Total URLs to index: {len(urls)}")
        for idx, u in enumerate(urls[:5], 1):
            logger.info(f"    {idx}. {u}")
        if len(urls) > 5:
            logger.info(f"    ... and {len(urls) - 5} more URLs.")

        if not key:
            logger.warning(
                "Skipping live POST request because INDEXNOW_KEY is not configured in .env."
            )
        return True

    # 4. Batch submission (up to 10,000 URLs per IndexNow specification)
    batch_size = 10000
    success = True
    for i in range(0, len(urls), batch_size):
        batch = urls[i : i + batch_size]
        logger.info(
            f"Pinging IndexNow for batch {i // batch_size + 1} ({len(batch)} URLs)..."
        )
        try:
            post_indexnow_batch(host, key, key_location, batch)
        except Exception as e:
            logger.error(f"Failed to submit batch to IndexNow: {e}")
            success = False

    return success


def main():
    parser = argparse.ArgumentParser(description="FixMyCode IndexNow Batch Submitter")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate IndexNow ping and display URLs without making HTTP requests",
    )
    parser.add_argument(
        "--key",
        type=str,
        help="Override INDEXNOW_KEY environment variable",
    )
    parser.add_argument(
        "--write-key-only",
        action="store_true",
        help="Only write the public/{INDEXNOW_KEY}.txt file and exit",
    )
    args = parser.parse_args()

    run_indexnow(
        dry_run=args.dry_run,
        override_key=args.key,
        write_file_only=args.write_key_only,
    )


if __name__ == "__main__":
    main()
