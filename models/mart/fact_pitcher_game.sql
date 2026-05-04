with logs as (
    select * from {{ ref('stg_pitcher_game_logs') }}
),

players as (
    select player_id, full_name from {{ ref('stg_players') }}
),

joined as (
    select
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
        case
            when logs.innings_pitched > 0
            then round((logs.strikeouts / logs.innings_pitched) * 9, 2)
        end as k_per_9,
        case
            when logs.innings_pitched > 0
            then round((logs.walks / logs.innings_pitched) * 9, 2)
        end as bb_per_9,
        case
            when logs.innings_pitched > 0
            then round((logs.hits / logs.innings_pitched) * 9, 2)
        end as h_per_9,
        case
            when logs.walks > 0
            then round(logs.strikeouts / logs.walks::float, 2)
        end as k_bb_ratio,
        case
            when logs.pitches_thrown > 0
            then round(logs.strikes / logs.pitches_thrown::float, 3)
        end as strike_pct
    from logs
    left join players on logs.player_id = players.player_id
)

select * from joined
