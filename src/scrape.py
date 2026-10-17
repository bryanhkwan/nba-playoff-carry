"""Download Basketball-Reference playoff pages into data/raw.

Polite on purpose: one request every 4 seconds (Sports Reference blocks clients
that send more than 20 requests a minute), and pages already on disk are skipped,
so a rerun only fetches what's missing.
"""
import ssl
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
BASE = "https://www.basketball-reference.com/playoffs"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; playoff-carry personal research; low volume)"}
DELAY_SECONDS = 4.0
# 1977 is fetched only to check whether it already has all six stats (METHOD.md, Data).
FIRST_YEAR, LAST_YEAR = 1977, 2026


def pages():
    yield "series.html", f"{BASE}/series.html"
    for year in range(FIRST_YEAR, LAST_YEAR + 1):
        yield f"NBA_{year}_advanced.html", f"{BASE}/NBA_{year}_advanced.html"


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    # The default context trusts the operating system's certificate store (the same
    # one browsers use), which works on machines where certifi's bundle doesn't.
    context = ssl.create_default_context()
    fetched = 0
    for name, url in pages():
        path = RAW / name
        if path.exists():
            continue
        if fetched:
            time.sleep(DELAY_SECONDS)
        fetched += 1
        try:
            request = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(request, context=context, timeout=30) as resp:
                html = resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as err:
            if err.code == 429:
                sys.exit(f"Rate limited at {url}; stopping. Wait an hour before rerunning.")
            print(f"{err.code} {url}", flush=True)
            continue
        path.write_text(html, encoding="utf-8")
        print(f"ok {name} ({len(html):,} chars)", flush=True)
    print(f"done: {fetched} requests", flush=True)


if __name__ == "__main__":
    main()
