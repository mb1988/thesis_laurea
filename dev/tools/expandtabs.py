# -*- coding: utf-8 -*-
"""Expand tabs to spaces in the project's Python sources.

Python 2's tokenizer treats a tab as "advance to the next multiple of 8" and
happily accepts files that mix tabs and spaces.  Python 3 rejects those files
with TabError.  Expanding with tabsize 8 reproduces exactly the indentation
Python 2 computed, so the converted files keep the original behaviour (warts
and all) instead of silently changing which statements are in which block.

Usage:  python dev/tools/expandtabs.py [--check]
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKIP_DIRS = {".venv", ".git", "__pycache__", "instance"}


def python_sources():
    for path in sorted(REPO_ROOT.rglob("*.py")):
        if SKIP_DIRS & set(path.relative_to(REPO_ROOT).parts):
            continue
        yield path


def main(argv):
    check_only = "--check" in argv
    changed = []

    for path in python_sources():
        original = path.read_text(encoding="utf-8")
        if "\t" not in original:
            continue
        expanded = original.expandtabs(8)
        changed.append(path)
        if not check_only:
            path.write_text(expanded, encoding="utf-8", newline="")

    verb = "would rewrite" if check_only else "rewrote"
    for path in changed:
        print("%s %s" % (verb, path.relative_to(REPO_ROOT)))
    print("%d file(s) %s" % (len(changed), "need attention" if check_only else "normalised"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
