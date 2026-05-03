# dbt Project Setup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a complete dbt project that transforms `RAW.PLAYERS` and `RAW.PITCHER_GAME_LOGS` in Snowflake into a pitcher performance star schema across three schemas: RAW (source), STAGING (cleaned views), MART (dimensional tables + aggregations).

**Architecture:** Staging layer cleans and renames raw tables as views. Mart layer builds `dim_pitcher`, `fact_pitcher_game` (with computed rate stats), and `mart_pitcher_season` (season rollup) as tables. A `generate_schema_name` macro ensures models land in `STAGING` and `MART` rather than dbt's default `RAW_STAGING`/`RAW_MART`.

**Tech Stack:** dbt 1.11.8, dbt-snowflake 1.11.4, Snowflake (SF_GIANTS_DB)

---

## File Map

| Action | Path |
|--------|------|
| Modify | `dbt_project.yml` |
| Delete | `models/example/` (entire directory) |
| Create | `macros/generate_schema_name.sql` |
| Create | `models/staging/sources.yml` |
| Create | `models/staging/schema.yml` |
| Create | `models/staging/stg_players.sql` |
| Create | `models/staging/stg_pitcher_game_logs.sql` |
| Create | `models/mart/schema.yml` |
| Create | `models/mart/dim_pitcher.sql` |
| Create | `models/mart/fact_pitcher_game.sql` |
| Create | `models/mart/mart_pitcher_season.sql` |

---

### Task 1: Update dbt_project.yml and remove example models

**Files:**
- Modify: `dbt_project.yml`
- Delete: `models/example/`

- [ ] **Step 1: Replace the models block in dbt_project.yml**

Replace the entire `models:` section at the bottom of `dbt_project.yml` with:

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

The full file should look like:

```yaml
name: 'sf_giants_analytics'
version: '1.0.0'

profile: 'sf_giants_analytics'

model-paths: ["models"]
analysis-paths: ["analyses"]
test-paths: ["tests"]
seed-paths: ["seeds"]
macro-paths: ["macros"]
snapshot-paths: ["snapshots"]

clean-targets:
  - "target"
  - "dbt_packages"

models:
  sf_giants_analytics:
    staging:
      +materialized: view
      +schema: STAGING
    mart:
      +materialized: table
      +schema: MART
```

- [ ] **Step 2: Delete the example models directory**

```bash
rm -rf models/example
```

- [ ] **Step 3: Commit**

```bash
git add dbt_project.yml
git rm -r models/example
git commit -m "Configure dbt_project.yml schema routing and remove example models"
```

---

### Task 2: Add generate_schema_name macro

**Files:**
- Create: `macros/generate_schema_name.sql`

**Why this is needed:** dbt's default `generate_schema_name` appends the custom schema to the target schema from `profiles.yml`. Since the target schema is `RAW`, staging models would land in `RAW_STAGING` instead of `STAGING`. This macro overrides that behavior to use the custom schema name directly.

- [ ] **Step 1: Create `macros/generate_schema_name.sql`**

```sql
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- else -%}
        {{ custom_schema_name | trim | upper }}
    {%- endif -%}
{%- endmacro %}
```

- [ ] **Step 2: Commit**

```bash
git add macros/generate_schema_name.sql
git commit -m "Add generate_schema_name macro for clean STAGING/MART schema routing"
```

---

### Task 3: Validate Snowflake connection

**Files:** none

- [ ] **Step 1: Run dbt debug**

```bash
dbt debug
```

Expected output ends with:
```
All checks passed!
```

If it fails, the most common causes are:
- `profiles.yml` not found → check `~/.dbt/profiles.yml` exists
- Wrong account identifier → Snowflake account should be `wlgoqiq-psc32625`
- Wrong credentials → verify `SNOWFLAKE_USER` / password in `~/.dbt/profiles.yml`
- Warehouse not running → start `SF_GIANTS_WH` in Snowflake console

Do not proceed until `dbt debug` passes.

---

### Task 4: Create staging sources.yml

**Files:**
- Create: `models/staging/sources.yml`

- [ ] **Step 1: Create `models/staging/sources.yml`**

```yaml
version: 2

sources:
  - name: raw
    database: SF_GIANTS_DB
    schema: RAW
    tables:
      - name: players
      - name: pitcher_game_logs
```

- [ ] **Step 2: Commit**

```bash
git add models/staging/sources.yml
git commit -m "Add dbt sources declaration for RAW.PLAYERS and RAW.PITCHER_GAME_LOGS"
```

---

### Task 5: Write stg_players

**Files:**
- Create: `models/staging/stg_players.sql`
- Create: `models/staging/schema.yml`

- [ ] **Step 1: Create `models/staging/stg_players.sql`**

```sql
with source as (
    select * from {{ source('raw', 'players') }}
),

renamed as (
    select
        player_id,
        full_name,
        try_to_date(birth_date)  as birth_date,
        pitch_hand,
        bat_side,
        position,
        try_to_date(mlb_debut)   as mlb_debut_date,
        active
    from source
)

select * from renamed
```

- [ ] **Step 2: Run the model**

```bash
dbt run --select stg_players
```

Expected output:
```
1 of 1 OK created sql view model STAGING.stg_players
```

- [ ] **Step 3: Create `models/staging/schema.yml` with tests**

```yaml
version: 2

models:
  - name: stg_players
    columns:
      - name: player_id
        tests:
          - not_null
          - unique
      - name: full_name
        tests:
          - not_null
```

- [ ] **Step 4: Run tests**

```bash
dbt test --select stg_players
```

Expected output:
```
4 of 4 PASS
```

- [ ] **Step 5: Commit**

```bash
git add models/staging/stg_players.sql models/staging/schema.yml
git commit -m "Add stg_players staging model with tests"
```

---

### Task 6: Write stg_pitcher_game_logs

**Files:**
- Create: `models/staging/stg_pitcher_game_logs.sql`
- Modify: `models/staging/schema.yml`

- [ ] **Step 1: Create `models/staging/stg_pitcher_game_logs.sql`**

```sql
with source as (
    select * from {{ source('raw', 'pitcher_game_logs') }}
),

renamed as (
    select
        player_id,
        game_pk,
        try_to_date(game_date)   as game_date,
        team_id,
        team_name,
        is_home,
        wins,
        losses,
        era::float               as era,
        innings_pitched::float   as innings_pitched,
        strikeouts,
        walks,
        hits,
        earned_runs,
        home_runs,
        whip::float              as whip,
        pitches_thrown,
        strikes
    from source
)

select * from renamed
```

- [ ] **Step 2: Run the model**

```bash
dbt run --select stg_pitcher_game_logs
```

Expected output:
```
1 of 1 OK created sql view model STAGING.stg_pitcher_game_logs
```

- [ ] **Step 3: Add tests to `models/staging/schema.yml`**

Append under the existing `models:` list:

```yaml
  - name: stg_pitcher_game_logs
    columns:
      - name: player_id
        tests:
          - not_null
      - name: game_pk
        tests:
          - not_null
      - name: game_date
        tests:
          - not_null
```

- [ ] **Step 4: Run tests**

```bash
dbt test --select stg_pitcher_game_logs
```

Expected output:
```
3 of 3 PASS
```

- [ ] **Step 5: Commit**

```bash
git add models/staging/stg_pitcher_game_logs.sql models/staging/schema.yml
git commit -m "Add stg_pitcher_game_logs staging model with tests"
```

---

### Task 7: Write dim_pitcher

**Files:**
- Create: `models/mart/dim_pitcher.sql`
- Create: `models/mart/schema.yml`

- [ ] **Step 1: Create `models/mart/dim_pitcher.sql`**

```sql
with stg as (
    select * from {{ ref('stg_players') }}
)

select
    player_id,
    full_name,
    pitch_hand,
    bat_side,
    position,
    birth_date,
    mlb_debut_date,
    active
from stg
```

- [ ] **Step 2: Run the model**

```bash
dbt run --select dim_pitcher
```

Expected output:
```
1 of 1 OK created sql table model MART.dim_pitcher
```

- [ ] **Step 3: Create `models/mart/schema.yml` with tests**

```yaml
version: 2

models:
  - name: dim_pitcher
    columns:
      - name: player_id
        tests:
          - not_null
          - unique
      - name: full_name
        tests:
          - not_null
```

- [ ] **Step 4: Run tests**

```bash
dbt test --select dim_pitcher
```

Expected output:
```
2 of 2 PASS
```

- [ ] **Step 5: Commit**

```bash
git add models/mart/dim_pitcher.sql models/mart/schema.yml
git commit -m "Add dim_pitcher mart model with tests"
```

---

### Task 8: Write fact_pitcher_game

**Files:**
- Create: `models/mart/fact_pitcher_game.sql`
- Modify: `models/mart/schema.yml`

- [ ] **Step 1: Create `models/mart/fact_pitcher_game.sql`**

```sql
with logs as (
    select * from {{ ref('stg_pitcher_game_logs') }}
),

players as (
    select player_id, full_name from {{ ref('stg_players') }}
),

joined as (
    select
        logs.player_id,
        players.full_name,
        logs.game_pk,
        logs.game_date,
        logs.team_id,
        logs.team_name,
        logs.is_home,
        logs.wins,
        logs.losses,
        logs.era,
        logs.innings_pitched,
        logs.strikeouts,
        logs.walks,
        logs.hits,
        logs.earned_runs,
        logs.home_runs,
        logs.whip,
        logs.pitches_thrown,
        logs.strikes,
        case
            when logs.innings_pitched > 0
            then round((logs.strikeouts / logs.innings_pitched) * 9, 2)
        end as k_per_9,
        case
            when logs.innings_pitched > 0
            then round((logs.walks / logs.innings_pitched) * 9, 2)
        end as bb_per_9,
        case
            when logs.innings_pitched > 0
            then round((logs.hits / logs.innings_pitched) * 9, 2)
        end as h_per_9,
        case
            when logs.walks > 0
            then round(logs.strikeouts / logs.walks::float, 2)
        end as k_bb_ratio,
        case
            when logs.pitches_thrown > 0
            then round(logs.strikes / logs.pitches_thrown::float, 3)
        end as strike_pct
    from logs
    left join players on logs.player_id = players.player_id
)

select * from joined
```

- [ ] **Step 2: Run the model**

```bash
dbt run --select fact_pitcher_game
```

Expected output:
```
1 of 1 OK created sql table model MART.fact_pitcher_game
```

- [ ] **Step 3: Add tests to `models/mart/schema.yml`**

Append under the existing `models:` list:

```yaml
  - name: fact_pitcher_game
    columns:
      - name: player_id
        tests:
          - not_null
      - name: game_pk
        tests:
          - not_null
      - name: game_date
        tests:
          - not_null
```

- [ ] **Step 4: Run tests**

```bash
dbt test --select fact_pitcher_game
```

Expected output:
```
3 of 3 PASS
```

- [ ] **Step 5: Commit**

```bash
git add models/mart/fact_pitcher_game.sql models/mart/schema.yml
git commit -m "Add fact_pitcher_game mart model with computed rate stats and tests"
```

---

### Task 9: Write mart_pitcher_season

**Files:**
- Create: `models/mart/mart_pitcher_season.sql`
- Modify: `models/mart/schema.yml`

- [ ] **Step 1: Create `models/mart/mart_pitcher_season.sql`**

```sql
with fact as (
    select * from {{ ref('fact_pitcher_game') }}
),

aggregated as (
    select
        player_id,
        full_name,
        count(*)                        as games,
        round(sum(innings_pitched), 1)  as total_ip,
        sum(strikeouts)                 as total_strikeouts,
        sum(walks)                      as total_walks,
        sum(hits)                       as total_hits,
        sum(earned_runs)                as total_earned_runs,
        sum(home_runs)                  as total_home_runs,
        sum(wins)                       as wins,
        sum(losses)                     as losses,
        case
            when sum(innings_pitched) > 0
            then round((sum(earned_runs) / sum(innings_pitched)) * 9, 2)
        end as season_era,
        case
            when sum(innings_pitched) > 0
            then round((sum(walks) + sum(hits)) / sum(innings_pitched), 3)
        end as season_whip,
        case
            when sum(innings_pitched) > 0
            then round((sum(strikeouts) / sum(innings_pitched)) * 9, 2)
        end as season_k_per_9,
        case
            when sum(innings_pitched) > 0
            then round((sum(walks) / sum(innings_pitched)) * 9, 2)
        end as season_bb_per_9
    from fact
    group by player_id, full_name
)

select * from aggregated
```

- [ ] **Step 2: Run the model**

```bash
dbt run --select mart_pitcher_season
```

Expected output:
```
1 of 1 OK created sql table model MART.mart_pitcher_season
```

- [ ] **Step 3: Add tests to `models/mart/schema.yml`**

Append under the existing `models:` list:

```yaml
  - name: mart_pitcher_season
    columns:
      - name: player_id
        tests:
          - not_null
          - unique
      - name: full_name
        tests:
          - not_null
```

- [ ] **Step 4: Run tests**

```bash
dbt test --select mart_pitcher_season
```

Expected output:
```
2 of 2 PASS
```

- [ ] **Step 5: Commit**

```bash
git add models/mart/mart_pitcher_season.sql models/mart/schema.yml
git commit -m "Add mart_pitcher_season rollup model with tests"
```

---

### Task 10: Full run and validation

**Files:** none

- [ ] **Step 1: Run all models from scratch**

```bash
dbt run
```

Expected output — all 5 models succeed:
```
1 of 5 OK created sql view model STAGING.stg_players
2 of 5 OK created sql view model STAGING.stg_pitcher_game_logs
3 of 5 OK created sql table model MART.dim_pitcher
4 of 5 OK created sql table model MART.fact_pitcher_game
5 of 5 OK created sql table model MART.mart_pitcher_season
```

- [ ] **Step 2: Run all tests**

```bash
dbt test
```

Expected: all tests pass (15 total across staging and mart schema.yml files).

- [ ] **Step 3: Verify schemas in Snowflake**

In the Snowflake console, confirm:
- `SF_GIANTS_DB.STAGING.STG_PLAYERS` exists (view)
- `SF_GIANTS_DB.STAGING.STG_PITCHER_GAME_LOGS` exists (view)
- `SF_GIANTS_DB.MART.DIM_PITCHER` exists (table)
- `SF_GIANTS_DB.MART.FACT_PITCHER_GAME` exists (table)
- `SF_GIANTS_DB.MART.MART_PITCHER_SEASON` exists (table)
