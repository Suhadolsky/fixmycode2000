#!/usr/bin/env python3
"""
run_pipeline.py - Master Orchestrator for FixMyCode pSEO Platform

CLI Modes:
  python run_pipeline.py --demo
    -> Seeds 10 realistic test error codes via 2_extractor.py --seed-demo
    -> Builds the Astro static site (npm run build)
    -> Starts the local preview server (http://localhost:4321/)

  python run_pipeline.py --production
    -> Discovers manuals via 1_harvester.py
    -> Extracts structured data via 2_extractor.py
    -> Generates IndexNow verification key file
    -> Compiles Astro 5 static site
    -> Submits URLs to Bing/Yandex via 3_indexnow.py
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
if (BASE_DIR / "fixmycode").exists():
    REPO_ROOT = BASE_DIR / "fixmycode"
else:
    REPO_ROOT = BASE_DIR

PIPELINE_DIR = REPO_ROOT / "pipeline"
SITE_DIR = REPO_ROOT / "site"
DATA_DIR = REPO_ROOT / "data"
ERRORS_DB = DATA_DIR / "errors_db.json"


def print_banner(step_title: str):
    """Print high-visibility terminal section header."""
    print("\n" + "=" * 70)
    print(f"  FixMyCode: {step_title.upper()}")
    print("=" * 70)


def get_npm_executable() -> str:
    """Return the correct npm executable name for Windows/Unix."""
    return "npm.cmd" if sys.platform == "win32" else "npm"


def run_command(command: list[str], cwd: Path) -> bool:
    """Run a subprocess command and stream output."""
    cmd_str = " ".join(command)
    print(f"[RUN] {cmd_str} (in {cwd.name}/)")
    start = time.time()

    try:
        subprocess.run(command, cwd=cwd, check=True)
        elapsed = time.time() - start
        print(f"[SUCCESS] Completed in {elapsed:.1f}s")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Command exited with code {e.returncode}: {cmd_str}")
        return False
    except FileNotFoundError as e:
        print(f"[ERROR] Executable not found: {e}")
        return False


def run_demo_mode(port: int = 4321):
    """Execute Demo Pipeline: Seed Data -> Build Site -> Start Preview Server."""
    python_exe = sys.executable
    npm_exe = get_npm_executable()

    print_banner("Demo Mode: Step 1/3 - Seeding Database")
    seed_cmd = [
        python_exe,
        str(PIPELINE_DIR / "2_extractor.py"),
        "--seed-demo",
    ]
    if not run_command(seed_cmd, cwd=REPO_ROOT):
        print("[FATAL] Data seeding failed.")
        sys.exit(1)

    print_banner("Demo Mode: Step 2/3 - Compiling Astro 5 Static Site")
    key_cmd = [
        python_exe,
        str(PIPELINE_DIR / "3_indexnow.py"),
        "--write-key-only",
    ]
    run_command(key_cmd, cwd=REPO_ROOT)

    build_cmd = [npm_exe, "run", "build"]
    if not run_command(build_cmd, cwd=SITE_DIR):
        print("[FATAL] Astro build failed.")
        sys.exit(1)

    print_banner("Demo Mode: Step 3/3 - Launching Local Preview Server")
    print(f"[PREVIEW] Starting Astro preview server on port {port}...")
    print(f"[URL] http://localhost:{port}/")
    print("[URL] http://localhost:{port}/bosch/bosch-800-series-shpm78z55n-error-code-e24-fix/")
    print("Press Ctrl+C to stop the server at any time.\n")

    preview_cmd = [
        npm_exe,
        "run",
        "preview",
        "--",
        "--port",
        str(port),
        "--host",
        "0.0.0.0",
    ]
    try:
        subprocess.run(preview_cmd, cwd=SITE_DIR, check=True)
    except KeyboardInterrupt:
        print("\n[STOP] Preview server stopped by user.")


def run_production_mode(targets: list[str] = None, num_harvest: int = 10):
    """Execute Full Production Pipeline: Harvest -> Extract -> Build -> IndexNow."""
    python_exe = sys.executable
    npm_exe = get_npm_executable()
    overall_start = time.time()

    print_banner("Production Mode: Step 1/5 - Harvesting Service Manual PDFs")
    harvest_cmd = [
        python_exe,
        str(PIPELINE_DIR / "1_harvester.py"),
        "--num",
        str(num_harvest),
    ]
    if targets:
        harvest_cmd.extend(["--targets"] + targets)
    run_command(harvest_cmd, cwd=REPO_ROOT)

    print_banner("Production Mode: Step 2/5 - Gemini 2.5 Flash Structured Extraction")
    extract_cmd = [python_exe, str(PIPELINE_DIR / "2_extractor.py")]
    run_command(extract_cmd, cwd=REPO_ROOT)

    print_banner("Production Mode: Step 3/5 - Preparing IndexNow Verification Key")
    key_cmd = [
        python_exe,
        str(PIPELINE_DIR / "3_indexnow.py"),
        "--write-key-only",
    ]
    run_command(key_cmd, cwd=REPO_ROOT)

    print_banner("Production Mode: Step 4/5 - Compiling Astro 5 Static Site")
    build_cmd = [npm_exe, "run", "build"]
    if not run_command(build_cmd, cwd=SITE_DIR):
        print("[FATAL] Production Astro build failed. Aborting IndexNow ping.")
        sys.exit(1)

    print_banner("Production Mode: Step 5/5 - Pinging Search Engines via IndexNow")
    indexnow_cmd = [python_exe, str(PIPELINE_DIR / "3_indexnow.py")]
    run_command(indexnow_cmd, cwd=REPO_ROOT)

    elapsed = time.time() - overall_start
    print_banner("Production Pipeline Complete")
    print(f"Total Pipeline Runtime: {elapsed:.1f} seconds")
    print(f"Static Site Ready in: {SITE_DIR / 'dist'}")


def main():
    parser = argparse.ArgumentParser(
        description="FixMyCode End-to-End Programmatic SEO Pipeline"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--demo",
        action="store_true",
        help="Run demo mode: seed 10 records, build Astro site, and start preview server",
    )
    group.add_argument(
        "--production",
        action="store_true",
        help="Run full production pipeline: harvester -> extractor -> build -> IndexNow",
    )

    # Optional flags for production
    parser.add_argument(
        "--targets",
        nargs="+",
        help="Optional specific equipment search queries for 1_harvester.py",
    )
    parser.add_argument(
        "--num-harvest",
        type=int,
        default=10,
        help="Search result count per target in production mode (default: 10)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=4321,
        help="Preview server port in demo mode (default: 4321)",
    )

    args = parser.parse_args()
    load_dotenv(REPO_ROOT / ".env")

    if args.demo:
        run_demo_mode(port=args.port)
    elif args.production:
        run_production_mode(targets=args.targets, num_harvest=args.num_harvest)


if __name__ == "__main__":
    main()
