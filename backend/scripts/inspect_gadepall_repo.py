import urllib.request, json

def get_github_tree(repo, path=""):
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "ExamVault-Bot"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return f"Error: {e}"

for folder in ["papers/math/10", "papers/math/12"]:
    print(f"\nChecking '{folder}' in gadepall/cbse-papers:")
    items = get_github_tree("gadepall/cbse-papers", folder)
    if isinstance(items, list):
        for it in items[:30]:
            print(f"  {it['type']}: {it['name']} ({it.get('path')})")
    else:
        print(items)
