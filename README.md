# Automation Test Coverage Report

Live report: https://saifullaattar.github.io/automation-test-coverage/

## Prerequisites

Clone automation repo next to this repo:
```bash
cd ..
git clone https://github.com/mumzworld-tech/automation_web_2.0.git
```

Directory structure:
```
/parent-directory/
  ├── automation-test-coverage/  (this repo)
  └── automation_web_2.0/         (automation repo)
```

## Update Report

```bash
cd automation-test-coverage
python3 generate_coverage_report.py
git add index.html coverage_data.json covered_tests.txt
git commit -m "Update coverage report"
git push origin main
```

## Update Testmo Totals

Edit `generate_coverage_report.py` and update these lines:
```python
testmo_web_uae_total = 75  # Update from Testmo
testmo_web_ksa_total = 75  # Update from Testmo
testmo_android_total = 40  # Update from Testmo
testmo_ios_total = 40      # Update from Testmo
```

Then regenerate the report.

## Add Uncovered Tests

```bash
# Single tests
python3 add_uncovered_tests.py web_uae "test_name1" "test_name2"

# From file (one test per line)
python3 add_uncovered_tests.py --file android uncovered.txt
```

Then regenerate the report.

## Files

- `generate_coverage_report.py` - Report generator
- `add_uncovered_tests.py` - Add uncovered tests
- `index.html` - Live report
- `coverage_data.json` - JSON export
- `covered_tests.txt` - Text list

## Links

- Live: https://saifullaattar.github.io/automation-test-coverage/
- Automation: https://github.com/mumzworld-tech/automation_web_2.0
- Allure: https://allure-reports.mumzstage.com/allure-docker-service
- Testmo: https://mumzworld.testmo.net
