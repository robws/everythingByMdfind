"""Python environment diagnostic script"""
import sys
import os
from pathlib import Path


def diagnose_environment():
    """Analyze environment and return diagnosis"""
    script_project_root = Path(__file__).resolve().parent.parent
    expected_venv = script_project_root / ".venv"
    actual_venv = Path(sys.prefix)
    pythonpath = os.environ.get('PYTHONPATH')
    
    issues = []
    
    # Check interpreter mismatch
    if expected_venv.exists() and expected_venv.resolve() != actual_venv.resolve():
        issues.append(
            f"WRONG INTERPRETER: Script is in '{script_project_root.name}/' "
            f"but using '{actual_venv.parent.name}/.venv'\n"
            f"  → Fix: Add '{script_project_root.name}' to workspace file, "
            f"then select its .venv as interpreter"
        )
    
    # Check if project's venv packages are in sys.path
    if expected_venv.exists():
        # Find site-packages directory in expected venv
        expected_site_packages = None
        for item in expected_venv.glob("lib/python*/site-packages"):
            expected_site_packages = item
            break
        
        if expected_site_packages:
            site_packages_str = str(expected_site_packages)
            if not any(site_packages_str in p for p in sys.path):
                issues.append(
                    f"PROJECT PACKAGES NOT IMPORTABLE: '{script_project_root.name}/.venv' "
                    f"site-packages not in sys.path\n"
                    f"  → Project's installed packages won't be found"
                )
    
    # Check cwd mismatch
    current_cwd = Path(os.getcwd()).resolve()
    if current_cwd != script_project_root:
        issues.append(
            f"WRONG CWD: Running from '{current_cwd.name}/' "
            f"but script is in '{script_project_root.name}/'\n"
            f"  → Relative imports and file operations may fail"
        )
    
    return issues


print("=" * 70)
print("PYTHON ENVIRONMENT DIAGNOSTICS")
print("=" * 70)

# Show diagnosis first
issues = diagnose_environment()
if issues:
    print("\n⚠️  ISSUES DETECTED:")
    for i, issue in enumerate(issues, 1):
        print(f"\n{i}. {issue}")
    print("\n" + "-" * 70)
else:
    print("\n✓ No issues detected - environment looks correct")
    print("-" * 70)

print("\n--- INTERPRETER ---")
print(f"Executable: {sys.executable}")
print(f"Version: {sys.version}")

print("\n--- EXECUTION CONTEXT ---")
print(f"Script: {Path(__file__).resolve()}")
print(f"CWD: {os.getcwd()}")

print("\n--- VIRTUAL ENVIRONMENT ---")
venv = os.environ.get('VIRTUAL_ENV')
print(f"VIRTUAL_ENV: {venv if venv else '(not set)'}")

print("\n--- ENVIRONMENT VARIABLES ---")
pythonpath = os.environ.get('PYTHONPATH')
print(f"PYTHONPATH: {pythonpath if pythonpath else '(not set)'}")

print("\n--- sys.path (relevant module search paths) ---")
for i, path in enumerate(sys.path):
    # Filter out standard library paths - they're always there
    if any(x in path for x in ['python311.zip', 'lib/python3.11', 'lib-dynload']):
        continue
    # Show script directory and site-packages
    print(f"  {i}: {path}")
print("\n" + "=" * 70)
