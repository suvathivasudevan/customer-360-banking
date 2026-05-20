# Banking Report Analysis - dbt Project

A production-ready dbt project that transforms raw banking data into clean, analysis-ready tables for reporting and analytics. This project implements a medallion architecture (staging → intermediate → mart layers) using Databricks as the data warehouse.

## Overview

This dbt project processes banking data from multiple source tables (customers, accounts, transactions, loan applications) and produces clean, well-structured dimensional and fact tables ready for analytics and reporting.

**Technology Stack:**
- **Orchestration:** dbt (data build tool)
- **Warehouse:** Databricks SQL
- **Language:** SQL + YAML
- **Version:** 1.0.0

## Architecture

### Data Flow (Medallion Architecture)

```
RAW LAYER (Banking_raw schema)
├── customers
├── accounts
├── transactions
├── loan_applications
└── pipeline_watermark
         ↓
STAGING LAYER (Staging schema - Views)
├── stg_customers
├── stg_accounts
├── stg_loans
└── stg_transactions
         ↓
INTERMEDIATE LAYER (Intermediate schema - Views)
├── int_accounts_enriched
├── int_loans_enriched
└── int_transactions_enriched
         ↓
MART LAYER (Mart schema - Tables)
├── dim_customers (Dimension)
└── fct_transactions (Fact)
```

### Table Descriptions

**Staging Models (Data Cleaning & Normalization):**
- `stg_customers` - Cleaned customer records with standardized fields
- `stg_accounts` - Cleaned account data with proper typing
- `stg_loans` - Loan application records with standardized naming
- `stg_transactions` - Transaction records with normalized amounts and dates

**Intermediate Models (Business Logic):**
- `int_accounts_enriched` - Accounts with customer and transaction aggregations
- `int_loans_enriched` - Loans with customer and approval metrics
- `int_transactions_enriched` - Transactions with derived metrics and window functions

**Mart Models (Analytics Ready):**
- `dim_customers` - Slowly Changing Dimension (SCD) of customers with derived attributes
- `fct_transactions` - Fact table for transaction analysis with denormalized dimensions

## Project Structure

```
dbt_fin_report_analysis/
├── models/
│   ├── raw/                          # Source definitions
│   │   ├── sources.yml              # Data source configurations
│   │   ├── my_first_dbt_model.sql   # Example template
│   │   └── my_second_dbt_model.sql  # Example template
│   ├── staging/                     # Data cleaning & preparation
│   │   ├── stg_customers.sql
│   │   ├── stg_accounts.sql
│   │   ├── stg_loans.sql
│   │   └── stg_transactions.sql
│   ├── intermediate/                # Business logic & transformations
│   │   ├── int_accounts_enriched.sql
│   │   ├── int_loans_enriched.sql
│   │   └── int_transactions_enriched.sql
│   └── mart/                        # Final analytics tables
│       ├── dim_customers.sql
│       └── fct_transactions.sql
├── seeds/                           # Static data files
│   └── nz_cities.csv               # Reference data for NZ locations
├── tests/                           # dbt data quality tests
├── macros/                          # Custom dbt macros
├── analyses/                        # Ad-hoc analysis queries
├── dbt_project.yml                  # Project configuration
├── profiles.yml                     # Databricks connection config
└── README.md                        # This file
```

## Prerequisites

- **dbt** >= 1.0.0
  ```bash
  pip install dbt-databricks
  ```
- **Python** >= 3.9
- **Databricks Account** with SQL Warehouse access
- **Databricks Personal Access Token** for authentication

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/banking-report-analysis.git
cd dbt_fin_report_analysis
```

### 2. Install dbt

```bash
pip install dbt-databricks
```

### 3. Configure Databricks Connection

Update `profiles.yml` with your Databricks credentials:

```yaml
dbt_fin_report_analysis:
  outputs:
    dev:
      type: databricks
      catalog: dbt_fin_report_analysis
      host: <your-databricks-workspace-url>
      http_path: /sql/1.0/warehouses/<warehouse-id>
      token: <your-personal-access-token>
      schema: default
      threads: 4
  target: dev
```

**⚠️ Security Note:** Never commit `profiles.yml` to version control. Add it to `.gitignore` and use environment variables or secret management tools instead.

### 4. Install dbt Packages (if any)

```bash
dbt deps
```

## Running the Project

### Parse & Validate the Project

```bash
dbt parse
```

### Build All Models

```bash
dbt run
```

### Build Specific Models

```bash
# Run only staging models
dbt run --select path:models/staging

# Run only a specific model
dbt run --select stg_customers

# Run with dependencies
dbt run --select +dim_customers
```

### Run Data Quality Tests

```bash
dbt test
```

### Generate Documentation

```bash
dbt docs generate
dbt docs serve  # Opens interactive documentation at localhost:8000
```

### Build & Test (Combined)

```bash
dbt build
```

### Run with Debugging

```bash
dbt run --debug
```

## Model Materialization

| Layer | Type | Reason |
|-------|------|--------|
| **Staging** | View | Lightweight transformations, no data persistence needed |
| **Intermediate** | View | Complex logic, referenced by multiple marts |
| **Mart** | Table | Final analytics layer, frequently queried |

## Key Features

✅ **Medallion Architecture** - Clean separation of concerns (raw → staging → mart)  
✅ **Schema Organization** - Models organized by layer for clarity  
✅ **Source Definitions** - Centralized source configurations in `sources.yml`  
✅ **Seed Data** - Static reference data (NZ cities) for joins  
✅ **Scalable Design** - Easy to add new models and data sources  
✅ **Documentation** - Auto-generated dbt docs for transparency  

## Data Sources

All raw data comes from the `banking_raw` catalog in Databricks:

| Source | Table | Description |
|--------|-------|-------------|
| PostgreSQL | customers | Customer master data |
| PostgreSQL | accounts | Customer account records |
| PostgreSQL | transactions | All banking transactions |
| PostgreSQL | loan_applications | Loan application records |
| Watermark | pipeline_watermark | ELT pipeline incremental load tracking |

## Development Workflow

### Adding a New Model

1. Create a `.sql` file in the appropriate layer (e.g., `models/staging/stg_new_table.sql`)
2. Reference source tables using `{{ source('banking_raw', 'table_name') }}`
3. Use dbt Jinja2 features for dynamic SQL
4. Test locally: `dbt run --select stg_new_table`
5. Add tests to `schema.yml` or test files
6. Update documentation
7. Commit and push

### Example Model Template

```sql
-- models/staging/stg_example.sql
{{ config(
    materialized='view',
    schema='staging'
) }}

WITH source_data AS (
    SELECT
        id,
        name,
        created_at,
        updated_at
    FROM {{ source('banking_raw', 'example_table') }}
    WHERE deleted_at IS NULL
),

cleaned_data AS (
    SELECT
        id,
        TRIM(name) AS name,
        CAST(created_at AS TIMESTAMP) AS created_at,
        CAST(updated_at AS TIMESTAMP) AS updated_at
    FROM source_data
)

SELECT * FROM cleaned_data
```

## Testing

This project includes data quality tests to ensure data integrity:

```bash
# Run all tests
dbt test

# Run tests for specific model
dbt test --select dim_customers

# Test sources
dbt test --select source:banking_raw
```

Common test types:
- **Uniqueness** - Ensure ID fields have no duplicates
- **Not Null** - Validate critical fields are populated
- **Relationships** - Verify foreign key constraints
- **Accepted Values** - Check enumerations

## Performance Optimization

### Tips for Large Datasets

1. **Incremental Models** - For fact tables, use incremental materialization for faster builds
2. **Partitioning** - Partition large tables by date for faster queries
3. **Clustering** - Cluster by frequently filtered columns
4. **Indexing** - Create indexes on dimension keys
5. **Materialization** - Use tables for frequently queried models

Example incremental model:

```sql
{{ config(
    materialized='incremental',
    unique_key='transaction_id'
) }}

SELECT ...
{% if execute %}
    WHERE created_at > (SELECT MAX(created_at) FROM {{ this }})
{% endif %}
```

## Troubleshooting

### Connection Issues

```bash
# Test connection to Databricks
dbt debug
```

### Model Failures

```bash
# Check logs
cat logs/dbt.log

# Run with verbose output
dbt run --debug

# Validate SQL syntax
dbt parse
```

### Performance Issues

```bash
# Check model execution time
dbt run --profiles-dir . --debug

# Analyze query execution plans
-- Run directly in Databricks SQL editor
EXPLAIN SELECT ... FROM <model>
```

## Contributing

We welcome contributions! Please follow these guidelines:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/new-model`)
3. **Test** your changes locally (`dbt run && dbt test`)
4. **Document** your models with descriptions
5. **Commit** with clear messages
6. **Push** to your fork
7. **Create** a Pull Request

## Best Practices

- ✅ Use descriptive, snake_case naming for models
- ✅ Add `description` fields in schema YAML
- ✅ Write SQL with proper formatting and comments
- ✅ Test all models and sources
- ✅ Keep models focused on a single responsibility
- ✅ Use CTEs (WITH clauses) for readability
- ✅ Document assumptions and business logic
- ✅ Never hardcode values - use variables or ref()
- ✅ Use `{{ source() }}` for raw tables, `{{ ref() }}` for models
- ✅ Review dbt documentation before running on production

## Documentation

Auto-generated documentation is available after running:

```bash
dbt docs generate
dbt docs serve
```

This creates an interactive DAG (Directed Acyclic Graph) showing data flow and dependencies.

## Project Metadata

| Property | Value |
|----------|-------|
| **Name** | dbt_fin_report_analysis |
| **Version** | 1.0.0 |
| **Adapter** | Databricks |
| **Warehouse** | dbt_fin_report_analysis |
| **Profile** | dbt_fin_report_analysis |

## Resources & Learning

- 📚 [dbt Documentation](https://docs.getdbt.com/)
- 🎥 [dbt Learn](https://learn.getdbt.com/)
- 💬 [dbt Community Slack](https://community.getdbt.com/)
- 📖 [SQL Style Guide](https://sqlstyle.guide/)
- 🔗 [Databricks Documentation](https://docs.databricks.com/)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact & Support

For questions or issues:
- **GitHub Issues:** [Create an issue](https://github.com/yourusername/banking-report-analysis/issues)
- **Email:** your.email@example.com
- **Slack:** [Link to workspace channel]

## Changelog

### v1.0.0 (2026-05-20)
- Initial release
- Implemented medallion architecture
- Added staging, intermediate, and mart layers
- Configured Databricks SQL integration
- Created dimension and fact tables for banking analysis

---

**Last Updated:** May 20, 2026  
**dbt Version:** 1.0.0+  
**Databricks Runtime:** Compatible with all current versions