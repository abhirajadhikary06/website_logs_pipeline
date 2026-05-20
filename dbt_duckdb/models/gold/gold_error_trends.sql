{{ config(materialized='table') }}

WITH error_metrics AS (

    SELECT

        check_date,

        COUNT(*) AS total_checks,

        SUM(
            CASE
                WHEN is_error = TRUE THEN 1
                ELSE 0
            END
        ) AS total_errors,

        COUNT(DISTINCT website_name)
            AS unique_websites

    FROM {{ ref('fct_website_checks') }}

    GROUP BY check_date

),

final AS (

    SELECT

        *,

        {{ calculate_error_rate(
            'total_errors',
            'total_checks'
        ) }} AS error_rate

    FROM error_metrics

)

SELECT *
FROM final