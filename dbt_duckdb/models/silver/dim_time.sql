{{ config(
    materialized='table'
) }}

WITH raw_times AS (

    SELECT DISTINCT

        CAST(check_date AS DATE) AS check_date,
        check_year,
        check_month,
        check_hour,
        check_day_name,
        is_weekend,
        is_business_hour

    FROM {{ ref('int_website_dedup') }}

),

dates AS (

    SELECT

        check_date,
        MIN(check_year) AS check_year,
        MIN(check_month) AS check_month,
        MIN(check_hour) AS check_hour,
        MIN(check_day_name) AS check_day_name,
        MAX(CASE WHEN is_weekend THEN 1 ELSE 0 END) = 1 AS is_weekend,
        MAX(CASE WHEN is_business_hour THEN 1 ELSE 0 END) = 1 AS is_business_hour

    FROM raw_times

    GROUP BY check_date

),

final AS (

    SELECT

        {{ generate_surrogate_key([
            'check_date'
        ]) }} AS time_key,

        check_date,
        check_year,
        check_month,

        CASE
            WHEN check_month IN (1,2,3) THEN 1
            WHEN check_month IN (4,5,6) THEN 2
            WHEN check_month IN (7,8,9) THEN 3
            ELSE 4
        END AS quarter,

        EXTRACT(WEEK FROM CAST(check_date AS DATE)) AS week_of_year,

        check_day_name,
        check_hour,

        is_weekend,
        is_business_hour

    FROM dates

)

SELECT *
FROM final