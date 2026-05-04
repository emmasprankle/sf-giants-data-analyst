WITH date_spine AS (
    SELECT
        DATEADD(day, seq4(), DATE '2020-01-01') AS date_day
    FROM TABLE(GENERATOR(rowcount => 4018))
),

enriched AS (
    SELECT
        date_day,
        YEAR(date_day)                                       AS year,
        QUARTER(date_day)                                    AS quarter,
        MONTH(date_day)                                      AS month_number,
        MONTHNAME(date_day)                                  AS month_name,
        WEEKOFYEAR(date_day)                                 AS week_of_year,
        DAY(date_day)                                        AS day_of_month,
        DAYOFWEEK(date_day)                                  AS day_of_week,
        DAYNAME(date_day)                                    AS day_name,
        IFF(DAYOFWEEK(date_day) IN (0, 6), TRUE, FALSE)     AS is_weekend,
        IFF(MONTH(date_day) BETWEEN 4 AND 9, TRUE, FALSE)   AS is_mlb_season
    FROM date_spine
)

SELECT * FROM enriched
