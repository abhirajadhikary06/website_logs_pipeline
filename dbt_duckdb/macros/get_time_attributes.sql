{% macro get_time_attributes(ts_col) -%}
    date_trunc('minute', {{ ts_col }}) as check_minute,
    date_trunc('hour', {{ ts_col }}) as check_hour_ts,
    cast({{ ts_col }} as date) as check_date,
    extract(year from {{ ts_col }}) as check_year,
    extract(month from {{ ts_col }}) as check_month,
    extract(day from {{ ts_col }}) as check_day,
    extract(dow from {{ ts_col }}) as check_day_of_week,
    case extract(dow from {{ ts_col }})
        when 0 then 'Sunday'
        when 1 then 'Monday'
        when 2 then 'Tuesday'
        when 3 then 'Wednesday'
        when 4 then 'Thursday'
        when 5 then 'Friday'
        when 6 then 'Saturday'
        else null
    end as check_day_name,
    extract(hour from {{ ts_col }}) as check_hour,
    case
        when extract(dow from {{ ts_col }}) in (0, 6) then true
        else false
    end as is_weekend,
    case
        when extract(hour from {{ ts_col }}) between 9 and 18 then true
        else false
    end as is_business_hour
{%- endmacro %}
