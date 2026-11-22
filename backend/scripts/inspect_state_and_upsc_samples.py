import urllib.request
import json

headers = {"User-Agent": "Mozilla/5.0"}
url = "https://api.github.com/repos/Shabber10/ALL-PYQ-Papers/git/trees/main?recursive=1"
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=30) as resp:
    data = json.loads(resp.read().decode())
    tree = data.get("tree", [])

pdfs = [x["path"] for x in tree if x["path"].lower().endswith(".pdf")]

states = ["Bihar", "Rajasthan", "Maharashtra", "Andhra_Pradesh", "Telangana", "Uttar_Pradesh", "Kerala", "West_Bengal", "Madhya_Pradesh", "ICSE"]

print("--- State Board PDF Samples ---")
for s in states:
    matches = [p for p in pdfs if p.startswith(f"Boards/{s}")]
    print(f"\n{s} ({len(matches)} files):")
    for m in matches[:6]:
        print("  ", m)

upsc_types = ["CDS", "NDA", "CAPF", "Indian_Forest_Service", "Engineering_Services", "Combined_Medical_Services"]
print("\n--- UPSC Sub-exam PDF Samples ---")
for u in upsc_types:
    matches = [p for p in pdfs if p.startswith(f"UPSC/{u}")]
    print(f"\n{u} ({len(matches)} files):")
    for m in matches[:4]:
        print("  ", m)
