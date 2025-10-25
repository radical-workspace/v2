"""
Check that all static files referenced in the manifest exist and all referenced static files in templates are present in the manifest.
Fails if any are missing.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATICFILES = ROOT / "staticfiles"
MANIFEST = STATICFILES / "staticfiles.json"
TEMPLATES = ROOT / "templates"

if not MANIFEST.exists():
    print("No staticfiles.json manifest found. Did you run collectstatic?")
    sys.exit(1)

with MANIFEST.open(encoding="utf-8") as f:
    manifest = json.load(f)

manifest_files = set(manifest.get("paths", {}).keys())

# Check all manifest files exist
missing = []
for rel in manifest_files:
    if not (STATICFILES / rel).exists():
        missing.append(rel)

if missing:
    print("Missing files listed in staticfiles.json manifest:")
    for m in missing:
        print(f" - {m}")
    sys.exit(2)

# Check all {% static %} references are present in manifest
import re
def find_template_static_paths():
    paths = set()
    for p in TEMPLATES.rglob("*.html"):
        try:
            text = p.read_text(encoding="utf-8")
        except Exception:
            continue
        for m in re.findall(r"\{\%\s*static\s+['\"]([^'\"]+)['\"]\s*\%\}", text):
            paths.add(m)
    return paths

missing_in_manifest = []
for ref in find_template_static_paths():
    if ref not in manifest_files:
        missing_in_manifest.append(ref)

if missing_in_manifest:
    print("Static files referenced in templates but missing from manifest:")
    for m in missing_in_manifest:
        print(f" - {m}")
    sys.exit(3)

print("Static manifest integrity OK.")
sys.exit(0)
