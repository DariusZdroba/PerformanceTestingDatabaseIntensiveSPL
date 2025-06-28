#!/usr/bin/env python3
"""
Simple Database Performance Benchmark
Compares subquery vs JOIN performance and modular vs flat query performance
to validate research findings
"""

import mysql.connector
import time
import os
import click
from code_testing.config import DB_CONFIG

def get_connection():
    """Get a simple database connection."""
    return mysql.connector.connect(**DB_CONFIG)

def get_table_names(dataset):
    """Get table names for the dataset."""
    if dataset == 'sample':
        return {
            'CUSTOMER_TABLE': 'customer_sample',
            'ORDERS_TABLE': 'orders_sample', 
            'LINEITEM_TABLE': 'lineitem_sample',
            'PART_TABLE': 'part_sample'
        }
    else:
        return {
            'CUSTOMER_TABLE': 'customer',
            'ORDERS_TABLE': 'orders',
            'LINEITEM_TABLE': 'lineitem', 
            'PART_TABLE': 'part'
        }

def load_and_prepare_query(file_path, table_map):
    """Load SQL query and replace table placeholders."""
    with open(file_path, 'r') as f:
        sql = f.read()
    
    # Replace table placeholders
    for placeholder, table_name in table_map.items():
        sql = sql.replace(f'{{{placeholder}}}', table_name)
    
    return sql.strip()

def execute_query_simple(sql, timeout_seconds=None):
    """Execute a query and return execution time."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        start_time = time.time()
        cursor.execute(sql)
        results = cursor.fetchall()
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"    ✓ Query completed in {execution_time:.4f}s ({len(results)} rows)")
        return execution_time
        
    except Exception as e:
        print(f"    ✗ Query failed: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def run_amoeba_benchmark(dataset, timeout=None):
    """Run AMOEBA benchmark (subquery vs JOIN)."""
    print("=" * 60)
    print("🔬 AMOEBA EXPERIMENT: Subquery vs JOIN Performance")
    print("🎯 Research Goal: Validate that JOINs are faster than subqueries")
    print("=" * 60)
    
    pairs_dir = os.path.join('AMOEBA', 'pairs')
    if not os.path.exists(pairs_dir):
        print(f"❌ Error: {pairs_dir} directory not found")
        return {}
    
    results = {}
    table_map = get_table_names(dataset)
    
    # Process each query pair
    for pair_name in sorted(os.listdir(pairs_dir)):
        pair_path = os.path.join(pairs_dir, pair_name)
        if os.path.isdir(pair_path):
            # Skip expensive queries for sample dataset
            if dataset == 'sample' and 'expensive' in pair_name.lower():
                print(f"\n⏭️ Skipping {pair_name} (too expensive for sample)")
                continue
                
            print(f"\n--- Testing {pair_name} ---")
            pair_results = {}
            
            # Find SQL files in the pair directory
            sql_files = [f for f in os.listdir(pair_path) if f.endswith('.sql')]
            sql_files.sort()  # Ensure consistent order
            
            for sql_file in sql_files:
                file_path = os.path.join(pair_path, sql_file)
                print(f"Executing {sql_file}...")
                
                # Load and prepare query
                sql = load_and_prepare_query(file_path, table_map)
                
                # Execute query
                execution_time = execute_query_simple(sql, timeout)
                pair_results[sql_file] = execution_time
            
            # Analyze results
            if len(pair_results) == 2 and all(v is not None for v in pair_results.values()):
                times = list(pair_results.values())
                files = list(pair_results.keys())
                
                faster_idx = 0 if times[0] < times[1] else 1
                slower_idx = 1 - faster_idx
                
                faster_file = files[faster_idx]
                slower_file = files[slower_idx]
                faster_time = times[faster_idx]
                slower_time = times[slower_idx]
                
                improvement = ((slower_time - faster_time) / slower_time) * 100
                
                print(f"📊 Results:")
                print(f"   {faster_file}: {faster_time:.4f}s (FASTER)")
                print(f"   {slower_file}: {slower_time:.4f}s")
                print(f"   Performance improvement: {improvement:.1f}%")
                
                # Determine if JOIN was faster (research validation)
                join_faster = 'join' in faster_file.lower() or 'B_' in faster_file
                if join_faster:
                    print(f"   ✅ JOIN is faster (validates research)")
                else:
                    print(f"   ❌ Subquery is faster (unexpected)")
                    
                results[pair_name] = {
                    'faster_file': faster_file,
                    'slower_file': slower_file,
                    'faster_time': faster_time,
                    'slower_time': slower_time,
                    'improvement': improvement,
                    'join_faster': join_faster
                }
            else:
                print(f"   ⚠️ Could not compare results")
    
    return results

def run_spl_db_sync_benchmark(dataset, timeout=None):
    """Run SPL-DB-Sync benchmark (modular vs flat)."""
    print("\n" + "=" * 60)
    print("🏗️ SPL-DB-SYNC EXPERIMENT: Modular vs Flat Query Performance")
    print("🎯 Research Goal: Validate that modular queries are faster than flat queries")
    print("=" * 60)
    
    modular_dir = os.path.join('SPL-DB-Sync', 'modular_benchmark')
    flat_dir = os.path.join('SPL-DB-Sync', 'flat_benchmark')
    
    if not os.path.exists(modular_dir) or not os.path.exists(flat_dir):
        print(f"❌ Error: SPL-DB-Sync directories not found")
        return {}
    
    table_map = get_table_names(dataset)
    results = {}
    
    # Get all query files
    modular_files = [f for f in os.listdir(modular_dir) if f.endswith('.sql')]
    flat_files = [f for f in os.listdir(flat_dir) if f.endswith('.sql')]
    
    # Find matching pairs
    common_files = set(modular_files) & set(flat_files)
    
    for query_file in sorted(common_files):
        query_name = query_file.replace('.sql', '')
        print(f"\n--- Testing {query_name} ---")
        
        pair_results = {}
        
        # Test modular version
        modular_path = os.path.join(modular_dir, query_file)
        print(f"Executing modular_{query_file}...")
        sql = load_and_prepare_query(modular_path, table_map)
        modular_time = execute_query_simple(sql, timeout)
        pair_results['modular'] = modular_time
        
        # Test flat version
        flat_path = os.path.join(flat_dir, query_file)
        print(f"Executing flat_{query_file}...")
        sql = load_and_prepare_query(flat_path, table_map)
        flat_time = execute_query_simple(sql, timeout)
        pair_results['flat'] = flat_time
        
        # Analyze results
        if all(v is not None for v in pair_results.values()):
            modular_time = pair_results['modular']
            flat_time = pair_results['flat']
            
            if modular_time < flat_time:
                improvement = ((flat_time - modular_time) / flat_time) * 100
                print(f"📊 Results:")
                print(f"   modular: {modular_time:.4f}s (FASTER)")
                print(f"   flat: {flat_time:.4f}s")
                print(f"   Performance improvement: {improvement:.1f}%")
                print(f"   ✅ Modular is faster (validates research)")
                
                results[query_name] = {
                    'modular_time': modular_time,
                    'flat_time': flat_time,
                    'improvement': improvement,
                    'modular_faster': True
                }
            else:
                degradation = ((modular_time - flat_time) / modular_time) * 100
                print(f"📊 Results:")
                print(f"   flat: {flat_time:.4f}s (FASTER)")
                print(f"   modular: {modular_time:.4f}s")
                print(f"   Performance difference: {degradation:.1f}%")
                print(f"   ❌ Flat is faster (unexpected)")
                
                results[query_name] = {
                    'modular_time': modular_time,
                    'flat_time': flat_time,
                    'improvement': -degradation,
                    'modular_faster': False
                }
        else:
            print(f"   ⚠️ Could not compare results")
    
    return results

@click.command()
@click.option('--experiment', type=click.Choice(['amoeba', 'spl-db-sync', 'all']), default='all',
              help='Which experiment to run')
@click.option('--dataset', type=click.Choice(['full', 'sample']), default='sample',
              help='Dataset to use: full or sample')
@click.option('--timeout', type=int, default=60,
              help='Timeout in seconds for sample dataset (0 = no timeout)')
def main(experiment, dataset, timeout):
    """Run database performance benchmarks to validate research findings."""
    
    print("=" * 70)
    print("🚀 DATABASE PERFORMANCE RESEARCH VALIDATION")
    print(f"📊 Dataset: {dataset}")
    print(f"⏱️ Timeout: {timeout}s" if timeout > 0 else "⏱️ No timeout")
    print("=" * 70)
    
    overall_start = time.time()
    amoeba_results = {}
    spl_results = {}
    
    # Run experiments
    if experiment in ['amoeba', 'all']:
        amoeba_results = run_amoeba_benchmark(dataset, timeout if timeout > 0 else None)
    
    if experiment in ['spl-db-sync', 'all']:
        spl_results = run_spl_db_sync_benchmark(dataset, timeout if timeout > 0 else None)
    
    overall_end = time.time()
    total_time = overall_end - overall_start
    
    # Final Summary
    print("\n" + "=" * 70)
    print("📈 RESEARCH VALIDATION SUMMARY")
    print("=" * 70)
    
    # AMOEBA Results
    if amoeba_results:
        join_wins = sum(1 for r in amoeba_results.values() if r['join_faster'])
        total_amoeba = len(amoeba_results)
        
        print(f"🔬 AMOEBA (Subquery vs JOIN):")
        print(f"   Total pairs tested: {total_amoeba}")
        print(f"   JOINs faster: {join_wins}")
        print(f"   Subqueries faster: {total_amoeba - join_wins}")
        print(f"   Success rate: {(join_wins/total_amoeba)*100:.1f}%")
        
        if join_wins > total_amoeba - join_wins:
            print("   🎉 SUCCESS: JOINs are generally faster!")
        else:
            print("   ⚠️ WARNING: Results don't match research findings.")
    
    # SPL-DB-Sync Results
    if spl_results:
        modular_wins = sum(1 for r in spl_results.values() if r['modular_faster'])
        total_spl = len(spl_results)
        
        print(f"\n🏗️ SPL-DB-SYNC (Modular vs Flat):")
        print(f"   Total pairs tested: {total_spl}")
        print(f"   Modular faster: {modular_wins}")
        print(f"   Flat faster: {total_spl - modular_wins}")
        print(f"   Success rate: {(modular_wins/total_spl)*100:.1f}%")
        
        if modular_wins > total_spl - modular_wins:
            print("   🎉 SUCCESS: Modular queries are generally faster!")
        else:
            print("   ⚠️ WARNING: Results don't match research findings.")
    
    # Overall Research Validation
    total_experiments = len(amoeba_results) + len(spl_results)
    total_successes = (sum(1 for r in amoeba_results.values() if r['join_faster']) + 
                      sum(1 for r in spl_results.values() if r['modular_faster']))
    
    if total_experiments > 0:
        overall_success = (total_successes / total_experiments) * 100
        print(f"\n🏆 OVERALL RESEARCH VALIDATION:")
        print(f"   Total experiments: {total_experiments}")
        print(f"   Successful validations: {total_successes}")
        print(f"   Overall success rate: {overall_success:.1f}%")
        
        if overall_success >= 66.7:  # 2/3 success rate
            print("   🎉 RESEARCH VALIDATED: Your findings are supported by the data!")
        else:
            print("   ⚠️ Mixed results. Consider testing with full dataset.")
    
    print(f"\n⏱️ Total execution time: {total_time:.2f} seconds")

if __name__ == '__main__':
    main() 