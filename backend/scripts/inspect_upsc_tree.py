import urllib.request, json

headers = {"User-Agent": "Mozilla/5.0"}
url = "https://api.github.com/repos/Shabber10/ALL-PYQ-Papers/git/trees/main?recursive=1"
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=30) as resp:
    data = json.loads(resp.read().decode())
    tree = data.get("tree", [])

upsc_files = [x["path"] for x in tree if x["path"].startswith("UPSC") and x["path"].endswith(".pdf")]
print(f"Total UPSC PDF files: {len(upsc_files)}")

# Group by subfolder under UPSC
subfolders = {}
for p in upsc_files:
    parts = p.split("/")
    sub = parts[1] if len(parts) > 1 else "root"
    subfolders[sub] = subfolders.get(sub, 0) + 1

print("UPSC Subcategories:", subfolders)

# Check Civil Services specifically
civil = [p for p in upsc_files if "civil" in p.lower() or "cse" in p.lower() or "prelim" in p.lower() or "mains" in p.lower() or "csp" in p.lower()]
print(f"Civil services / Prelims / Mains: {len(civil)}")
for c in civil[:15]:
    print(" ", c)

# Check if there's any folder called UPSC/CSE or UPSC/Civil_Services or Civil
if "CSE" in subfolders or "Civil_Services" in subfolders:
    print("Found direct civil services folder")
else:
    # Print sample from other folders
    for s in list(subfolders.keys())[:5]:
        sample = [p for p in upsc_files if p.startswith(f"UPSC/{s}")][:2]
        print(f"Sample {s}:", sample)
