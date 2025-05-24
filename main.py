import subprocess
import os

variants = ['loyalty', 'newsletter', 'full']
base_path = os.path.dirname(os.path.abspath(__file__))
test_dir = os.path.join(base_path, 'code_testing')
results_dir = os.path.join(base_path, 'results_code_testing')
os.makedirs(results_dir, exist_ok=True)
for variant in variants:
    print(f"\n🔧 Running tests for variant: {variant}")

    env = os.environ.copy()
    env["FEATURE_VARIANT"] = variant

    result_csv = os.path.join(results_dir, f"results_{variant}.csv")

    result = subprocess.run([
        "pytest",
        test_dir,
        "--csv", result_csv
    ], env=env)

    if result.returncode == 0:
        print(f"✅ Tests for '{variant}' completed successfully. Results saved to {result_csv}")
    else:
        print(f"⚠️ Some tests for '{variant}' may have failed. Check {result_csv}")
