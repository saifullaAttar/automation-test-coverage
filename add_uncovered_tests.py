#!/usr/bin/env python3
"""
Add uncovered tests from Testmo to the coverage report
Usage: python3 add_uncovered_tests.py <platform> <test_name1> <test_name2> ...
       python3 add_uncovered_tests.py --file <platform> <file.txt>

Platforms: web_uae, web_ksa, android, ios

Example:
  python3 add_uncovered_tests.py web_uae "test_guest_checkout" "test_payment_cod"
  python3 add_uncovered_tests.py --file android uncovered_android.txt
"""
import sys
import json
from pathlib import Path

def load_coverage_data():
    json_path = Path("coverage_data.json")
    if json_path.exists():
        return json.loads(json_path.read_text())
    return None

def save_and_regenerate(uncovered_tests):
    # Update the generate script with uncovered tests
    script_path = Path("generate_coverage_report.py")
    content = script_path.read_text()
    
    # Format the uncovered tests dict
    uncovered_str = json.dumps(uncovered_tests, indent=4)
    
    # Replace the placeholder
    import re
    pattern = r"uncovered_tests = \{[^}]*\}"
    replacement = f"uncovered_tests = {uncovered_str}"
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    script_path.write_text(content)
    
    print("✅ Updated uncovered tests in generate_coverage_report.py")
    print("Now run: python3 generate_coverage_report.py")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    
    # Load existing data
    data = load_coverage_data()
    if not data:
        print("❌ No coverage data found. Run generate_coverage_report.py first.")
        sys.exit(1)
    
    uncovered = data.get('uncovered_tests', {})
    
    # Check if reading from file
    if sys.argv[1] == '--file':
        platform = sys.argv[2]
        file_path = Path(sys.argv[3])
        
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            sys.exit(1)
        
        tests = [line.strip() for line in file_path.read_text().splitlines() if line.strip()]
    else:
        platform = sys.argv[1]
        tests = sys.argv[2:]
    
    if platform not in ['web_uae', 'web_ksa', 'android', 'ios']:
        print(f"❌ Invalid platform: {platform}")
        print("Valid platforms: web_uae, web_ksa, android, ios")
        sys.exit(1)
    
    # Add tests
    if platform not in uncovered:
        uncovered[platform] = []
    
    uncovered[platform].extend(tests)
    uncovered[platform] = list(set(uncovered[platform]))  # Remove duplicates
    
    print(f"✅ Added {len(tests)} uncovered tests to {platform}")
    print(f"Total uncovered for {platform}: {len(uncovered[platform])}")
    
    save_and_regenerate(uncovered)
