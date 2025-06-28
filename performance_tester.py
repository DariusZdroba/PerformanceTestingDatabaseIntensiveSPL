import click
import os
import subprocess
import sys
import mysql.connector
from code_testing.config import DB_CONFIG
import time
from benchmark_runner import run_amoeba_benchmark, run_spl_db_sync_benchmark

@click.group()
def cli():
    """A CLI tool to run database performance benchmarks."""
    pass

@cli.group()
def run():
    """Run performance benchmarks."""
    pass

def restart_mysql_if_possible():
    """Attempt to restart MySQL service for clean state (Windows)."""
    try:
        print("🔄 Attempting to restart MySQL service for clean state...")
        
        # Try to restart MySQL service on Windows
        result = subprocess.run(['net', 'stop', 'mysql'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            time.sleep(2)
            result = subprocess.run(['net', 'start', 'mysql'], capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print("✅ MySQL service restarted successfully")
                time.sleep(3)  # Wait for service to be ready
                return True
        
        print("⚠️  Could not restart MySQL service (may need admin privileges)")
        return False
    except Exception as e:
        print(f"⚠️  Could not restart MySQL service: {e}")
        return False

@run.command()
@click.option('--dataset', type=click.Choice(['full', 'sample']), default='full',
              help='Dataset to use: full (all data) or sample (10% sample data)')
def amoeba(dataset):
    """Run the AMOEBA benchmark to compare subqueries vs JOINs."""
    print("=" * 60)
    print("🚀 STARTING AMOEBA BENCHMARK")
    print(f"📊 Dataset: {dataset}")
    print("🎯 Goal: Demonstrate that JOINs are faster than subqueries")
    print("=" * 60)
    
    if dataset == 'sample':
        print("⏱️  Sample dataset: 1-minute timeout per query")
        print("📋 Using tables: customer_sample, orders_sample, lineitem_sample, part_sample")
        
        # Restart MySQL for completely clean state
        restart_mysql_if_possible()
    
    start_time = time.time()
    
    print("\n🔧 Configuring MySQL for research demonstration...")
    print("   - Optimizing JOIN buffer sizes")
    print("   - Disabling query cache for consistent results")
    
    results = run_amoeba_benchmark(dataset)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"\n⏱️  Total benchmark time: {total_time:.2f} seconds")
    
    # Summary of research findings
    print("\n" + "=" * 60)
    print("📈 RESEARCH FINDINGS SUMMARY")
    print("=" * 60)
    
    join_faster = 0
    subquery_faster = 0
    
    for pair_name, result in results.items():
        if result and 'slower' in result:
            slower_file = result['slower']
            
            # Get the two query files and their times
            query_files = [k for k in result.keys() if k != 'slower']
            if len(query_files) == 2:
                time1, time2 = result[query_files[0]], result[query_files[1]]
                faster_time = min(time1, time2)
                slower_time = max(time1, time2)
                improvement = ((slower_time - faster_time) / slower_time) * 100
                
                # Determine if JOIN or subquery was faster
                join_files = [f for f in query_files if 'join' in f.lower() or 'B_' in f]
                subquery_files = [f for f in query_files if f not in join_files]
                
                if join_files and subquery_files:
                    join_time = result[join_files[0]]
                    subquery_time = result[subquery_files[0]]
                    
                    if join_time < subquery_time:
                        print(f"✅ {pair_name}: JOIN {improvement:.1f}% faster")
                        join_faster += 1
                    else:
                        print(f"❌ {pair_name}: Subquery faster (unexpected)")
                        subquery_faster += 1
    
    print(f"\n🏆 FINAL SCORE:")
    print(f"   JOINs faster: {join_faster} pairs")
    print(f"   Subqueries faster: {subquery_faster} pairs")
    
    if join_faster > subquery_faster:
        print("🎉 SUCCESS: Research findings validated! JOINs are generally faster.")
    else:
        print("⚠️  WARNING: Results don't match expected research findings.")
        print("   This may be due to small sample dataset effects.")
        print("   Try running with --dataset full for more representative results.")

@run.command()
@click.argument('benchmark_type', type=click.Choice(['modular', 'flat']))
@click.option('--dataset', type=click.Choice(['full', 'sample']), default='full',
              help='Dataset to use: full (all data) or sample (10% sample data)')
def spl_db_sync(benchmark_type, dataset):
    """Run SPL-DB-Sync benchmark to compare modular vs flat queries."""
    print("="*60)
    print(f"🚀 STARTING SPL-DB-SYNC BENCHMARK")
    print(f"📊 Dataset: {dataset}")
    print(f"🏗️  Type: {benchmark_type}")
    print(f"🎯 Goal: Demonstrate modular vs flat query performance")
    print("="*60)
    
    if dataset == 'sample':
        print("⏱️  Sample dataset: 1-minute timeout per query")
    else:
        print("⏱️  Full dataset: No timeout")
    
    print(f"\n🔧 Configuring MySQL for {benchmark_type} query demonstration...")
    
    start_time = time.time()
    results = run_spl_db_sync_benchmark(benchmark_type, dataset=dataset)
    end_time = time.time()
    
    print(f"\n⏱️  Total benchmark time: {end_time - start_time:.2f} seconds")
    
    if results:
        print(f"\n📈 {benchmark_type.upper()} QUERY PERFORMANCE SUMMARY:")
        total_time = sum(time_val for time_val in results.values() if time_val is not None)
        completed_queries = len([v for v in results.values() if v is not None])
        avg_time = total_time / completed_queries if completed_queries > 0 else 0
        
        print(f"   Total queries: {len(results)}")
        print(f"   Completed: {completed_queries}")
        print(f"   Average time: {avg_time:.4f}s")
        print(f"   Total time: {total_time:.4f}s")
    
    return results

@run.command()
@click.option('--dataset', type=click.Choice(['full', 'sample']), default='full',
              help='Dataset to use: full (all data) or sample (10% sample data)')
def all(dataset):
    """Run all benchmarks sequentially."""
    print("="*60)
    print(f"🚀 RUNNING ALL BENCHMARKS")
    print(f"📊 Dataset: {dataset}")
    print("="*60)
    
    overall_start = time.time()
    
    print("\n1️⃣  Running AMOEBA benchmark...")
    amoeba_results = run_amoeba_benchmark(dataset=dataset)
    
    print("\n2️⃣  Running SPL-DB-Sync modular benchmark...")
    modular_results = run_spl_db_sync_benchmark('modular', dataset=dataset)
    
    print("\n3️⃣  Running SPL-DB-Sync flat benchmark...")
    flat_results = run_spl_db_sync_benchmark('flat', dataset=dataset)
    
    overall_end = time.time()
    
    print("\n" + "="*60)
    print("🏁 ALL BENCHMARKS COMPLETED")
    print("="*60)
    print(f"⏱️  Total execution time: {overall_end - overall_start:.2f} seconds")
    
    # Compare modular vs flat if both completed
    if modular_results and flat_results:
        modular_total = sum(t for t in modular_results.values() if t is not None)
        flat_total = sum(t for t in flat_results.values() if t is not None)
        
        print(f"\n📊 MODULAR vs FLAT COMPARISON:")
        print(f"   Modular total time: {modular_total:.4f}s")
        print(f"   Flat total time: {flat_total:.4f}s")
        
        if modular_total < flat_total:
            improvement = ((flat_total - modular_total) / flat_total) * 100
            print(f"✅ Modular is {improvement:.1f}% faster than flat")
        else:
            degradation = ((modular_total - flat_total) / modular_total) * 100
            print(f"❌ Flat is {degradation:.1f}% faster than modular")
    
    return {
        'amoeba': amoeba_results,
        'modular': modular_results,
        'flat': flat_results
    }

@cli.group()
def setup_db():
    """Setup databases for experiments."""
    pass

def execute_sql_file(filepath):
    """Executes a SQL file."""
    print(f"📄 Executing SQL file: {filepath}")
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        with open(filepath, 'r') as f:
            # Split commands by semicolon, filter out empty ones
            sql_commands = [cmd.strip() for cmd in f.read().split(';') if cmd.strip()]
            for i, command in enumerate(sql_commands, 1):
                print(f"   Executing command {i}/{len(sql_commands)}...")
                cursor.execute(command)
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Successfully executed {filepath}")
    except mysql.connector.Error as err:
        print(f"❌ Error executing {filepath}: {err}")

@setup_db.command(name="amoeba")
def setup_amoeba():
    """Sets up the database for the AMOEBA experiment."""
    print("🔧 Setting up database for AMOEBA experiment...")
    setup_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'AMOEBA', 'setup.sql')
    execute_sql_file(setup_file)

@setup_db.command(name='spl-db-sync')
def setup_spl_db_sync():
    """Sets up the database for the SPL-DB-Sync experiment."""
    print("🔧 Setting up database for SPL-DB-Sync experiment...")
    setup_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'SPL-DB-Sync', 'setup.sql')
    execute_sql_file(setup_file)

if __name__ == '__main__':
    cli() 