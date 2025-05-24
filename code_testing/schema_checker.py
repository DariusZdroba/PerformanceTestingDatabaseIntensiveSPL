from config import get_connection

def table_exists(table_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_schema = DATABASE()
        AND table_name = %s
    """, (table_name,))
    exists = cursor.fetchone()[0] > 0
    conn.close()
    return exists
