import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}

def get_tree(owner, repo, branch="main"):
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    try:
        req = urllib.request.Request(url, headers=headers)
        data = urllib.request.urlopen(req, timeout=10, context=ctx).read()
        return json.loads(data)
    except Exception as e:
        print(f"Error fetching repo {owner}/{repo}: {e}")
        return None

tree = get_tree("Shabber10", "ALL-PYQ-Papers")
if tree and 'tree' in tree:
    print(f"Total items in Shabber10/ALL-PYQ-Papers: {len(tree['tree'])}")
    for item in tree['tree']:
        if item['path'].endswith('.pdf') or item['type'] == 'tree':
            print(f"  {item['type']:<5} {item['path']}")
else:
    print("Tree fetch returned None or no tree property")
