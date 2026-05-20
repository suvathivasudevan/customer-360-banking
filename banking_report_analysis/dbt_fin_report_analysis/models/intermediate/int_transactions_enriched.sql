with accounts as(
    select * from {{ ref('stg_accounts') }}
),
customers as (
    select  * from {{ ref('stg_customers') }}
),
transactions as(
    select * from {{ ref('stg_transactions') }}
),
enriched as(
select 
    t.transaction_id,
    t.account_id,
    t.abs_amount,
    t.is_debit,
    t.is_credit,
    a.customer_id,
    c.full_name                             as customer_name,
    c.customer_segment,
    a.account_type,
    

    case
        when t.abs_amount < 10 then 'MICRO'
        when t.abs_amount >= 10 and t.abs_amount < 100 then 'SMALL'
        when t.abs_amount >= 100 and t.abs_amount < 1000 then 'MEDIUM'
        else 'LARGE'
    end as transaction_size_band,
    case
        when t.merchant_category = 'GAMBLING' then true
        else false
    end  as is_gambling,
    case 
        when t.merchant_category = 'CRYPTO' then true
        else false
    end as is_crypto,
    case 
        when t.fraud_score > 70 then true
        else false
    end as is_fraud,
    
    -- then derive
    case
        when nc.city_name is null then true
        else false
    end as is_overseas
    
   from accounts a left join customers c on a.customer_id = c.customer_id
   left join transactions t on a.account_id = t.account_id
   left join {{ ref('nz_cities') }} nc on t.merchant_city = nc.city_name
)
select * from enriched
    