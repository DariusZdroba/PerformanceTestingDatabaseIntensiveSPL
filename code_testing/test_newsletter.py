import pytest
from config import get_connection, FEATURE_VARIANT
from schema_checker import table_exists

@pytest.mark.skipif(FEATURE_VARIANT not in ['newsletter', 'full'], reason="Newsletter feature disabled")
def test_newsletter_table_exists():
    assert table_exists("CUSTOMER_NEWSLETTER"), "CUSTOMER_NEWSLETTER table is missing"

@pytest.mark.skipif(FEATURE_VARIANT not in ['newsletter', 'full'], reason="Newsletter feature disabled")
def test_email_format_valid():
    if not table_exists("CUSTOMER_NEWSLETTER"):
        pytest.skip("CUSTOMER_NEWSLETTER table not available")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(r"""
        SELECT COUNT(*) FROM CUSTOMER_NEWSLETTER
        WHERE EMAIL NOT REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    """)
    invalid_count = cursor.fetchone()[0]
    conn.close()
    assert invalid_count == 0, f"{invalid_count} emails have invalid format"
