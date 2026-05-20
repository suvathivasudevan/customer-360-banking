
with source as (

    select DISTINCT * from {{ source('banking_raw', 'customers') }}

),

deduplicated as (
    select *,
        row_number() over (
            partition by customer_id
            order by last_modified_date desc
        ) as row_num
    from source
),

cleaned as (

    select
        customer_id,
        first_name,
        last_name,
        first_name || ' ' || last_name       as full_name,
        date_of_birth,
        email,
        phone,
        address_street,
        address_city,
        address_region,
        postcode,
        upper(customer_segment)              as customer_segment,
        upper(kyc_status)                    as kyc_status,
        created_date,
        last_modified_date,

        -- derived columns
        datediff(current_date(), date_of_birth) / 365  as age_years,
        case
            when upper(kyc_status) = 'VERIFIED' then true
            else false
        end                                  as is_kyc_verified

    from deduplicated where row_num = 1

)

select * from cleaned