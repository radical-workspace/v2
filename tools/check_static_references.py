#!/usr/bin/env python3
"""Check that all `{% static 'path' %}` references in templates exist in either
the `static/` source tree or the collected `staticfiles/` directory.

Exit code 0 if all references resolved, 2 if missing references found.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = ROOT / "templates"
STATIC_SRC = ROOT / "static"
STATIC_COLLECTED = ROOT / "staticfiles"

STATIC_TAG_RE = re.compile(r'''\{%\s*static\s+['"]([^'"]+)['"]\s*%}''')


def find_template_static_paths() -> set[str]:
    paths: set[str] = set()
    for p in TEMPLATES_DIR.rglob("*.html"):
        try:
            text = p.read_text(encoding="utf-8")
        except Exception:
            continue
        for m in STATIC_TAG_RE.finditer(text):
            paths.add(m.group(1))
    return paths


def exists_in_static(path: str) -> bool:
    src = STATIC_SRC / path
    coll = STATIC_COLLECTED / path
    return src.exists() or coll.exists()


def main() -> int:
    if not TEMPLATES_DIR.exists():
        print("No templates directory found; skipping static reference check.")
        return 0

    missing = []
    refs = find_template_static_paths()
    for r in sorted(refs):
        if not exists_in_static(r):
            missing.append(r)

    if missing:
        print("Missing static files referenced in templates:")
        for m in missing:
            print(f" - {m}")
        print("\nEnsure these files exist under `static/` or are collected into `staticfiles/`.")
        return 2

    print("All static references resolved.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
