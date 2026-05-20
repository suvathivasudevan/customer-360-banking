with source as (
    select * from {{ source('banking_raw', 'accounts') }}
),

deduplication as (
    select *, row_number() over(
        partition by account_id
        order by last_modified_date desc
    ) as row_num
    from source 
),

cleaned as (
    select
        account_id,
        customer_id,
        account_number,

        -- standardise text fields
        upper(account_type)                     as account_type,
        upper(status)                           as account_status,
        upper(currency)                         as currency,
        initcap(product_name)                   as product_name,

        -- financials
        coalesce(balance, 0)                    as balance,
        coalesce(credit_limit, 0)               as credit_limit,

        -- dates
        open_date,
        close_date,
        last_modified_date,

        -- derived flags
        case
            when upper(status) = 'ACTIVE' then true
            else false
        end                                     as is_active,

        case
            when close_date is not null then true
            else false
        end                                     as is_closed,

        case
            when upper(account_type) = 'CREDIT' then true
            else false
        end                                     as is_credit_account,

        -- how long account has been open (in days)
        datediff(current_date(), open_date)     as account_age_days

    from deduplication where row_num = 1
)

select * from cleaned