"""
NZ Banking Data Generator
Generates realistic NZ banking data for all 5 core tables.
Inserts directly into your local Postgres database.

Install dependencies first:
    pip install faker psycopg2-binary

Run:
    python generate_nz_banking_data.py
"""

import random
import psycopg2
from faker import Faker
from datetime import datetime, timedelta
from decimal import Decimal

fake = Faker('en_NZ')
random.seed(42)

# ── Update these to match your local Postgres ──────────────────────────────
DB_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "database": "banking_dev",   # create this DB first: createdb banking_dev
    "user":     "postgres",
    "password": "postgres"
}

# ── Volume knobs ───────────────────────────────────────────────────────────
NUM_CUSTOMERS    = 1_000
NUM_ACCOUNTS     = 1_500   # some customers have multiple accounts
NUM_TRANSACTIONS = 50_000
NUM_LOANS        = 500

# ── NZ-specific reference data ─────────────────────────────────────────────
NZ_REGIONS = [
    "Auckland", "Wellington", "Canterbury", "Waikato", "Bay of Plenty",
    "Otago", "Manawatu-Whanganui", "Hawke's Bay", "Taranaki", "Northland"
]

NZ_CITIES = {
    "Auckland":              ["Auckland CBD", "North Shore", "Manukau", "Waitakere", "Henderson"],
    "Wellington":            ["Wellington CBD", "Lower Hutt", "Upper Hutt", "Porirua"],
    "Canterbury":            ["Christchurch", "Rolleston", "Rangiora"],
    "Waikato":               ["Hamilton", "Cambridge", "Te Awamutu"],
    "Bay of Plenty":         ["Tauranga", "Rotorua", "Whakatane"],
    "Otago":                 ["Dunedin", "Queenstown", "Alexandra"],
    "Manawatu-Whanganui":    ["Palmerston North", "Whanganui"],
    "Hawke's Bay":           ["Napier", "Hastings"],
    "Taranaki":              ["New Plymouth", "Stratford"],
    "Northland":             ["Whangarei", "Kerikeri"]
}

NZ_MERCHANTS = {
    "GROCERIES":    ["Countdown", "Pak'nSave", "New World", "Four Square", "Fresh Choice"],
    "FUEL":         ["Z Energy", "BP", "Mobil", "Gull", "Allied Petroleum"],
    "DINING":       ["McDonald's NZ", "KFC NZ", "Hell Pizza", "Domino's NZ",
                     "Burger King NZ", "Subway NZ", "The Coffee Club", "Mojo Coffee"],
    "UTILITIES":    ["Mercury Energy", "Genesis Energy", "Contact Energy", "Meridian Energy",
                     "Vector Lines", "Watercare Services"],
    "TRANSPORT":    ["AT HOP", "Metlink Wellington", "Uber NZ", "AA Petrol",
                     "Air New Zealand", "Jetstar NZ"],
    "RETAIL":       ["The Warehouse", "Kmart NZ", "Farmers", "Briscoes",
                     "Rebel Sport", "Whitcoulls", "JB Hi-Fi NZ"],
    "HEALTHCARE":   ["Unichem Pharmacy", "Life Pharmacy", "Green Cross Health",
                     "Southern Cross Health"],
    "GOVERNMENT":   ["IRD", "NZTA", "ACC", "Work and Income NZ"],
    "ONLINE":       ["Trade Me", "Amazon AU", "Netflix NZ", "Spotify NZ",
                     "Adobe NZ", "Microsoft NZ", "Google NZ"],
    "ATM":          ["ANZ ATM", "ASB ATM", "BNZ ATM", "Westpac ATM", "Kiwibank ATM"]
}

CHANNELS = ["EFTPOS", "ONLINE", "ATM", "DIRECT_DEBIT", "DIRECT_CREDIT",
            "MOBILE_APP", "BRANCH", "INTERNET_BANKING"]

CHANNEL_WEIGHTS = [35, 25, 10, 12, 8, 6, 2, 2]   # % realistic distribution

ACCOUNT_TYPES = ["CHEQUE", "SAVINGS", "CREDIT", "TERM_DEPOSIT"]
ACCOUNT_TYPE_WEIGHTS = [45, 35, 15, 5]

CUSTOMER_SEGMENTS = ["RETAIL", "SME", "CORPORATE", "PRIVATE_BANKING"]
SEGMENT_WEIGHTS    = [75, 15, 7, 3]

LOAN_TYPES = ["HOME_LOAN", "PERSONAL_LOAN", "AUTO_LOAN", "BUSINESS_LOAN"]
LOAN_WEIGHTS = [50, 25, 15, 10]

# ── NZ bank account number helper (bank-branch-account-suffix) ─────────────
NZ_BANKS = ["01", "02", "03", "06", "11", "12", "15", "30", "31", "38"]

def nz_account_number(bank_code=None):
    bank   = bank_code or random.choice(NZ_BANKS)
    branch = str(random.randint(100, 9999)).zfill(4)
    acct   = str(random.randint(1000000, 9999999))
    suffix = str(random.randint(0, 99)).zfill(2)
    return f"{bank}-{branch}-{acct}-{suffix}"

# ── Random timestamp helper ────────────────────────────────────────────────
def rand_ts(start_days_ago=730, end_days_ago=0):
    start = datetime.now() - timedelta(days=start_days_ago)
    end   = datetime.now() - timedelta(days=end_days_ago)
    return start + (end - start) * random.random()

# ── DDL ────────────────────────────────────────────────────────────────────
DDL = """
CREATE TABLE IF NOT EXISTS customers (
    customer_id        SERIAL PRIMARY KEY,
    first_name         VARCHAR(50)  NOT NULL,
    last_name          VARCHAR(50)  NOT NULL,
    date_of_birth      DATE         NOT NULL,
    email              VARCHAR(100) UNIQUE,
    phone              VARCHAR(20),
    address_street     VARCHAR(200),
    address_city       VARCHAR(100),
    address_region     VARCHAR(50),
    postcode           VARCHAR(10),
    customer_segment   VARCHAR(20),
    kyc_status         VARCHAR(20),
    created_date       TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    last_modified_date TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS accounts (
    account_id         SERIAL PRIMARY KEY,
    customer_id        INT          REFERENCES customers(customer_id),
    account_number     VARCHAR(25)  UNIQUE NOT NULL,
    account_type       VARCHAR(30),
    product_name       VARCHAR(100),
    bsb_number         VARCHAR(15),
    balance            DECIMAL(18,2) DEFAULT 0,
    credit_limit       DECIMAL(18,2),
    currency           CHAR(3)      DEFAULT 'NZD',
    status             VARCHAR(20),
    open_date          DATE         NOT NULL,
    close_date         DATE,
    last_modified_date TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id     SERIAL PRIMARY KEY,
    account_id         INT          REFERENCES accounts(account_id),
    transaction_date   TIMESTAMP    NOT NULL,
    value_date         DATE,
    amount             DECIMAL(18,2) NOT NULL,
    transaction_type   VARCHAR(30),
    channel            VARCHAR(30),
    merchant_name      VARCHAR(200),
    merchant_category  VARCHAR(50),
    merchant_city      VARCHAR(100),
    reference          VARCHAR(200),
    balance_after      DECIMAL(18,2),
    is_fraud_flagged   BOOLEAN      DEFAULT FALSE,
    fraud_score        DECIMAL(5,2),
    status             VARCHAR(20)  DEFAULT 'SETTLED',
    last_modified_date TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS loan_applications (
    application_id     SERIAL PRIMARY KEY,
    customer_id        INT          REFERENCES customers(customer_id),
    loan_type          VARCHAR(30),
    applied_amount     DECIMAL(18,2),
    approved_amount    DECIMAL(18,2),
    interest_rate      DECIMAL(5,2),
    term_months        INT,
    application_date   DATE,
    decision_date      DATE,
    status             VARCHAR(20),
    decline_reason     VARCHAR(200),
    credit_score       INT,
    debt_to_income     DECIMAL(5,2),
    last_modified_date TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pipeline_watermark (
    table_name         VARCHAR(100) PRIMARY KEY,
    last_watermark     TIMESTAMP    NOT NULL,
    last_run_status    VARCHAR(20),
    rows_extracted     INT          DEFAULT 0,
    last_run_date      TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);
"""

WATERMARK_SEED = """
INSERT INTO pipeline_watermark (table_name, last_watermark, last_run_status)
VALUES
  ('transactions',      '2024-01-01 00:00:00', 'SUCCESS'),
  ('customers',         '2024-01-01 00:00:00', 'SUCCESS'),
  ('accounts',          '2024-01-01 00:00:00', 'SUCCESS'),
  ('loan_applications', '2024-01-01 00:00:00', 'SUCCESS')
ON CONFLICT (table_name) DO NOTHING;
"""

# ── Generators ─────────────────────────────────────────────────────────────

def make_customers(n):
    rows = []
    for _ in range(n):
        region = random.choice(NZ_REGIONS)
        city   = random.choice(NZ_CITIES[region])
        dob    = fake.date_of_birth(minimum_age=18, maximum_age=80)
        rows.append((
            fake.first_name(),
            fake.last_name(),
            dob,
            fake.unique.email(),
            fake.phone_number(),
            fake.street_address(),
            city,
            region,
            fake.postcode(),
            random.choices(CUSTOMER_SEGMENTS, SEGMENT_WEIGHTS)[0],
            random.choices(["VERIFIED", "PENDING", "FLAGGED"], [85, 12, 3])[0],
            rand_ts(730, 30),   # created between 2 years ago and last month
            rand_ts(30, 0),     # last modified in last 30 days
        ))
    return rows

def make_accounts(customer_ids):
    product_map = {
        "CHEQUE":       ["Everyday Account", "Transaction Account", "Access Account"],
        "SAVINGS":      ["Online Saver", "Notice Saver", "Bonus Saver"],
        "CREDIT":       ["Visa Platinum", "Visa Classic", "Low Rate Card"],
        "TERM_DEPOSIT": ["90-day TD", "6-month TD", "1-year TD"]
    }
    rows = []
    used_ids = set()
    for cid in customer_ids:
        n_accounts = random.choices([1, 2, 3], [60, 30, 10])[0]
        for _ in range(n_accounts):
            acc_type = random.choices(ACCOUNT_TYPES, ACCOUNT_TYPE_WEIGHTS)[0]
            product  = random.choice(product_map[acc_type])
            balance  = round(random.uniform(-500, 150000), 2)
            limit    = round(random.choice([2000, 5000, 10000, 15000, 20000]), 2) \
                       if acc_type == "CREDIT" else None
            open_dt  = rand_ts(1500, 30).date()
            acc_num  = nz_account_number()
            while acc_num in used_ids:
                acc_num = nz_account_number()
            used_ids.add(acc_num)
            rows.append((
                cid, acc_num, acc_type, product,
                nz_account_number()[:9],   # BSB portion
                balance, limit, "NZD",
                random.choices(["ACTIVE","DORMANT","CLOSED"],
                               [88, 9, 3])[0],
                open_dt, None,
                rand_ts(30, 0),
            ))
    return rows

def make_transactions(account_ids, n):
    rows = []
    for _ in range(n):
        acct_id  = random.choice(account_ids)
        category = random.choice(list(NZ_MERCHANTS.keys()))
        merchant = random.choice(NZ_MERCHANTS[category])
        region   = random.choice(NZ_REGIONS)
        city     = random.choice(NZ_CITIES[region])
        channel  = random.choices(CHANNELS, CHANNEL_WEIGHTS)[0]
        txn_dt   = rand_ts(365, 0)
        val_date = (txn_dt + timedelta(days=random.choice([0, 1, 2]))).date()

        # Realistic NZ transaction amounts per category
        amount_ranges = {
            "GROCERIES": (15, 350), "FUEL": (30, 180), "DINING": (8, 120),
            "UTILITIES": (50, 400), "TRANSPORT": (3, 800), "RETAIL": (10, 500),
            "HEALTHCARE": (15, 250), "GOVERNMENT": (20, 2000),
            "ONLINE": (5, 600), "ATM": (20, 500)
        }
        lo, hi   = amount_ranges.get(category, (5, 500))
        amount   = round(random.uniform(lo, hi), 2)
        is_debit = random.random() < 0.82   # 82% of txns are debits
        txn_type = "DEBIT" if is_debit else "CREDIT"
        if not is_debit:
            amount = round(random.uniform(500, 8000), 2)   # credits tend larger

        # Fraud: 2% fraud rate, higher amounts, weird hours
        fraud_score = round(random.uniform(0.7, 1.0), 2) \
                      if random.random() < 0.02 else round(random.uniform(0, 0.3), 2)
        is_fraud = fraud_score > 0.75

        rows.append((
            acct_id, txn_dt, val_date,
            amount, txn_type, channel,
            merchant, category, city,
            fake.sentence(nb_words=4),
            round(random.uniform(-1000, 50000), 2),
            is_fraud, fraud_score,
            random.choices(["SETTLED","PENDING","REVERSED"],[90,8,2])[0],
            rand_ts(7, 0),
        ))
    return rows

def make_loans(customer_ids, n):
    decline_reasons = [
        "Insufficient income", "High debt-to-income ratio",
        "Adverse credit history", "Employment not verified",
        "LVR exceeds policy limit", None, None, None   # None = approved
    ]
    rows = []
    sampled = random.choices(customer_ids, k=n)
    for cid in sampled:
        loan_type   = random.choices(LOAN_TYPES, LOAN_WEIGHTS)[0]
        app_date    = rand_ts(730, 30).date()
        credit_score= random.randint(300, 1000)
        status      = random.choices(
            ["APPROVED","DECLINED","SUBMITTED","WITHDRAWN"],
            [55, 25, 15, 5]
        )[0]

        amount_map  = {
            "HOME_LOAN": (200000, 1200000),
            "PERSONAL_LOAN": (2000, 50000),
            "AUTO_LOAN": (10000, 80000),
            "BUSINESS_LOAN": (20000, 500000)
        }
        lo, hi      = amount_map[loan_type]
        applied     = round(random.uniform(lo, hi), 2)
        approved    = round(applied * random.uniform(0.7, 1.0), 2) \
                      if status == "APPROVED" else None
        rate        = round(random.uniform(5.5, 14.5), 2)
        term        = random.choice([12, 24, 36, 60, 120, 180, 240, 300])
        dec_reason  = None if status == "APPROVED" \
                      else random.choice([r for r in decline_reasons if r])
        decision_dt = (app_date + timedelta(days=random.randint(1, 10))) \
                      if status != "SUBMITTED" else None

        rows.append((
            cid, loan_type, applied, approved,
            rate, term, app_date, decision_dt,
            status, dec_reason,
            credit_score,
            round(random.uniform(10, 65), 2),
            rand_ts(30, 0),
        ))
    return rows

# ── Main ───────────────────────────────────────────────────────────────────

def main():
    print("Connecting to Postgres...")
    conn = psycopg2.connect(**DB_CONFIG)
    cur  = conn.cursor()

    print("Creating tables...")
    cur.execute(DDL)
    cur.execute(WATERMARK_SEED)
    conn.commit()

    # Customers
    print(f"Inserting {NUM_CUSTOMERS} customers...")
    customers = make_customers(NUM_CUSTOMERS)
    cur.executemany("""
        INSERT INTO customers
          (first_name, last_name, date_of_birth, email, phone,
           address_street, address_city, address_region, postcode,
           customer_segment, kyc_status, created_date, last_modified_date)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, customers)
    conn.commit()

    cur.execute("SELECT customer_id FROM customers")
    customer_ids = [r[0] for r in cur.fetchall()]

    # Accounts
    print(f"Inserting accounts (~{NUM_ACCOUNTS})...")
    accounts = make_accounts(customer_ids)
    cur.executemany("""
        INSERT INTO accounts
          (customer_id, account_number, account_type, product_name,
           bsb_number, balance, credit_limit, currency,
           status, open_date, close_date, last_modified_date)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, accounts)
    conn.commit()

    cur.execute("SELECT account_id FROM accounts")
    account_ids = [r[0] for r in cur.fetchall()]

    # Transactions
    print(f"Inserting {NUM_TRANSACTIONS} transactions...")
    txns = make_transactions(account_ids, NUM_TRANSACTIONS)
    cur.executemany("""
        INSERT INTO transactions
          (account_id, transaction_date, value_date, amount,
           transaction_type, channel, merchant_name, merchant_category,
           merchant_city, reference, balance_after,
           is_fraud_flagged, fraud_score, status, last_modified_date)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, txns)
    conn.commit()

    # Loans
    print(f"Inserting {NUM_LOANS} loan applications...")
    loans = make_loans(customer_ids, NUM_LOANS)
    cur.executemany("""
        INSERT INTO loan_applications
          (customer_id, loan_type, applied_amount, approved_amount,
           interest_rate, term_months, application_date, decision_date,
           status, decline_reason, credit_score, debt_to_income, last_modified_date)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, loans)
    conn.commit()

    # Summary
    print("\nDone! Row counts:")
    for tbl in ["customers","accounts","transactions","loan_applications","pipeline_watermark"]:
        cur.execute(f"SELECT COUNT(*) FROM {tbl}")
        print(f"  {tbl:<22} {cur.fetchone()[0]:>8,} rows")

    cur.close()
    conn.close()
    print("\nPostgres is ready. Next step: connect ADF to this database.")

if __name__ == "__main__":
    main()