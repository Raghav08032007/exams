import urllib.request, re

url = "https://boards10.github.io/cbse-class-10-maths-pyq.html"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, timeout=10) as resp:
    html = resp.read().decode('utf-8', errors='ignore')
    links = re.findall(r'href=[\'"]([^\'"]+)[\'"]', html, re.I)
    print(f"Total links: {len(links)}")
    for l in links[:30]:
        print("  ", l)
