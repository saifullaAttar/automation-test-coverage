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
- Click **💾 Save for Everyone** to persist changes for all users (requires password)

### Persisting Changes
Edits are saved to a shared GitHub Gist (`37aafe3290f5c00dbd0ddb910a19f939`).
1. Make your edits in the browser
2. Click **💾 Save for Everyone**
3. Enter password: `Mumz@SDET2026`
4. First time only: enter a GitHub PAT with `gist` scope (saved in your browser)

All users will see the updated mappings on next page load.

### Resetting
Click **Reset** to discard localStorage edits and reload from the shared Gist.

## Regenerating

When new tests are added to `automation_web_2.0`:
```bash
make clean && make generate
```

Then update the explicit mappings in `build_mapping.py` for any new TestMO cases.

## Auto-Update from FALCON Lambda

After each regression run, the FALCON Lambda can auto-append results to `regression_runs.json` via the GitHub Gist API. Add this to the post-run step in `handler.js`:

```javascript
// After test run completes, append to regression_runs.json in the coverage Gist
const coverageGist = '37aafe3290f5c00dbd0ddb910a19f939';
const token = process.env.COVERAGE_GIST_TOKEN;
const regResp = await fetch(`https://api.github.com/gists/${coverageGist}`, {
  headers: { 'Authorization': `token ${token}` }
});
const gist = await regResp.json();
const runs = JSON.parse(gist.files['regression_runs.json']?.content || '[]');
runs.push({
  date: new Date().toISOString().split('T')[0],
  environment: process.env.ENV_CHOICE,
  country: combo.country,
  platform: combo.os,
  passed: totalPassed,
  failed: totalFailed,
  skipped: totalSkipped,
  total: totalPassed + totalFailed + totalSkipped
});
await fetch(`https://api.github.com/gists/${coverageGist}`, {
  method: 'PATCH',
  headers: { 'Authorization': `token ${token}`, 'Content-Type': 'application/json' },
  body: JSON.stringify({ files: { 'regression_runs.json': { content: JSON.stringify(runs, null, 2) } } })
});
```

Set `COVERAGE_GIST_TOKEN` as a Lambda environment variable with a GitHub PAT that has `gist` scope.

## Coverage Summary

- **TestMO Cases:** 124 (81 Web from Run #2154 + 43 App from Run #2192)
- **Automated Tests:** 93 (35 UAE + 32 KSA + 26 App)
- **Web Coverage:** 31/81 (38%)
- **App Coverage:** 17/43 (39%)
- **Target:** 80% by Q3 2026

## Stack
- Python + Selenium + Appium + Pytest + Allure
- Test Management: [TestMO](https://mumzworld.testmo.net/runs/view/2154)
- CI: BrowserStack
