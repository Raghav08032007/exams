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

# Check default branch of gadepall/cbse-papers
repo_info = fetch_json('https://api.github.com/repos/gadepall/cbse-papers')
if repo_info:
    branch = repo_info.get('default_branch', 'main')
    print(f"gadepall/cbse-papers default branch: {branch}")
    gadepall = fetch_json(f'https://api.github.com/repos/gadepall/cbse-papers/git/trees/{branch}?recursive=1')
    if gadepall:
        tree = gadepall.get('tree', [])
        print(f"gadepall/cbse-papers total files: {len(tree)}")
        c10 = [x['path'] for x in tree if '10' in x['path'] or 'math' in x['path'].lower()]
        print(f"gadepall/cbse-papers matching count: {len(c10)}")
        for f in c10[:15]:
            print(" ", f)

# Check Studywithanil/CBSE-Class10-PYQ
pyq1 = fetch_json('https://api.github.com/repos/Studywithanil/CBSE-Class10-PYQ/git/trees/main?recursive=1')
if not pyq1:
    pyq1 = fetch_json('https://api.github.com/repos/Studywithanil/CBSE-Class10-PYQ/git/trees/master?recursive=1')
if pyq1:
    print(f"Studywithanil/CBSE-Class10-PYQ total files: {len(pyq1.get('tree', []))}")
    for f in pyq1.get('tree', [])[:15]:
        print(" ", f['path'])
