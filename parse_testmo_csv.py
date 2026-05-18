#!/usr/bin/env python3
"""Parse TestMO CSV export into structured JSON."""
import csv
import json
import re
import sys
from pathlib import Path

def strip_html(text):
    """Remove HTML tags and decode entities."""
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', ' ', text)
    text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&#39;', "'")
    return re.sub(r'\s+', ' ', text).strip()

def parse_csv(csv_path):
    tests = []
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            tests.append({
                "case_id": row["Case ID"].strip(),
                "test_id": row["Test ID"].strip(),
                "name": row["Test"].strip(),
                "folder": row["Folder"].strip(),
                "functionality": row.get("Functionality", "").strip(),
                "priority": row["Priority"].strip(),
                "status": row["Status"].strip(),
                "summary": strip_html(row.get("Summary", "")),
                "tags": row.get("Tags", "").strip(),
            })
    return tests

if __name__ == "__main__":
    csv_path = sys.argv[1] if len(sys.argv) > 1 else str(Path.home() / "Downloads/testmo-export-run-2154.csv")
    tests = parse_csv(csv_path)
    output = Path(__file__).parent / "testmo_tests.json"
    output.write_text(json.dumps(tests, indent=2))
    print(f"✅ Parsed {len(tests)} TestMO tests → {output}")
