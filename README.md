# Mumzworld Automation Test Coverage Report

**Live:** https://saifullaattar.github.io/automation-test-coverage/

Single source of truth for automation coverage against the TestMO regression suite (Run #2154).

## Quick Start

```bash
make generate   # Parse CSV + extract tests + build mapping
make open       # Generate and open in browser
```

## How It Works

1. `parse_testmo_csv.py` — Parses TestMO CSV export into `testmo_tests.json`
2. `extract_tests.py` — Scans `automation_web_2.0` repo for test functions → `automated_tests.json`
3. `build_mapping.py` — Maps TestMO cases to automated tests → `mapping.json`
4. `index.html` — Editable report that loads `mapping.json`

## Editing Mappings

The report is **editable in the browser**:
- Click "+ Add test" on any row to map an automated test
- Click "×" on a tag to remove a mapping
- Add notes in the Notes column
- Edits are saved to localStorage automatically

### Persisting Changes
1. Make your edits in the browser
2. Click **Export JSON** to download the updated `mapping.json`
3. Replace `mapping.json` in this repo and commit

### Resetting
Click **Reset** to discard localStorage edits and reload from the committed `mapping.json`.

## Regenerating

When new tests are added to `automation_web_2.0`:
```bash
make clean && make generate
```

Then update the explicit mappings in `build_mapping.py` for any new TestMO cases.

## Coverage Summary

- **TestMO Cases:** 81 (from Run #2154)
- **Automated Tests:** 90 (35 UAE + 32 KSA + 23 App)
- **Current Coverage:** 31/81 (38%)

## Stack
- Python + Selenium + Appium + Pytest + Allure
- Test Management: [TestMO](https://mumzworld.testmo.net/runs/view/2154)
- CI: BrowserStack
