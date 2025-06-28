import mysql.connector
from code_testing.config import DB_CONFIG

try:
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Check for sample tables
    cursor.execute("SHOW TABLES LIKE '%_SAMPLE'")
    sample_tables = cursor.fetchall()
    
    print("Sample tables found:")
    for table in sample_tables:
        print(f"  - '{table[0]}'")
    
    if not sample_tables:
        print("No sample tables found!")
    
    # Check for regular tables
    cursor.execute("SHOW TABLES LIKE 'CUSTOMER'")
    regular_tables = cursor.fetchall()
    
    print("\nRegular tables found:")
    for table in regular_tables:
        print(f"  - '{table[0]}'")
    
    # Check all tables to see the exact case
    cursor.execute("SHOW TABLES")
    all_tables = cursor.fetchall()
    
    print("\nAll tables in database:")
    for table in all_tables:
        print(f"  - '{table[0]}'")
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}") 