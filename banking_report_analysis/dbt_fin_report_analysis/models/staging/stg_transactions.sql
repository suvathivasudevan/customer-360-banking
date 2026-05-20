with source as(
    select DISTINCT * from {{source('banking_raw', 'transactions') }}
),

deduplicated as (
    select *,
        row_number() over (
            partition by transaction_id
            order by transaction_date desc
        ) as row_num
    from source
),

cleaned as(
    select
        upper(transaction_id) as transaction_id,
        account_id as account_id,
        upper(channel) as channel,
        upper(merchant_category) as merchant_category,
        upper(status) as status,
        initcap(merchant_name) as merchant_name,
        initcap(merchant_city) as merchant_city,
        coalesce(reference, 'NOT APPLICABLE') as reference,
        coalesce(balance_after, 0) as balance_after,
        coalesce(fraud_score, 0) as fraud_score,
        is_fraud_flagged as is_fraud,
        abs(amount) as abs_amount,
        transaction_date as transaction_date,
        upper(transaction_type) as transaction_type,

        -- derived columns
        case
        when upper(transaction_type) = 'DEBIT' then true
        else false
        end as is_debit,
        case
            when upper(transaction_type) = 'CREDIT' then true
            else false
        end as is_credit,
        case
            when status = 'DECLINED' then true
            else false
        end as is_declined,
        case
            when status = 'SETTLED' then true
            else false
        end as is_settled,
        extract(year from transaction_date) as transaction_year,
        extract(month from transaction_date) as transaction_month,
        extract(hour from transaction_date) as transaction_hour,
            case
            when transaction_hour between 0 and 5 then 'LOW RISK'
            when transaction_hour between 6 and 11 then 'MEDIUM RISK'
            when transaction_hour between 12 and 17 then 'HIGH RISK'
            else 'VERY HIGH RISK'
            end as fraud_risk_band
        
    from deduplicated where row_num = 1
)
select * from cleaned