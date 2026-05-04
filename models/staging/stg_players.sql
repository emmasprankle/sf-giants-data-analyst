WITH source AS (
    SELECT * FROM {{ source('raw', 'players') }}
),

renamed AS (
    SELECT
        player_id,
        full_name,
        TRY_TO_DATE(birth_date)  AS birth_date,
        pitch_hand,
        bat_side,
        position,
        TRY_TO_DATE(mlb_debut)   AS mlb_debut_date,
        active
    FROM source
)

SELECT * FROM renamed
