import urllib.request, json

def get_github_tree(repo, path=""):
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "ExamVault-Bot"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return f"Error: {e}"

res = get_github_tree("Shabber10/ALL-PYQ-Papers", "Boards/Maharashtra/2020")
if isinstance(res, list):
    for f in res:
        print(f"  {f['name']} -> {f['download_url']}")
else:
    print(res)
