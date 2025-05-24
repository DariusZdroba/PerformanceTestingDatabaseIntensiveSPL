import pytest
from config import get_connection

def test_customer_table_exists():
    """Check that the CUSTOMER table exists and has rows"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM CUSTOMER")
    count = cursor.fetchone()[0]
    conn.close()
    assert count > 0, "CUSTOMER table is empty or missing"

def test_order_table_exists():
    """Check that the ORDERS table exists and has rows"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM ORDERS")
    count = cursor.fetchone()[0]
    conn.close()
    assert count > 0, "ORDERS table is empty or missing"

def test_join_customer_orders():
    """Validate JOIN logic between CUSTOMER and ORDERS"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT C.C_CUSTKEY, COUNT(O.O_ORDERKEY)
        FROM CUSTOMER C
        JOIN ORDERS O ON C.C_CUSTKEY = O.O_CUSTKEY
        GROUP BY C.C_CUSTKEY
        LIMIT 5
    """)
    results = cursor.fetchall()
    conn.close()
    assert len(results) > 0, "JOIN failed or returned no results"

def test_total_order_price_threshold():
    """Check that some orders exceed a large price (e.g., 100000)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM ORDERS WHERE O_TOTALPRICE > 100000")
    count = cursor.fetchone()[0]
    conn.close()
    assert count > 0, "No large total price orders found"
