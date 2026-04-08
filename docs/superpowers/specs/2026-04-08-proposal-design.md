# Proposal Design: Baseball Pitching Performance Analytics Pipeline

**Date:** 2026-04-08
**Status:** Approved

---

## Project Identity

**Project name:** Baseball Pitching Performance Analytics Pipeline
**Job posting:** Baseball Operations Analyst, San Francisco Giants
**Repo:** https://github.com/emmasprankle/sports-ticketing-data-analyst

---

## Framing

The proposal is framed around the two things the Giants posting emphasizes most: *research* (extracting insights from player performance data) and *tooling* (prototyping lightweight visualizations for Baseball Ops). The reflection explicitly connects class skills (SQL, dbt, dashboards, pipelines) to those two job responsibilities, and closes with transferability to other sports analytics roles.

---

## Data Sources

### Source 1 — API (structured pipeline)
- **Tool:** MLB Stats API via `python-statsapi` (free, no API key)
- **Data:** Per-game pitcher stats — ERA, strikeouts, walks, innings pitched, WHIP, hits allowed, earned runs, home/away flag
- **Destination:** Snowflake raw schema
- **Automation:** GitHub Actions on a schedule

### Source 2 — Web scrape (knowledge base)
- **Sites (3+):**
  - sfgiants.com — press releases, player profiles, front office news
  - FanGraphs — pitching research articles, sabermetrics methodology
  - Baseball Prospectus or The Athletic — pitching commentary and analysis
- **Target:** 15+ raw sources in `knowledge/raw/`
- **Synthesis:** Claude Code-generated wiki pages in `knowledge/wiki/`

---

## Star Schema Design

**Fact table:** `fact_pitcher_game_log`
- Grain: one row per pitcher per game
- Measures: ERA, innings pitched, strikeouts, walks, hits allowed, earned runs, WHIP

**Dimension tables:**
- `dim_pitcher` — name, team, handedness (L/R), position
- `dim_team` — team name, league, division
- `dim_date` — game date, month, season, day of week
- `dim_game` — home/away flag, opponent, ballpark

---

## Analytical Focus

**Descriptive:** Which pitchers had the lowest ERA this season? How do strikeout rates vary by team?

**Diagnostic:** Does ERA increase in late innings (6th+)? Which pitchers show the most home/away performance split?

---

## Proposal Reflection (approved)

This posting for a Baseball Operations Analyst at the San Francisco Giants requires proficiency in SQL, Python, statistical analysis, and the ability to prototype lightweight tools and visualizations for non-technical stakeholders — all skills directly developed in this course. The role emphasizes extracting actionable insights from baseball datasets and supporting long-term research projects, which maps precisely to what this project builds: an automated pipeline that pulls MLB pitching data via the MLB Stats API, loads it into Snowflake, transforms it through dbt staging and mart layers into a pitcher performance star schema, and surfaces it through an interactive Streamlit dashboard. The dbt models demonstrate dimensional modeling and SQL-based analytical thinking; the GitHub Actions pipeline demonstrates production-grade orchestration; and the knowledge base — built by scraping Giants press releases and FanGraphs research articles — demonstrates the ability to synthesize unstructured domain content into queryable insights. This project transfers directly to any sports analytics, baseball operations, or data analyst role that requires moving from raw data to research-ready tools, including roles at other MLB teams, sports technology companies, or performance analytics firms.

---

## Deliverables for Proposal Submission (Due Apr 13)

- `docs/job-posting.pdf` — saved (exists)
- `docs/proposal.md` → export to `docs/proposal.pdf`
- `CLAUDE.md` — project context file
- Public GitHub repo with `.gitignore` and directory structure
