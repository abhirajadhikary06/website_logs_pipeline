{{ config(materialized='table') }}

SELECT

    website_name,

    check_date,
    check_hour,

    COUNT(*) AS total_checks,

    AVG(response_time_ms)
        AS avg_response_time_ms,

    SUM(
        CASE
            WHEN is_error = TRUE THEN 1
            ELSE 0
        END
    ) AS error_count,

    SUM(
        CASE
            WHEN is_success = TRUE THEN 1
            ELSE 0
        END
    ) AS success_count,

    SUM(
        CASE
            WHEN sla_breach = TRUE THEN 1
            ELSE 0
        END
    ) AS sla_breach_count

FROM {{ ref('fct_website_checks') }}

GROUP BY
    website_name,
    check_date,
    check_hour