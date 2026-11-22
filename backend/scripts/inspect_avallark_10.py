import urllib.request
import json

headers = {"User-Agent": "Mozilla/5.0"}
url = "https://api.github.com/repos/avallark/NCERT-TextBooks/contents/10"
req = urllib.request.Request(url, headers=headers)

try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        items = json.loads(resp.read().decode())
        print(f"Found {len(items)} items in folder 10:")
        for item in items:
            print(" -", item["name"], "| download_url:", item.get("download_url"))
except Exception as e:
    print("Error:", e)
