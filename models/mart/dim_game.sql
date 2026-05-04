with games as (
    select distinct
        game_pk,
        game_date
    from {{ ref('fact_pitcher_game') }}
)

select * from games
