import urllib.request, json

def get_github_tree(repo, path=""):
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "ExamVault-Bot"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return f"Error: {e}"

print("Checking 'Boards/CBSE' in Shabber10/ALL-PYQ-Papers:")
items = get_github_tree("Shabber10/ALL-PYQ-Papers", "Boards/CBSE")
if isinstance(items, list):
    for it in items[:35]:
        print(f"  {it['type']}: {it['name']} ({it.get('path')})")
        if it['type'] == 'dir':
            sub = get_github_tree("Shabber10/ALL-PYQ-Papers", it['path'])
            if isinstance(sub, list):
                years = [s['name'] for s in sub if s['type'] == 'dir']
                print(f"     Subdirectories: {years}")
else:
    print(items)
