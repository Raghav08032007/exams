import urllib.request, json

url = "https://raw.githubusercontent.com/boards10/boards10.github.io/main/final_meta.json"
req = urllib.request.Request(url, headers={"User-Agent": "ExamVault-Bot"})
with urllib.request.urlopen(req, timeout=10) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    print(f"final_meta.json loaded! Type: {type(data)}")
    if isinstance(data, list):
        print(f"Total entries: {len(data)}")
        for it in data[:10]:
            print("  ", it)
    elif isinstance(data, dict):
        print("Keys:", list(data.keys())[:20])
        for k in list(data.keys())[:5]:
            print(f"  {k}: {data[k]}")
