import urllib.request

url = "https://raw.githubusercontent.com/gadepall/cbse-papers/master/papers/cs/2015.pdf"
req = urllib.request.Request(url, headers={"User-Agent": "ExamVault-Bot"})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        content = resp.read()
        print(f"gadepall 2015 CS paper fetched: {len(content)} bytes, header: {content[:20]}")
except Exception as e:
    print("gadepall fetch error:", e)

url2 = "https://raw.githubusercontent.com/gadepall/cbse-papers/master/papers/math/10/2018/1.pdf"
req2 = urllib.request.Request(url2, headers={"User-Agent": "ExamVault-Bot"})
try:
    with urllib.request.urlopen(req2, timeout=10) as resp:
        content2 = resp.read()
        print(f"gadepall 2018 Math 10 paper fetched: {len(content2)} bytes, header: {content2[:20]}")
except Exception as e:
    print("gadepall math 10 fetch error:", e)
