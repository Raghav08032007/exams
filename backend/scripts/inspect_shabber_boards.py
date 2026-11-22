import urllib.request
import json

url = "https://api.github.com/repos/Shabber10/ALL-PYQ-Papers/git/trees/main?recursive=1"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
resp = urllib.request.urlopen(req, timeout=30)
data = json.loads(resp.read().decode())
tree = data.get("tree", [])

tn_files = [x["path"] for x in tree if "Boards/TamilNadu" in x["path"] and x["path"].endswith(".pdf")]
cbse_files = [x["path"] for x in tree if "Boards/CBSE" in x["path"] and x["path"].endswith(".pdf")]
boards_files = [x["path"] for x in tree if x["path"].startswith("Boards/") and x["path"].endswith(".pdf")]

print(f"Total PDFs in Boards/: {len(boards_files)}")
print(f"Total PDFs in Boards/TamilNadu: {len(tn_files)}")
for f in tn_files:
    print("  TN:", f)

print(f"\nTotal PDFs in Boards/CBSE: {len(cbse_files)}")
for f in cbse_files[:15]:
    print("  CBSE:", f)
