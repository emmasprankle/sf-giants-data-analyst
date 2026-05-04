WITH stg AS (
    SELECT * FROM {{ ref('stg_players') }}
)

SELECT
    player_id,
    full_name,
    pitch_hand,
    bat_side,
    position,
    birth_date,
    mlb_debut_date,
    active
FROM stg
