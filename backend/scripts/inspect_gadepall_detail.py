import urllib.request
import json

headers = {"User-Agent": "Mozilla/5.0"}
url = "https://api.github.com/repos/gadepall/cbse-papers/git/trees/main?recursive=1"
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=20) as resp:
    data = json.loads(resp.read().decode())
    tree = data.get("tree", [])

pdfs = [x["path"] for x in tree if x["path"].lower().endswith(".pdf")]
print(f"Total PDFs in gadepall/cbse-papers: {len(pdfs)}")

c10 = [p for p in pdfs if "/10/" in p or p.startswith("10/")]
c12 = [p for p in pdfs if "/12/" in p or p.startswith("12/")]
print(f"Class 10 PDFs: {len(c10)}")
print(f"Class 12 PDFs: {len(c12)}")

print("\nSample Class 10 PDFs in gadepall:")
for p in c10[:15]:
    print(" ", p)
