#!/usr/bin/env python3
"""
Import uncovered tests from Testmo
Creates uncovered_tests.json with tests that are in Testmo but not automated

Format of input file (one test per line):
testmo_id,test_name

Example:
12345,test_guest_checkout
12346,test_payment_cod
"""
import json
import sys
from pathlib import Path

def import_uncovered_tests(platform, file_path):
    """Import uncovered tests from a CSV file"""
    uncovered_path = Path("uncovered_tests.json")
    
    # Load existing data
    if uncovered_path.exists():
        data = json.loads(uncovered_path.read_text())
    else:
        data = {'web_uae': [], 'web_ksa': [], 'app': []}
    
    # Read input file
    with open(file_path, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    tests = []
    for line in lines:
        if ',' in line:
            testmo_id, name = line.split(',', 1)
            tests.append({'testmo_id': testmo_id.strip(), 'name': name.strip()})
        else:
            # If no comma, treat as test name only
            tests.append({'testmo_id': '', 'name': line.strip()})
    
    data[platform] = tests
    
    # Save
    uncovered_path.write_text(json.dumps(data, indent=2))
    print(f"✅ Imported {len(tests)} uncovered tests for {platform}")
    print(f"   Saved to: {uncovered_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        print("\nUsage: python3 import_testmo_tests.py <platform> <file>")
        print("Platforms: web_uae, web_ksa, app")
        print("\nExample:")
        print("  python3 import_testmo_tests.py web_uae testmo_uae_uncovered.txt")
        sys.exit(1)
    
    platform = sys.argv[1]
    file_path = sys.argv[2]
    
    if platform not in ['web_uae', 'web_ksa', 'app']:
        print(f"❌ Invalid platform: {platform}")
        print("Valid platforms: web_uae, web_ksa, app")
        sys.exit(1)
    
    if not Path(file_path).exists():
        print(f"❌ File not found: {file_path}")
        sys.exit(1)
    
    import_uncovered_tests(platform, file_path)
    print("\nNow run: python3 generate_coverage_report.py")
