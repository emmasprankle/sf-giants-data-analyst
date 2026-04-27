"""
Source 2: FanGraphs → knowledge/raw/
Pattern: request → parse → loop → save

Scrapes FanGraphs pages for SF Giants pitchers using the Firecrawl API
and writes each page as a markdown file to knowledge/raw/.

Output filenames: knowledge/raw/fangraphs_<slug>.md
"""

import os
import re
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────
# Change URLs and slugs here; the loop/save logic below stays the same

FIRECRAWL_BASE_URL = "https://api.firecrawl.dev/v1"

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "knowledge" / "raw"

SCRAPE_TARGETS = [
    {
        "slug": "giants-pitching-leaderboard-2024",
        "url": "https://www.fangraphs.com/leaders/major-league"
               "?pos=all&stats=pit&lg=all&qual=y&type=8"
               "&team=30&season=2024&season1=2024",
    },
    {
        "slug": "logan-webb-player-page",
        "url": "https://www.fangraphs.com/players/logan-webb/657277/stats/pitching",
    },
    {
        "slug": "kyle-harrison-player-page",
        "url": "https://www.fangraphs.com/players/kyle-harrison/sa3017678/stats/pitching",
    },
    {
        "slug": "robbie-ray-player-page",
        "url": "https://www.fangraphs.com/players/robbie-ray/13128/stats/pitching",
    },
    {
        "slug": "jordan-hicks-player-page",
        "url": "https://www.fangraphs.com/players/jordan-hicks/sa3007869/stats/pitching",
    },
]

FIRECRAWL_SCRAPE_PARAMS = {
    "formats": ["markdown"],
    "onlyMainContent": True,
}

REQUEST_DELAY_SECONDS = 2


# ── Helpers ───────────────────────────────────────────────────────────────────

def firecrawl_headers():
    api_key = os.environ["FIRECRAWL_API_KEY"]
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def scrape(url):
    resp = requests.post(
        f"{FIRECRAWL_BASE_URL}/scrape",
        headers=firecrawl_headers(),
        json={"url": url, **FIRECRAWL_SCRAPE_PARAMS},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    if not data.get("success"):
        raise ValueError(f"Firecrawl returned success=false for {url}: {data}")
    return data["data"]["markdown"]


def sanitize_filename(slug):
    return re.sub(r"[^\w\-]", "_", slug) + ".md"


def save(slug, markdown, source_url):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    filename = sanitize_filename(slug)
    path = OUTPUT_DIR / filename
    header = f"---\nsource: {source_url}\nslug: {slug}\n---\n\n"
    path.write_text(header + markdown, encoding="utf-8")
    return path


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print(f"Saving markdown to {OUTPUT_DIR}\n")

    for i, target in enumerate(SCRAPE_TARGETS):
        slug = target["slug"]
        url = target["url"]
        print(f"[{i+1}/{len(SCRAPE_TARGETS)}] Scraping: {slug}")
        print(f"  URL: {url}")

        markdown = scrape(url)
        path = save(slug, markdown, url)

        word_count = len(markdown.split())
        print(f"  Saved {word_count:,} words → {path.name}\n")

        if i < len(SCRAPE_TARGETS) - 1:
            time.sleep(REQUEST_DELAY_SECONDS)

    print(f"Done. {len(SCRAPE_TARGETS)} files written to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
