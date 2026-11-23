import urllib.request, urllib.parse

url = "https://raw.githubusercontent.com/Shabber10/ALL-PYQ-Papers/main/Boards/CBSE/10/2026/CBSE-Class-10-2026-mathematics.pdf"
safe_url = urllib.parse.quote(url, safe=":/%?=&")
print("Original:", url)
print("Safe URL:", safe_url)

req = urllib.request.Request(
    safe_url,
    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
)
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        print("Status:", resp.status)
        data = resp.read()
        print("Length:", len(data))
except Exception as e:
    print("Error:", e)
