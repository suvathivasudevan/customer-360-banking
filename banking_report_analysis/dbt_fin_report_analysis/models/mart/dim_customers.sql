with customers as(
    select * from {{ ref('stg_customers') }}
),

account_summary as(
    select 
        customer_id,
        count(distinct account_id) as total_accounts,
        sum(case when is_active is true then 1 else 0 end) as active_accounts_count,
        sum(case when account_type ='SAVINGS' then 1 else 0 end) as savings_accounts_count,
        sum(case when account_type ='CREDIT' then 1 else 0 end) as credit_accounts_count,
        sum(case when account_type ='MORTGAGE' then 1 else 0 end) as loan_accounts_count,
        sum(balance) as total_balance,
        min(open_date) as first_account_open_date,
        max(case when account_type = 'CREDIT' then credit_utilisation_pct else 0 end) as max_credit_utilisation_pct,
        
         -- boolean flags — if ANY account matches, return true
        max(case when is_active = true       then 1 else 0 end) = 1  as has_active_account,
        max(case when account_type = 'MORTGAGE' then 1 else 0 end) = 1 as has_mortgage,
        max(case when account_type = 'CREDIT'   then 1 else 0 end) = 1 as has_credit_account

    from {{ ref('int_accounts_enriched') }}
    group by customer_id
),

loan_summary as(
    select 
        customer_id,
        count(distinct application_id) as total_loan_applications,
        sum(case when is_approved = true then 1 else 0 end) as total_approved_loans,
        sum(case when is_declined = true then 1 else 0 end) as total_declined_loans,
        sum(case when is_pending = true then 1 else 0 end) as total_pending_loans,
        sum(approved_amount) as total_approved_amount,
        max(case when is_high_risk = true then 1 else 0 end) = 1 as has_high_risk_loan,
        -- boolean flags — if ANY loan matches, return true 
        max(case when is_approved = true then 1 else 0 end) = 1 as has_approved_loan,
        max(case when is_declined = true then 1 else 0 end) = 1 as has_declined_loan,
        max(case when is_pending = true then 1 else 0 end) = 1 as has_pending_loan,
        max(credit_score_band) as latest_credit_score_band,
        round(avg(debt_to_income), 2)                            as avg_debt_to_income

    from {{ ref('int_loans_enriched') }}
    group by customer_id
),
transaction_summary as(
    select 
        customer_id,
        count(distinct transaction_id) as total_transactions,
        sum(case when is_debit = true then abs_amount else 0 end) as total_debits,
        sum(case when is_credit = true then abs_amount else 0 end) as total_credits,
    
        sum(case when is_fraud = true then 1 else 0 end) as fraud_count,
        sum(case when is_gambling = true then 1 else 0 end) as gambling_count,
        sum(case when is_crypto = true then 1 else 0 end) as crypto_count,
        sum(case when is_overseas = true then 1 else 0 end) as overseas_count,

        max(case when is_fraud = true then 1 else 0 end) = 1 as has_fraudulent_transaction,
        max(case when is_gambling = true then 1 else 0 end) = 1 as has_gambling_transaction,
        round(avg(abs_amount), 2)                                as avg_transaction_value

    from {{ ref('int_transactions_enriched') }}
    group by customer_id
),

customer_360 as(
    select 
    c.customer_id,
    c.full_name,
    c.date_of_birth,
    c.email,
    c.phone,
    c.address_street,
    c.address_city, 
    c.address_region,
    c.postcode,
    c.customer_segment,
    c.kyc_status,
    c.age_years,
    c.is_kyc_verified,

    -- ── account summary ───────────────────
        coalesce(a.total_accounts, 0)                            as total_accounts,
        coalesce(a.active_accounts_count, 0)                      as active_account_count,
        coalesce(a.savings_accounts_count, 0)                     as savings_account_count,
        coalesce(a.credit_accounts_count, 0)                      as credit_account_count,
        coalesce(a.loan_accounts_count, 0)                    as mortgage_account_count,
        coalesce(a.total_balance, 0)                             as total_balance,
        coalesce(a.max_credit_utilisation_pct, 0)                as max_credit_utilisation_pct,
        a.first_account_open_date,
        coalesce(a.has_active_account, false)                    as has_active_account,
        coalesce(a.has_mortgage, false)                          as has_mortgage,
        coalesce(a.has_credit_account, false)                    as has_credit_account,

        -- ── loan summary ──────────────────────
        coalesce(l.total_loan_applications, 0)                   as total_loan_applications,
        coalesce(l.total_approved_loans, 0)                      as total_approved_loans,
        coalesce(l.total_declined_loans, 0)                      as total_declined_loans,
        coalesce(l.total_approved_amount, 0)                     as total_approved_amount,
        coalesce(l.has_declined_loan, false)                     as has_declined_loan,
        coalesce(l.avg_debt_to_income, 0)                        as avg_debt_to_income,
        l.latest_credit_score_band

    from customers c
    left join account_summary a on c.customer_id = a.customer_id
    left join loan_summary l on c.customer_id = l.customer_id
    left join transaction_summary t on c.customer_id = t.customer_id

)

select * from customer_360