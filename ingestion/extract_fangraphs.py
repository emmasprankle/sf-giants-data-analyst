"""
Source 2: Baseball analytics sites → knowledge/raw/
Pattern: request → parse → loop → save

Scrapes baseball analytics pages for SF Giants pitchers using the Firecrawl API
and writes each page as a markdown file to knowledge/raw/.

Sources: FanGraphs leaderboards + glossary, Baseball Reference, Baseball Savant
Output filenames: knowledge/raw/<slug>.md
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
    # ── FanGraphs leaderboards (fangraphs.com) ────────────────────────────────
    # qual=0 returns all Giants pitchers, not just qualified starters
    {
        "slug": "fangraphs-giants-pitching-dashboard-2024",
        "url": "https://www.fangraphs.com/leaders/major-league"
               "?pos=all&stats=pit&lg=all&qual=0&type=8"
               "&team=30&season=2024&season1=2024",
    },
    {
        "slug": "fangraphs-giants-plate-discipline-2024",
        "url": "https://www.fangraphs.com/leaders/major-league"
               "?pos=all&stats=pit&lg=all&qual=0&type=5"
               "&team=30&season=2024&season1=2024",
    },

    # ── FanGraphs glossary / library (library.fangraphs.com) ─────────────────
    {
        "slug": "fangraphs-glossary-fip",
        "url": "https://library.fangraphs.com/pitching/fip/",
    },
    {
        "slug": "fangraphs-glossary-era",
        "url": "https://library.fangraphs.com/pitching/era/",
    },
    {
        "slug": "fangraphs-glossary-whip",
        "url": "https://library.fangraphs.com/pitching/whip/",
    },
    {
        "slug": "fangraphs-glossary-babip",
        "url": "https://library.fangraphs.com/pitching/babip/",
    },
    {
        "slug": "fangraphs-glossary-xfip",
        "url": "https://library.fangraphs.com/pitching/xfip/",
    },
    {
        "slug": "fangraphs-glossary-lob-pct",
        "url": "https://library.fangraphs.com/pitching/lob/",
    },

    # ── Baseball Reference (baseball-reference.com) ───────────────────────────
    {
        "slug": "baseball-reference-giants-2024-pitching",
        "url": "https://www.baseball-reference.com/teams/SFG/2024-pitching.shtml",
    },
    {
        "slug": "baseball-reference-logan-webb",
        "url": "https://www.baseball-reference.com/players/w/webblo01.shtml",
    },
    {
        "slug": "baseball-reference-kyle-harrison",
        "url": "https://www.baseball-reference.com/players/h/harriky01.shtml",
    },

    # ── Baseball Savant / Statcast (baseballsavant.mlb.com) ───────────────────
    {
        "slug": "baseballsavant-expected-stats-giants-2024",
        "url": "https://baseballsavant.mlb.com/leaderboard/expected_statistics"
               "?type=pitcher&year=2024&position=1&team=137&min=1",
    },
    {
        "slug": "baseballsavant-statcast-glossary",
        "url": "https://baseballsavant.mlb.com/csv-docs",
    },
    {
        "slug": "baseballsavant-logan-webb",
        "url": "https://baseballsavant.mlb.com/savant-player/logan-webb-657277",
    },
    {
        "slug": "baseballsavant-kyle-harrison",
        "url": "https://baseballsavant.mlb.com/savant-player/kyle-harrison-690986",
    },
    {
        "slug": "baseballsavant-jordan-hicks",
        "url": "https://baseballsavant.mlb.com/savant-player/jordan-hicks-663855",
    },
    {
        "slug": "baseballsavant-blake-snell",
        "url": "https://baseballsavant.mlb.com/savant-player/blake-snell-605483",
    },
    {
        "slug": "baseballsavant-ryan-walker",
        "url": "https://baseballsavant.mlb.com/savant-player/ryan-walker-676254",
    },
    {
        "slug": "baseballsavant-camilo-doval",
        "url": "https://baseballsavant.mlb.com/savant-player/camilo-doval-666808",
    },
    {
        "slug": "baseballsavant-hayden-birdsong",
        "url": "https://baseballsavant.mlb.com/savant-player/hayden-birdsong-806185",
    },
    {
        "slug": "baseballsavant-landen-roupp",
        "url": "https://baseballsavant.mlb.com/savant-player/landen-roupp-694738",
    },
]

FIRECRAWL_SCRAPE_PARAMS = {
    "formats": ["markdown"],
    "onlyMainContent": True,
    "waitFor": 3000,
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
