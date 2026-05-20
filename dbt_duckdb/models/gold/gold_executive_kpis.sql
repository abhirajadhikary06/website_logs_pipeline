{{ config(materialized='table') }}

WITH kpis AS (

    SELECT

        COUNT(*) AS total_checks,

        COUNT(DISTINCT website_name)
            AS total_websites,

        AVG(response_time_ms)
            AS avg_response_time_ms,

        SUM(
            CASE
                WHEN is_success = TRUE THEN 1
                ELSE 0
            END
        ) AS successful_checks,

        SUM(
            CASE
                WHEN is_error = TRUE THEN 1
                ELSE 0
            END
        ) AS failed_checks,

        SUM(
            CASE
                WHEN sla_breach = TRUE THEN 1
                ELSE 0
            END
        ) AS sla_breach_count

    FROM {{ ref('fct_website_checks') }}

),

final AS (

    SELECT

        *,

        {{ calculate_uptime_percentage(
            'successful_checks',
            'total_checks'
        ) }} AS uptime_percentage,

        {{ calculate_error_rate(
            'failed_checks',
            'total_checks'
        ) }} AS error_rate,

        {{ calculate_sla_breach_percentage(
            'sla_breach_count',
            'total_checks'
        ) }} AS sla_breach_percentage

    FROM kpis

)

SELECT *
FROM final