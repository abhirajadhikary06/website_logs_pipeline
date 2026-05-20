{% macro calculate_error_rate(error_count, total_checks) -%}

coalesce(

    round(
        (
            cast({{ error_count }} as double)
            /
            nullif(cast({{ total_checks }} as double), 0)
        ) * 100,
        2
    ),

    0

)

{%- endmacro %}