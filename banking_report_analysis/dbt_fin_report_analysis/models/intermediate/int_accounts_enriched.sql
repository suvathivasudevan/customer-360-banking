with accounts as(
    select DISTINCT * from {{ ref('stg_accounts') }}
),
customers as (
    select DISTINCT * from {{ ref('stg_customers') }}
),


enriched as(
select 
    a.account_id,
        a.customer_id,
        c.full_name                             as customer_name,
        c.customer_segment,
        c.kyc_status,
        a.account_number,
        a.account_type,
        a.product_name,
        a.account_status,
        a.balance,
        a.credit_limit,
        a.currency,
        a.is_active,
        a.is_closed,
        a.is_credit_account,
        a.open_date,
        a.close_date,
        a.account_age_days,

        -- credit utilisation (how much of credit limit is used)
        case
        when a.credit_limit > 0
        then round(abs(a.balance) / a.credit_limit * 100, 2)
        else null
        end  as credit_utilisation_pct,

        -- credit health flag based on utilisation
        case
        when a.credit_limit > 0 and round(abs(a.balance) / a.credit_limit) > 0.8
        then 'HIGH UTILIZATION'
        when a.credit_limit > 0 and round(abs(a.balance) / a.credit_limit) > 0.5
        then 'MEDIUM UTILIZATION'
        when a.credit_limit > 0 and round(abs(a.balance) / a.credit_limit) >= 0
        then 'LOW UTILIZATION'
        else 'NOT APPLICABLE'
        end as credit_health_flag,

        -- account age bucket
        case
        when a.account_age_days <180 then 'New'
        when a.account_age_days <365 then  'LESS THAN 1 YEAR'
        when a.account_age_days <1095  then '1_TO_3_YEARS'
        else 'MORE_THAN_3_YEARS'
        end as account_age_band,

        -- balance health
        case
            when a.balance < 0               then 'NEGATIVE'
            when a.balance = 0               then 'ZERO'
            when a.balance < 1000            then 'LOW'
            when a.balance < 10000           then 'MEDIUM'
            else 'HIGH'
        end                                     as balance_band

        from accounts a left join customers c on 
        a.customer_id = c.customer_id
    
)

select * from enriched



