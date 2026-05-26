#!/usr/bin/env python3
"""Generate coverage_trend.json from automation_web_2.0 git commit history."""
import json
import subprocess
import re
from collections import defaultdict
from pathlib import Path
from datetime import datetime

REPO = Path.home() / "automation_web_2.0"

def get_monthly_stats():
    """Analyze git log for test-related commits grouped by month."""
    # Get commits touching test files in the last 12 months
    result = subprocess.run(
        ["git", "log", "--since=12 months ago", "--pretty=format:%H|%ai|%s",
         "--diff-filter=ACMR", "--", "tests/"],
        capture_output=True, text=True, cwd=REPO
    )

    months = defaultdict(lambda: {"tests_added": 0, "tests_fixed": 0, "total_commits": 0})

    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        parts = line.split("|", 2)
        if len(parts) < 3:
            continue
        commit_hash, date_str, message = parts
        month_key = datetime.fromisoformat(date_str.strip()).strftime("%b %Y")
        msg_lower = message.lower()

        months[month_key]["total_commits"] += 1

        # Classify commit
        if any(kw in msg_lower for kw in ["add", "new", "feat", "create", "implement"]):
            months[month_key]["tests_added"] += 1
        elif any(kw in msg_lower for kw in ["fix", "update", "refactor", "improve", "adjust", "stable"]):
            months[month_key]["tests_fixed"] += 1
        else:
            # Count files added vs modified in this commit
            diff_result = subprocess.run(
                ["git", "diff-tree", "--no-commit-id", "--name-status", "-r", commit_hash, "--", "tests/"],
                capture_output=True, text=True, cwd=REPO
            )
            added = sum(1 for l in diff_result.stdout.strip().split("\n") if l.startswith("A"))
            if added > 0:
                months[month_key]["tests_added"] += 1
            else:
                months[month_key]["tests_fixed"] += 1

    # Sort by date and convert to list
    sorted_months = sorted(months.items(), key=lambda x: datetime.strptime(x[0], "%b %Y"))
    return [{"month": k, **v} for k, v in sorted_months]


if __name__ == "__main__":
    trend = get_monthly_stats()
    output = Path(__file__).parent / "coverage_trend.json"
    output.write_text(json.dumps(trend, indent=2))
    print(f"✅ Generated coverage_trend.json with {len(trend)} months of data")
    for entry in trend:
        print(f"   {entry['month']}: +{entry['tests_added']} added, {entry['tests_fixed']} fixed, {entry['total_commits']} commits")
