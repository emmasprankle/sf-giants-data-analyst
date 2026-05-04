WITH fact AS (
    SELECT * FROM {{ ref('fact_pitcher_game') }}
),

with_pitches_per_inning AS (
    SELECT
        *,
        CASE
            WHEN innings_pitched > 0
            THEN ROUND(pitches_thrown / innings_pitched, 2)
        END AS pitches_per_inning
    FROM fact
),

rolling AS (
    SELECT
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
        ROUND(AVG(era) OVER (
            PARTITION BY player_id
            ORDER BY game_date
            ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
        ), 2) AS rolling_era,
        ROUND(AVG(whip) OVER (
            PARTITION BY player_id
            ORDER BY game_date
            ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
        ), 3) AS rolling_whip,
        ROUND(AVG(k_per_9) OVER (
            PARTITION BY player_id
            ORDER BY game_date
            ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
        ), 2) AS rolling_k_per_9,
        ROUND(AVG(bb_per_9) OVER (
            PARTITION BY player_id
            ORDER BY game_date
            ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
        ), 2) AS rolling_bb_per_9,
        ROUND(AVG(strike_pct) OVER (
            PARTITION BY player_id
            ORDER BY game_date
            ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
        ), 3) AS rolling_strike_pct,
        ROUND(AVG(pitches_per_inning) OVER (
            PARTITION BY player_id
            ORDER BY game_date
            ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
        ), 2) AS rolling_pitches_per_inning
    FROM with_pitches_per_inning
)

SELECT * FROM rolling
