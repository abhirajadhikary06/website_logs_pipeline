{{ config(materialized='table') }}

WITH sla_metrics AS (

    SELECT

        website_name,
        check_date,

        COUNT(*) AS total_checks,

        SUM(
            CASE
                WHEN sla_breach = TRUE THEN 1
                ELSE 0
            END
        ) AS sla_breach_count,

        AVG(response_time_ms)
            AS avg_response_time_ms

    FROM {{ ref('fct_website_checks') }}

    GROUP BY
        website_name,
        check_date

),

final AS (

    SELECT

        *,

        {{ calculate_sla_breach_percentage(
            'sla_breach_count',
            'total_checks'
        ) }} AS sla_breach_percentage

    FROM sla_metrics

)

SELECT *
FROM final