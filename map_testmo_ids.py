#!/usr/bin/env python3
"""
Map Testmo IDs to automated tests
Creates/updates testmo_mapping.json

Format of input file (one mapping per line):
test_name,testmo_id

Example:
test_uae_checkout_cc_no_coupon,12345
test_uae_checkout_cod_no_coupon,12346
"""
import json
import sys
from pathlib import Path

def map_testmo_ids(platform, file_path):
    """Map Testmo IDs to automated test names"""
    mapping_path = Path("testmo_mapping.json")
    
    # Load existing data
    if mapping_path.exists():
        data = json.loads(mapping_path.read_text())
    else:
        data = {'web_uae': {}, 'web_ksa': {}, 'app': {}}
    
    # Read input file
    with open(file_path, 'r') as f:
        lines = [line.strip() for line in f if line.strip() and ',' in line]
    
    count = 0
    for line in lines:
        test_name, testmo_id = line.split(',', 1)
        data[platform][test_name.strip()] = testmo_id.strip()
        count += 1
    
    # Save
    mapping_path.write_text(json.dumps(data, indent=2))
    print(f"✅ Mapped {count} tests to Testmo IDs for {platform}")
    print(f"   Saved to: {mapping_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        print("\nUsage: python3 map_testmo_ids.py <platform> <file>")
        print("Platforms: web_uae, web_ksa, app")
        print("\nExample:")
        print("  python3 map_testmo_ids.py web_uae testmo_uae_mapping.txt")
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
    
    map_testmo_ids(platform, file_path)
    print("\nNow run: python3 generate_coverage_report.py")
