import urllib.request
import json
import collections

headers = {"User-Agent": "Mozilla/5.0"}
url = "https://api.github.com/repos/Shabber10/ALL-PYQ-Papers/git/trees/main?recursive=1"
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=30) as resp:
    data = json.loads(resp.read().decode())
    tree = data.get("tree", [])

pdfs = [x for x in tree if x["path"].lower().endswith(".pdf")]
print(f"Total PDFs in Shabber10/ALL-PYQ-Papers: {len(pdfs)}")

# Breakdown by top-level and second-level folders
breakdown = collections.defaultdict(list)
for p in pdfs:
    path = p["path"]
    parts = path.split("/")
    if len(parts) >= 2:
        key = f"{parts[0]}/{parts[1]}"
    else:
        key = parts[0]
    breakdown[key].append(path)

print("\n--- Folder Breakdown ---")
for k, v in sorted(breakdown.items(), key=lambda x: len(x[1]), reverse=True):
    print(f"{k:<35}: {len(v)} PDFs")

# Look specifically at Boards/
print("\n--- State Boards in Boards/ ---")
board_sub = collections.defaultdict(list)
for p in pdfs:
    if p["path"].startswith("Boards/"):
        parts = p["path"].split("/")
        if len(parts) >= 2:
            board_sub[parts[1]].append(p["path"])
for b, v in sorted(board_sub.items(), key=lambda x: len(x[1]), reverse=True):
    print(f"  Boards/{b:<25}: {len(v)} PDFs")

# Look specifically at UPSC/
print("\n--- UPSC Subcategories ---")
upsc_sub = collections.defaultdict(list)
for p in pdfs:
    if p["path"].startswith("UPSC/"):
        parts = p["path"].split("/")
        if len(parts) >= 2:
            upsc_sub[parts[1]].append(p["path"])
for u, v in sorted(upsc_sub.items(), key=lambda x: len(x[1]), reverse=True):
    print(f"  UPSC/{u:<25}: {len(v)} PDFs")
