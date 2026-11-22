import urllib.request
import json

url = "https://api.github.com/repos/Shabber10/ALL-PYQ-Papers/git/trees/main?recursive=1"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
resp = urllib.request.urlopen(req, timeout=30)
data = json.loads(resp.read().decode())
tree = data.get("tree", [])

board_folders = set()
for x in tree:
    if x["path"].startswith("Boards/"):
        parts = x["path"].split('/')
        if len(parts) >= 2:
            board_folders.add(parts[1])

print("Subfolders under Boards/ in Shabber10:")
for bf in sorted(list(board_folders)):
    pdf_count = len([x for x in tree if x["path"].startswith(f"Boards/{bf}/") and x["path"].endswith(".pdf")])
    print(f"  Boards/{bf}: {pdf_count} PDFs")
