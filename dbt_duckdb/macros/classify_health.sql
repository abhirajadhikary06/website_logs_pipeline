{% macro classify_health(status_code, response_time_ms, is_error) -%}
    case
        when {{ is_error }} = true then 'critical'
        when {{ status_code }} >= 500 then 'critical'
        when {{ status_code }} >= 400 then 'warning'
        when {{ response_time_ms }} is null then 'unknown'
        when {{ response_time_ms }} < 500 then 'healthy'
        when {{ response_time_ms }} < 2000 then 'degraded'
        else 'critical'
    end
{%- endmacro %}
