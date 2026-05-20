{% macro calculate_sla_breach_percentage(sla_breach_count, total_checks) -%}

coalesce(

    round(
        (
            cast({{ sla_breach_count }} as double)
            /
            nullif(cast({{ total_checks }} as double), 0)
        ) * 100,
        2
    ),

    0

)

{%- endmacro %}