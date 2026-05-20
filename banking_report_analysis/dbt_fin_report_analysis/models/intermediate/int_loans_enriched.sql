with loans as (
    select DISTINCT * from {{ ref('stg_loans') }} 
),

customers as (
    select DISTINCT * from {{ ref('stg_customers') }}
),

enriched_loans as (
    select
        l.customer_id,
        c.full_name as customer_name,
        c.customer_segment,
        c.kyc_status,
        c.age_years,
        l.application_id,
        l.is_approved,
        l.is_declined,
        l.is_pending,
        l.credit_score_band,
        l.approved_amount,
        l.debt_to_income,

        case
            when l.debt_to_income < 0.3 then 'LOW'
            when l.debt_to_income >= 0.3 and l.debt_to_income < 0.5 then 'MEDIUM'
            when l.debt_to_income >= 0.5 then 'HIGH'
            else 'NOT APPLICABLE'
        end as debt_to_income_band,

        case
            when l.applied_amount < 10000 then 'SMALL'
            when l.applied_amount >= 10000 and l.applied_amount < 100000 then 'MEDIUM'
            when l.applied_amount >= 100000 then 'LARGE'
            else 'UNKNOWN'
        end as loan_size_band,

        case
            when l.credit_score < 650 and l.debt_to_income > 0.4 then true
            else false
        end as is_high_risk

    from loans l 
    left join customers c 
        on l.customer_id = c.customer_id    
)

select * from enriched_loans;