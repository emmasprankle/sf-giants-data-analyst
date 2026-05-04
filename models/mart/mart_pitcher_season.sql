WITH fact AS (
    SELECT * FROM {{ ref('fact_pitcher_game') }}
),

aggregated AS (
    SELECT
        player_id,
        full_name,
        COUNT(*)                        AS games,
        ROUND(SUM(innings_pitched), 1)  AS total_ip,
        SUM(strikeouts)                 AS total_strikeouts,
        SUM(walks)                      AS total_walks,
        SUM(hits)                       AS total_hits,
        SUM(earned_runs)                AS total_earned_runs,
        SUM(home_runs)                  AS total_home_runs,
        SUM(wins)                       AS wins,
        SUM(losses)                     AS losses,
        CASE
            WHEN SUM(innings_pitched) > 0
            THEN ROUND((SUM(earned_runs) / SUM(innings_pitched)) * 9, 2)
        END AS season_era,
        CASE
            WHEN SUM(innings_pitched) > 0
            THEN ROUND((SUM(walks) + SUM(hits)) / SUM(innings_pitched), 3)
        END AS season_whip,
        CASE
            WHEN SUM(innings_pitched) > 0
            THEN ROUND((SUM(strikeouts) / SUM(innings_pitched)) * 9, 2)
        END AS season_k_per_9,
        CASE
            WHEN SUM(innings_pitched) > 0
            THEN ROUND((SUM(walks) / SUM(innings_pitched)) * 9, 2)
        END AS season_bb_per_9
    FROM fact
    GROUP BY player_id, full_name
)

SELECT * FROM aggregated
