{{
    config(
        materialized = 'table',
        post_hook = ["ALTER TABLE {{ this }} SET TBLPROPERTIES ('delta.feature.allowColumnDefaults' = 'supported')"]
    )
}}

with transactions as (
    select * from {{ ref('stg_transactions') }}
),

accounts as (
    select * from {{ ref('stg_accounts') }}
),

customers as (
    select * from {{ ref('stg_customers') }}
),

-- join transactions with enriched flags from intermediate
trans_enriched as (
    select * from {{ ref('int_transactions_enriched') }}
),


final as(
select 
    t.transaction_id,
    t.account_id,
    a.customer_id,
    c.full_name                             as customer_name,
    c.customer_segment,
    c.kyc_status,
    a.account_type,
    a.account_number,
    a.product_name,
  
    te.transaction_size_band,
    te.is_fraud,
    te.is_gambling,
    te.is_crypto,
    te.is_overseas,

    t.transaction_date,
    t.transaction_month,
    t.transaction_year,
    t.transaction_hour,
    t.abs_amount,
    t.channel,
    t.transaction_type,
    t.merchant_category,
    t.merchant_name,
    t.merchant_city,
    t.status,
    t.reference,
    t.balance_after,
    t.fraud_score,
    t.is_declined,
    t.is_settled,
    t.fraud_risk_band,
    t.is_debit,
    t.is_credit,

-- ── derived ───────────────────────────
        case
            when te.is_fraud = true
                 and te.is_overseas = true                   then 'HIGH'
            when te.is_fraud = true                     then 'HIGH'
            when t.fraud_score > 70                          then 'HIGH'
            when te.is_gambling = true
                 and t.fraud_score > 30                      then 'MEDIUM'
            when te.is_overseas = true                       then 'MEDIUM'
            when te.is_gambling = true                       then 'LOW_RISK'
            else                                                  'NORMAL'
        end                                                  as transaction_risk_level,

        -- amount band directly here as well for easy filtering
        case
            when t.abs_amount < 10                           then 'MICRO'
            when t.abs_amount >= 10
                 and t.abs_amount < 100                      then 'SMALL'
            when t.abs_amount >= 100
                 and t.abs_amount < 1000                     then 'MEDIUM'
            else                                                  'LARGE'
        end                                                  as amount_band,

        a.last_modified_date

    from transactions t
    left join accounts  a  on t.account_id  = a.account_id
    left join customers c  on a.customer_id = c.customer_id
    left join trans_enriched te on t.transaction_id = te.transaction_id
)

select * from final

