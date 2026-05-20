{{ config(materialized='view') }}

WITH enriched AS (

    SELECT

        id,

        url,
        website_name,
        domain,

        response_time_ms,
        response_time_s,

        status_code,
        status_group,

        performance_bucket,

        is_error,
        is_success,
        is_redirect,
        is_slow_response,

        checked_at,

        {{ classify_health(
            'status_code',
            'response_time_ms',
            'is_error'
        ) }} AS health_status,

        {{ bucket_response_time('response_time_ms') }} AS performance_bucket,

        CASE
            WHEN ({{ bucket_response_time('response_time_ms') }}) IN ('slow', 'very_slow')
                THEN TRUE
            ELSE FALSE
        END AS sla_breach

    FROM {{ ref('int_website_dedup') }}

)

SELECT *
FROM enriched