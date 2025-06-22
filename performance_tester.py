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
    """Run experiments."""
    pass

@run.command(name='code-testing')
@click.option('--variant', type=click.Choice(['loyalty', 'newsletter', 'full', 'all']), default='all', help='The feature variant to test.')
def code_testing(variant):
    """Runs the code-based tests using pytest."""
    print("Running code testing experiment")
    variants = ['loyalty', 'newsletter', 'full'] if variant == 'all' else [variant]
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    test_dir = os.path.join(base_path, 'code_testing')
    results_dir = os.path.join(base_path, 'results_code_testing')
    os.makedirs(results_dir, exist_ok=True)

    for v in variants:
        print(f"\n🔧 Running tests for variant: {v}")

        env = os.environ.copy()
        env["FEATURE_VARIANT"] = v

        result_csv = os.path.join(results_dir, f"results_{v}.csv")

        result = subprocess.run([
            sys.executable,
            "-m",
            "pytest",
            test_dir,
            "--csv", result_csv
        ], env=env)

        if result.returncode == 0:
            print(f"✅ Tests for '{v}' completed successfully. Results saved to {result_csv}")
        else:
            print(f"⚠️ Some tests for '{v}' may have failed. Check {result_csv}")

@run.command()
def amoeba():
    """Runs the AMOEBA experiment."""
    click.echo("Running AMOEBA experiment...")
    results = run_amoeba_benchmark()
    if results:
        for pair, res in results.items():
            click.echo(f"\nResults for pair: {pair}")
            for q, t in res.items():
                if q != 'slower':
                    click.echo(f"  {q}: {t:.4f}s")
            click.echo(f"  Slower query: {res['slower']}")

@run.command(name='spl-db-sync')
@click.option('--benchmark', type=click.Choice(['flat', 'modular']), default='flat', help='The benchmark to run.')
def spl_db_sync(benchmark):
    """Runs the SPL-DB-Sync experiment."""
    click.echo(f"Running SPL-DB-Sync {benchmark} benchmark...")
    results = run_spl_db_sync_benchmark(benchmark)
    if results:
        click.echo(f"\nResults for {benchmark} benchmark:")
        for query, t in results.items():
            click.echo(f"  {query}: {t:.4f}s")

@run.command(name='all')
@click.pass_context
def run_all(ctx):
    """Runs all experiments sequentially."""
    click.secho("🚀 Starting all experiments...", fg="green")

    # 1. Setup and run AMOEBA
    click.secho("\n--- Running AMOEBA ---", fg="cyan")
    ctx.invoke(setup_amoeba)
    ctx.invoke(amoeba)

    # 2. Setup and run SPL-DB-Sync
    click.secho("\n--- Running SPL-DB-Sync ---", fg="cyan")
    ctx.invoke(setup_spl_db_sync)
    ctx.invoke(spl_db_sync, benchmark='flat')
    ctx.invoke(spl_db_sync, benchmark='modular')

    # 3. Run Code Testing
    click.secho("\n--- Running Code Testing ---", fg="cyan")
    ctx.invoke(code_testing, variant='all')
    
    click.secho("\n✅ All experiments completed!", fg="green")

@cli.group()
def setup_db():
    """Setup databases for experiments."""
    pass

def execute_sql_file(filepath):
    """Executes a SQL file."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        with open(filepath, 'r') as f:
            # Split commands by semicolon, filter out empty ones
            sql_commands = [cmd.strip() for cmd in f.read().split(';') if cmd.strip()]
            for command in sql_commands:
                cursor.execute(command)
        conn.commit()
        cursor.close()
        conn.close()
        click.echo(f"Successfully executed {filepath}")
    except mysql.connector.Error as err:
        click.echo(f"Error executing {filepath}: {err}")

@setup_db.command(name="amoeba")
def setup_amoeba():
    """Sets up the database for the AMOEBA experiment."""
    click.echo("Setting up database for AMOEBA")
    setup_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'AMOEBA', 'setup.sql')
    execute_sql_file(setup_file)

@setup_db.command(name='spl-db-sync')
def setup_spl_db_sync():
    """Sets up the database for the SPL-DB-Sync experiment."""
    click.echo("Setting up database for SPL-DB-Sync")
    setup_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'SPL-DB-Sync', 'setup.sql')
    execute_sql_file(setup_file)


if __name__ == '__main__':
    cli() 