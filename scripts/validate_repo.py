from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []

for path in ROOT.rglob("*.py"):
    if path == Path(__file__).resolve():
        continue
    try:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        errors.append(f"Python syntax: {path.relative_to(ROOT)}: {exc}")

for path in ROOT.rglob(".gitignore"):
    lines = {
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    if "RESULT.md" in lines or "**/RESULT.md" in lines:
        errors.append(f"RESULT.md must be tracked: {path.relative_to(ROOT)}")

required = [
    "README.md",
    "VERSIONS.md",
    "project-01-container-runtime/README.md",
    "project-09-final-stack/README.md",
]
for rel in required:
    if not (ROOT / rel).exists():
        errors.append(f"Missing required file: {rel}")

file_count = sum(1 for p in ROOT.rglob("*") if p.is_file())
print(f"Files: {file_count}")

if errors:
    print("\nValidation failed:")
    for error in errors:
        print(f"- {error}")
    raise SystemExit(1)

print("Validation passed.")
