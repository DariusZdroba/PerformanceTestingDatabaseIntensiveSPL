import mysql.connector
import time
import os
from code_testing.config import DB_CONFIG

def get_db_connection():
    """Establishes a connection to the database."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

def execute_query(connection, query):
    """Executes a single SQL query and returns the execution time."""
    cursor = connection.cursor()
    start_time = time.time()
    cursor.execute(query)
    end_time = time.time()
    cursor.fetchall()  # Fetch results to ensure query completion
    cursor.close()
    return end_time - start_time

def run_amoeba_benchmark():
    """Runs the full AMOEBA benchmark."""
    conn = get_db_connection()
    if not conn:
        return

    pairs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'AMOEBA', 'pairs')
    results = {}

    for pair_folder in os.listdir(pairs_dir):
        pair_path = os.path.join(pairs_dir, pair_folder)
        if os.path.isdir(pair_path):
            queries = {}
            for sql_file in os.listdir(pair_path):
                if sql_file.endswith('.sql'):
                    with open(os.path.join(pair_path, sql_file), 'r') as f:
                        queries[sql_file] = f.read()
            
            if len(queries) == 2:
                q1_name, q1_sql = list(queries.items())[0]
                q2_name, q2_sql = list(queries.items())[1]

                time1 = execute_query(conn, q1_sql)
                time2 = execute_query(conn, q2_sql)

                results[pair_folder] = {
                    q1_name: time1,
                    q2_name: time2,
                    'slower': q1_name if time1 > time2 else q2_name
                }
    
    conn.close()
    return results

def run_spl_db_sync_benchmark(benchmark_type):
    """Runs the SPL-DB-Sync benchmark."""
    conn = get_db_connection()
    if not conn:
        return

    benchmark_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'SPL-DB-Sync', f'{benchmark_type}_benchmark')
    results = {}

    for sql_file in os.listdir(benchmark_dir):
        if sql_file.endswith('.sql'):
            with open(os.path.join(benchmark_dir, sql_file), 'r') as f:
                query_sql = f.read()
                execution_time = execute_query(conn, query_sql)
                results[sql_file] = execution_time
    
    conn.close()
    return results 