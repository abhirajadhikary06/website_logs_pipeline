{{ config(materialized='table') }}

WITH websites AS (

    SELECT DISTINCT

        website_name,
        domain

    FROM {{ source('bronze', 'transform_website_checks_log') }}

),

final AS (

    SELECT

        {{ generate_surrogate_key([
            'website_name',
            'domain'
        ]) }} AS website_key,

        website_name,
        domain

    FROM websites

)

SELECT *
FROM final