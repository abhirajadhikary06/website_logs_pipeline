{{ config(materialized='view') }}

WITH latency AS (

    SELECT

        website_name,

        AVG(response_time_ms)
            AS avg_latency_ms,

        MIN(response_time_ms)
            AS min_latency_ms,

        MAX(response_time_ms)
            AS max_latency_ms,

        percentile_cont(0.95)
        WITHIN GROUP (
            ORDER BY response_time_ms
        ) AS p95_latency_ms,

        COUNT(*) AS total_checks,

        SUM(

            CASE

                WHEN {{ bucket_response_time(
                    'response_time_ms'
                ) }} IN ('slow', 'very_slow')

                    THEN 1

                ELSE 0

            END

        ) AS sla_breach_count

    FROM {{ ref('int_website_dedup') }}

    GROUP BY website_name

)

SELECT *
FROM latency