#!/usr/bin/env python3
"""Extract automated test inventory from automation_web_2.0 repo."""
import ast
import json
import re
import sys
from pathlib import Path

def extract_tests_from_file(filepath):
    """Extract test functions with metadata from a Python test file."""
    source = filepath.read_text()
    tests = []
    
    # Find all test functions with their decorators and docstrings
    # Use regex to find decorator blocks + function defs
    pattern = re.compile(
        r'((?:@[^\n]+\n)*)'  # decorators
        r'def (test_\w+)\([^)]*\):\s*\n'  # function def
        r'(?:\s*"""(.*?)""")?',  # optional docstring
        re.DOTALL
    )
    
    for match in pattern.finditer(source):
        decorators_block, func_name, docstring = match.groups()
        
        # Extract allure metadata from decorators
        title = ""
        tags = []
        feature = ""
        
        title_match = re.search(r'@allure\.title\(["\'](.+?)["\']\)', decorators_block)
        if title_match:
            title = title_match.group(1)
        
        for tag_match in re.finditer(r'@allure\.tag\((.+?)\)', decorators_block):
            raw = tag_match.group(1)
            tags.extend([t.strip().strip('"\'') for t in raw.split(',')])
        
        feature_match = re.search(r'@allure\.feature\(["\'](.+?)["\']\)', decorators_block)
        if feature_match:
            feature = feature_match.group(1)
        
        # Clean docstring
        doc = ""
        if docstring:
            doc = re.sub(r'\s+', ' ', docstring).strip()
        
        tests.append({
            "name": func_name,
            "file": filepath.name,
            "title": title,
            "tags": tags,
            "feature": feature,
            "docstring": doc[:200] if doc else "",
        })
    
    return tests

def scan_platform(base_path, rel_dir):
    """Scan a platform directory for test files."""
    full_path = base_path / rel_dir
    if not full_path.exists():
        print(f"⚠️  {full_path} not found")
        return []
    
    all_tests = []
    for f in sorted(full_path.rglob("test_*.py")):
        all_tests.extend(extract_tests_from_file(f))
    return all_tests

if __name__ == "__main__":
    repo = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "automation_web_2.0"
    
    result = {
        "web_uae": scan_platform(repo, "tests/web/UAE"),
        "web_ksa": scan_platform(repo, "tests/web/KSA"),
        "app": scan_platform(repo, "tests/app"),
    }
    
    output = Path(__file__).parent / "automated_tests.json"
    output.write_text(json.dumps(result, indent=2))
    
    print(f"✅ Extracted: UAE={len(result['web_uae'])}, KSA={len(result['web_ksa'])}, App={len(result['app'])}")
    print(f"   Total: {sum(len(v) for v in result.values())} → {output}")
