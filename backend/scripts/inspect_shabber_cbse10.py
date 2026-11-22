import urllib.request
import json

url = "https://api.github.com/repos/Shabber10/ALL-PYQ-Papers/git/trees/main?recursive=1"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
resp = urllib.request.urlopen(req, timeout=30)
data = json.loads(resp.read().decode())
tree = data.get("tree", [])

cbse_10 = [x["path"] for x in tree if x["path"].startswith("Boards/CBSE/10/") and x["path"].endswith(".pdf")]
print(f"Total Class 10 CBSE PDFs in Shabber10: {len(cbse_10)}")

years = {}
for p in cbse_10:
    parts = p.split('/')
    if len(parts) >= 4:
        yr = parts[3]
        fname = parts[-1].lower()
        if yr not in years:
            years[yr] = []
        years[yr].append(fname)

print("Years available in Shabber10 CBSE 10:")
for yr in sorted(years.keys()):
    print(f"  {yr}: {len(years[yr])} papers")

print("\nSample Math/Science/Social/English/Tamil in Shabber10:")
for p in cbse_10:
    low = p.lower()
    if any(k in low for k in ['math', 'science', 'social', 'english', 'tamil']):
        print(" ", p)
