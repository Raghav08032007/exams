import urllib.request
import json

url = "https://api.github.com/repos/gadepall/cbse-papers/git/trees/main?recursive=1"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
resp = urllib.request.urlopen(req, timeout=25)
data = json.loads(resp.read().decode())
tree = data.get("tree", [])

pdfs = [x["path"] for x in tree if x["path"].lower().endswith(".pdf")]
print(f"Total PDFs in gadepall/cbse-papers: {len(pdfs)}")

years_10 = set()
years_12 = set()
for p in pdfs:
    parts = p.split('/')
    if len(parts) >= 3:
        year = parts[0]
        std = parts[2]
        if std == '10':
            years_10.add(year)
        elif std == '12':
            years_12.add(year)

print(f"gadepall Class 10 years: {sorted(list(years_10))}")
print(f"gadepall Class 12 years: {sorted(list(years_12))}")
