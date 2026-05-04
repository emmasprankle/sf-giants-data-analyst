WITH logs AS (
    SELECT * FROM {{ ref('stg_pitcher_game_logs') }}
),

players AS (
    SELECT player_id, full_name FROM {{ ref('stg_players') }}
),

joined AS (
    SELECT
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
        CASE
            WHEN logs.innings_pitched > 0
            THEN ROUND((logs.strikeouts / logs.innings_pitched) * 9, 2)
        END AS k_per_9,
        CASE
            WHEN logs.innings_pitched > 0
            THEN ROUND((logs.walks / logs.innings_pitched) * 9, 2)
        END AS bb_per_9,
        CASE
            WHEN logs.innings_pitched > 0
            THEN ROUND((logs.hits / logs.innings_pitched) * 9, 2)
        END AS h_per_9,
        CASE
            WHEN logs.walks > 0
            THEN ROUND(logs.strikeouts / logs.walks::FLOAT, 2)
        END AS k_bb_ratio,
        CASE
            WHEN logs.pitches_thrown > 0
            THEN ROUND(logs.strikes / logs.pitches_thrown::FLOAT, 3)
        END AS strike_pct
    FROM logs
    LEFT JOIN players ON logs.player_id = players.player_id
)

SELECT * FROM joined
