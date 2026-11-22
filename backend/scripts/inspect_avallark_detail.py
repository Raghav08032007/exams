import urllib.request, json

headers = {"User-Agent": "Mozilla/5.0"}
url = "https://api.github.com/repos/avallark/NCERT-TextBooks/git/trees/master?recursive=1"
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=30) as resp:
    data = json.loads(resp.read().decode())
    tree = data.get("tree", [])

pdfs = [x["path"] for x in tree if x["path"].lower().endswith(".pdf")]
print(f"Total PDFs in avallark: {len(pdfs)}")

# Group by folder
folders = {}
for p in pdfs:
    folder = p.split("/")[0]
    folders[folder] = folders.get(folder, 0) + 1

print("Folders:", folders)
for f in sorted(folders.keys()):
    sample = [p for p in pdfs if p.startswith(f)][:5]
    print(f"\n--- Folder {f} ({folders[f]} PDFs) ---")
    for s in sample:
        print(" ", s)
