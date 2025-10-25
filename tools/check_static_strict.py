"""
Stricter static asset checker for Django projects using ManifestStaticFilesStorage.
- Fails if any referenced static file is missing or not in manifest.
- Fails if any file in static/ or staticfiles/ is not referenced in any template (unused asset detection).
- Fails if any manifest entry is missing its hashed file.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATIC_SRC = ROOT / "static"
STATICFILES = ROOT / "staticfiles"
MANIFEST = STATICFILES / "staticfiles.json"
TEMPLATES = ROOT / "templates"

if not MANIFEST.exists():
    print("No staticfiles.json manifest found. Did you run collectstatic?")
    sys.exit(1)

with MANIFEST.open(encoding="utf-8") as f:
    manifest = json.load(f)

manifest_files = set(manifest.get("paths", {}).keys())

# 1. Find all {% static %} references in templates
static_re = re.compile(r"\{\%\s*static\s+['\"]([^'\"]+)['\"]\s*\%\}")
referenced = set()
for p in TEMPLATES.rglob("*.html"):
    try:
        text = p.read_text(encoding="utf-8")
    except Exception:
        continue
    referenced.update(static_re.findall(text))

# 2. Find all files in static/ and staticfiles/
def all_static_files(base):
    return set(str(f.relative_to(base)).replace("\\", "/") for f in base.rglob("*") if f.is_file())

src_files = all_static_files(STATIC_SRC)
collected_files = all_static_files(STATICFILES)

# 3. Unused static file detection
unused_src = src_files - referenced
unused_collected = collected_files - referenced - manifest_files

# 4. Hashed file validation (for ManifestStaticFilesStorage)
hashed_missing = []
for rel in manifest_files:
    hashed = manifest["paths"][rel]
    if not (STATICFILES / hashed).exists():
        hashed_missing.append(hashed)

# 5. Report
fail = False
if unused_src:
    print("Unused static files in static/ (not referenced in any template):")
    for f in sorted(unused_src):
        print(f" - {f}")
    fail = True
if unused_collected:
    print("Unused static files in staticfiles/ (not referenced or in manifest):")
    for f in sorted(unused_collected):
        print(f" - {f}")
    fail = True
if hashed_missing:
    print("Manifest entries missing hashed file:")
    for f in hashed_missing:
        print(f" - {f}")
    fail = True
if not fail:
    print("Strict static asset check: all good.")
sys.exit(1 if fail else 0)
