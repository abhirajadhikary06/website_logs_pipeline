{{ config(
    materialized='incremental',
    unique_key='check_key'
) }}

WITH base AS (

    SELECT *
    FROM {{ ref('int_website_dedup') }}

    {% if is_incremental() %}

        WHERE checked_at >
        (
            SELECT MAX(checked_at)
            FROM {{ this }}
        )

    {% endif %}

),

final AS (

    SELECT

        CASE

            WHEN b.id IS NOT NULL
                THEN 'id:' || CAST(b.id AS VARCHAR)

            ELSE md5(

                COALESCE(b.url, '') || '|'
                || COALESCE(CAST(b.checked_at AS VARCHAR), '') || '|'
                || COALESCE(CAST(b.status_code AS VARCHAR), '') || '|'
                || COALESCE(CAST(b.response_time_ms AS VARCHAR), '') || '|'
                || COALESCE(b.status_message, '')

            )

        END AS check_key,

        b.id,

        b.url,
        b.website_name,
        b.domain,

        b.status_code,
        b.status_message,
        b.status_group,

        b.response_time_ms,
        b.response_time_s,

        {{ bucket_response_time('b.response_time_ms') }}
            AS performance_bucket,

        b.is_error,
        b.is_success,
        b.is_redirect,
        b.is_slow_response,

        b.checked_at,
        b.check_date,
        b.check_month,
        b.check_year,
        b.check_hour,
        b.check_day_name,

        b.ingestion_time,
        b.load_time,

        {{ classify_health(
            'b.status_code',
            'b.response_time_ms',
            'b.is_error'
        ) }} AS health_status,

        CASE

            WHEN {{ bucket_response_time(
                'b.response_time_ms'
            ) }} IN ('slow', 'very_slow')

                THEN TRUE

            ELSE FALSE

        END AS sla_breach,

        dt.time_key,
        dw.website_key,
        ds.status_key

    FROM base b

    LEFT JOIN {{ ref('dim_time') }} dt
        ON dt.check_date = b.check_date

    LEFT JOIN {{ ref('dim_website') }} dw
        ON dw.website_name = b.website_name
       AND dw.domain = b.domain

    LEFT JOIN {{ ref('dim_status') }} ds
        ON ds.status_code = b.status_code
       AND ds.status_group = b.status_group

)

SELECT *
FROM final