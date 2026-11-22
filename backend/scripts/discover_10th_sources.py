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

# Check gadepall/cbse-papers
gadepall = fetch_json('https://api.github.com/repos/gadepall/cbse-papers/git/trees/master?recursive=1')
if gadepall:
    tree = gadepall.get('tree', [])
    print(f"gadepall/cbse-papers total files: {len(tree)}")
    c10 = [x['path'] for x in tree if '10' in x['path'] or 'class10' in x['path'].lower()]
    print(f"gadepall/cbse-papers Class 10 files: {len(c10)}")
    for f in c10[:15]:
        print(" ", f)

# Search CBSE class 10 repos
cbse_repos = fetch_json('https://api.github.com/search/repositories?q=cbse+class+10+papers&sort=stars&order=desc')
if cbse_repos:
    print("\nTop CBSE Repos:")
    for r in cbse_repos.get('items', [])[:6]:
        print(f"  {r['full_name']} (stars: {r['stargazers_count']}) - {r['html_url']}")

# Search Tamil Nadu SSLC papers
tn_repos = fetch_json('https://api.github.com/search/repositories?q=sslc+question+papers&sort=stars&order=desc')
if tn_repos:
    print("\nTop SSLC Repos:")
    for r in tn_repos.get('items', [])[:6]:
        print(f"  {r['full_name']} (stars: {r['stargazers_count']}) - {r['html_url']}")

tn_repos2 = fetch_json('https://api.github.com/search/repositories?q=tamilnadu+question+papers&sort=stars&order=desc')
if tn_repos2:
    print("\nTop Tamil Nadu Repos:")
    for r in tn_repos2.get('items', [])[:6]:
        print(f"  {r['full_name']} (stars: {r['stargazers_count']}) - {r['html_url']}")
