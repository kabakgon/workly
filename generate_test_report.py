#!/usr/bin/env python
"""
Script to generate test reports for Workly 2.0.

Usage:
    python generate_test_report.py [--html] [--xml] [--text]
    
Options:
    --html    Generate HTML coverage report (default)
    --xml     Generate XML coverage report
    --text    Generate text coverage report
    --all     Generate all report types
"""

import os
import sys
import subprocess
import argparse

def run_command(command, description):
    """Run a shell command and return success status."""
    print(f"\n{'='*60}")
    print(f"📊 {description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=False,
            text=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        return False

def check_coverage_installed():
    """Check if coverage is installed."""
    try:
        import coverage
        return True
    except ImportError:
        print("⚠️  Coverage is not installed. Installing...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "coverage"], check=True)
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install coverage. Please install manually: pip install coverage")
            return False

def main():
    parser = argparse.ArgumentParser(description='Generate test reports for Workly 2.0')
    parser.add_argument('--html', action='store_true', help='Generate HTML coverage report')
    parser.add_argument('--xml', action='store_true', help='Generate XML coverage report')
    parser.add_argument('--text', action='store_true', help='Generate text coverage report')
    parser.add_argument('--all', action='store_true', help='Generate all report types')
    parser.add_argument('--verbosity', type=int, default=2, help='Test verbosity level (0-2)')
    
    args = parser.parse_args()
    
    # If no options specified, default to HTML
    if not (args.html or args.xml or args.text or args.all):
        args.html = True
    
    if args.all:
        args.html = True
        args.xml = True
        args.text = True
    
    # Check if coverage is installed
    if not check_coverage_installed():
        return 1
    
    # Run tests with coverage
    print("\n" + "="*60)
    print("🧪 Running tests with coverage...")
    print("="*60)
    
    coverage_cmd = f"coverage run --source='.' manage.py test --verbosity={args.verbosity}"
    if not run_command(coverage_cmd, "Running tests with coverage"):
        return 1
    
    # Generate reports
    success = True
    
    if args.text:
        if not run_command("coverage report", "Generating text coverage report"):
            success = False
    
    if args.xml:
        if not run_command("coverage xml", "Generating XML coverage report"):
            success = False
        else:
            print("\n✅ XML report generated: coverage.xml")
    
    if args.html:
        if not run_command("coverage html", "Generating HTML coverage report"):
            success = False
        else:
            html_path = os.path.join("htmlcov", "index.html")
            print(f"\n✅ HTML report generated: {html_path}")
            print(f"📂 Open in browser: file://{os.path.abspath(html_path)}")
    
    if success:
        print("\n" + "="*60)
        print("✨ All reports generated successfully!")
        print("="*60)
        return 0
    else:
        print("\n" + "="*60)
        print("⚠️  Some reports failed to generate")
        print("="*60)
        return 1

if __name__ == "__main__":
    sys.exit(main())

