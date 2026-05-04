WITH games AS (
    SELECT
        game_pk,
        game_date,
        MAX(is_home) AS is_home
    FROM {{ ref('fact_pitcher_game') }}
    GROUP BY game_pk, game_date
)

SELECT * FROM games
