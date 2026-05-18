#!/usr/bin/env python3
"""
Generate Automation Test Coverage Report for GitHub Pages
"""
import json
import re
from pathlib import Path
from datetime import datetime

def count_tests_by_category(directory):
    """Count tests and categorize them with full details"""
    automation_path = Path("../automation_web_2.0") / directory
    if not automation_path.exists():
        print(f"⚠️  Warning: {automation_path} not found. Make sure automation_web_2.0 is cloned next to this repo.")
        return {}, []
    
    test_files = list(automation_path.rglob("test_*.py"))
    categories = {}
    all_tests = []
    
    for file in test_files:
        with open(file, 'r') as f:
            content = f.read()
            tests = re.findall(r'^\s*def (test_\w+)', content, re.MULTILINE)
            
            # Categorize by file name
            file_name = file.stem
            category = file_name.replace('test_', '').replace('_', ' ').title()
            
            if category not in categories:
                categories[category] = []
            
            for test in tests:
                test_info = {
                    'name': test,
                    'file': file.name,
                    'category': category,
                    'path': str(file.relative_to(automation_path))
                }
                categories[category].append(test_info)
                all_tests.append(test_info)
    
    return categories, all_tests

def separate_app_tests(app_tests):
    """Separate app tests into Android and iOS"""
    android_tests = {}
    ios_tests = {}
    
    for category, tests in app_tests.items():
        android_tests[category] = []
        ios_tests[category] = []
        
        for test in tests:
            # Check test name or file for platform indicators
            test_name = test['name'].lower()
            if 'android' in test_name:
                android_tests[category].append(test)
            elif 'ios' in test_name:
                ios_tests[category].append(test)
            else:
                # If no specific platform, add to both
                android_tests[category].append(test)
                ios_tests[category].append(test)
    
    return android_tests, ios_tests

# Collect test data
web_uae, web_uae_list = count_tests_by_category("tests/web/UAE")
web_ksa, web_ksa_list = count_tests_by_category("tests/web/KSA")
app_tests, app_list = count_tests_by_category("tests/app")

# Calculate totals
web_uae_total = len(web_uae_list)
web_ksa_total = len(web_ksa_list)
app_total = len(app_list)
grand_total = web_uae_total + web_ksa_total + app_total

# Testmo regression suite totals (manual input based on regression suites)
testmo_web_uae_total = 75  # Placeholder - update from Testmo
testmo_web_ksa_total = 75  # Placeholder - update from Testmo
testmo_app_total = 80      # Placeholder - update from Testmo (Android + iOS combined)

testmo_web_total = testmo_web_uae_total + testmo_web_ksa_total
testmo_total = testmo_web_total + testmo_app_total

# Calculate coverage percentages
web_uae_coverage = round(web_uae_total / testmo_web_uae_total * 100, 1) if testmo_web_uae_total > 0 else 0
web_ksa_coverage = round(web_ksa_total / testmo_web_ksa_total * 100, 1) if testmo_web_ksa_total > 0 else 0
app_coverage = round(app_total / testmo_app_total * 100, 1) if testmo_app_total > 0 else 0
web_coverage = round((web_uae_total + web_ksa_total) / testmo_web_total * 100, 1) if testmo_web_total > 0 else 0
overall_coverage = round(grand_total / testmo_total * 100, 1)

# Load Testmo mapping if exists
testmo_mapping_path = Path("testmo_mapping.json")
if testmo_mapping_path.exists():
    testmo_mapping = json.loads(testmo_mapping_path.read_text())
else:
    testmo_mapping = {
        'web_uae': {},
        'web_ksa': {},
        'app': {}
    }

# Generate test lists for JSON export with Testmo IDs
covered_tests = {
    'web_uae': [{'name': t['name'], 'file': t['file'], 'testmo_id': testmo_mapping.get('web_uae', {}).get(t['name'], '')} for t in web_uae_list],
    'web_ksa': [{'name': t['name'], 'file': t['file'], 'testmo_id': testmo_mapping.get('web_ksa', {}).get(t['name'], '')} for t in web_ksa_list],
    'app': [{'name': t['name'], 'file': t['file'], 'testmo_id': testmo_mapping.get('app', {}).get(t['name'], '')} for t in app_list]
}

# Load uncovered tests from file
uncovered_path = Path("uncovered_tests.json")
if uncovered_path.exists():
    uncovered_tests = json.loads(uncovered_path.read_text())
else:
    uncovered_tests = {
        'web_uae': [],
        'web_ksa': [],
        'app': []
    }

# Generate HTML report
html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mumzworld Automation Test Coverage</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}
        .container {{ 
            max-width: 1400px; 
            margin: 0 auto; 
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .header p {{ font-size: 1.1em; opacity: 0.9; }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 40px;
            background: #f8f9fa;
        }}
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s;
        }}
        .stat-card:hover {{ transform: translateY(-5px); }}
        .stat-number {{ 
            font-size: 2.5em; 
            font-weight: bold; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        .stat-label {{ 
            font-size: 1em; 
            color: #666; 
            margin-top: 10px;
        }}
        .coverage-section {{
            padding: 40px;
        }}
        .coverage-header {{
            font-size: 2em;
            margin-bottom: 30px;
            color: #333;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}
        .progress-bar {{
            background: #e0e0e0;
            border-radius: 50px;
            height: 40px;
            margin: 20px 0;
            overflow: hidden;
            position: relative;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            border-radius: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            transition: width 1s ease;
        }}
        .test-list {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            max-height: 400px;
            overflow-y: auto;
        }}
        .test-item {{
            padding: 10px;
            margin: 5px 0;
            background: white;
            border-radius: 4px;
            border-left: 3px solid #667eea;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }}
        .uncovered-item {{
            border-left-color: #e74c3c;
        }}
        .section-tabs {{
            display: flex;
            gap: 10px;
            margin: 20px 0;
            flex-wrap: wrap;
        }}
        .tab-btn {{
            padding: 10px 20px;
            background: #e0e0e0;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s;
        }}
        .tab-btn.active {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        .tab-content {{
            display: none;
        }}
        .tab-content.active {{
            display: block;
        }}
        .footer {{
            background: #2d3748;
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .footer a {{
            color: #667eea;
            text-decoration: none;
        }}
        .timestamp {{
            color: #a0aec0;
            font-size: 0.9em;
            margin-top: 10px;
        }}
        .split-view {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 20px 0;
        }}
        .covered-section {{
            background: #d4edda;
            padding: 20px;
            border-radius: 8px;
        }}
        .uncovered-section {{
            background: #f8d7da;
            padding: 20px;
            border-radius: 8px;
        }}
        @media (max-width: 768px) {{
            .split-view {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 Mumzworld Automation Test Coverage</h1>
            <p>Repository: mumzworld-tech/automation_web_2.0</p>
            <p>Framework: Python + Selenium + Appium + Pytest + Allure</p>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{grand_total}</div>
                <div class="stat-label">Total Automated</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{web_uae_total}</div>
                <div class="stat-label">Web UAE</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{web_ksa_total}</div>
                <div class="stat-label">Web KSA</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{app_total}</div>
                <div class="stat-label">Mobile App</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{overall_coverage}%</div>
                <div class="stat-label">Overall Coverage</div>
            </div>
        </div>

        <div class="coverage-section">
            <h2 class="coverage-header">🌐 Web UAE Automation</h2>
            <p><strong>Automated:</strong> {web_uae_total} | <strong>Total in Testmo:</strong> {testmo_web_uae_total} | <strong>Coverage:</strong> {web_uae_coverage}%</p>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {web_uae_coverage}%">{web_uae_coverage}%</div>
            </div>
            
            <div class="section-tabs">
                <button class="tab-btn active" onclick="showTab('uae-covered')">✅ Covered Tests ({web_uae_total})</button>
                <button class="tab-btn" onclick="showTab('uae-uncovered')">❌ Not Covered ({len(uncovered_tests.get('web_uae', []))})</button>
            </div>
            
            <div id="uae-covered" class="tab-content active">
                <div class="test-list">
                    {''.join(f'<div class="test-item">✅ {t["name"]} <span style="color:#999">({t["file"]})</span>' + (f' <span style="color:#667eea">Testmo: {t["testmo_id"]}</span>' if t.get("testmo_id") else '') + '</div>' for t in covered_tests['web_uae'])}
                </div>
            </div>
            
            <div id="uae-uncovered" class="tab-content">
                <div class="test-list">
                    {''.join(f'<div class="test-item uncovered-item">❌ {t["name"]} <span style="color:#999">Testmo: {t["testmo_id"]}</span></div>' for t in uncovered_tests.get('web_uae', [])) if uncovered_tests.get('web_uae') else '<div class="test-item uncovered-item">⚠️ No uncovered tests data. Run: python3 import_testmo_tests.py</div>'}
                </div>
            </div>
        </div>

        <div class="coverage-section" style="background: #f8f9fa;">
            <h2 class="coverage-header">🌐 Web KSA Automation</h2>
            <p><strong>Automated:</strong> {web_ksa_total} | <strong>Total in Testmo:</strong> {testmo_web_ksa_total} | <strong>Coverage:</strong> {web_ksa_coverage}%</p>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {web_ksa_coverage}%">{web_ksa_coverage}%</div>
            </div>
            
            <div class="section-tabs">
                <button class="tab-btn active" onclick="showTab('ksa-covered')">✅ Covered Tests ({web_ksa_total})</button>
                <button class="tab-btn" onclick="showTab('ksa-uncovered')">❌ Not Covered ({len(uncovered_tests.get('web_ksa', []))})</button>
            </div>
            
            <div id="ksa-covered" class="tab-content active">
                <div class="test-list">
                    {''.join(f'<div class="test-item">✅ {t["name"]} <span style="color:#999">({t["file"]})</span>' + (f' <span style="color:#667eea">Testmo: {t["testmo_id"]}</span>' if t.get("testmo_id") else '') + '</div>' for t in covered_tests['web_ksa'])}
                </div>
            </div>
            
            <div id="ksa-uncovered" class="tab-content">
                <div class="test-list">
                    {''.join(f'<div class="test-item uncovered-item">❌ {t["name"]} <span style="color:#999">Testmo: {t["testmo_id"]}</span></div>' for t in uncovered_tests.get('web_ksa', [])) if uncovered_tests.get('web_ksa') else '<div class="test-item uncovered-item">⚠️ No uncovered tests data. Run: python3 import_testmo_tests.py</div>'}
                </div>
            </div>
        </div>

        <div class="coverage-section">
            <h2 class="coverage-header">📱 Mobile App Automation (Android & iOS)</h2>
            <p><strong>Automated:</strong> {app_total} | <strong>Total in Testmo:</strong> {testmo_app_total} | <strong>Coverage:</strong> {app_coverage}%</p>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {app_coverage}%">{app_coverage}%</div>
            </div>
            
            <div class="section-tabs">
                <button class="tab-btn active" onclick="showTab('app-covered')">✅ Covered Tests ({app_total})</button>
                <button class="tab-btn" onclick="showTab('app-uncovered')">❌ Not Covered ({len(uncovered_tests.get('app', []))})</button>
            </div>
            
            <div id="app-covered" class="tab-content active">
                <div class="test-list">
                    {''.join(f'<div class="test-item">✅ {t["name"]} <span style="color:#999">({t["file"]})</span>' + (f' <span style="color:#667eea">Testmo: {t["testmo_id"]}</span>' if t.get("testmo_id") else '') + '</div>' for t in covered_tests['app'])}
                </div>
            </div>
            
            <div id="app-uncovered" class="tab-content">
                <div class="test-list">
                    {''.join(f'<div class="test-item uncovered-item">❌ {t["name"]} <span style="color:#999">Testmo: {t["testmo_id"]}</span></div>' for t in uncovered_tests.get('app', [])) if uncovered_tests.get('app') else '<div class="test-item uncovered-item">⚠️ No uncovered tests data. Run: python3 import_testmo_tests.py</div>'}
                </div>
            </div>
        </div>

        <div class="footer">
            <p><strong>Mumzworld SDET Team</strong></p>
            <p style="margin-top: 10px;">
                <a href="https://github.com/mumzworld-tech/automation_web_2.0" target="_blank">GitHub Repository</a> | 
                <a href="https://allure-reports.mumzstage.com/allure-docker-service" target="_blank">Allure Reports</a> | 
                <a href="https://mumzworld.testmo.net" target="_blank">Testmo</a>
            </p>
            <p class="timestamp">Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
    
    <script>
        function showTab(tabId) {{
            // Hide all tab contents
            document.querySelectorAll('.tab-content').forEach(content => {{
                content.classList.remove('active');
            }});
            
            // Remove active class from all buttons
            document.querySelectorAll('.tab-btn').forEach(btn => {{
                btn.classList.remove('active');
            }});
            
            // Show selected tab
            document.getElementById(tabId).classList.add('active');
            
            // Activate clicked button
            event.target.classList.add('active');
        }}
    </script>
</body>
</html>
"""

# Write the HTML file
output_path = Path("index.html")
output_path.write_text(html_content)

# Export JSON data for programmatic access
json_data = {
    'summary': {
        'total_automated': grand_total,
        'web_uae': web_uae_total,
        'web_ksa': web_ksa_total,
        'app': app_total,
        'overall_coverage': overall_coverage
    },
    'covered_tests': covered_tests,
    'uncovered_tests': uncovered_tests,
    'testmo_totals': {
        'web_uae': testmo_web_uae_total,
        'web_ksa': testmo_web_ksa_total,
        'app': testmo_app_total
    }
}

json_path = Path("coverage_data.json")
json_path.write_text(json.dumps(json_data, indent=2))

print(f"✅ Coverage report generated: {output_path}")
print(f"✅ JSON data exported: {json_path}")
print(f"\n📊 Summary:")
print(f"  Web UAE: {web_uae_total} / {testmo_web_uae_total} ({web_uae_coverage}%)")
print(f"  Web KSA: {web_ksa_total} / {testmo_web_ksa_total} ({web_ksa_coverage}%)")
print(f"  App: {app_total} / {testmo_app_total} ({app_coverage}%)")
print(f"  Total: {grand_total} tests")
print(f"  Overall Coverage: {overall_coverage}%")
