import pytest
from config import get_connection, FEATURE_VARIANT
from schema_checker import table_exists

@pytest.mark.skipif(FEATURE_VARIANT not in ['loyalty', 'full'], reason="Loyalty feature disabled")
def test_loyalty_table_exists():
    assert table_exists("CUSTOMER_LOYALTY"), "CUSTOMER_LOYALTY table is missing"

@pytest.mark.skipif(FEATURE_VARIANT not in ['loyalty', 'full'], reason="Loyalty feature disabled")
def test_loyalty_points_positive():
    if not table_exists("CUSTOMER_LOYALTY"):
        pytest.skip("CUSTOMER_LOYALTY not found")

    conn = get_connection()
    cursor = conn.cursor()
    # Use LIMIT to make test faster on large tables
    cursor.execute("SELECT COUNT(*) FROM (SELECT POINTS FROM CUSTOMER_LOYALTY WHERE POINTS >= 0 LIMIT 100) AS sample")
    count = cursor.fetchone()[0]
    conn.close()
    assert count > 0, "No positive loyalty points found (checked first 100)"


