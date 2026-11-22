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

b10 = fetch_json('https://api.github.com/repos/boards10/boards10.github.io/git/trees/main?recursive=1')
if not b10:
    b10 = fetch_json('https://api.github.com/repos/boards10/boards10.github.io/git/trees/master?recursive=1')

if b10:
    tree = b10.get('tree', [])
    print(f"boards10 total files: {len(tree)}")
    pdfs = [x['path'] for x in tree if x['path'].endswith('.pdf')]
    print(f"boards10 total PDFs: {len(pdfs)}")
    
    # Let's count by subject / folder
    folders = {}
    for p in pdfs:
        parts = p.split('/')
        cat = parts[0] if len(parts) > 1 else 'root'
        folders[cat] = folders.get(cat, 0) + 1
    print("Folders breakdown:", folders)

    # Let's see some sample paths for science, social, english, tamil, math
    for sub in ['science', 'social', 'english', 'tamil', 'math']:
        matches = [p for p in pdfs if sub in p.lower()]
        print(f"\nSample {sub} ({len(matches)} files):")
        for m in matches[:5]:
            print(" ", m)
