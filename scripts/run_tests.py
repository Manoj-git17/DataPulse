"""
DataPulse - Automated Test Suite Runner.
Executes all Python unit/integration tests and frontend build checks.
Returns standard exit code (0 = success, 1 = failure) for local work and CI/CD pipelines.
"""

import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent


def run_pytest() -> bool:
    print("\n" + "=" * 65)
    print("STEP 1: RUNNING BACKEND, ETL, DATABASE & API TESTS (PYTEST)")
    print("=" * 65)

    python_executable = ROOT_DIR / ".venv" / "Scripts" / "python.exe"
    if not python_executable.exists():
        python_executable = sys.executable

    cmd = [str(python_executable), "-m", "pytest", "-v"]
    res = subprocess.run(cmd, cwd=str(ROOT_DIR))
    return res.returncode == 0


def run_frontend_build_check() -> bool:
    print("\n" + "=" * 65)
    print("STEP 2: RUNNING FRONTEND PRODUCTION BUILD CHECK (VITE)")
    print("=" * 65)

    frontend_dir = ROOT_DIR / "frontend"
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"

    res = subprocess.run([npm_cmd, "run", "build"], cwd=str(frontend_dir))
    return res.returncode == 0


def main():
    print("*" * 65)
    print("DATAPULSE COMPREHENSIVE QUALITY ASSURANCE RUNNER")
    print("*" * 65)

    pytest_ok = run_pytest()
    frontend_ok = run_frontend_build_check()

    print("\n" + "=" * 65)
    print("SUMMARY")
    print("=" * 65)
    print(f"Backend & ETL Tests : {' PASSED' if pytest_ok else '❌ FAILED'}")
    print(f"Frontend Build      : {' PASSED' if frontend_ok else '❌ FAILED'}")
    print("=" * 65)

    if pytest_ok and frontend_ok:
        print("\n ALL SYSTEMS NOMINAL: PROJECT READY FOR PORTFOLIO & DEPLOYMENT!\n")
        sys.exit(0)
    else:
        print("\n❌ QUALITY ASSURANCE CHECKS FAILED.\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
