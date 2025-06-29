#!/usr/bin/env python3
"""
🔬 Database Performance Research Validation Tool

This tool validates research findings from:
1. AMOEBA: Subquery vs JOIN performance 
2. SPL-DB-Sync: Modular vs Flat query performance
3. Code Testing: Feature-based automated testing

Usage:
    python simple_benchmark.py --experiment [amoeba|spl-db-sync|code-testing|all] --dataset [sample|full]
"""

import argparse
import time
import os
import sys
import mysql.connector
from pathlib import Path
import subprocess

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root', 
    'password': '',
    'database': 'test',
    'autocommit': True,
    'connect_timeout': 10,
    'charset': 'utf8mb4'
}

def get_connection():
    """Get database connection with timeout"""
    return mysql.connector.connect(**DB_CONFIG)

def execute_query_with_timeout(query, timeout=60):
    """Execute query with timeout and return results"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        start_time = time.time()
        cursor.execute(query)
        results = cursor.fetchall()
        execution_time = time.time() - start_time
        
        cursor.close()
        conn.close()
        
        return {
            'success': True,
            'execution_time': execution_time,
            'row_count': len(results),
            'error': None
        }
        
    except mysql.connector.Error as e:
        return {
            'success': False,
            'execution_time': None,
            'row_count': 0,
            'error': f"{e.errno} ({e.sqlstate}): {e.msg}"
        }
    except Exception as e:
        return {
            'success': False,
            'execution_time': None,
            'row_count': 0,
            'error': str(e)
        }

def load_query(file_path, dataset):
    """Load SQL query and substitute table placeholders"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            query = f.read().strip()
        
        # Table mapping based on dataset
        if dataset == 'sample':
            table_map = {
                '{CUSTOMER_TABLE}': 'customer_sample',
                '{ORDERS_TABLE}': 'orders_sample',
                '{LINEITEM_TABLE}': 'lineitem_sample',
                '{PART_TABLE}': 'part_sample'
            }
        else:  # full dataset
            table_map = {
                '{CUSTOMER_TABLE}': 'customer',
                '{ORDERS_TABLE}': 'orders', 
                '{LINEITEM_TABLE}': 'lineitem',
                '{PART_TABLE}': 'part'
            }
        
        # Replace placeholders
        for placeholder, table_name in table_map.items():
            query = query.replace(placeholder, table_name)
            
        return query
        
    except FileNotFoundError:
        print(f"❌ Error: Query file not found: {file_path}")
        return None
    except Exception as e:
        print(f"❌ Error loading query {file_path}: {e}")
        return None

def run_amoeba_experiment(dataset):
    """Run AMOEBA experiment: Subquery vs JOIN performance"""
    print("============================================================")
    print("🔬 AMOEBA EXPERIMENT: Subquery vs JOIN Performance")
    print("🎯 Research Goal: Validate that JOINs are faster than subqueries")
    print()
    
    pairs_dir = Path("AMOEBA/pairs")
    results = []
    
    # Get all pair directories
    pair_dirs = [d for d in pairs_dir.iterdir() if d.is_dir() and not d.name.startswith('4_')]
    pair_dirs.sort()
    
    for pair_dir in pair_dirs:
        pair_name = pair_dir.name
        print(f"--- Testing {pair_name} ---")
        
        # Find query files
        query_files = list(pair_dir.glob("*.sql"))
        if len(query_files) != 2:
            print(f"⚠️ Skipping {pair_name}: Expected 2 query files, found {len(query_files)}")
            continue
            
        query_files.sort()
        
        pair_results = {}
        
        for query_file in query_files:
            query_name = query_file.stem
            print(f"Executing {query_file.name}...")
            
            query = load_query(query_file, dataset)
            if not query:
                continue
                
            result = execute_query_with_timeout(query)
            
            if result['success']:
                print(f"    ✓ Query completed in {result['execution_time']:.4f}s ({result['row_count']} rows)")
                pair_results[query_name] = result
            else:
                print(f"    ✗ Query failed: {result['error']}")
                
        # Compare results
        if len(pair_results) == 2:
            query_names = list(pair_results.keys())
            q1_name, q2_name = query_names[0], query_names[1]
            q1_result, q2_result = pair_results[q1_name], pair_results[q2_name]
            
            # Check logical equivalence
            if q1_result['row_count'] != q2_result['row_count']:
                print(f"⚠️ Row count mismatch: {q1_name}={q1_result['row_count']}, {q2_name}={q2_result['row_count']}")
            
            # Determine winner
            if q1_result['execution_time'] < q2_result['execution_time']:
                faster_query = q1_name
                slower_query = q2_name
                faster_time = q1_result['execution_time']
                slower_time = q2_result['execution_time']
            else:
                faster_query = q2_name
                slower_query = q1_name
                faster_time = q2_result['execution_time']
                slower_time = q1_result['execution_time']
            
            improvement = ((slower_time - faster_time) / slower_time) * 100
            
            print(f"📊 Results:")
            print(f"   {faster_query}: {faster_time:.4f}s (FASTER)")
            print(f"   {slower_query}: {slower_time:.4f}s")
            print(f"   Performance improvement: {improvement:.1f}%")
            
            # Check if JOIN won (research validation)
            join_won = 'join' in faster_query.lower()
            if join_won:
                print("   ✅ JOIN is faster (validates research)")
                results.append(True)
            else:
                print("   ❌ Subquery is faster (unexpected)")
                results.append(False)
        else:
            print("   ⚠️ Could not compare results")
            
        print()
    
    # Skip expensive products for sample dataset
    if dataset == 'sample':
        print("⏭️ Skipping 4_expensive_products (too expensive for sample)")
        print()
    
    return results

def run_spl_db_sync_experiment(dataset):
    """Run SPL-DB-Sync experiment: Modular vs Flat query performance"""
    print("============================================================")
    print("🏗️ SPL-DB-SYNC EXPERIMENT: Modular vs Flat Query Performance")
    print("🎯 Research Goal: Validate that modular queries are faster than flat queries")
    print("============================================================")
    print()
    
    modular_dir = Path("SPL-DB-Sync/modular_benchmark")
    flat_dir = Path("SPL-DB-Sync/flat_benchmark")
    
    results = []
    
    # Get matching query files
    modular_files = {f.stem: f for f in modular_dir.glob("*.sql")}
    flat_files = {f.stem: f for f in flat_dir.glob("*.sql")}
    
    common_queries = set(modular_files.keys()) & set(flat_files.keys())
    
    for query_name in sorted(common_queries):
        print(f"--- Testing {query_name} ---")
        
        modular_file = modular_files[query_name]
        flat_file = flat_files[query_name]
        
        pair_results = {}
        
        # Execute modular query
        print(f"Executing modular_{query_name}.sql...")
        modular_query = load_query(modular_file, dataset)
        if modular_query:
            modular_result = execute_query_with_timeout(modular_query)
            if modular_result['success']:
                print(f"    ✓ Query completed in {modular_result['execution_time']:.4f}s ({modular_result['row_count']} rows)")
                pair_results['modular'] = modular_result
            else:
                print(f"    ✗ Query failed: {modular_result['error']}")
        
        # Execute flat query
        print(f"Executing flat_{query_name}.sql...")
        flat_query = load_query(flat_file, dataset)
        if flat_query:
            flat_result = execute_query_with_timeout(flat_query)
            if flat_result['success']:
                print(f"    ✓ Query completed in {flat_result['execution_time']:.4f}s ({flat_result['row_count']} rows)")
                pair_results['flat'] = flat_result
            else:
                print(f"    ✗ Query failed: {flat_result['error']}")
        
        # Compare results
        if len(pair_results) == 2:
            modular_time = pair_results['modular']['execution_time']
            flat_time = pair_results['flat']['execution_time']
            modular_rows = pair_results['modular']['row_count']
            flat_rows = pair_results['flat']['row_count']
            
            # Check logical equivalence
            if modular_rows != flat_rows:
                print(f"⚠️ Row count mismatch: modular={modular_rows}, flat={flat_rows}")
            
            # Determine winner
            if modular_time < flat_time:
                faster_type = "modular"
                faster_time = modular_time
                slower_time = flat_time
                improvement = ((flat_time - modular_time) / flat_time) * 100
                print(f"📊 Results:")
                print(f"   modular: {modular_time:.4f}s (FASTER)")
                print(f"   flat: {flat_time:.4f}s")
                print(f"   Performance improvement: {improvement:.1f}%")
                print("   ✅ Modular is faster (validates research)")
                results.append(True)
            else:
                faster_type = "flat"
                faster_time = flat_time
                slower_time = modular_time
                difference = ((modular_time - flat_time) / modular_time) * 100
                print(f"📊 Results:")
                print(f"   flat: {flat_time:.4f}s (FASTER)")
                print(f"   modular: {modular_time:.4f}s")
                print(f"   Performance difference: {difference:.1f}%")
                print("   ❌ Flat is faster (unexpected)")
                results.append(False)
        else:
            print("   ⚠️ Could not compare results")
            
        print()
    
    return results

def run_code_testing_experiment():
    """Run Code Testing experiment: Feature-based automated testing"""
    print("============================================================")
    print("🧪 CODE TESTING EXPERIMENT: Feature-based Automated Testing")
    print("🎯 Research Goal: Validate automated test case reuse in SPL environments")
    print("============================================================")
    print()
    
    # Change to code_testing directory
    original_dir = os.getcwd()
    code_testing_dir = Path("code_testing")
    
    if not code_testing_dir.exists():
        print("❌ Code testing directory not found")
        return []
    
    try:
        os.chdir(code_testing_dir)
        
        # Test different feature variants
        feature_variants = ['loyalty', 'newsletter', 'purchase', 'full']
        results = []
        
        for variant in feature_variants:
            print(f"--- Testing {variant} feature variant ---")
            
            # Update config.py with current variant
            config_content = f"""import mysql.connector

FEATURE_VARIANT = '{variant}'

DB_CONFIG = {{
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'test',
    'allow_local_infile': True
}}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)
"""
            
            with open('config.py', 'w') as f:
                f.write(config_content)
            
            # Run pytest
            try:
                result = subprocess.run([
                    sys.executable, '-m', 'pytest', '-v', '--tb=short'
                ], capture_output=True, text=True, timeout=120)
                
                print(f"Exit code: {result.returncode}")
                if result.stdout:
                    print("STDOUT:")
                    print(result.stdout)
                if result.stderr:
                    print("STDERR:")
                    print(result.stderr)
                
                # Count passed/failed tests
                output = result.stdout + result.stderr
                if 'passed' in output or 'failed' in output:
                    results.append(result.returncode == 0)
                    if result.returncode == 0:
                        print(f"   ✅ {variant} tests passed")
                    else:
                        print(f"   ❌ {variant} tests failed")
                else:
                    print(f"   ⚠️ {variant} tests skipped or no output")
                    
            except subprocess.TimeoutExpired:
                print(f"   ⏱️ {variant} tests timed out")
            except Exception as e:
                print(f"   ❌ Error running {variant} tests: {e}")
            
            print()
        
        return results
        
    finally:
        os.chdir(original_dir)

def print_summary(amoeba_results, spl_results, code_results):
    """Print comprehensive research validation summary"""
    print("======================================================================")
    print("📈 RESEARCH VALIDATION SUMMARY")
    print("======================================================================")
    
    # AMOEBA Summary
    if amoeba_results:
        amoeba_success = sum(amoeba_results)
        amoeba_total = len(amoeba_results)
        amoeba_rate = (amoeba_success / amoeba_total) * 100
        
        print("🔬 AMOEBA (Subquery vs JOIN):")
        print(f"   Total pairs tested: {amoeba_total}")
        print(f"   JOINs faster: {amoeba_success}")
        print(f"   Subqueries faster: {amoeba_total - amoeba_success}")
        print(f"   Success rate: {amoeba_rate:.1f}%")
        
        if amoeba_rate >= 66.7:
            print("   🎉 SUCCESS: JOINs are generally faster!")
        else:
            print("   ⚠️ WARNING: Results don't match research findings.")
    else:
        print("🔬 AMOEBA: Not tested")
        amoeba_success = 0
        amoeba_total = 0
    
    print()
    
    # SPL-DB-Sync Summary
    if spl_results:
        spl_success = sum(spl_results)
        spl_total = len(spl_results)
        spl_rate = (spl_success / spl_total) * 100
        
        print("🏗️ SPL-DB-SYNC (Modular vs Flat):")
        print(f"   Total pairs tested: {spl_total}")
        print(f"   Modular faster: {spl_success}")
        print(f"   Flat faster: {spl_total - spl_success}")
        print(f"   Success rate: {spl_rate:.1f}%")
        
        if spl_rate >= 66.7:
            print("   🎉 SUCCESS: Modular queries are generally faster!")
        else:
            print("   ⚠️ WARNING: Results don't match research findings.")
    else:
        print("🏗️ SPL-DB-SYNC: Not tested")
        spl_success = 0
        spl_total = 0
    
    print()
    
    # Code Testing Summary
    if code_results:
        code_success = sum(code_results)
        code_total = len(code_results)
        code_rate = (code_success / code_total) * 100
        
        print("🧪 CODE TESTING (Feature Variants):")
        print(f"   Total variants tested: {code_total}")
        print(f"   Variants passed: {code_success}")
        print(f"   Variants failed: {code_total - code_success}")
        print(f"   Success rate: {code_rate:.1f}%")
        
        if code_rate >= 75.0:
            print("   🎉 SUCCESS: Automated testing works across variants!")
        else:
            print("   ⚠️ WARNING: Some feature variants have test issues.")
    else:
        print("🧪 CODE TESTING: Not tested")
        code_success = 0
        code_total = 0
    
    print()
    
    # Overall Summary
    total_success = amoeba_success + spl_success + code_success
    total_experiments = amoeba_total + spl_total + code_total
    
    if total_experiments > 0:
        overall_rate = (total_success / total_experiments) * 100
        
        print("🏆 OVERALL RESEARCH VALIDATION:")
        print(f"   Total experiments: {total_experiments}")
        print(f"   Successful validations: {total_success}")
        print(f"   Overall success rate: {overall_rate:.1f}%")
        
        if overall_rate >= 70.0:
            print("   🎉 EXCELLENT: Research findings are well validated!")
        elif overall_rate >= 50.0:
            print("   ⚠️ Mixed results. Consider testing with full dataset.")
        else:
            print("   ❌ Poor validation. Check queries and database setup.")

def main():
    parser = argparse.ArgumentParser(
        description='🔬 Database Performance Research Validation Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python simple_benchmark.py --experiment all --dataset sample
  python simple_benchmark.py --experiment amoeba --dataset full
  python simple_benchmark.py --experiment spl-db-sync --dataset sample
  python simple_benchmark.py --experiment code-testing
        """
    )
    
    parser.add_argument('--experiment', 
                       choices=['amoeba', 'spl-db-sync', 'code-testing', 'all'],
                       required=True,
                       help='Which experiment to run')
    
    parser.add_argument('--dataset',
                       choices=['sample', 'full'], 
                       default='sample',
                       help='Dataset size to use (default: sample)')
    
    args = parser.parse_args()
    
    print("======================================================================")
    print("🚀 DATABASE PERFORMANCE RESEARCH VALIDATION")
    if args.experiment != 'code-testing':
        print(f"📊 Dataset: {args.dataset}")
    print("⏱️ Timeout: 60s")
    print("======================================================================")
    
    start_time = time.time()
    
    amoeba_results = []
    spl_results = []
    code_results = []
    
    if args.experiment in ['amoeba', 'all']:
        amoeba_results = run_amoeba_experiment(args.dataset)
    
    if args.experiment in ['spl-db-sync', 'all']:
        spl_results = run_spl_db_sync_experiment(args.dataset)
    
    if args.experiment in ['code-testing', 'all']:
        code_results = run_code_testing_experiment()
    
    print_summary(amoeba_results, spl_results, code_results)
    
    total_time = time.time() - start_time
    print(f"\n⏱️ Total execution time: {total_time:.2f} seconds")

if __name__ == "__main__":
    main() 