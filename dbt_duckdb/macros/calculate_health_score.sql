{% macro calculate_health_score(
    uptime_percentage,
    error_rate,
    sla_breach_percentage
) -%}

greatest(

    0,

    round(

        100
        - (cast({{ error_rate }} as double) * 0.5)
        - (cast({{ sla_breach_percentage }} as double) * 0.3)
        + (cast({{ uptime_percentage }} as double) * 0.2),

        2

    )

)

{%- endmacro %}