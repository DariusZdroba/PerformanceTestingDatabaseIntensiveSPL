# 🔬 Database Performance Research Validation Tool

## 📋 Overview

This project implements a **research validation tool** for database performance testing, specifically designed to reproduce and validate findings from two key research papers:

1. **🧬 AMOEBA**: *Automatic Detection of Performance Bugs in Database Systems using Equivalent Queries*
2. **🏗️ SPL-DB-Sync**: *Seamless Database Transformation during Feature-Driven Changes*
3. **🏗️ Act-SPL**: *Automated code-based test case reuse for software product line testing*

The tool provides automated benchmarking to validate that:
- **JOINs are faster than subqueries** (AMOEBA hypothesis)
- **Modular queries are faster than flat queries** (SPL-DB-Sync hypothesis)
- **Code-based test reuse improves efficiency of SPL validation** (ActSPL hypothesis)

## 🚀 Quick Start

### Prerequisites
- MySQL database with TPC-H sample data
- Python 3.7+
- Required Python packages (see `requirements.txt`)

### Installation
```bash
pip install -r requirements.txt
```

### Database Setup
Your MySQL database should have these tables:
- **Sample tables**: `customer_sample`, `orders_sample`, `lineitem_sample`, `part_sample` (10% data)
- **Full tables**: `customer`, `orders`, `lineitem`, `part`, `nation`, `region`, `supplier`, `partsupp`

### Running Experiments
```bash
# Run all experiments on sample data
python simple_benchmark.py --experiment all --dataset sample

# Run specific experiment on full data
python simple_benchmark.py --experiment amoeba --dataset full
python simple_benchmark.py --experiment spl-db-sync --dataset full

# Quick validation (recommended)
python simple_benchmark.py --experiment all --dataset sample
```

## 📁 Project Structure

```
📦 AutomatedCodeBasePerformanceTesting/
├── 🧬 AMOEBA/                          # Subquery vs JOIN experiments
│   ├── pairs/
│   │   ├── 1_total_price/              # Customer order value comparison
│   │   │   ├── 1A_nested_in.sql       # Inefficient: Correlated subquery
│   │   │   └── 1B_join.sql            # Efficient: INNER JOIN
│   │   ├── 2_date_filter/              # Date-based customer filtering
│   │   │   ├── 2A_exists.sql          # Inefficient: EXISTS subquery
│   │   │   └── 2B_join.sql            # Efficient: INNER JOIN
│   │   └── 3_total_spent/              # Customer spending aggregation
│   │       ├── 3A_scalar_subquery.sql # Inefficient: Correlated scalar subqueries
│   │       └── 3B_group_by_join.sql   # Efficient: JOIN with GROUP BY
│   └── setup.sql                       # AMOEBA experiment setup
├── 🏗️ SPL-DB-Sync/                     # Modular vs Flat query experiments
│   ├── modular_benchmark/              # Efficient, well-structured queries
│   │   ├── loyalty_query.sql          # Clean JOIN with GROUP BY
│   │   ├── newsletter_query.sql       # Efficient customer filtering
│   │   └── purchase_sumary_query.sql  # Optimized aggregation
│   ├── flat_benchmark/                 # Inefficient, poorly structured queries
│   │   ├── loyalty_query.sql          # Multiple correlated subqueries
│   │   ├── newsletter_query.sql       # Complex nested EXISTS
│   │   └── purchase_sumary_query.sql  # Repeated aggregation calculations
│   └── setup.sql                       # SPL-DB-Sync experiment setup
├── 🛠️ simple_benchmark.py              # Main benchmarking tool
├── 🔍 check_tables.py                  # Database table verification
├── 📋 requirements.txt                 # Python dependencies
└── 📖 README.md                        # This file
```

## 🔬 Research Experiments

### 🧬 AMOEBA Experiment: Subquery vs JOIN Performance

**Research Goal**: Validate that JOINs are generally faster than equivalent subqueries.

**Query Pairs**:
1. **Total Price**: Find customers with high-value orders (>$100K)
   - `1A_nested_in.sql`: Uses correlated `IN` subquery
   - `1B_join.sql`: Uses efficient `INNER JOIN`

2. **Date Filter**: Find customers with recent high-value orders
   - `2A_exists.sql`: Uses `EXISTS` subquery with date filtering
   - `2B_join.sql`: Uses `INNER JOIN` with same filters

3. **Total Spent**: Calculate total customer spending with filtering
   - `3A_scalar_subquery.sql`: Uses correlated scalar subqueries
   - `3B_group_by_join.sql`: Uses `GROUP BY` with `HAVING`

### 🏗️ SPL-DB-Sync Experiment: Modular vs Flat Query Performance

**Research Goal**: Validate that well-structured (modular) queries are faster than poorly-structured (flat) queries.

**Query Pairs**:
1. **Loyalty Query**: Customer loyalty tier classification
   - **Modular**: Clean `JOIN` with `GROUP BY` and `CASE`
   - **Flat**: Multiple correlated subqueries repeating same calculation

2. **Newsletter Query**: High-value customer identification
   - **Modular**: Efficient `JOIN` with proper filtering
   - **Flat**: Complex nested `EXISTS` with redundant checks

3. **Purchase Summary**: Customer spending analytics
   - **Modular**: Single `JOIN` with `GROUP BY` aggregation
   - **Flat**: Multiple separate subqueries for same aggregations

## 📊 Understanding Results

### Success Criteria
- **AMOEBA**: JOINs should be faster than subqueries
- **SPL-DB-Sync**: Modular queries should be faster than flat queries

### Sample Output
```
🔬 AMOEBA (Subquery vs JOIN):
   Total pairs tested: 3
   JOINs faster: 3
   Success rate: 100.0% ✅

🏗️ SPL-DB-SYNC (Modular vs Flat):
   Total pairs tested: 3
   Modular faster: 2
   Success rate: 66.7% ⚠️
```

### Performance Factors
- **Dataset Size**: Larger datasets show more pronounced differences
- **Query Complexity**: More complex queries benefit more from optimization
- **Database Configuration**: MySQL optimizer settings affect results
- **Hardware**: CPU and memory impact query execution times

## 🎯 Research Validation

This tool helps validate key database performance principles:

1. **Query Structure Matters**: Well-structured queries consistently outperform poorly-structured ones
2. **JOIN Efficiency**: Modern database optimizers handle JOINs better than correlated subqueries
3. **Aggregation Optimization**: Single `GROUP BY` operations are more efficient than multiple subqueries
4. **Real-world Applicability**: The query patterns represent common developer mistakes vs. best practices

## 🛠️ Technical Details

### Database Requirements
- **Engine**: MySQL 5.7+ or 8.0+
- **Data**: TPC-H benchmark dataset (sample or full)
- **Tables**: Customer, Orders, LineItem, Part, Nation, Region, Supplier, PartSupp

### Query Design Principles
- **Logical Equivalence**: All query pairs return identical results
- **Realistic Patterns**: Inefficient queries represent common developer mistakes
- **Measurable Differences**: Performance gaps are significant enough to measure
- **Educational Value**: Demonstrates best practices vs. anti-patterns

### Performance Measurement
- **Timeout**: 60 seconds per query
- **Metrics**: Execution time in seconds
- **Validation**: Row count verification for logical equivalence
- **Reporting**: Success rates and performance improvements

## 📚 Research Papers

1. **AMOEBA**: Jiang, A., et al. "Automatic Detection of Performance Bugs in Database Systems using Equivalent Queries." *ICSE 2021*.

2. **SPL-DB-Sync**: Nadi, S., et al. "Seamless Database Transformation during Feature-Driven Changes." *ICSE 2019*.

3. **ActSPL**: Pilsu N., Seonah L., Uicheon L., "Automated code-based test case reuse for software product line testing  *ICSE 2023*
"

## 🤝 Contributing

This tool is designed for research validation and educational purposes. Feel free to:
- Add new query pairs following the established patterns
- Test with different database systems
- Extend the benchmarking framework
- Improve the reporting and analysis features

## 📄 License

This project is for academic and research use. Please cite the original research papers when using this tool in your work.
