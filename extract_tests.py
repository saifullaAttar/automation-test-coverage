#!/usr/bin/env python3
"""Extract the automated test inventory from automation_web_2.0 @ origin/main.

Reads the tree with `git show origin/main:<path>` so the working copy is never
touched -- the repo is usually parked on a feature branch and the report must
always reflect main.

Each test is emitted with a platform-qualified `ref` ("app::test_foo"). That
matters: 10 test names exist in two files at once (the app cart/checkout suites
were ported from the web ones and kept their names), so a bare name cannot say
which test covers a TestMO case.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

# platform -> directory in the repo
PLATFORMS = {
    "app": "tests/app",
    "web_uae": "tests/web/UAE",
    "web_ksa": "tests/web/KSA",
    "web_commons": "tests/web/commons",
}

# Preferred ref, with fallbacks. A CI checkout is a detached HEAD and may not
# carry refs/remotes/origin/*, so falling back to a local `main` and finally to
# HEAD keeps the workflow working instead of silently reading the wrong tree.
REF_CANDIDATES = ("origin/main", "main", "HEAD")
REF = "origin/main"

# Tickets that delivered / hardened Arabic locale support. Files they touched
# are treated as AR-verified, as are files that carry locale-aware code.
ARABIC_TICKETS = ["FALCONS-321", "FALCONS-330", "FALCONS-335", "FALCONS-336"]
LOCALE_MARKER = re.compile(r"LOCALE|locale_|\.locale|lang=")

DEF_RE = re.compile(r"^def (test_\w+)\(", re.M)


def git(repo, *args):
    out = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True)
    if out.returncode:
        raise SystemExit(f"git {' '.join(args)} failed: {out.stderr.strip()}")
    return out.stdout


def resolve_ref(repo):
    """First candidate ref that exists in this clone."""
    for ref in REF_CANDIDATES:
        out = subprocess.run(["git", "rev-parse", "--verify", "--quiet", ref],
                             cwd=repo, capture_output=True, text=True)
        if out.returncode == 0:
            return ref
    raise SystemExit(f"none of {REF_CANDIDATES} exist in {repo}")


def list_test_files(repo, rel_dir):
    names = git(repo, "ls-tree", "-r", "--name-only", REF, "--", rel_dir).split()
    return [n for n in names if re.search(r"/test_[^/]*\.py$", n)]


def arabic_ticket_files(repo):
    """Test files touched by any of the Arabic tickets."""
    touched = set()
    for ticket in ARABIC_TICKETS:
        for sha in git(repo, "log", REF, "--format=%H", f"--grep={ticket}").split():
            for line in git(repo, "show", "--name-only", "--format=", sha).splitlines():
                if line.startswith("tests/"):
                    touched.add(line.strip())
    return touched


def decorator_block(lines, def_idx):
    """Lines directly above a def, back to the previous blank line."""
    block, i = [], def_idx - 1
    while i >= 0 and lines[i].strip():
        block.insert(0, lines[i])
        i -= 1
    return "\n".join(block)


def docstring_after(lines, def_idx):
    i = def_idx
    while i < len(lines) and not lines[i].rstrip().endswith("):"):
        i += 1
    i += 1
    if i >= len(lines) or not lines[i].strip().startswith('"""'):
        return ""
    first = lines[i].strip().lstrip('"')
    parts = [first] if first.strip() else []
    if first.rstrip().endswith('"""'):
        return re.sub(r"\s+", " ", first.rstrip('"')).strip()
    i += 1
    while i < len(lines) and '"""' not in lines[i]:
        parts.append(lines[i].strip())
        i += 1
    return re.sub(r"\s+", " ", " ".join(parts)).strip()


def parse_skip(block):
    m = re.search(r"@pytest\.mark\.skip\(\s*(?:reason\s*=\s*)?[\"'](.*?)[\"']", block, re.S)
    if m:
        return {"type": "hard", "reason": re.sub(r"\s+", " ", m.group(1)).strip()}
    if "@pytest.mark.skip(" in block:
        return {"type": "hard", "reason": ""}
    if "@pytest.mark.skipif" in block:
        m = re.search(r"@pytest\.mark\.skipif\(\s*(.+?)(?:,\s*reason|\n)", block, re.S)
        cond = re.sub(r"\s+", " ", m.group(1)).strip() if m else ""
        return {"type": "conditional", "reason": cond}
    return None


def parse_file(source, path, platform, ar_verified):
    lines = source.split("\n")
    tests = []
    for i, line in enumerate(lines):
        m = DEF_RE.match(line)
        if not m:
            continue
        name = m.group(1)
        block = decorator_block(lines, i)

        title = re.search(r"@allure\.title\([\"'](.+?)[\"']\)", block)
        feature = re.search(r"@allure\.feature\([\"'](.+?)[\"']\)", block)
        story = re.search(r"@allure\.story\([\"'](.+?)[\"']\)", block)
        severity = re.search(r"severity_level\.(\w+)", block)

        tags = []
        for tm in re.finditer(r"@allure\.tag\((.+?)\)", block, re.S):
            tags += [t.strip().strip("\"'") for t in tm.group(1).split(",") if t.strip()]

        tests.append({
            "ref": f"{platform}::{name}",
            "name": name,
            "platform": platform,
            "path": path,
            "file": path.rsplit("/", 1)[-1],
            "title": title.group(1) if title else "",
            "feature": feature.group(1) if feature else "",
            "story": story.group(1) if story else "",
            "severity": severity.group(1).lower() if severity else "",
            "tags": tags,
            "docstring": docstring_after(lines, i)[:400],
            "parametrized": "@pytest.mark.parametrize" in block,
            "skip": parse_skip(block),
            "locales": ["en", "ar"] if ar_verified else ["en"],
        })
    return tests


def disambiguate(tests):
    """Make every ref unique.

    "platform::name" is enough for almost everything, but a name can repeat
    inside one platform too -- test_uae_cart_apply_gift_wrap_and_place_order
    lives in both tests/web/UAE/test_cart.py (hard-skipped duplicate) and
    tests/web/UAE/test_checkout.py (the live copy). Those get the file stem
    appended so the two can never be confused for one another.
    """
    seen = {}
    for t in tests:
        seen.setdefault(t["name"], []).append(t)
    for name, group in seen.items():
        if len(group) > 1:
            for t in group:
                stem = t["file"].removesuffix(".py")
                t["ref"] = f"{t['platform']}::{name}@{stem}"


def main():
    repo = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "automation_web_2.0"
    globals()["REF"] = resolve_ref(repo)
    head = git(repo, "rev-parse", "--short", REF).strip()
    print(f"Reading {repo} @ {REF} ({head}) -- working copy untouched")
    if REF != REF_CANDIDATES[0]:
        print(f"  note: {REF_CANDIDATES[0]} not present; used {REF}")

    ar_files = arabic_ticket_files(repo)
    result = {}
    for platform, rel_dir in PLATFORMS.items():
        files = list_test_files(repo, rel_dir)
        tests = []
        for path in files:
            src = git(repo, "show", f"{REF}:{path}")
            ar = path in ar_files or bool(LOCALE_MARKER.search(src))
            tests += parse_file(src, path, platform, ar)
        disambiguate(tests)
        result[platform] = tests
        print(f"  {platform:12s} {len(files)} files, {len(tests):3d} tests")

    result["_meta"] = {"ref": REF, "sha": head, "repo": str(repo)}
    out = Path(__file__).parent / "automated_tests.json"
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False))

    flat = [t for k, v in result.items() if k != "_meta" for t in v]
    hard = sum(1 for t in flat if t["skip"] and t["skip"]["type"] == "hard")
    cond = sum(1 for t in flat if t["skip"] and t["skip"]["type"] == "conditional")
    ar = sum(1 for t in flat if "ar" in t["locales"])
    print(f"Total {len(flat)} tests -- {len(flat) - hard - cond} active, "
          f"{hard} hard-skipped, {cond} OS-gated, {ar} AR-verified -> {out}")


if __name__ == "__main__":
    main()
