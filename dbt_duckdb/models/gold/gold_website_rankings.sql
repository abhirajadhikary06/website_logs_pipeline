{{ config(materialized='table') }}

WITH rankings AS (

    SELECT

        website_name,

        AVG(response_time_ms)
            AS avg_response_time_ms,

        SUM(
            CASE
                WHEN is_error = TRUE THEN 1
                ELSE 0
            END
        ) AS total_errors,

        SUM(
            CASE
                WHEN sla_breach = TRUE THEN 1
                ELSE 0
            END
        ) AS total_sla_breaches,

        COUNT(*) AS total_checks

    FROM {{ ref('fct_website_checks') }}

    GROUP BY website_name

),

final AS (

    SELECT

        *,

        {{ calculate_error_rate(
            'total_errors',
            'total_checks'
        ) }} AS error_rate,

        RANK() OVER (
            ORDER BY avg_response_time_ms ASC
        ) AS fastest_rank,

        RANK() OVER (
            ORDER BY total_errors DESC
        ) AS error_rank,

        RANK() OVER (
            ORDER BY total_sla_breaches DESC
        ) AS sla_rank

    FROM rankings

)

SELECT *
FROM final