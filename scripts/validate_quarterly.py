#!/usr/bin/env python3
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from validators.schema_validator import validate_output

cfg = json.loads(Path("config/sources.json").read_text())
errors = []

for s in cfg["sources"]:
    if s["frequency"] != "quarterly":
        continue
    for o in s["output_files"]:
        p = Path("output/lnc-knowledge-base") / o["file"].replace("{year}", "2025")
        if p.exists():
            errs = validate_output(p, s)
            if errs:
                errors.extend(errs)

if errors:
    for e in errors:
        print(f"ERROR: {e}")
    sys.exit(1)

print("All validations passed")
