{% macro generate_surrogate_key(field_list) -%}

{# Use a separator to avoid collisions between concatenated values #}
md5(
    {%- for field in field_list -%}
        coalesce(cast({{ field }} as varchar), '')
        {%- if not loop.last %} || '|' || {% endif -%}
    {%- endfor -%}
)

{%- endmacro %}
