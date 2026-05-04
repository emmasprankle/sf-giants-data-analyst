# Star Schema Extension Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `dim_game` and `mart_pitcher_rolling` to the mart layer to support a pitching coach's trend view alongside the existing season-totals comparison view.

**Architecture:** `dim_game` is built from `fact_pitcher_game` deduplicated on `game_pk` (one row per game, not per pitcher-game). `mart_pitcher_rolling` extends `fact_pitcher_game` with 5-start rolling averages using SQL window functions partitioned by `player_id` and ordered by `game_date`. Both are materialized as tables and tested via `schema.yml`.

**Tech Stack:** dbt 1.11.8, dbt-snowflake 1.11.4, Snowflake (SF_GIANTS_DB)

---

## File Map

| Action | Path |
|--------|------|
| Create | `models/mart/dim_game.sql` |
| Create | `models/mart/mart_pitcher_rolling.sql` |
| Modify | `models/mart/schema.yml` |

---

### Task 1: Write dim_game

**Files:**
- Create: `models/mart/dim_game.sql`
- Modify: `models/mart/schema.yml`

- [ ] **Step 1: Create `models/mart/dim_game.sql`**

```sql
with games as (
    select distinct
        game_pk,
        game_date,
        is_home
    from {{ ref('fact_pitcher_game') }}
)

select * from games
```

- [ ] **Step 2: Run the model**

```bash
dbt run --select dim_game
```

Expected output:
```
1 of 1 OK created sql table model MART.dim_game
```

Row count should be less than `fact_pitcher_game` (809 rows) since multiple pitchers share the same game. Expect roughly 150–180 distinct games for a full 2024 season.

- [ ] **Step 3: Append tests to `models/mart/schema.yml`**

The file currently ends after `mart_pitcher_season`. Append under the existing `models:` list:

```yaml
  - name: dim_game
    columns:
      - name: game_pk
        tests:
          - not_null
          - unique
      - name: game_date
        tests:
          - not_null
```

- [ ] **Step 4: Run tests**

```bash
dbt test --select dim_game
```

Expected output:
```
3 of 3 PASS
```

The `unique` test on `game_pk` verifies the deduplication worked correctly.

- [ ] **Step 5: Commit**

```bash
git add models/mart/dim_game.sql models/mart/schema.yml
git commit -m "Add dim_game mart model with deduplication and tests"
```

---

### Task 2: Write mart_pitcher_rolling

**Files:**
- Create: `models/mart/mart_pitcher_rolling.sql`
- Modify: `models/mart/schema.yml`

- [ ] **Step 1: Create `models/mart/mart_pitcher_rolling.sql`**

```sql
with fact as (
    select * from {{ ref('fact_pitcher_game') }}
),

with_pitches_per_inning as (
    select
        *,
        case
            when innings_pitched > 0
            then round(pitches_thrown / innings_pitched, 2)
        end as pitches_per_inning
    from fact
),

rolling as (
    select
        player_id,
        full_name,
        game_pk,
        game_date,
        is_home,
        innings_pitched,
        era,
        whip,
        k_per_9,
        bb_per_9,
        strike_pct,
        pitches_per_inning,
        round(avg(era) over (
            partition by player_id
            order by game_date
            rows between 4 preceding and current row
        ), 2) as rolling_era,
        round(avg(whip) over (
            partition by player_id
            order by game_date
            rows between 4 preceding and current row
        ), 3) as rolling_whip,
        round(avg(k_per_9) over (
            partition by player_id
            order by game_date
            rows between 4 preceding and current row
        ), 2) as rolling_k_per_9,
        round(avg(bb_per_9) over (
            partition by player_id
            order by game_date
            rows between 4 preceding and current row
        ), 2) as rolling_bb_per_9,
        round(avg(strike_pct) over (
            partition by player_id
            order by game_date
            rows between 4 preceding and current row
        ), 3) as rolling_strike_pct,
        round(avg(pitches_per_inning) over (
            partition by player_id
            order by game_date
            rows between 4 preceding and current row
        ), 2) as rolling_pitches_per_inning
    from with_pitches_per_inning
)

select * from rolling
```

- [ ] **Step 2: Run the model**

```bash
dbt run --select mart_pitcher_rolling
```

Expected output:
```
1 of 1 OK created sql table model MART.mart_pitcher_rolling
```

Row count should equal `fact_pitcher_game` (809 rows) — same grain, just adds rolling columns.

- [ ] **Step 3: Append tests to `models/mart/schema.yml`**

Append under the existing `models:` list (after dim_game):

```yaml
  - name: mart_pitcher_rolling
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
dbt test --select mart_pitcher_rolling
```

Expected output:
```
3 of 3 PASS
```

- [ ] **Step 5: Commit**

```bash
git add models/mart/mart_pitcher_rolling.sql models/mart/schema.yml
git commit -m "Add mart_pitcher_rolling with 5-start rolling averages and tests"
```

---

### Task 3: Full run and validation

**Files:** none

- [ ] **Step 1: Run all models**

```bash
dbt run
```

Expected output — all 7 models succeed:
```
1 of 7 OK created sql view model STAGING.stg_pitcher_game_logs
2 of 7 OK created sql view model STAGING.stg_players
3 of 7 OK created sql table model MART.dim_pitcher
4 of 7 OK created sql table model MART.dim_game
5 of 7 OK created sql table model MART.fact_pitcher_game
6 of 7 OK created sql table model MART.mart_pitcher_rolling
7 of 7 OK created sql table model MART.mart_pitcher_season
```

- [ ] **Step 2: Run all tests**

```bash
dbt test
```

Expected: all 21 tests pass (15 existing + 3 dim_game + 3 mart_pitcher_rolling).

- [ ] **Step 3: Spot-check rolling averages in Snowflake**

Run this query in the Snowflake console to verify rolling values are reasonable for a single pitcher:

```sql
select
    full_name,
    game_date,
    era,
    rolling_era,
    k_per_9,
    rolling_k_per_9
from SF_GIANTS_DB.MART.MART_PITCHER_ROLLING
where full_name = 'Logan Webb'
order by game_date
limit 10;
```

Expected: `rolling_era` for the first row equals `era` (only 1 game in window). By row 5 onward, `rolling_era` should be the average of the previous 5 games' ERA values.
