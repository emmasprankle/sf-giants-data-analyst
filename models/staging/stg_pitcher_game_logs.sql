WITH source AS (
    SELECT * FROM {{ source('raw', 'pitcher_game_logs') }}
),

renamed AS (
    SELECT
        player_id,
        game_pk,
        TRY_TO_DATE(game_date)   AS game_date,
        team_id,
        team_name,
        is_home,
        wins,
        losses,
        era::FLOAT               AS era,
        innings_pitched::FLOAT   AS innings_pitched,
        strikeouts,
        walks,
        hits,
        earned_runs,
        home_runs,
        whip::FLOAT              AS whip,
        pitches_thrown,
        strikes
    FROM source
)

SELECT * FROM renamed
