{{ config(materialized='table') }}

WITH website_metrics AS (

    SELECT

        website_key,
        website_name,
        domain,

        COUNT(*) AS total_checks,

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

        AVG(response_time_ms)
            AS avg_response_time_ms,

        percentile_cont(0.95)
        WITHIN GROUP (
            ORDER BY response_time_ms
        ) AS p95_latency_ms,

        SUM(
            CASE
                WHEN sla_breach = TRUE THEN 1
                ELSE 0
            END
        ) AS sla_breach_count

    FROM {{ ref('fct_website_checks') }}

    GROUP BY
        website_key,
        website_name,
        domain

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
        ) }} AS sla_breach_percentage,

        {{ calculate_health_score(
            calculate_uptime_percentage(
                'successful_checks',
                'total_checks'
            ),
            calculate_error_rate(
                'failed_checks',
                'total_checks'
            ),
            calculate_sla_breach_percentage(
                'sla_breach_count',
                'total_checks'
            )
        ) }} AS health_score

    FROM website_metrics

)

SELECT *
FROM final