# CLAUDE.md — Project Context

## Project
Baseball Pitching Performance Analytics Pipeline — built to demonstrate skills for a Baseball Operations Analyst role at the San Francisco Giants.

## What This Project Does
- Pulls MLB pitching data from the MLB Stats API (2024 full season, SF Giants pitchers)
- Loads raw data into Snowflake (RAW schema)
- Transforms it through RAW → STAGING → MART layers using dbt into a pitcher performance star schema
- Surfaces insights via a Streamlit dashboard
- Builds a knowledge base by scraping Giants press releases and FanGraphs articles, summarized into wiki pages

## Tech Stack
- **Warehouse:** Snowflake (SF_GIANTS_DB, warehouse SF_GIANTS_WH, role ACCOUNTADMIN)
- **Transformation:** dbt 1.11.8 + dbt-snowflake 1.11.4
- **Orchestration:** GitHub Actions (scheduled)
- **Dashboard:** Streamlit (Streamlit Community Cloud)
- **IDE:** Cursor + Claude Code

## Repo Structure
- `docs/` — proposal, job posting, specs and plans under `docs/superpowers/`
- `models/staging/` — dbt staging views (stg_players, stg_pitcher_game_logs)
- `models/mart/` — dbt mart tables (star schema)
- `tests/` — singular dbt tests
- `macros/` — generate_schema_name override
- `dashboard/` — Streamlit app
- `knowledge_base/` — scraped sources and wiki pages
- `.github/workflows/` — GitHub Actions pipeline
- `docs/job-posting.pdf` — SF Giants Baseball Operations Analyst posting

## dbt Architecture

### Schema routing
Three Snowflake schemas — RAW (source data), STAGING (views), MART (tables). A custom `macros/generate_schema_name.sql` macro prevents dbt's default behavior of prefixing the target schema onto custom schema names (which would produce RAW_STAGING instead of STAGING).

### Models (8 total, all passing)
| Model | Layer | Type | Rows |
|---|---|---|---|
| stg_players | STAGING | view | — |
| stg_pitcher_game_logs | STAGING | view | — |
| dim_pitcher | MART | table | 28 |
| dim_game | MART | table | 247 |
| dim_date | MART | table | 4,018 |
| fact_pitcher_game | MART | table | 809 |
| mart_pitcher_rolling | MART | table | 809 |
| mart_pitcher_season | MART | table | 28 |

### Star schema
- **Fact:** `fact_pitcher_game` — grain: one row per pitcher per game. Composite PK: `(player_id, game_pk)`. Computes k_per_9, bb_per_9, h_per_9, k_bb_ratio, strike_pct.
- **Dims:** `dim_pitcher` (28 SF Giants pitchers), `dim_game` (247 games, deduplicated from fact via GROUP BY + MAX), `dim_date` (2020–2030 date spine via Snowflake GENERATOR)
- **Marts:** `mart_pitcher_season` (season rollup per pitcher), `mart_pitcher_rolling` (5-start rolling averages via window functions partitioned by player_id ordered by game_date)

### Tests (25 total, all passing)
- Schema tests in `models/staging/schema.yml` and `models/mart/schema.yml`: not_null and unique on all primary keys
- Singular test `tests/assert_fact_pitcher_game_pk.sql`: catches duplicate or null composite PKs on fact_pitcher_game (covers both duplicate loads and unidentifiable records in one query)

## Conventions
- **SQL keywords:** uppercase (SELECT, FROM, WITH, CASE, WHEN, etc.)
- **dbt refs:** `{{ ref('model_name') }}` and `{{ source('raw', 'table') }}`
- **Materializations:** staging = view, mart = table

## What's Done
- [x] Raw data extraction scripts (Source 1 and Source 2)
- [x] Snowflake RAW schema loaded with 2024 season data
- [x] dbt staging layer (stg_players, stg_pitcher_game_logs)
- [x] dbt mart star schema (dim_pitcher, dim_game, dim_date, fact_pitcher_game, mart_pitcher_season, mart_pitcher_rolling)
- [x] 25 dbt tests passing (schema tests + composite PK singular test)
- [x] dbt docs site generated (`dbt docs generate && dbt docs serve`)

## What's Next
- [ ] Build the Streamlit dashboard (connect to Snowflake, visualize mart tables)
- [ ] Set up GitHub Actions workflow to run `dbt run && dbt test` on a schedule
- [ ] Knowledge base: scrape Giants press releases and FanGraphs articles, summarize into wiki pages
- [ ] Deploy Streamlit app to Streamlit Community Cloud
