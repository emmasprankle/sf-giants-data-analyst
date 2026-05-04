# Star Schema Extension Design — Pitching Coach Views

**Date:** 2026-05-03
**Project:** sf_giants_analytics

## Overview

Extend the existing mart layer with two new objects to support pitching coach use cases: season-level comparison and game-by-game trend tracking with rolling averages.

---

## Stakeholder & Use Cases

**Stakeholder:** Pitching coach / player development staff

**Use cases:**
1. **Comparison view** — rank and compare all pitchers by season totals (`mart_pitcher_season`, already exists)
2. **Trend view** — track an individual pitcher's performance across starts, with 5-start rolling averages to smooth noise

---

## What Stays the Same

- `fact_pitcher_game` — no changes; already has `is_home`, `game_date`, `game_pk`, and all required stats
- `mart_pitcher_season` — no changes; powers the season-totals leaderboard

---

## New Objects

### `dim_game`

One row per game. Sourced from `fact_pitcher_game` via `distinct on game_pk` — required because `fact_pitcher_game` has one row per pitcher per game, so multiple pitchers per game must be collapsed.

**Columns:**
| Column | Type | Notes |
|--------|------|-------|
| `game_pk` | INTEGER | PK |
| `game_date` | DATE | |
| `is_home` | BOOLEAN | True = Giants home game |

**Note:** Opponent is not available in current raw data. Future enhancement would require pulling opponent from the MLB Stats API by `game_pk`.

**Materialization:** table

---

### `mart_pitcher_rolling`

One row per pitcher per game. Extends `fact_pitcher_game` with 5-start rolling averages for each key metric, computed via SQL window functions.

**Window definition:**
```sql
partition by player_id
order by game_date
rows between 4 preceding and current row
```

**Columns:**
| Column | Source |
|--------|--------|
| `player_id` | fact_pitcher_game |
| `full_name` | fact_pitcher_game |
| `game_pk` | fact_pitcher_game |
| `game_date` | fact_pitcher_game |
| `is_home` | fact_pitcher_game |
| `innings_pitched` | fact_pitcher_game |
| `era` | fact_pitcher_game |
| `whip` | fact_pitcher_game |
| `k_per_9` | fact_pitcher_game |
| `bb_per_9` | fact_pitcher_game |
| `strike_pct` | fact_pitcher_game |
| `pitches_per_inning` | computed: pitches_thrown / innings_pitched |
| `rolling_era` | 5-game avg of era |
| `rolling_whip` | 5-game avg of whip |
| `rolling_k_per_9` | 5-game avg of k_per_9 |
| `rolling_bb_per_9` | 5-game avg of bb_per_9 |
| `rolling_strike_pct` | 5-game avg of strike_pct |
| `rolling_pitches_per_inning` | 5-game avg of pitches_per_inning |

**Materialization:** table

---

## Final Mart Layer

```
mart_pitcher_season     → season leaderboard / comparison view
mart_pitcher_rolling    → per-pitcher trend view with rolling averages
dim_game                → game dimension (date, home/away)
dim_pitcher             → pitcher attributes (existing)
fact_pitcher_game       → grain: one row per pitcher per game (existing)
```

---

## File Map

| Action | Path |
|--------|------|
| Create | `models/mart/dim_game.sql` |
| Create | `models/mart/mart_pitcher_rolling.sql` |
| Modify | `models/mart/schema.yml` (add tests for both new models) |
