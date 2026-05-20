{% macro safe_divide(numerator, denominator, default_value=0) -%}
    case
        when {{ denominator }} is null or {{ denominator }} = 0 then {{ default_value }}
        else cast({{ numerator }} as double) / cast({{ denominator }} as double)
    end
{%- endmacro %}