# Proposal Submission Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete all proposal submission deliverables for the Baseball Pitching Performance Analytics Pipeline project, due April 13.

**Architecture:** Create the project's foundational scaffolding — directory structure, `CLAUDE.md` context file, and `README.md` skeleton — then export the proposal to PDF. No application code is written in this plan; that begins in Plan 2 (Milestone 1).

**Tech Stack:** Git, Markdown, GitHub (public repo)

---

## File Structure

Files created or modified in this plan:

| File | Action | Purpose |
|---|---|---|
| `CLAUDE.md` | Create | Project context for Claude Code — how to query knowledge base, env vars, project overview |
| `README.md` | Create | Portfolio README skeleton with all required sections (filled in during Milestone 2) |
| `ingestion/.gitkeep` | Create | Reserve ingestion directory |
| `ingestion/mlb_stats/.gitkeep` | Create | Reserve MLB Stats API subdirectory |
| `dbt/.gitkeep` | Create | Reserve dbt project directory |
| `dashboard/.gitkeep` | Create | Reserve Streamlit dashboard directory |
| `knowledge/raw/.gitkeep` | Create | Reserve raw scraped sources directory |
| `knowledge/wiki/.gitkeep` | Create | Reserve synthesized wiki pages directory |
| `.github/workflows/.gitkeep` | Create | Reserve GitHub Actions workflows directory |
| `docs/proposal.pdf` | Manual export | Export `docs/proposal.md` to PDF |

---

## Task 1: Create Project Directory Structure

**Files:**
- Create: `ingestion/.gitkeep`
- Create: `ingestion/mlb_stats/.gitkeep`
- Create: `dbt/.gitkeep`
- Create: `dashboard/.gitkeep`
- Create: `knowledge/raw/.gitkeep`
- Create: `knowledge/wiki/.gitkeep`
- Create: `.github/workflows/.gitkeep`

- [ ] **Step 1: Create all directories and placeholder files**

Run:
```bash
mkdir -p ingestion/mlb_stats dbt dashboard knowledge/raw knowledge/wiki .github/workflows
touch ingestion/.gitkeep ingestion/mlb_stats/.gitkeep dbt/.gitkeep dashboard/.gitkeep knowledge/raw/.gitkeep knowledge/wiki/.gitkeep .github/workflows/.gitkeep
```

- [ ] **Step 2: Verify structure**

Run:
```bash
find . -not -path './.git/*' -not -path './docs/*' -not -name '.DS_Store' | sort
```

Expected output:
```
.
./.gitignore
./CLAUDE.md (not yet)
./README.md (not yet)
./.github
./.github/workflows
./.github/workflows/.gitkeep
./dashboard
./dashboard/.gitkeep
./dbt
./dbt/.gitkeep
./ingestion
./ingestion/.gitkeep
./ingestion/mlb_stats
./ingestion/mlb_stats/.gitkeep
./knowledge
./knowledge/raw
./knowledge/raw/.gitkeep
./knowledge/wiki
./knowledge/wiki/.gitkeep
```

- [ ] **Step 3: Commit**

```bash
git add ingestion/ dbt/ dashboard/ knowledge/ .github/
git commit -m "scaffold: add project directory structure"
```

---

## Task 2: Create CLAUDE.md

**Files:**
- Create: `CLAUDE.md`

- [ ] **Step 1: Create CLAUDE.md**

Create `CLAUDE.md` at the repo root with this exact content:

```markdown
# CLAUDE.md — Baseball Pitching Performance Analytics Pipeline

This file gives Claude Code the context it needs to assist with this project.

## Project Overview

An end-to-end analytics pipeline for baseball pitching performance research,
targeting the skills required for a Baseball Operations Analyst role at the
San Francisco Giants. The pipeline pulls per-game MLB pitcher stats via the
MLB Stats API, loads them into Snowflake, transforms them through dbt into a
star schema, and surfaces insights through a Streamlit dashboard.

## Tech Stack

| Layer | Tool |
|---|---|
| Data Warehouse | Snowflake (AWS US East 1) |
| Transformation | dbt |
| Orchestration | GitHub Actions (scheduled) |
| Dashboard | Streamlit (deployed to Streamlit Community Cloud) |
| API Source | MLB Stats API (`python-statsapi`, free, no key required) |
| Web Scrape | Firecrawl or requests + BeautifulSoup |
| Knowledge Base | Claude Code (scrape → synthesize → query) |

## Repository Structure

```
sports-ticketing-data-analyst/
├── .github/workflows/     # GitHub Actions pipeline definitions
├── ingestion/
│   └── mlb_stats/         # MLB Stats API extraction scripts
├── dbt/                   # dbt project (staging + mart models)
├── dashboard/             # Streamlit app
├── knowledge/
│   ├── raw/               # Scraped raw sources (15+ files, 3+ sites)
│   └── wiki/              # Claude Code-generated synthesis pages
└── docs/                  # Proposal, job posting, design specs, plans
```

## Environment Variables

Never commit credentials. Store all secrets in `.env` (gitignored) locally
and as GitHub Actions secrets in the repo settings.

Required environment variables:
```
SNOWFLAKE_ACCOUNT=
SNOWFLAKE_USER=
SNOWFLAKE_PASSWORD=
SNOWFLAKE_DATABASE=
SNOWFLAKE_WAREHOUSE=
SNOWFLAKE_ROLE=
SNOWFLAKE_SCHEMA=
```

## Data Model (Star Schema)

**Fact table:** `fact_pitcher_game_log`
- Grain: one row per pitcher per game
- Measures: ERA, innings_pitched, strikeouts, walks, hits_allowed, earned_runs, whip

**Dimension tables:**
- `dim_pitcher` — pitcher_id, name, team, handedness, position
- `dim_team` — team_id, name, league, division
- `dim_date` — date_id, game_date, month, season_year, day_of_week
- `dim_game` — game_id, home_away_flag, opponent_team_id, ballpark

## Key Business Questions

**Descriptive (what happened):**
- Which pitchers had the lowest ERA this season?
- How do strikeout rates vary across teams?

**Diagnostic (why it happened):**
- Does ERA increase in late innings (6th+)? Which pitchers degrade most under fatigue?
- Which pitchers show the largest home vs away performance split?

## Knowledge Base

### Structure

- `knowledge/raw/` — scraped source files (markdown or text), one file per source
- `knowledge/wiki/` — synthesized wiki pages generated by Claude Code
- `knowledge/index.md` — index of all wiki pages with one-line summaries

### Sources

Sources are scraped from:
- sfgiants.com — press releases, player profiles, front office announcements
- fangraphs.com — pitching research articles, sabermetrics methodology
- Baseball Prospectus or The Athletic — pitching analysis and commentary

### How to Query the Knowledge Base

To answer questions about the project domain, Claude Code should:

1. Read `knowledge/index.md` to identify relevant wiki pages
2. Read the relevant wiki pages in `knowledge/wiki/`
3. Cross-reference with raw sources in `knowledge/raw/` when more detail is needed
4. Synthesize across multiple sources — do not just summarize a single file

Example questions this knowledge base should answer:
- "What does my knowledge base say about pitcher fatigue and inning-by-inning ERA trends?"
- "What public research exists on home/away performance splits for starting pitchers?"
- "What are the Giants' organizational priorities for pitching development?"

### Conventions

- Always cite the source file(s) you drew from when answering knowledge base questions
- If a question can't be answered from the knowledge base, say so clearly
- Wiki pages take precedence over raw sources for synthesized insights
- Raw sources take precedence for specific quotes, dates, and factual details
```

- [ ] **Step 2: Verify the file was created**

Run:
```bash
wc -l CLAUDE.md
```
Expected: 100+ lines

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: add CLAUDE.md with project context and knowledge base query conventions"
```

---

## Task 3: Create README.md Skeleton

**Files:**
- Create: `README.md`

- [ ] **Step 1: Create README.md**

Create `README.md` at the repo root with this exact content:

```markdown
# Baseball Pitching Performance Analytics Pipeline

An end-to-end analytics pipeline that extracts MLB pitcher game-log data,
loads it into Snowflake, transforms it through a dbt star schema, and
surfaces pitching performance insights through an interactive Streamlit
dashboard — built to demonstrate skills required for a Baseball Operations
Analyst role.

**Live dashboard:** _[link added after Milestone 2 deployment]_

---

## Tech Stack

| Layer | Tool |
|---|---|
| Data Warehouse | Snowflake |
| Transformation | dbt |
| Orchestration | GitHub Actions |
| Dashboard | Streamlit |
| API Source | MLB Stats API |
| Web Scrape | _[added in Milestone 2]_ |

---

## Pipeline Architecture

_[Pipeline diagram added in Milestone 1]_

---

## Data Model (ERD)

_[ERD generated from dbt models, added in Milestone 2]_

---

## Setup & Running the Pipeline

### Prerequisites

- Python 3.11+
- Snowflake trial account (AWS US East 1)
- dbt Core installed (`pip install dbt-snowflake`)

### Environment Variables

Copy `.env.example` to `.env` and fill in your Snowflake credentials:

```bash
cp .env.example .env
```

Required variables:
```
SNOWFLAKE_ACCOUNT=
SNOWFLAKE_USER=
SNOWFLAKE_PASSWORD=
SNOWFLAKE_DATABASE=
SNOWFLAKE_WAREHOUSE=
SNOWFLAKE_ROLE=
SNOWFLAKE_SCHEMA=
```

### Run the ingestion pipeline

```bash
cd ingestion/mlb_stats
pip install -r requirements.txt
python load_pitcher_game_logs.py
```

### Run dbt transformations

```bash
cd dbt
dbt deps
dbt run
dbt test
```

### Run the dashboard locally

```bash
cd dashboard
pip install -r requirements.txt
streamlit run app.py
```

---

## Insights Summary

_[Added after Milestone 2 — descriptive and diagnostic findings]_

---

## Knowledge Base

The `knowledge/` folder contains scraped sources and synthesized wiki pages
about MLB pitching analytics and the San Francisco Giants organization.
Query it via Claude Code in this repo.

See `CLAUDE.md` for query conventions.
```

- [ ] **Step 2: Verify the file was created**

Run:
```bash
wc -l README.md
```
Expected: 80+ lines

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: add README skeleton with setup instructions"
```

---

## Task 4: Export Proposal to PDF

**Files:**
- Create: `docs/proposal.pdf` (manual step — not automated)

- [ ] **Step 1: Open docs/proposal.md in a markdown viewer**

Options (use whichever is available):
- **VS Code:** Right-click `docs/proposal.md` → "Open Preview" → right-click preview → "Print" → save as PDF
- **Cursor:** Same as VS Code
- **Browser:** Open `docs/proposal.md` with a markdown preview extension, then File → Print → Save as PDF
- **Pandoc (if installed):** `pandoc docs/proposal.md -o docs/proposal.pdf`

- [ ] **Step 2: Save the PDF as docs/proposal.pdf**

Verify the file exists:
```bash
ls -lh docs/proposal.pdf
```
Expected: file exists, size > 10KB

- [ ] **Step 3: Commit**

```bash
git add docs/proposal.pdf
git commit -m "docs: add proposal PDF for submission"
```

---

## Task 5: Final Verification Before Submission

- [ ] **Step 1: Verify all required files exist**

Run:
```bash
ls docs/job-posting.pdf docs/proposal.pdf CLAUDE.md README.md
```
Expected: all four files listed with no errors

- [ ] **Step 2: Verify repo is public on GitHub**

Open `https://github.com/emmasprankle/sports-ticketing-data-analyst` in a browser (logged out or in incognito). Confirm you can see the repo without logging in.

- [ ] **Step 3: Verify .env is gitignored**

Run:
```bash
echo "SNOWFLAKE_PASSWORD=test" > .env
git status
```
Expected: `.env` does NOT appear in the git status output (it is ignored).

```bash
rm .env
```

- [ ] **Step 4: Submit repo URL to Brightspace**

Submit `https://github.com/emmasprankle/sports-ticketing-data-analyst` to Brightspace by April 13 at 9:55 AM.

---

## What's Next

After this plan is complete, proceed to **Plan 2: Milestone 1** which covers:
- MLB Stats API extraction script (`ingestion/mlb_stats/load_pitcher_game_logs.py`)
- Snowflake raw schema setup
- dbt staging + mart models (star schema)
- GitHub Actions scheduled pipeline
- Pipeline diagram in README
