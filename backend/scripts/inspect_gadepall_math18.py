import urllib.request, json

def get_github_tree(repo, path=""):
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "ExamVault-Bot"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return f"Error: {e}"

items = get_github_tree("gadepall/cbse-papers", "papers/math/10/2018")
if isinstance(items, list):
    for it in items:
        print(f"  {it['type']}: {it['name']} ({it.get('download_url')})")
else:
    print(items)
