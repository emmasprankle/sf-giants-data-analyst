with source as (
    select * from {{ source('raw', 'players') }}
),

renamed as (
    select
        player_id,
        full_name,
        try_to_date(birth_date)  as birth_date,
        pitch_hand,
        bat_side,
        position,
        try_to_date(mlb_debut)   as mlb_debut_date,
        active
    from source
)

select * from renamed
