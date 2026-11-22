import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = 'https://api.github.com/repos/boards10/boards10.github.io/git/trees/main?recursive=1'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, context=ctx) as resp:
    tree = json.loads(resp.read().decode('utf-8')).get('tree', [])

pdfs = [x['path'] for x in tree if x['path'].endswith('.pdf')]
print(f"Total PDFs in boards10: {len(pdfs)}")

# Group by category
by_cat = {}
for p in pdfs:
    cat = p.split('/')[1]
    by_cat.setdefault(cat, []).append(p)

for cat, files in by_cat.items():
    print(f"Category '{cat}': {len(files)} files")
    for f in files[:5]:
        print(" ", f)
