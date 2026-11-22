import json

# Let's inspect the tree
with open("backend/scripts/harvesters/inspect_github_repo.py", "r") as f:
    pass

import urllib.request, ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {'User-Agent': 'Mozilla/5.0'}

url = "https://api.github.com/repos/Shabber10/ALL-PYQ-Papers/git/trees/main?recursive=1"
data = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=headers), context=ctx).read())

items = [x['path'] for x in data.get('tree', []) if x['path'].endswith('.pdf')]
print(f"Total PDF files in repo: {len(items)}")

# Check Tamil Nadu
tn_items = [p for p in items if 'tamil' in p.lower()]
print(f"\nTamil Nadu items ({len(tn_items)}):")
for p in tn_items[:20]:
    print(" ", p)

# Check CBSE 10 & 12
cbse_10 = [p for p in items if 'cbse/10' in p.lower() or 'class-10' in p.lower()]
cbse_12 = [p for p in items if 'cbse/12' in p.lower() or 'class-12' in p.lower()]
print(f"\nCBSE 10 items: {len(cbse_10)}, sample:")
for p in cbse_10[:10]:
    print(" ", p)
print(f"\nCBSE 12 items: {len(cbse_12)}, sample:")
for p in cbse_12[:10]:
    print(" ", p)

# Check JEE
jee_items = [p for p in items if 'jee' in p.lower()]
print(f"\nJEE items: {len(jee_items)}, sample:")
for p in jee_items[:10]:
    print(" ", p)

# Check NEET
neet_items = [p for p in items if 'neet' in p.lower()]
print(f"\nNEET items: {len(neet_items)}, sample:")
for p in neet_items[:10]:
    print(" ", p)

# Check UPSC
upsc_items = [p for p in items if 'upsc/civil' in p.lower() or 'upsc/cse' in p.lower() or 'upsc/ias' in p.lower()]
print(f"\nUPSC Civil Services items: {len(upsc_items)}, sample:")
for p in upsc_items[:10]:
    print(" ", p)
