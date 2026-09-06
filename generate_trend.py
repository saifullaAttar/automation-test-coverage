#!/usr/bin/env python3
"""Build coverage_trend.json: test functions added and changed per month.

Two things this deliberately does NOT do, both of which it used to:

* Read the automation repo's current branch. It reads `origin/main`, the same
  ref the rest of the report is generated from. Reading HEAD meant the chart
  described whatever feature branch happened to be checked out -- and silently
  lost the newest month whenever that branch was behind main.
* Guess from commit messages. "add|new|feat" in a subject line is not evidence a
  test was added. Every commit's diff is read and `def test_...` lines are
  counted, so the numbers are what actually happened to the suite.

The window always ends on the current month, even when that month has no
commits yet, so the chart runs up to today rather than stopping at the last
burst of activity.
"""
import json
import re
import subprocess
import sys
from collections import OrderedDict
from datetime import date
from pathlib import Path

REPO = Path.home() / "automation_web_2.0"
REF = "origin/main"
MONTHS_BACK = 12

ADDED = re.compile(r"^\+def (test_\w+)", re.M)
REMOVED = re.compile(r"^-def (test_\w+)", re.M)


def git(*args):
    out = subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True)
    if out.returncode:
        raise SystemExit(f"git {' '.join(args)} failed: {out.stderr.strip()}")
    return out.stdout


def month_window():
    """Every month from MONTHS_BACK ago to the current one, in order."""
    today = date.today()
    y, m = today.year, today.month
    months = []
    for back in range(MONTHS_BACK - 1, -1, -1):
        total = (y * 12 + (m - 1)) - back
        months.append(date(total // 12, total % 12 + 1, 1))
    return months


def main():
    repo = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO
    globals()["REPO"] = repo

    window = month_window()
    since = window[0].isoformat()
    buckets = OrderedDict((d.strftime("%b %Y"), {"month": d.strftime("%b %Y"),
                                                "tests_added": 0, "tests_fixed": 0,
                                                "total_commits": 0}) for d in window)

    log = git("log", REF, f"--since={since}", "--no-merges",
              "--format=%x00%H|%ad", "--date=short", "-p", "--unified=0", "--", "tests/")

    for chunk in log.split("\x00"):
        if not chunk.strip():
            continue
        header, _, diff = chunk.partition("\n")
        _, _, when = header.partition("|")
        key = date.fromisoformat(when.strip()).strftime("%b %Y")
        if key not in buckets:
            continue
        added = len(ADDED.findall(diff))
        removed = len(REMOVED.findall(diff))
        buckets[key]["total_commits"] += 1
        buckets[key]["tests_added"] += added
        # A commit that touched tests without adding one changed existing tests.
        if added == 0 and removed == 0:
            buckets[key]["tests_fixed"] += 1

    out = list(buckets.values())
    Path(__file__).parent.joinpath("coverage_trend.json").write_text(json.dumps(out, indent=2))
    head = git("rev-parse", "--short", REF).strip()
    print(f"Trend from {REF} ({head}) — {len(out)} months to {out[-1]['month']}")
    for d in out:
        print(f"  {d['month']:9s} +{d['tests_added']:3d} tests, {d['tests_fixed']:3d} change-only commits, {d['total_commits']:3d} commits")


if __name__ == "__main__":
    main()
