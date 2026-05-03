"""Download Get It Done data from the SD open data portal.

Run locally (the portal is not reachable from all environments):
    python 02-analysis/pull_data.py

The city reorganized the dataset into one file of OPEN reports plus CLOSED
reports split by year. Exact filenames occasionally change — if a download
404s, get the current links from:
    https://data.sandiego.gov/datasets/get-it-done-311/
and update FILES below. Everything downstream reads from data/ and does not
care about source filenames.
"""

from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

BASE = "https://seshat.datasd.org/get_it_done_reports"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Keep the analysis window small and recent: full-year 2024 + 2025, plus the
# current open file. Add years if a longer baseline is needed.
FILES = {
    "closed_2025.csv": f"{BASE}/get_it_done_requests_closed_2025_datasd.csv",
    "open.csv": f"{BASE}/get_it_done_requests_open_datasd.csv",
}


def download(url: str, dest: Path) -> None:
    print(f"-> {url}")
    with urllib.request.urlopen(url) as resp, open(dest, "wb") as fh:
        while chunk := resp.read(1 << 20):
            fh.write(chunk)
    size_mb = dest.stat().st_size / 1e6
    print(f"   saved {dest.name} ({size_mb:.1f} MB)")


def main() -> int:
    DATA_DIR.mkdir(exist_ok=True)
    failures = []
    for name, url in FILES.items():
        dest = DATA_DIR / name
        if dest.exists():
            print(f"   {name} already present, skipping")
            continue
        try:
            download(url, dest)
        except Exception as exc:  # noqa: BLE001 - report and continue
            failures.append((name, url, exc))
            print(f"   FAILED: {exc}")

    if failures:
        print("\nSome downloads failed. Check current filenames at:")
        print("  https://data.sandiego.gov/datasets/get-it-done-311/")
        return 1

    print("\nDone. Next: python scripts/verify_data.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())

