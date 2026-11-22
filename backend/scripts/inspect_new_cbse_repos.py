import urllib.request
import json

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

repos = [
    "gadepall/cbse-papers",
    "boards10/boards10.github.io"
]

for repo in repos:
    print(f"\n================ Inspecting {repo} ================")
    for branch in ["master", "main"]:
        url = f"https://api.github.com/repos/{repo}/git/trees/{branch}?recursive=1"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode())
                tree = data.get("tree", [])
                print(f"Branch '{branch}': Found {len(tree)} entries")
                pdfs = [x for x in tree if x["path"].lower().endswith((".pdf", ".tex", ".html"))]
                print(f"Documents count: {len(pdfs)}")
                for p in pdfs[:15]:
                    print("  -", p["path"])
                break
        except Exception as e:
            print(f"Branch '{branch}' failed: {e}")
