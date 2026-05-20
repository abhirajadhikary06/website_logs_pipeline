{% macro calculate_uptime_percentage(successful_checks, total_checks) -%}

coalesce(

    round(
        (
            cast({{ successful_checks }} as double)
            /
            nullif(cast({{ total_checks }} as double), 0)
        ) * 100,
        2
    ),

    0

)

{%- endmacro %}