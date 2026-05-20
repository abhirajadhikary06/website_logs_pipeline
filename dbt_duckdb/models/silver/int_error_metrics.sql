{{ config(materialized='view') }}

WITH metrics AS (

    SELECT

        website_name,

        COUNT(*) AS total_requests,

        SUM(

            CASE

                WHEN is_success = TRUE
                    THEN 1

                ELSE 0

            END

        ) AS successful_requests,

        SUM(

            CASE

                WHEN is_error = TRUE
                    THEN 1

                ELSE 0

            END

        ) AS failed_requests,

        SUM(

            CASE

                WHEN is_redirect = TRUE
                    THEN 1

                ELSE 0

            END

        ) AS redirected_requests

    FROM {{ ref('int_website_dedup') }}

    GROUP BY website_name

),

final AS (

    SELECT

        website_name,

        total_requests,

        successful_requests,
        failed_requests,
        redirected_requests,

        ROUND(
            {{ safe_divide('successful_requests * 100.0', 'total_requests') }},
            2
        ) AS success_rate,

        ROUND(
            {{ safe_divide('failed_requests * 100.0', 'total_requests') }},
            2
        ) AS error_rate,

        ROUND(
            {{ safe_divide('redirected_requests * 100.0', 'total_requests') }},
            2
        ) AS redirect_rate

    FROM metrics

)

SELECT *
FROM final
