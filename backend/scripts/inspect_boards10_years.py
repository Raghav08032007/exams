import urllib.request
import json
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = 'https://api.github.com/repos/boards10/boards10.github.io/git/trees/main?recursive=1'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, context=ctx) as resp:
    tree = json.loads(resp.read().decode('utf-8')).get('tree', [])

pdfs = [x['path'] for x in tree if x['path'].endswith('.pdf')]

# Let's inspect science & social & english files
for sub in ['science', 'social', 'english', 'math']:
    sub_pdfs = [p for p in pdfs if p.startswith(f'papers/{sub}/')]
    print(f"\n=== {sub} ({len(sub_pdfs)} files) ===")
    by_pattern = {}
    for p in sub_pdfs:
        fn = p.split('/')[-1]
        m = re.search(r'(20[0-2][0-9])', fn)
        yr = m.group(1) if m else 'coded'
        by_pattern.setdefault(yr, []).append(p)
    for yr, fl in sorted(by_pattern.items()):
        print(f"  {yr}: {len(fl)} files (sample: {fl[0].split('/')[-1]})")
