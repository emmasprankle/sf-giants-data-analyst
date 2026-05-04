with source as (
    select * from {{ source('raw', 'pitcher_game_logs') }}
),

renamed as (
    select
        player_id,
        game_pk,
        try_to_date(game_date)   as game_date,
        team_id,
        team_name,
        is_home,
        wins,
        losses,
        era::float               as era,
        innings_pitched::float   as innings_pitched,
        strikeouts,
        walks,
        hits,
        earned_runs,
        home_runs,
        whip::float              as whip,
        pitches_thrown,
        strikes
    from source
)

select * from renamed
