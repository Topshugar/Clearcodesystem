import re
import pathlib

path = pathlib.Path("app.py")
if not path.exists():
    print("app.py not found in this folder. Put this scanner in same folder as app.py")
    exit()

code = path.read_text()
lines = code.splitlines()

pattern = re.compile(r'f["\'].*SELECT.*\{.*\}.*["\']|f["\'].*INSERT.*\{.*\}.*["\']|f["\'].*UPDATE.*\{.*\}.*["\']|f["\'].*DELETE.*\{.*\}.*["\']', re.IGNORECASE)

found = False
for i, line in enumerate(lines, 1):
    if pattern.search(line) or ('f"' in line or "f'" in line) and "SELECT" in line.upper():
        print(f"[!] Line {i}: VULNERABLE -> {line.strip()}")
        found = True
    if ".execute(f" in line:
        print(f"[!] Line {i}: VULNERABLE execute(f) -> {line.strip()}")
        found = True

if not found:
    print("[OK] No f-string SQL found. You might be safe on SELECTs.")
else:
    print("\n--- FIX EXAMPLE ---")
    print('BAD: cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")')
    print('GOOD: cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))')
