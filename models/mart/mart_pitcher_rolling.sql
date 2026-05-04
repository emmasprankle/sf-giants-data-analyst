with fact as (
    select * from {{ ref('fact_pitcher_game') }}
),

with_pitches_per_inning as (
    select
        *,
        case
            when innings_pitched > 0
            then round(pitches_thrown / innings_pitched, 2)
        end as pitches_per_inning
    from fact
),

rolling as (
    select
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
        round(avg(era) over (
            partition by player_id
            order by game_date
            rows between 4 preceding and current row
        ), 2) as rolling_era,
        round(avg(whip) over (
            partition by player_id
            order by game_date
            rows between 4 preceding and current row
        ), 3) as rolling_whip,
        round(avg(k_per_9) over (
            partition by player_id
            order by game_date
            rows between 4 preceding and current row
        ), 2) as rolling_k_per_9,
        round(avg(bb_per_9) over (
            partition by player_id
            order by game_date
            rows between 4 preceding and current row
        ), 2) as rolling_bb_per_9,
        round(avg(strike_pct) over (
            partition by player_id
            order by game_date
            rows between 4 preceding and current row
        ), 3) as rolling_strike_pct,
        round(avg(pitches_per_inning) over (
            partition by player_id
            order by game_date
            rows between 4 preceding and current row
        ), 2) as rolling_pitches_per_inning
    from with_pitches_per_inning
)

select * from rolling
