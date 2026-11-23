import urllib.request

url = "https://boards10.github.io/papers/english/01_2026_main_set1.pdf"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        print("Status:", resp.status)
        print("Content-Type:", resp.headers.get('Content-Type'))
        content = resp.read()
        print("Length:", len(content))
        print("Header:", content[:30])
except Exception as e:
    print("Fetch error:", e)

# Also test raw.githubusercontent.com
url2 = "https://raw.githubusercontent.com/boards10/boards10.github.io/main/papers/english/01_2026_main_set1.pdf"
req2 = urllib.request.Request(url2, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
try:
    with urllib.request.urlopen(req2, timeout=10) as resp:
        print("\nRaw Status:", resp.status)
        content2 = resp.read()
        print("Raw Length:", len(content2))
except Exception as e:
    print("Raw Fetch error:", e)
