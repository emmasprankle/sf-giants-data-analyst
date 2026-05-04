with date_spine as (
    select
        dateadd(day, seq4(), date '2020-01-01') as date_day
    from table(generator(rowcount => 4018))
),

enriched as (
    select
        date_day,
        year(date_day)                                       as year,
        quarter(date_day)                                    as quarter,
        month(date_day)                                      as month_number,
        monthname(date_day)                                  as month_name,
        weekofyear(date_day)                                 as week_of_year,
        day(date_day)                                        as day_of_month,
        dayofweek(date_day)                                  as day_of_week,
        dayname(date_day)                                    as day_name,
        iff(dayofweek(date_day) in (0, 6), true, false)     as is_weekend,
        iff(month(date_day) between 4 and 9, true, false)   as is_mlb_season
    from date_spine
)

select * from enriched
