import urllib.request
import json

headers = {"User-Agent": "Mozilla/5.0"}
url = "https://api.github.com/repos/manjunath5496/NCERT-Books/contents"
req = urllib.request.Request(url, headers=headers)

try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        items = json.loads(resp.read().decode())
        print(f"Found {len(items)} top-level items in manjunath5496/NCERT-Books:")
        for item in items[:15]:
            print(" -", item["name"], "|", item["type"])
except Exception as e:
    print("Error:", e)
