import urllib.request, json

def get_github_tree(repo, path=""):
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "ExamVault-Bot"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return f"Error: {e}"

boards = [
    "Maharashtra", "Andhra_Pradesh", "West_Bengal", "Kerala", 
    "Tamil_Nadu", "Uttar_Pradesh", "Bihar", "Telangana", "Rajasthan"
]

print("=== INSPECTING STATE BOARDS IN Shabber10/ALL-PYQ-Papers ===")
for b in boards:
    path = f"Boards/{b}"
    res = get_github_tree("Shabber10/ALL-PYQ-Papers", path)
    if isinstance(res, list):
        dirs = [d['name'] for d in res if d['type'] == 'dir']
        files = [f['name'] for f in res if f['type'] == 'file']
        print(f"Board: {b} -> subdirs: {dirs[:10]}, files: {len(files)}")
    else:
        print(f"Board: {b} -> {res}")
