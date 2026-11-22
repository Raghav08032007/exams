import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request('https://api.github.com/repos/gadepall/cbse-papers/git/trees/main?recursive=1', headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, context=ctx) as resp:
    tree = json.loads(resp.read().decode('utf-8')).get('tree', [])

c10_math = [x['path'] for x in tree if x['path'].endswith('.pdf') and ('math' in x['path'].lower()) and ('10' in x['path'])]
print(f"Total Class 10 Math PDFs in gadepall: {len(c10_math)}")
for p in c10_math:
    print(p)
