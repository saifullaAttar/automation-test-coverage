# Automation Test Coverage Report

Live report: https://saifullaattar.github.io/automation-test-coverage/

## Prerequisites

Clone automation repo next to this repo:
```bash
cd ..
git clone https://github.com/mumzworld-tech/automation_web_2.0.git
```

## Update Report

```bash
cd automation-test-coverage
python3 generate_coverage_report.py
git add .
git commit -m "Update coverage report"
git push origin main
```

## Add Testmo IDs to Covered Tests

Create a file with format: `test_name,testmo_id`
```
test_uae_checkout_cc_no_coupon,12345
test_uae_checkout_cod_no_coupon,12346
```

Then run:
```bash
python3 map_testmo_ids.py web_uae mapping_file.txt
python3 generate_coverage_report.py
```

## Add Uncovered Tests from Testmo

Create a file with format: `testmo_id,test_name`
```
12347,test_guest_checkout
12348,test_payment_wallet
```

Then run:
```bash
python3 import_testmo_tests.py web_uae uncovered_file.txt
python3 generate_coverage_report.py
```

## Update Testmo Totals

Edit `generate_coverage_report.py`:
```python
testmo_web_uae_total = 75  # Update from Testmo
testmo_web_ksa_total = 75  # Update from Testmo
testmo_app_total = 80      # Update from Testmo (Android + iOS combined)
```

## Files

- `generate_coverage_report.py` - Report generator
- `map_testmo_ids.py` - Map Testmo IDs to automated tests
- `import_testmo_tests.py` - Import uncovered tests from Testmo
- `testmo_mapping.json` - Testmo ID mappings (auto-generated)
- `uncovered_tests.json` - Uncovered tests list (auto-generated)
- `index.html` - Live report
- `coverage_data.json` - JSON export
