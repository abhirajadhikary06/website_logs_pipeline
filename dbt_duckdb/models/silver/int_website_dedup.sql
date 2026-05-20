{{ config(materialized='view') }}

WITH ranked AS (

    SELECT

        *,

        {{ get_time_attributes('checked_at') }},

        ROW_NUMBER() OVER (

            PARTITION BY
                url,
                checked_at

            ORDER BY
                ingestion_time DESC

        ) AS row_num

    FROM {{ source('bronze', 'transform_website_checks_log') }}

)

SELECT *

FROM ranked

WHERE row_num = 1