import urllib.request

url = "https://boards10.github.io/papers/english/01_2026_main_set1.pdf"
headers = {"User-Agent": "Mozilla/5.0"}
try:
    resp = urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=10)
    data = resp.read(100)
    print("OK:", resp.status, "Magic bytes:", data[:10])
except Exception as e:
    print("Direct failed:", e)
    # Try raw github
    url2 = "https://raw.githubusercontent.com/boards10/boards10.github.io/main/papers/english/01_2026_main_set1.pdf"
    try:
        resp2 = urllib.request.urlopen(urllib.request.Request(url2, headers=headers), timeout=10)
        data2 = resp2.read(100)
        print("Raw OK:", resp2.status, "Magic bytes:", data2[:10])
    except Exception as e2:
        print("Raw failed:", e2)
