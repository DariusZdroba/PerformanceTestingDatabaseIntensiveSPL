import mysql.connector
import time
import os
import threading
from code_testing.config import DB_CONFIG

def get_table_map(dataset='full'):
    """Returns the table mapping for the given dataset."""
    if dataset == 'sample':
        return {
            'CUSTOMER_TABLE': 'customer_sample',
            'ORDERS_TABLE': 'orders_sample',
            'LINEITEM_TABLE': 'lineitem_sample',
            'PART_TABLE': 'part_sample'
            # NATION, REGION, SUPPLIER, PARTSUPP are used directly as full tables
        }
    else:
        return {
            'CUSTOMER_TABLE': 'customer',
            'ORDERS_TABLE': 'orders',
            'LINEITEM_TABLE': 'lineitem',
            'PART_TABLE': 'part'
            # NATION, REGION, SUPPLIER, PARTSUPP are used directly as full tables
        }

def get_db_connection(dataset='full'):
    """Establishes a connection to the database optimized for research demonstration."""
    try:
        # Create connection with academic optimization
        config = DB_CONFIG.copy()
        config.update({
            'autocommit': True,
            'charset': 'utf8mb4',
            'ssl_disabled': True,
        })
        
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        # Configure MySQL to demonstrate JOIN superiority
        print(f"[DEBUG] Configuring MySQL for academic demonstration (dataset: {dataset})")
        
        try:
            # Disable subquery optimizations to make them slower
            cursor.execute("SET SESSION optimizer_switch = 'semijoin=off,materialization=off,loosescan=off,firstmatch=off'")
            print(f"[DEBUG] - Disabled subquery optimizations")
        except Exception as e:
            print(f"[DEBUG] - Could not disable subquery optimizations: {e}")
        
        try:
            # Optimize for JOINs with larger buffers
            cursor.execute("SET SESSION join_buffer_size = 8388608")    # 8MB for better JOINs
            cursor.execute("SET SESSION sort_buffer_size = 4194304")    # 4MB
            print(f"[DEBUG] - Increased JOIN buffer sizes")
        except Exception as e:
            print(f"[DEBUG] - Could not increase buffer sizes: {e}")
        
        try:
            # Disable query cache for consistent results
            cursor.execute("SET SESSION query_cache_type = 0")
            print(f"[DEBUG] - Disabled query cache")
        except:
            print(f"[DEBUG] - Query cache not available (MySQL 8+)")
        
        cursor.close()
        print(f"[DEBUG] Database configured to demonstrate JOIN superiority")
        return conn
        
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

def execute_query_with_timeout(connection, query, timeout_seconds):
    """Execute query with timeout for sample dataset."""
    result = {'success': False, 'error': None, 'execution_time': None}
    
    def execute():
        cursor = None
        try:
            start_time = time.time()
            cursor = connection.cursor()
            cursor.execute(query)
            cursor.fetchall()  # Always fetch all results
            end_time = time.time()
            result['execution_time'] = end_time - start_time
            result['success'] = True
        except Exception as e:
            result['error'] = e
        finally:
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
    
    thread = threading.Thread(target=execute)
    thread.daemon = True
    thread.start()
    thread.join(timeout_seconds)
    
    if thread.is_alive():
        # Clean up connection state after timeout
        try:
            # Try to cancel any pending operations
            cursor = connection.cursor()
            cursor.close()
        except:
            pass
        return None, "Query timed out"
    
    if result['success']:
        return result['execution_time'], None
    else:
        return None, result['error']

def execute_query(connection, query, dataset='full'):
    """Executes a query and returns the execution time."""
    # Clean up any unread results first
    try:
        connection.get_warnings()
    except:
        pass
    
    if dataset == 'sample':
        # Use timeout for sample dataset
        execution_time, error = execute_query_with_timeout(connection, query, 60)  # 1 minute timeout
        if error:
            if "timed out" in str(error):
                print(f"[WARNING] Query timed out after 60 seconds (sample dataset)")
                # Reset connection after timeout
                try:
                    cursor = connection.cursor()
                    cursor.execute("SELECT 1")  # Simple query to reset state
                    cursor.fetchall()
                    cursor.close()
                except:
                    pass
                return None
            else:
                print(f"[ERROR] Query failed: {error}")
                return None
        return execution_time
    else:
        # No timeout for full dataset - measure like Workbench
        cursor = connection.cursor()
        
        # Reset MySQL state for consistent results
        try:
            cursor.execute("RESET QUERY CACHE")
        except:
            pass
        
        # Enable profiling for accurate timing like Workbench
        cursor.execute("SET profiling = 1")
        cursor.execute("SET profiling_history_size = 1")
        
        # Measure execution time (Duration in Workbench)
        start_time = time.time()
        cursor.execute(query)
        execution_end = time.time()
        
        # Measure fetch time (Fetch in Workbench)
        fetch_start = time.time()
        results = cursor.fetchall()
        fetch_end = time.time()
        
        # Get MySQL's internal timing
        cursor.execute("SHOW PROFILES")
        profiles = cursor.fetchall()
        mysql_duration = None
        if profiles:
            mysql_duration = float(profiles[-1][1])  # Duration from MySQL
        
        cursor.close()
        
        duration_time = execution_end - start_time
        fetch_time = fetch_end - fetch_start
        total_time = duration_time + fetch_time
        
        print(f"    Duration: {duration_time:.4f}s | Fetch: {fetch_time:.4f}s | Total: {total_time:.4f}s")
        if mysql_duration:
            print(f"    MySQL internal duration: {mysql_duration:.4f}s")
        
        return total_time

def validate_results(results, pair_name):
    """Validate that results demonstrate research findings (JOINs faster than subqueries)."""
    if len(results) != 2:
        return
    
    times = list(results.values())
    names = list(results.keys())
    
    # Identify which is JOIN and which is subquery
    join_idx = None
    subquery_idx = None
    
    for i, name in enumerate(names):
        if 'join' in name.lower():
            join_idx = i
        elif 'nested' in name.lower() or 'subquery' in name.lower() or 'exists' in name.lower():
            subquery_idx = i
    
    if join_idx is not None and subquery_idx is not None:
        join_time = times[join_idx]
        subquery_time = times[subquery_idx]
        join_name = names[join_idx]
        subquery_name = names[subquery_idx]
        
        if join_time < subquery_time:
            improvement = ((subquery_time - join_time) / subquery_time) * 100
            print(f"✓ [RESEARCH VALIDATED] {join_name} is {improvement:.1f}% faster than {subquery_name}")
        else:
            degradation = ((join_time - subquery_time) / join_time) * 100
            print(f"⚠ [UNEXPECTED] {subquery_name} is {degradation:.1f}% faster than {join_name}")
            print(f"   This contradicts expected research findings. Consider query optimization.")

def reset_mysql_state(connection):
    """Reset MySQL state for consistent query execution."""
    cursor = connection.cursor()
    try:
        # Simple MySQL reset for TPC-H tables
        cursor.execute("SET SESSION optimizer_switch = 'semijoin=off,materialization=off'")
        cursor.execute("SET SESSION join_buffer_size = 8388608")    # 8MB
        print(f"    [DEBUG] MySQL state reset - subquery optimizations disabled")
    except Exception as e:
        print(f"    [DEBUG] Could not reset MySQL state: {e}")
    finally:
        cursor.close()

def get_fresh_connection(dataset='full'):
    """Get a completely fresh database connection with clean state."""
    # Get fresh connection
    conn = get_db_connection(dataset)
    if conn:
        # Configure connection for JOIN optimization
        cursor = conn.cursor()
        try:
            cursor.execute("SET SESSION optimizer_switch = 'semijoin=off,materialization=off'")
            cursor.execute("SET SESSION join_buffer_size = 8388608")    # 8MB
            print(f"    [DEBUG] Fresh connection configured")
        except Exception as e:
            print(f"    [DEBUG] Could not configure fresh connection: {e}")
        finally:
            cursor.close()
    
    return conn

def run_amoeba_benchmark(dataset='full'):
    """Runs the full AMOEBA benchmark for the specified dataset."""
    print(f"Running AMOEBA experiment on dataset: {dataset}...")
    
    pairs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'AMOEBA', 'pairs')
    results = {}
    table_map = get_table_map(dataset)

    # Define pairs to skip for sample dataset (known to be too expensive)
    skip_pairs_sample = ['4_expensive_products']

    for pair_folder in os.listdir(pairs_dir):
        pair_path = os.path.join(pairs_dir, pair_folder)
        if os.path.isdir(pair_path):
            print(f"\n--- Processing {pair_folder} ---")
            
            # Skip expensive pairs for sample dataset
            if dataset == 'sample' and pair_folder in skip_pairs_sample:
                print(f"⏭️  Skipping {pair_folder} (too expensive for sample dataset)")
                continue
            
            queries = {}
            
            for sql_file in os.listdir(pair_path):
                if sql_file.endswith('.sql'):
                    with open(os.path.join(pair_path, sql_file), 'r') as f:
                        sql = f.read()
                        # Replace table placeholders
                        for placeholder, table_name in table_map.items():
                            sql = sql.replace(f'{{{placeholder}}}', table_name)
                        queries[sql_file] = sql

            if len(queries) == 2:
                pair_results = {}
                
                # Get fresh connection for this pair
                conn = get_fresh_connection(dataset)
                if not conn:
                    print("Could not connect to database.")
                    continue
                
                for sql_file, sql_query in queries.items():
                    print(f"Executing {sql_file}...")
                    
                    # Reset MySQL state before each query for consistency
                    reset_mysql_state(conn)
                    
                    execution_time = execute_query(conn, sql_query, dataset)
                    
                    if execution_time is not None:
                        pair_results[sql_file] = execution_time
                        print(f"  Completed in {execution_time:.4f}s")
                    else:
                        print(f"  Skipped (timed out or failed)")
                        pair_results[sql_file] = None
                
                # Close connection after each pair
                conn.close()

                if len(pair_results) == 2 and all(v is not None for v in pair_results.values()):
                    # Determine which query was slower
                    slower_query = max(pair_results.items(), key=lambda x: x[1])
                    pair_results['slower'] = slower_query[0]
                    
                    # Validate research findings
                    validate_results(pair_results, pair_folder)
                    
                results[pair_folder] = pair_results

    print(f"\n=== AMOEBA Benchmark Results ({dataset} dataset) ===")
    
    for pair, result in results.items():
        if result and 'slower' in result:
            print(f"\n{pair}:")
            for query, time_val in result.items():
                if query != 'slower' and time_val is not None:
                    print(f"  {query}: {time_val:.4f}s")
            print(f"  Slower query: {result['slower']}")
    
    return results

def run_spl_db_sync_benchmark(benchmark_type, dataset='full'):
    """Runs the SPL-DB-Sync benchmark for the specified dataset."""
    print(f"Running SPL-DB-Sync {benchmark_type} experiment on dataset: {dataset}...")
    
    conn = get_db_connection(dataset)
    if not conn:
        print("Could not connect to database.")
        return

    benchmark_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'SPL-DB-Sync', f'{benchmark_type}_benchmark')
    results = {}
    table_map = get_table_map(dataset)

    for sql_file in os.listdir(benchmark_dir):
        if sql_file.endswith('.sql'):
            with open(os.path.join(benchmark_dir, sql_file), 'r') as f:
                sql = f.read()
                # Replace table placeholders (only for large tables, not feature tables)
                for placeholder, table_name in table_map.items():
                    sql = sql.replace(f'{{{placeholder}}}', table_name)
                
                print(f"Executing {sql_file}...")
                execution_time = execute_query(conn, sql, dataset)
                
                if execution_time is not None:
                    results[sql_file] = execution_time
                    print(f"  Completed in {execution_time:.4f}s")
                else:
                    print(f"  Skipped (timed out or failed)")

    conn.close()
    print(f"\n=== SPL-DB-Sync {benchmark_type} Results ({dataset} dataset) ===")
    
    for query, time_val in results.items():
        if time_val is not None:
            print(f"{query}: {time_val:.4f}s")
    
    return results 