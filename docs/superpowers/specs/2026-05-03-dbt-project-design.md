# dbt Project Design — SF Giants Pitching Analytics

**Date:** 2026-05-03
**Project:** sf_giants_analytics

## Overview

Set up a dbt project that transforms SF Giants pitching data from raw Snowflake tables into a pitcher performance star schema across three schemas: RAW (source), STAGING (cleaned views), and MART (dimensional tables and aggregations).

---

## Snowflake Schema Architecture

```
SF_GIANTS_DB
├── RAW      ← written by ingestion scripts; declared as dbt source, never built by dbt
├── STAGING  ← dbt views; clean and rename only, no business logic
└── MART     ← dbt tables; dimensional model + computed metrics + aggregations
```

RAW is read-only from dbt's perspective. The ingestion scripts (`extract_mlb_stats.py`) write two tables there:

- `RAW.PLAYERS` — one row per SF Giants pitcher
- `RAW.PITCHER_GAME_LOGS` — one row per pitcher per game (2024 regular season)

---

## File Structure

```
dbt_project.yml
models/
  staging/
    sources.yml                ← declares RAW.PLAYERS and RAW.PITCHER_GAME_LOGS as dbt sources
    schema.yml                 ← not_null and unique tests for staging models
    stg_players.sql
    stg_pitcher_game_logs.sql
  mart/
    schema.yml                 ← not_null and unique tests for mart models
    dim_pitcher.sql
    fact_pitcher_game.sql
    mart_pitcher_season.sql
macros/
  generate_schema_name.sql     ← overrides dbt default so schemas are STAGING/MART, not RAW_STAGING/RAW_MART
```

---

## Layer Definitions

### Staging (`STAGING` schema, materialized as views)

One model per raw table. Jobs: cast types, rename columns, drop internal metadata columns (`_loaded_at`). No joins, no aggregations, no business logic.

`**stg_players**`

- Cast `birth_date` and `mlb_debut` from VARCHAR to DATE
- Rename `id` → `player_id` for clarity
- Pass through: `full_name`, `pitch_hand`, `bat_side`, `position`, `active`

`**stg_pitcher_game_logs**`

- Cast `game_date` from VARCHAR to DATE
- Ensure `innings_pitched` is FLOAT
- Pass through all pitching stats: `era`, `strikeouts`, `walks`, `hits`, `earned_runs`, `home_runs`, `whip`, `pitches_thrown`, `strikes`, `wins`, `losses`, `is_home`

---

### Mart (`MART` schema, materialized as tables)

`**dim_pitcher**` — pitcher attributes dimension

- Source: `stg_players`
- Columns: `player_id` (PK), `full_name`, `pitch_hand`, `bat_side`, `position`, `mlb_debut_date`, `birth_date`, `active`

`**fact_pitcher_game**` — game-level fact table (lowest grain: one row per pitcher per game)

- Source: `stg_pitcher_game_logs` joined to `stg_players` for `full_name`
- Raw stats: `innings_pitched`, `strikeouts`, `walks`, `hits`, `earned_runs`, `home_runs`, `whip`, `pitches_thrown`, `strikes`, `wins`, `losses`, `is_home`, `team_name`
- Computed rate stats:
  - `k_per_9` = (strikeouts / innings_pitched) * 9
  - `bb_per_9` = (walks / innings_pitched) * 9
  - `h_per_9` = (hits / innings_pitched) * 9
  - `k_bb_ratio` = strikeouts / nullif(walks, 0)
  - `strike_pct` = strikes / nullif(pitches_thrown, 0)

`**mart_pitcher_season`** — season rollup, built on top of `fact_pitcher_game`

- One row per pitcher for the 2024 season
- Aggregated: `games`, `total_ip`, `total_strikeouts`, `total_walks`, `total_hits`, `total_earned_runs`, `total_home_runs`, `wins`, `losses`
- Computed season rates: `season_era`, `season_whip`, `season_k_per_9`, `season_bb_per_9`

---

## dbt_project.yml Configuration

```yaml
models:
  sf_giants_analytics:
    staging:
      +materialized: view
      +schema: STAGING
    mart:
      +materialized: table
      +schema: MART
```

---

## Macros

`**generate_schema_name.sql**` — dbt's default behavior appends custom schema names to the target schema (e.g. `RAW_STAGING`). This macro overrides that to use the custom schema name directly (`STAGING`, `MART`), keeping Snowflake clean.

---

## Tests

Each `schema.yml` will include:

- `not_null` on all primary and foreign keys
- `unique` on `player_id` (dim_pitcher), `game_pk` + `player_id` composite (fact_pitcher_game)

---

## What Is Not Included


| Feature      | Reason excluded                                                  |
| ------------ | ---------------------------------------------------------------- |
| `seeds/`     | All data comes from API ingestion scripts; no static CSVs needed |
| `snapshots/` | Raw tables are fully refreshed each run; no SCD tracking needed  |
| `analyses/`  | All SQL is materialized as proper models                         |


