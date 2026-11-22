import urllib.request

headers = {"User-Agent": "Mozilla/5.0"}
url = "https://raw.githubusercontent.com/Shabber10/ALL-PYQ-Papers/main/README.md"
req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        content = resp.read().decode('utf-8', errors='ignore')
        print(content[2500:])
except Exception as e:
    print("Error:", e)
