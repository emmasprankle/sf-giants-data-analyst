with stg as (
    select * from {{ ref('stg_players') }}
)

select
    player_id,
    full_name,
    pitch_hand,
    bat_side,
    position,
    birth_date,
    mlb_debut_date,
    active
from stg
