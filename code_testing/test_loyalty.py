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
    cursor.execute("SELECT COUNT(*) FROM CUSTOMER_LOYALTY WHERE POINTS >= 0")
    count = cursor.fetchone()[0]
    assert count > 0, "No positive loyalty points found"
    conn.close()
