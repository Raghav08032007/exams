import urllib.request
import json
import re

headers = {"User-Agent": "Mozilla/5.0"}
url = "https://api.github.com/repos/Shabber10/ALL-PYQ-Papers/git/trees/main?recursive=1"
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=30) as resp:
    data = json.loads(resp.read().decode())
    tree = data.get("tree", [])

pdfs = [x["path"] for x in tree if x["path"].lower().endswith(".pdf")]
print(f"Total PDFs: {len(pdfs)}")

# Samples of each pattern
cbse10 = [p for p in pdfs if p.startswith("Boards/CBSE/10")]
cbse12 = [p for p in pdfs if p.startswith("Boards/CBSE/12")]
jee = [p for p in pdfs if p.startswith("JEE")]
neet = [p for p in pdfs if p.startswith("NEET")]
upsc = [p for p in pdfs if p.startswith("UPSC/Civil_Services")]
tn = [p for p in pdfs if p.startswith("Boards/Tamil_Nadu")]

print("\nCBSE 10 samples (total:", len(cbse10), ")")
for p in cbse10[:10]:
    print(" ", p)

print("\nCBSE 12 samples (total:", len(cbse12), ")")
for p in cbse12[:10]:
    print(" ", p)

print("\nJEE samples (total:", len(jee), ")")
for p in jee[:10]:
    print(" ", p)

print("\nNEET samples (total:", len(neet), ")")
for p in neet[:10]:
    print(" ", p)

print("\nUPSC samples (total:", len(upsc), ")")
for p in upsc[:10]:
    print(" ", p)

print("\nTN samples (total:", len(tn), ")")
for p in tn:
    print(" ", p)
