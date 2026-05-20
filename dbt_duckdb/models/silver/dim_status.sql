{{ config(materialized='table') }}

WITH statuses AS (

    SELECT DISTINCT

        status_code,
        status_group,
        is_error,
        is_success,
        is_redirect

    FROM {{ source('bronze', 'transform_website_checks_log') }}

),

final AS (

    SELECT

        {{ generate_surrogate_key([
            'status_code',
            'status_group'
        ]) }} AS status_key,

        status_code,
        status_group,
        is_error,
        is_success,
        is_redirect

    FROM statuses

)

SELECT *
FROM final