#!/usr/bin/env python3
"""Parse a TestMO CSV export into structured JSON.

Handles both export layouts we use:

* run export      -- "Test ID", "Test", "Status"           (mWEB, run 2154)
* repository export -- "Case", "Status (latest)"           (App, repository 241)

The `Automated` column is what decides scope. Only cases flagged YES or NO are
automation candidates and count towards coverage; "Not planned" cases are kept
but excluded from every percentage. This mirrors the TestMO filter
`custom_automated: [18, 144]`.

Some repository exports omit the case-name column entirely. Pass --allow-unnamed
to accept one: each case is then labelled with TestMO's own Summary text and
marked `name_source: "summary"`, so the report never shows a name that TestMO
did not write. Without the flag an unnamed export is refused.

Usage:
    python3 parse_testmo_csv.py <csv> [output.json] [--allow-unnamed]
"""
import csv
import json
import re
import sys
from pathlib import Path

IN_SCOPE_FLAGS = {"YES", "NO"}


def strip_html(text):
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    for entity, char in (("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"),
                         ("&quot;", '"'), ("&#39;", "'"), ("&nbsp;", " ")):
        text = text.replace(entity, char)
    return re.sub(r"\s+", " ", text).strip()


def first_sentence(text, limit=110):
    """A display label taken from TestMO's own Summary -- never invented here."""
    text = text.strip()
    if not text:
        return ""
    cut = text.split(". ")[0].strip().rstrip(".")
    return cut if len(cut) <= limit else cut[:limit].rsplit(" ", 1)[0] + "…"


def parse_csv(csv_path, allow_unnamed=False):
    with open(csv_path, "r", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        raise SystemExit(f"{csv_path} has no rows")

    cols = rows[0].keys()
    name_col = next((c for c in ("Test", "Case") if c in cols), None)
    status_col = "Status" if "Status" in cols else "Status (latest)"
    if name_col is None and not allow_unnamed:
        raise SystemExit(
            f"{csv_path} has no 'Test' or 'Case' column -- re-export from TestMO "
            f"with the case name column ticked, or pass --allow-unnamed to label "
            f"cases from their Summary. Columns found: {list(cols)}"
        )

    tests = []
    for row in rows:
        flag = (row.get("Automated") or "").strip() or "Unknown"
        summary = strip_html(row.get("Summary", ""))
        if name_col:
            name, name_source = row[name_col].strip(), "testmo"
        else:
            name, name_source = first_sentence(summary), "summary"
        tests.append({
            "case_id": row["Case ID"].strip(),
            "test_id": (row.get("Test ID") or "").strip(),
            "name": name,
            "name_source": name_source,
            "folder": (row.get("Folder") or "").strip(),
            "functionality": (row.get("Functionality") or "").strip(),
            "priority": (row.get("Priority") or "").strip(),
            "status": (row.get(status_col) or "").strip(),
            "automated_flag": flag,
            "in_scope": flag.upper() in IN_SCOPE_FLAGS,
            "summary": summary,
            "steps": strip_html(row.get("Steps To Reproduce", "")),
            "preconditions": strip_html(row.get("Preconditions", "")),
            "tags": (row.get("Tags") or "").strip(),
        })
    return tests


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    allow_unnamed = "--allow-unnamed" in sys.argv
    csv_path = args[0]
    out = Path(args[1]) if len(args) > 1 else Path(__file__).parent / "testmo_tests.json"

    tests = parse_csv(csv_path, allow_unnamed=allow_unnamed)
    out.write_text(json.dumps(tests, indent=2, ensure_ascii=False))

    in_scope = sum(1 for t in tests if t["in_scope"])
    flags = {}
    for t in tests:
        flags[t["automated_flag"]] = flags.get(t["automated_flag"], 0) + 1
    print(f"Parsed {len(tests)} cases from {Path(csv_path).name} -> {out}")
    print(f"  in scope (YES/NO): {in_scope}   excluded: {len(tests) - in_scope}   {flags}")
    unnamed = sum(1 for t in tests if t["name_source"] == "summary")
    if unnamed:
        print(f"  no case-name column: {unnamed} cases labelled from their TestMO Summary")


if __name__ == "__main__":
    main()
