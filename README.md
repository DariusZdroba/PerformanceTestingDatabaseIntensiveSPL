
# Automated Database Performance Testing for SPL Environments

## Project Structure

```
root/
├── AMOEBA/
│   ├── pairs/
│   │   ├── 1_total_price/
│   │   │   ├── 1A_nested_in.sql
│   │   │   └── 1B_join.sql
│   │   ├── 2_date_filter/
│   │   │   ├── 2A_exists.sql
│   │   │   └── 2B_join.sql
│   │   ├── 3_total_spent/
│   │   │   ├── 3A_scalar_subquery.sql
│   │   │   └── 3B_group_by_join.sql
│   │   └── 4_expensive_products/
│   │       ├── 4A_nested_multilevel.sql
│   │       └── 4B_multi_join_flat.sql
│   └── setup.sql
├── code_testing/
│   ├── config.py
│   ├── schema_checker.py
│   ├── test_base.py
│   ├── test_loyalty.py
│   ├── test_newsletter.py
│   └── test_purchase_summary.py
├── SPL-DB-SYNC/
│   ├── setup.sql
│   ├── flat_benchmark/
│   │   ├── loyalty_query.sql
│   │   ├── newsletter_query.sql
│   │   └── purchase_summary_query.sql
│   └── modular_benchmark/
│       ├── loyalty_query.sql
│       ├── newsletter_query.sql
│       └── purchase_summary_query.sql
├── results_code_testing/
│   ├── results_full.csv
│   ├── results_loyalty.csv
│   └── results_newsletter.csv
├── main.py
├── requirements.txt
└── README.md
```

## Overview

This project contains experiments and benchmarks related to database performance testing within Software Product Line (SPL) environments. It implements and tests approaches from three main research papers:

1. **AMOEBA** - Automated detection of performance bugs using equivalent queries.
2. **SPL-DB-Sync** - Seamless database transformation during feature-driven changes.
3. **Automated Code-Based Test Case Reuse** - Code reuse and testing automation in SPLs.

## Contents

### AMOEBA

- Contains SQL query pairs used for benchmarking performance bug detection.
- Located in `AMOEBA/pairs/` with subfolders organizing query sets by theme.
- `setup.sql` contains database setup scripts relevant to AMOEBA experiments.

### Code Testing

- Python-based test suite located in `code_testing/`.
- Contains configuration (`config.py`), schema verification (`schema_checker.py`), and test cases for different SPL modules:
  - `test_base.py`
  - `test_loyalty.py`
  - `test_newsletter.py`
  - `test_purchase_summary.py`
- Test results saved as CSV files in `results_code_testing/`.

### SPL-DB-Sync

- SQL scripts and benchmark queries organized in `SPL-DB-SYNC/`.
- Separate folders for flat and modular benchmarking.
- Setup scripts to create and populate necessary tables.

## Running the Tests

1. Ensure your MySQL database is set up with the provided SQL scripts.
2. Install required Python packages:
   ```
   pip install -r requirements.txt
   ```
3. Run tests for different feature variants (e.g., loyalty, newsletter, full) using:
   ```
   python main.py
   ```
4. Test results will be saved in `results_code_testing/` as CSV files.
