with source as(

    select DISTINCT * from {{ source('banking_raw', 'loan_applications') }}
),

deduplicated as (
    select *,
        row_number() over (
            partition by application_id
            order by last_modified_date desc
        ) as row_num
    from source
),

cleaned  as(
    select
        customer_id,
        application_id,
        applied_amount,
        upper(loan_type) as loan_type,
        upper(status) as status,
        coalesce(decline_reason, 'NOT APPLICABLE') as  decline_reason,
        coalesce(approved_amount, 0) as approved_amount,
        coalesce(interest_rate, 0) as interest_rate,
        coalesce(term_months, 0) as term_months,
        coalesce(credit_score, 0) as credit_score,
        coalesce(debt_to_income, 0) as debt_to_income,
        decision_date,

        case
        when status = 'APPROVED' then true
        else false
        end as is_approved,
        case
        when status = 'DECLINED' then true
        else false
        end as is_declined,
        case
        when status = 'PENDING' then true
        else false
        end as is_pending,

        approved_amount/applied_amount*100 as loan_amount_approved_pct,

        datediff(decision_date, application_date) as decision_time_days,
        
        case
        when credit_score >= 750 then 'EXCELLENT'
        when credit_score >= 700 then 'GOOD'
        when credit_score >= 650 then 'FAIR'
        else 'POOR'
        end as credit_score_band

        from deduplicated where row_num = 1

)

select * from cleaned