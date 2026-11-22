import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def fetch_json(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

gadepall = fetch_json('https://api.github.com/repos/gadepall/cbse-papers/git/trees/main?recursive=1')
if gadepall:
    tree = gadepall.get('tree', [])
    pdfs = [x['path'] for x in tree if x['path'].endswith('.pdf')]
    print(f"gadepall total PDFs: {len(pdfs)}")
    c10_pdfs = [p for p in pdfs if '/10/' in p]
    print(f"Class 10 PDFs: {len(c10_pdfs)}")
    for p in c10_pdfs:
        print(" ", p)
