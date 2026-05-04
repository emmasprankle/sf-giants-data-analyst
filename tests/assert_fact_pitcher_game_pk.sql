-- Fails if any (player_id, game_pk) pair is duplicated or either key column is null.
-- Duplicate rows mean the same pitcher-game was loaded twice.
-- Null keys mean a record is unidentifiable and can't be joined.

WITH duplicates AS (
    SELECT player_id, game_pk
    FROM {{ ref('fact_pitcher_game') }}
    GROUP BY player_id, game_pk
    HAVING COUNT(*) > 1
),

nulls AS (
    SELECT player_id, game_pk
    FROM {{ ref('fact_pitcher_game') }}
    WHERE player_id IS NULL OR game_pk IS NULL
)

SELECT * FROM duplicates
UNION ALL
SELECT * FROM nulls
