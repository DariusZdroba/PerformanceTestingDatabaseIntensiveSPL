import pytest
from config import get_connection, FEATURE_VARIANT
from schema_checker import table_exists

@pytest.mark.skipif(FEATURE_VARIANT not in ['purchase', 'full'], reason="Purchase feature disabled")
def test_purchase_summary_table_exists():
    assert table_exists("CUSTOMER_PURCHASE_SUMMARY"), "CUSTOMER_PURCHASE_SUMMARY table is missing"

@pytest.mark.skipif(FEATURE_VARIANT not in ['purchase', 'full'], reason="Purchase feature disabled")
def test_total_spent_positive():
    if not table_exists("CUSTOMER_PURCHASE_SUMMARY"):
        pytest.skip("CUSTOMER_PURCHASE_SUMMARY not found")

    conn = get_connection()
    cursor = conn.cursor()
    # Use LIMIT to make test faster on large tables
    cursor.execute("SELECT COUNT(*) FROM (SELECT TOTAL_SPENT FROM CUSTOMER_PURCHASE_SUMMARY WHERE TOTAL_SPENT > 0 LIMIT 100) AS sample")
    count = cursor.fetchone()[0]
    conn.close()
    assert count > 0, "No customers with TOTAL_SPENT > 0 found (checked first 100)"

@pytest.mark.skipif(FEATURE_VARIANT not in ['purchase', 'full'], reason="Purchase feature disabled")
def test_foreign_key_matches_customer():
    if not table_exists("CUSTOMER_PURCHASE_SUMMARY"):
        pytest.skip("CUSTOMER_PURCHASE_SUMMARY not found")

    conn = get_connection()
    cursor = conn.cursor()
    # Use LIMIT to make test faster on large tables
    cursor.execute("""
        SELECT COUNT(*) FROM (
            SELECT cps.C_CUSTKEY FROM CUSTOMER_PURCHASE_SUMMARY cps
            LEFT JOIN CUSTOMER c ON cps.C_CUSTKEY = c.C_CUSTKEY
            WHERE c.C_CUSTKEY IS NULL
            LIMIT 100
        ) AS unmatched
    """)
    unmatched = cursor.fetchone()[0]
    conn.close()
    assert unmatched == 0, f"{unmatched} summary records do not match any customer (checked first 100)"
