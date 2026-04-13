# CLAUDE.md — Project Context

## Project
Baseball Pitching Performance Analytics Pipeline — built to demonstrate skills for a Baseball Operations Analyst role at the San Francisco Giants.

## What This Project Does
- Pulls MLB pitching data from the MLB Stats API
- Loads raw data into Snowflake
- Transforms it through raw → staging → mart layers using dbt into a pitcher performance star schema
- Surfaces insights via a Streamlit dashboard
- Builds a knowledge base by scraping Giants press releases and FanGraphs articles, summarized into wiki pages

## Tech Stack
- **Warehouse:** Snowflake
- **Transformation:** dbt
- **Orchestration:** GitHub Actions (scheduled)
- **Dashboard:** Streamlit (Streamlit Community Cloud)
- **IDE:** Cursor + Claude Code

## Repo Structure
- `docs/` — proposal, job posting
- `models/` — dbt models (raw, staging, mart)
- `dashboard/` — Streamlit app
- `knowledge_base/` — scraped sources and wiki pages
- `.github/workflows/` — GitHub Actions pipeline

## Key osal.md` — project proposal and job posting reflection
- `docs/job-posting.pdf` — SF Giants Baseball Operations Analyst posting
