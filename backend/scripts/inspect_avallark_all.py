import urllib.request
import json

headers = {"User-Agent": "Mozilla/5.0"}
for fld in ['8', '9', '11']:
    url = f"https://api.github.com/repos/avallark/NCERT-TextBooks/contents/{fld}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            items = json.loads(resp.read().decode())
            print(f"\n--- Folder {fld} ({len(items)} books) ---")
            for item in items:
                print(" -", item["name"])
    except Exception as e:
        print(f"Error {fld}:", e)
