#!/usr/bin/env python3
"""
Bakerydemo Maintainer Script
============================
A single script that runs all maintenance checks for the
wagtail/bakerydemo repository.

Usage:
    python scripts/maintain.py                    # run all checks
    python scripts/maintain.py --check upgrades   # check for available upgrades
    python scripts/maintain.py --check security   # audit security vulnerabilities
    python scripts/maintain.py --check ci         # replicate CI checks locally
    python scripts/maintain.py --check deprecations  # find deprecated API usage

Must be run from the root of a cloned wagtail/bakerydemo repository.
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path


GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"


def header(text):
    print(f"\n{BOLD}{BLUE}{'=' * 50}{RESET}")
    print(f"{BOLD}{BLUE}{text}{RESET}")
    print(f"{BOLD}{BLUE}{'=' * 50}{RESET}\n")


def success(text):
    print(f"{GREEN}PASSED{RESET}  {text}")


def failure(text):
    print(f"{RED}FAILED{RESET}  {text}")


def warning(text):
    print(f"{YELLOW}WARNING{RESET} {text}")


def info(text):
    print(f"{BLUE}INFO{RESET}    {text}")


def run_command(command, capture=True):
    result = subprocess.run(
        command,
        capture_output=capture,
        text=True,
        cwd=Path.cwd()
    )
    return result


def check_project_root():
    """Confirm we are running from the bakerydemo project root."""
    required = ["manage.py", "requirements", "bakerydemo"]
    missing = [r for r in required if not Path(r).exists()]
    if missing:
        print(f"{RED}Error: This script must be run from the root of a")
        print(f"cloned wagtail/bakerydemo repository.{RESET}")
        print(f"Missing: {', '.join(missing)}")
        sys.exit(1)


def check_upgrades():
    """Check for available Wagtail and Django version upgrades."""
    header("Upgrade Check")

    packages = {
        "wagtail": "https://docs.wagtail.org/en/latest/releases/index.html",
        "Django": "https://docs.djangoproject.com/en/stable/releases/",
    }

    all_current = True

    for package, release_notes in packages.items():
        installed_result = run_command(
            [sys.executable, "-m", "pip", "show", package]
        )
        installed_version = None
        for line in installed_result.stdout.splitlines():
            if line.startswith("Version:"):
                installed_version = line.split(":")[1].strip()
                break

        latest_result = run_command(
            [sys.executable, "-m", "pip", "index", "versions", package]
        )
        latest_version = None
        if latest_result.returncode == 0 and latest_result.stdout:
            first_line = latest_result.stdout.splitlines()[0]
            try:
                versions_str = first_line.split("(")[1].rstrip(")")
                versions = [v.strip() for v in versions_str.split(",")]
                latest_version = versions[0] if versions else None
            except (IndexError, AttributeError):
                latest_version = None

        if installed_version and latest_version:
            if installed_version == latest_version:
                success(f"{package}: {installed_version} — up to date")
            else:
                warning(
                    f"{package}: {installed_version} installed, "
                    f"{latest_version} available"
                )
                print(f"         Release notes: {release_notes}")
                print(f"         To upgrade: update requirements/base.txt")
                print(
                    f"         Then run: pip install -r requirements/development.txt"
                )
                print(f"         Then run: python manage.py migrate && python manage.py test\n")
                all_current = False
        else:
            warning(f"{package}: could not determine current or latest version")

    if all_current:
        print(f"\n{GREEN}All packages are up to date.{RESET}")
    else:
        print(
            f"\n{YELLOW}Upgrades available. Review release notes for breaking "
            f"changes before upgrading.{RESET}"
        )

    return all_current


def check_security():
    """Audit all dependencies for known security vulnerabilities."""
    header("Security Audit")

    pip_audit_check = run_command(
        [sys.executable, "-m", "pip", "show", "pip-audit"]
    )
    if pip_audit_check.returncode != 0:
        info("pip-audit not installed. Installing...")
        install_result = run_command(
            [sys.executable, "-m", "pip", "install", "pip-audit"],
            capture=False
        )
        if install_result.returncode != 0:
            failure("Could not install pip-audit. Install it manually: pip install pip-audit")
            return False

    req_files = [
        "requirements/base.txt",
        "requirements/production.txt",
    ]

    all_clean = True

    for req_file in req_files:
        if not Path(req_file).exists():
            warning(f"{req_file} not found — skipping")
            continue

        print(f"Auditing {req_file}...")
        result = run_command(
            [sys.executable, "-m", "pip_audit", "-r", req_file, "--format", "columns"]
        )

        if result.returncode == 0:
            success(f"No vulnerabilities found in {req_file}")
        else:
            failure(f"Vulnerabilities found in {req_file}")
            print(result.stdout)
            print(f"\n{YELLOW}Action required:{RESET}")
            print("  1. Identify the fixed version from the advisory")
            print("  2. Update the version pin in the requirements file")
            print("  3. Run: pip install -r requirements/development.txt")
            print("  4. Run: python manage.py test")
            print("  5. Submit a PR titled: Security: upgrade [package] to X.Y.Z")
            print("  6. Reference the CVE number in the PR description\n")
            all_clean = False

    if all_clean:
        print(f"\n{GREEN}No security vulnerabilities found.{RESET}")
    else:
        print(f"\n{RED}Security vulnerabilities detected. Fix immediately.{RESET}")

    return all_clean


def check_ci():
    """Replicate the CI pipeline checks locally."""
    header("CI Health Check")

    checks = [
        {
            "name": "Django system check",
            "command": [sys.executable, "manage.py", "check"],
            "fix": "Review the error output and fix the reported issues.",
        },
        {
            "name": "Missing migrations check",
            "command": [sys.executable, "manage.py", "makemigrations", "--check"],
            "fix": "Run: python manage.py makemigrations && python manage.py migrate",
        },
        {
            "name": "Full test suite",
            "command": [sys.executable, "manage.py", "test"],
            "fix": "Review failing tests and fix the underlying code.",
        },
    ]

    results = []

    for check in checks:
        result = run_command(check["command"])
        if result.returncode == 0:
            success(check["name"])
            results.append(True)
        else:
            failure(check["name"])
            if result.stdout:
                print(f"  Output: {result.stdout[:300]}")
            if result.stderr:
                print(f"  Error:  {result.stderr[:300]}")
            print(f"  Fix:    {check['fix']}\n")
            results.append(False)

    passed = sum(results)
    total = len(results)

    print(f"\n{BOLD}CI Results: {passed}/{total} checks passed{RESET}")

    if passed == total:
        print(f"{GREEN}All CI checks passed. Safe to push.{RESET}")
    else:
        print(f"{RED}Some checks failed. Fix before pushing to avoid CI failures.{RESET}")

    return passed == total


def check_deprecations():
    """Check for deprecated Wagtail and Django API usage."""
    header("Deprecation Check")

    print("Running tests with deprecation warnings as errors...")
    print("This catches any deprecated API usage that will break in future releases.\n")

    result = run_command([
        sys.executable,
        "-W", "error::DeprecationWarning",
        "-W", "error::PendingDeprecationWarning",
        "manage.py", "test"
    ])

    if result.returncode == 0:
        success("No deprecation warnings found")
        print(
            f"\n{GREEN}Codebase is clean of deprecated API usage.{RESET}"
        )
        return True
    else:
        failure("Deprecation warnings found")
        print(result.stderr[:1000] if result.stderr else result.stdout[:1000])
        print(f"\n{YELLOW}Action required:{RESET}")
        print("  Review the deprecation warnings above.")
        print("  Update the affected code to use the current API.")
        print("  Check the relevant release notes for migration guidance:")
        print("  https://docs.wagtail.org/en/latest/releases/index.html")
        print("  https://docs.djangoproject.com/en/stable/releases/\n")
        return False


def run_all():
    """Run all maintenance checks."""
    header("Bakerydemo Full Maintenance Check")
    print("Running all checks. This may take a few minutes.\n")

    results = {
        "Upgrade check": check_upgrades(),
        "Security audit": check_security(),
        "CI health check": check_ci(),
        "Deprecation check": check_deprecations(),
    }

    header("Summary")

    for check_name, passed in results.items():
        if passed:
            success(check_name)
        else:
            failure(check_name)

    passed_count = sum(results.values())
    total_count = len(results)

    print(f"\n{BOLD}{passed_count}/{total_count} checks passed{RESET}")

    if passed_count == total_count:
        print(f"{GREEN}All maintenance checks passed. Project is healthy.{RESET}\n")
    else:
        failed = [name for name, passed in results.items() if not passed]
        print(f"{RED}Issues found in: {', '.join(failed)}{RESET}")
        print("Review the output above for details and fix instructions.\n")


def main():
    parser = argparse.ArgumentParser(
        description="Bakerydemo maintainer script. Runs all maintenance checks.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/maintain.py                       Run all checks
  python scripts/maintain.py --check upgrades      Check for available upgrades
  python scripts/maintain.py --check security      Audit security vulnerabilities
  python scripts/maintain.py --check ci            Replicate CI checks locally
  python scripts/maintain.py --check deprecations  Find deprecated API usage
        """
    )
    parser.add_argument(
        "--check",
        choices=["upgrades", "security", "ci", "deprecations"],
        help="Run a specific check instead of all checks",
    )

    args = parser.parse_args()
    check_project_root()

    if args.check == "upgrades":
        check_upgrades()
    elif args.check == "security":
        check_security()
    elif args.check == "ci":
        check_ci()
    elif args.check == "deprecations":
        check_deprecations()
    else:
        run_all()


if __name__ == "__main__":
    main()
