import urllib.request, json

headers = {"User-Agent": "Mozilla/5.0"}
url = "https://api.github.com/repos/Shabber10/ALL-PYQ-Papers/git/trees/main?recursive=1"
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=30) as resp:
    data = json.loads(resp.read().decode())
    tree = data.get("tree", [])

prelims = [x["path"] for x in tree if "prelim" in x["path"].lower() and x["path"].endswith(".pdf")]
print("Prelims count:", len(prelims))
for p in prelims:
    print(" ", p)
