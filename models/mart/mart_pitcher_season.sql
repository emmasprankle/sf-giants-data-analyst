with fact as (
    select * from {{ ref('fact_pitcher_game') }}
),

aggregated as (
    select
        player_id,
        full_name,
        count(*)                        as games,
        round(sum(innings_pitched), 1)  as total_ip,
        sum(strikeouts)                 as total_strikeouts,
        sum(walks)                      as total_walks,
        sum(hits)                       as total_hits,
        sum(earned_runs)                as total_earned_runs,
        sum(home_runs)                  as total_home_runs,
        sum(wins)                       as wins,
        sum(losses)                     as losses,
        case
            when sum(innings_pitched) > 0
            then round((sum(earned_runs) / sum(innings_pitched)) * 9, 2)
        end as season_era,
        case
            when sum(innings_pitched) > 0
            then round((sum(walks) + sum(hits)) / sum(innings_pitched), 3)
        end as season_whip,
        case
            when sum(innings_pitched) > 0
            then round((sum(strikeouts) / sum(innings_pitched)) * 9, 2)
        end as season_k_per_9,
        case
            when sum(innings_pitched) > 0
            then round((sum(walks) / sum(innings_pitched)) * 9, 2)
        end as season_bb_per_9
    from fact
    group by player_id, full_name
)

select * from aggregated
