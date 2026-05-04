with games as (
    select
        game_pk,
        game_date,
        max(is_home) as is_home
    from {{ ref('fact_pitcher_game') }}
    group by game_pk, game_date
)

select * from games
