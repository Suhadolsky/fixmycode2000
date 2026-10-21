#!/usr/bin/env python3
"""
1_harvester.py - Automated PDF Service Manual Harvester
Finds and downloads service manuals via the Serper.dev API.
"""

import argparse
import hashlib
import logging
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set
from urllib.parse import unquote, urlparse

import requests
from dotenv import load_dotenv
from slugify import slugify
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("fixmycode.harvester")

# Project Directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_PDFS_DIR = DATA_DIR / "raw_pdfs"
PROCESSED_HASHES_FILE = DATA_DIR / "processed_hashes.json"

# Default Target Brands & Equipment Categories
DEFAULT_TARGETS: List[str] = [
    "Pentair pool heater",
    "Bosch dishwasher",
    "Breville espresso",
    "Hayward pool pump",
    "Navien tankless water heater",
]

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 FixMyCodeHarvester/1.0"
)

MAX_PDF_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB
REQUEST_TIMEOUT_SECONDS = 15


def load_environment() -> str:
    """Load and validate required environment variables."""
    load_dotenv(BASE_DIR / ".env")
    serper_api_key = os.getenv("SERPER_API_KEY")
    if not serper_api_key:
        logger.warning(
            "SERPER_API_KEY environment variable is missing or empty. "
            "Please configure it in fixmycode/.env"
        )
    return serper_api_key or ""


def calculate_file_md5(file_path: Path) -> str:
    """Calculate the MD5 hash of an existing file."""
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def get_existing_hashes() -> Set[str]:
    """Collect MD5 hashes from already downloaded and processed files."""
    existing_hashes: Set[str] = set()

    # Load recorded hashes from JSON if exists
    if PROCESSED_HASHES_FILE.exists():
        try:
            import json

            with open(PROCESSED_HASHES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    existing_hashes.update(data.keys())
        except Exception as e:
            logger.warning(f"Could not read {PROCESSED_HASHES_FILE}: {e}")

    # Check files currently sitting in raw_pdfs
    if RAW_PDFS_DIR.exists():
        for pdf_path in RAW_PDFS_DIR.glob("*.pdf"):
            try:
                existing_hashes.add(calculate_file_md5(pdf_path))
            except Exception as e:
                logger.debug(f"Failed to hash {pdf_path}: {e}")

    return existing_hashes


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((requests.RequestException,)),
    reraise=True,
)
def query_serper(search_term: str, api_key: str, num_results: int = 10) -> List[Dict[str, str]]:
    """Query Serper.dev Google Search API with retry logic."""
    url = "https://google.serper.dev/search"
    query_str = (
        f'filetype:pdf ("service manual" OR "tech sheet" OR "troubleshooting") '
        f'("error code" OR "fault code") {search_term}'
    )

    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "q": query_str,
        "num": num_results,
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    data = response.json()
    return data.get("organic", [])


def sanitize_filename(brand_category: str, url: str, title: str) -> str:
    """Generate a clean, filesystem-safe filename for a downloaded PDF."""
    parsed = urlparse(url)
    raw_name = Path(unquote(parsed.path)).stem

    # Clean raw_name
    raw_name = re.sub(r"[^\w\s-]", "", raw_name).strip()
    if not raw_name or len(raw_name) < 3:
        raw_name = slugify(title)[:40] if title else "manual"

    brand_slug = slugify(brand_category)[:30]
    file_slug = slugify(raw_name)[:40]
    url_hash = hashlib.sha256(url.encode("utf-8")).hexdigest()[:6]

    return f"{brand_slug}_{file_slug}_{url_hash}.pdf"


def validate_pdf_url(url: str, session: requests.Session) -> tuple[bool, Optional[int]]:
    """
    Validate that the URL points to a PDF and check Content-Length.
    Returns (is_valid, content_length).
    """
    parsed = urlparse(url)
    path_is_pdf = parsed.path.lower().endswith(".pdf")

    try:
        head_resp = session.head(
            url,
            allow_redirects=True,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        content_type = head_resp.headers.get("Content-Type", "").lower()
        content_length_header = head_resp.headers.get("Content-Length")
        content_length = int(content_length_header) if content_length_header and content_length_header.isdigit() else None

        if head_resp.status_code == 200:
            if "application/pdf" in content_type or path_is_pdf:
                return True, content_length

        # If HEAD returned 405 Method Not Allowed or 403 Forbidden, allow fallback
        if head_resp.status_code in (403, 405) and path_is_pdf:
            return True, None

    except requests.RequestException as e:
        logger.debug(f"HEAD request failed for {url}: {e}")
        if path_is_pdf:
            return True, None

    return path_is_pdf, None


def download_pdf(
    url: str,
    target_path: Path,
    session: requests.Session,
    known_hashes: Set[str],
) -> Optional[str]:
    """
    Download a PDF into target_path with size enforcement and hash deduplication.
    Returns the file's MD5 hash on success, or None on failure/skip.
    """
    temp_target = target_path.with_suffix(".tmp")
    hasher = hashlib.md5()
    bytes_downloaded = 0

    try:
        with session.get(url, stream=True, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            response.raise_for_status()

            # Verify Content-Type
            content_type = response.headers.get("Content-Type", "").lower()
            if "application/pdf" not in content_type and not urlparse(url).path.lower().endswith(".pdf"):
                logger.info(f"Skipping non-PDF Content-Type '{content_type}': {url}")
                return None

            # Verify Content-Length if provided
            content_length = response.headers.get("Content-Length")
            if content_length and content_length.isdigit():
                if int(content_length) > MAX_PDF_SIZE_BYTES:
                    logger.info(f"Skipping PDF exceeding 25MB ({int(content_length)} bytes): {url}")
                    return None

            # Stream download to disk and compute MD5 concurrently
            with open(temp_target, "wb") as f:
                for chunk in response.iter_content(chunk_size=16384):
                    if not chunk:
                        continue
                    bytes_downloaded += len(chunk)
                    if bytes_downloaded > MAX_PDF_SIZE_BYTES:
                        logger.warning(f"Aborting download: exceeded 25MB limit mid-stream for {url}")
                        temp_target.unlink(missing_ok=True)
                        return None
                    hasher.update(chunk)
                    f.write(chunk)

            file_md5 = hasher.hexdigest()

            # Deduplication check by MD5 hash
            if file_md5 in known_hashes:
                logger.info(f"Deduplication: MD5 {file_md5} already exists. Skipping {url}")
                temp_target.unlink(missing_ok=True)
                return None

            # Move temp file to final location
            temp_target.replace(target_path)
            known_hashes.add(file_md5)
            logger.info(f"Saved: {target_path.name} ({bytes_downloaded / 1024:.1f} KB, MD5: {file_md5})")
            return file_md5

    except requests.RequestException as e:
        logger.warning(f"Failed to download {url}: {e}")
        temp_target.unlink(missing_ok=True)
        return None
    except Exception as e:
        logger.error(f"Unexpected error downloading {url}: {e}")
        temp_target.unlink(missing_ok=True)
        return None


def run_harvester(
    targets: Optional[List[str]] = None,
    num_per_target: int = 10,
) -> None:
    """Execute the harvesting pipeline across target equipment categories."""
    api_key = load_environment()
    if not api_key:
        logger.error("Cannot run harvester without a valid SERPER_API_KEY in .env")
        return

    RAW_PDFS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    target_list = targets or DEFAULT_TARGETS
    logger.info(f"Starting harvest for {len(target_list)} target equipment categories...")

    known_hashes = get_existing_hashes()
    logger.info(f"Loaded {len(known_hashes)} existing hashes for deduplication.")

    session = requests.Session()
    session.headers.update({"User-Agent": DEFAULT_USER_AGENT})

    total_downloaded = 0
    total_skipped = 0

    for target in target_list:
        logger.info(f"\nSearching manuals for: '{target}'")
        try:
            results = query_serper(target, api_key, num_results=num_per_target)
        except Exception as e:
            logger.error(f"Search query failed for '{target}': {e}")
            continue

        logger.info(f"Found {len(results)} search results for '{target}'")

        for item in tqdm(results, desc=f"Processing {target[:20]}"):
            url = item.get("link", "")
            title = item.get("title", "")
            if not url:
                continue

            # Validate URL and size
            is_valid, length = validate_pdf_url(url, session)
            if not is_valid:
                continue

            if length and length > MAX_PDF_SIZE_BYTES:
                logger.info(f"Skipping {url} (Content-Length: {length / (1024*1024):.2f} MB > 25 MB)")
                total_skipped += 1
                continue

            filename = sanitize_filename(target, url, title)
            target_path = RAW_PDFS_DIR / filename

            if target_path.exists():
                logger.info(f"File already downloaded: {filename}")
                continue

            md5 = download_pdf(url, target_path, session, known_hashes)
            if md5:
                total_downloaded += 1
            else:
                total_skipped += 1

    logger.info(
        f"\nHarvester Run Finished. Downloaded: {total_downloaded}, "
        f"Skipped/Deduplicated: {total_skipped}. Total files in {RAW_PDFS_DIR}: {len(list(RAW_PDFS_DIR.glob('*.pdf')))}"
    )


def main():
    parser = argparse.ArgumentParser(description="FixMyCode PDF Service Manual Harvester")
    parser.add_argument(
        "--targets",
        nargs="+",
        help="List of brand and equipment categories (e.g. --targets 'Bosch dishwasher' 'Pentair pool heater')",
    )
    parser.add_argument(
        "--num",
        type=int,
        default=10,
        help="Number of search results to fetch per target (default: 10)",
    )
    args = parser.parse_args()

    run_harvester(targets=args.targets, num_per_target=args.num)


if __name__ == "__main__":
    main()
