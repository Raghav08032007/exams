import sys, os
import urllib.request
import json

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

repos = [
    "avallark/NCERT-TextBooks",
    "Shabber10/ALL-PYQ-Papers",
]

for repo in repos:
    print(f"\n=================== Checking {repo} ===================")
    url = f"https://api.github.com/repos/{repo}/git/trees/master?recursive=1"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            tree = data.get("tree", [])
            print(f"Total files/dirs in {repo}: {len(tree)}")
            
            # Group by extension and top directory
            extensions = {}
            top_dirs = set()
            sample_paths = []
            for item in tree:
                path = item.get("path", "")
                parts = path.split("/")
                top_dirs.add(parts[0])
                ext = os.path.splitext(path)[1].lower()
                extensions[ext] = extensions.get(ext, 0) + 1
                if len(sample_paths) < 20 and (ext in [".pdf", ".md", ".json", ""]):
                    sample_paths.append((item.get("type"), path))
            
            print("Top directories:", sorted(list(top_dirs))[:15])
            print("Extensions:", extensions)
            print("Sample files:")
            for t, p in sample_paths[:10]:
                print(f"  [{t}] {p}")
    except Exception as e:
        print(f"Error fetching {repo} master: {e}")
        # Try main branch
        url_main = f"https://api.github.com/repos/{repo}/git/trees/main?recursive=1"
        try:
            req_main = urllib.request.Request(url_main, headers=headers)
            with urllib.request.urlopen(req_main, timeout=15) as resp:
                data = json.loads(resp.read().decode())
                tree = data.get("tree", [])
                print(f"Total files/dirs in {repo} (main branch): {len(tree)}")
                extensions = {}
                top_dirs = set()
                sample_paths = []
                for item in tree:
                    path = item.get("path", "")
                    parts = path.split("/")
                    top_dirs.add(parts[0])
                    ext = os.path.splitext(path)[1].lower()
                    extensions[ext] = extensions.get(ext, 0) + 1
                    if len(sample_paths) < 20 and (ext in [".pdf", ".md", ".json", ""]):
                        sample_paths.append((item.get("type"), path))
                print("Top directories:", sorted(list(top_dirs))[:15])
                print("Extensions:", extensions)
                print("Sample files:")
                for t, p in sample_paths[:10]:
                    print(f"  [{t}] {p}")
        except Exception as e2:
            print(f"Error fetching {repo} main: {e2}")
