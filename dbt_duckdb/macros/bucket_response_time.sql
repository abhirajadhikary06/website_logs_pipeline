{% macro bucket_response_time(response_time_ms) -%}
    case
        when {{ response_time_ms }} is null then 'unknown'
        when {{ response_time_ms }} < 200 then 'fast'
        when {{ response_time_ms }} < 1000 then 'moderate'
        when {{ response_time_ms }} < 3000 then 'slow'
        else 'very_slow'
    end
{%- endmacro %}
