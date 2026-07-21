from pathlib import Path

Path("/data/result.txt").write_text("written\n", encoding="utf-8")
print("write successful")
