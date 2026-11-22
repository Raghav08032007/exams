import urllib.request
import json

headers = {"User-Agent": "Mozilla/5.0"}
url = "https://raw.githubusercontent.com/Shabber10/ALL-PYQ-Papers/main/README.md"
req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        content = resp.read().decode('utf-8', errors='ignore')
        print("=== README.md content ===")
        print(content[:3000])
except Exception as e:
    print("Error fetching README:", e)

# Also check if there are other markdown or json files in the repo
tree_url = "https://api.github.com/repos/Shabber10/ALL-PYQ-Papers/git/trees/main?recursive=1"
try:
    req2 = urllib.request.Request(tree_url, headers=headers)
    with urllib.request.urlopen(req2, timeout=20) as resp2:
        data = json.loads(resp2.read().decode())
        tree = data.get("tree", [])
        md_files = [x["path"] for x in tree if x["path"].lower().endswith((".md", ".txt", ".json"))]
        print("\n=== Other metadata/text files in repo ===")
        for f in md_files[:20]:
            print(" -", f)
except Exception as e2:
    print("Error fetching tree:", e2)
